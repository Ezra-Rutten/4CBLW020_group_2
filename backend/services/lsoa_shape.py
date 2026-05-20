import requests
import csv
import time
import pandas as pd
from shapely.geometry import Point
import requests
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import json
import csv
import time
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import geopandas as gpd
import matplotlib.pyplot as plt
import glob
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from pathlib import Path


# Reading LSOA shapes
base_path = "../data/LB_shp"
shapefiles = glob.glob(os.path.join(base_path, "**/*.shp"), recursive=True)
print(f"Found {len(shapefiles)} borough shapefiles")
lsoa_gdfs = [gpd.read_file(shp) for shp in shapefiles]
lsoa_london = gpd.GeoDataFrame(
    pd.concat(lsoa_gdfs, ignore_index=True),
    crs=lsoa_gdfs[0].crs
)

lsoa_london = lsoa_london.to_crs(epsg=27700)

lsoa_london["centroid"] = lsoa_london.geometry.centroid
lsoa_centroids = lsoa_london.set_geometry("centroid")

stations_df = pd.read_csv("../data/shape/metropolitan_police_stations.csv")

stations_gdf = gpd.GeoDataFrame(
    stations_df,
    geometry=gpd.points_from_xy(
        stations_df.longitude,
        stations_df.latitude
    ),
    crs="EPSG:4326"
).to_crs(epsg=27700)

lsoa_with_station = gpd.sjoin_nearest(
    lsoa_centroids,
    stations_gdf,
    how="left",
    distance_col="distance_to_station"
)

lsoa_station_map = lsoa_with_station[
    ["lsoa21cd", "station", "distance_to_station"]
]

lsoa_station_map.to_csv("../data/shape/lsoa_station_map.csv", index=False)
