import time
import math
import sqlite3

import cv2
import urllib
import numpy as np

from PIL import Image
from pathlib import Path


RADIUS = 6378137 # Радиус Земли
EQUATOR = 40075016.685578488 # Длина Экватора
DELAY = 0.03
E = 0.0818191908426 # Эксцентриситет
E2 = 0.00669437999014 # Эксцентриситет в квадрате
zoom = 20


def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 1 << zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile + 924


def concat_3x3_imgs(imgs):
    assert 3 == len(imgs), print(len(imgs))
    assert 3 == len(imgs[0]), len(imgs[0])
    img = imgs[0][0]
    width, height, channels = img.shape
    new_im = Image.new('RGB', (width * 3, height * 3))
    for i in range(3):
        for j in range(3):
            img = Image.frombytes(mode='RGB', size=(width, height), data=imgs[i][j])
            new_im.paste(img, box=(width * i, height * j))
    return new_im


def create_3x3_tile(x, y, zoom=20):
    imgs = []
    for idx_x in [x - 1, x, x + 1]:
        for idx_y in [y - 1, y, y + 1]:
             imgs.append(get_tile(idx_x, idx_y, zoom))
    imgs = np.array(imgs)
    imgs = imgs.reshape(3, 3, 256, 256, 3)
    img_3x3 = concat_3x3_imgs(imgs)
    return img_3x3


def create_3x3_tiles_from_sqlite_chunk(path_to_chunk: Path, imgs_save_path: Path):
    try:
        con = sqlite3.connect(path_to_chunk)
        cur = con.cursor()
        cur.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name;")
        res = cur.execute('select min(x), max(x), min(y), max(y) from t')
    except:
        con.close()
        return

    from_x, to_x, from_y, to_y = res.fetchone()

    imgs_save_path.mkdir(exist_ok=True)

    for x in range(from_x, to_x - 1):
        for y in range(from_y, to_y - 1):
            res = cur.execute(f"""select b from t where 
                                t.x in ({x}, {x + 1}, {x + 2}) 
                                and 
                                t.y in ({y}, {y + 1}, {y + 2})""")
            imgs = res.fetchall()
            imgs = np.array(imgs)
            imgs = imgs.reshape((3,3))
            img_3x3 = concat_3x3_imgs(imgs)
            img_name = Path(f'{x + 1}_{y + 1}.jpg')
            img_3x3.save(imgs_save_path / img_name)
    con.close()


def get_tile(x, y, zoom=20):
    # download the image, convert it to a NumPy array, and then read
    # it into OpenCV format
    time.sleep(DELAY)
    url = f'https://core-sat.maps.yandex.net/tiles?l=sat&v=3.1079.0&x={x}&y={y}&z={zoom}&scale=2&lang=ru_RU'
    # print(url)
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # return the image
    return image