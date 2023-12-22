import geopandas as gpd

from pathlib import Path
from collections import namedtuple
from tqdm import tqdm

from tile_processor import deg2num, create_3x3_tile

Point = namedtuple('Point', ['lon', 'lat'])

BASKET_COURT_COORD = Path('/Volumes/Expansion/Pet_projects/basket_court_recognition/Data/basketball court_points-2.geojson')
TRAIN_DATA = Path('/Volumes/Expansion/Pet_projects/basket_court_recognition/Data/train_data/')


def create_train_data(tile_coord, save_to):
    save_to = Path(save_to)
    save_to.mkdir(exist_ok=True, parents=True)
    df = gpd.read_file(tile_coord)
    train_points = df.geometry
    for point in tqdm(train_points):
        lat, lon = point.coords[0]
        x, y = deg2num(lon, lat, 20)
        img = create_3x3_tile(x, y)
        img.save(save_to / Path(f'{x}_{y}.png'))

create_train_data(BASKET_COURT_COORD, TRAIN_DATA)