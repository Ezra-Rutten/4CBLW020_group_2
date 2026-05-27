import geopandas as gpd
import pandas as pd
import glob
import os


def build_lsoa_map(
    shp_path: str = "../data/LB_shp",
    stations_path: str = "../data/shape/police_stations.csv",
    output_path: str = "../data/shape/lsoa_station_map.csv"
):
    base_path = shp_path
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

    stations_df = pd.read_csv(stations_path)

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

    lsoa_station_map = lsoa_with_station[["LSOA21CD", "station", "distance_to_station"]]
    lsoa_station_map.to_csv(output_path, index=False)
    print(f"Saved LSOA-to-station map to {output_path}")


if __name__ == "__main__":
    build_lsoa_map()