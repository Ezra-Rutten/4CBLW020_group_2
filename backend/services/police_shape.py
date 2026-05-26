import requests
import csv
import time
import pandas as pd
import requests
import csv
import time
import geopandas as gpd
import glob
import os
import geopandas as gpd
import pandas as pd

stations = [
    # London
    ("Acton Police Station", "W3 9BH", "metropolitan"),
    ("Bethnal Green Police Station", "E2 9NZ", "metropolitan"),
    ("Brixton Police Station", "SW9 7DD", "metropolitan"),
    ("Bromley Police Station", "BR1 1ER", "metropolitan"),
    ("Charing Cross Police Station", "WC2N 4JP", "metropolitan"),
    ("Chingford Police Station", "E4 7EA", "metropolitan"),
    ("Colindale Police Station", "NW9 5TW", "metropolitan"),
    ("Croydon Police Station", "CR9 1BP", "metropolitan"),
    ("Dagenham Police Station", "RM10 7TU", "metropolitan"),
    ("Edmonton Police Station", "N9 0PW", "metropolitan"),
    ("Hammersmith Police Station", "W6 7NX", "metropolitan"),
    ("Hayes Police Station", "UB4 8HU", "metropolitan"),
    ("Islington Police Station", "N1 0YY", "metropolitan"),
    ("Lavender Hill Police Station", "SW11 1JX", "metropolitan"),
    ("Lewisham Police Station", "SE13 5JZ", "metropolitan"),
    ("Plumstead Police Station", "SE18 1JY", "metropolitan"),
    ("Stoke Newington Police Station", "N16 8DS", "metropolitan"),
    ("Sutton Police Station", "SM1 4RF", "metropolitan"),
    ("Stratford Police Station", "E15 4SG", "metropolitan"),
    ("Twickenham Police Station", "TW1 3SY", "metropolitan"),
    ("Walworth Police Station", "SE17 3BB", "metropolitan"),
    ("Wembley Police Station", "HA0 2HH", "metropolitan"),
    # Birmingham
    ("Bournville Police Station", "B30 1QX", "west-midlands"),
    ("Stechford Police Station", "B33 8RR", "west-midlands"),
    ("Sutton Coldfield Police Station", "B74 2NR", "west-midlands"),
    ("Coventry Central Police Station", "CV1 2JX", "west-midlands"),
    ("Brierley Hill Police Station", "DY5 3DH", "west-midlands"),
    ("West Bromwich Police Station", "B70 8HS", "west-midlands"),
    ("Solihull Police Station", "B91 3QL", "west-midlands"),
    ("Bloxwich Police Station", "WS3 2PD", "west-midlands"),
    ("Wolverhampton Police Station", "WV1 3AA", "west-midlands"),
    # Leeds
    ("Leeds District HQ Police Station", "LS11 8BU", "west-yorkshire"),
    ("Wakefield District HQ Police Station", "WF6 1FD", "west-yorkshire"),
    ("Bradford District HQ Police Station", "BD5 0DZ", "west-yorkshire"),
    ("Halifax District HQ Police Station", "HX1 5TW", "west-yorkshire"),
    ("Kirklees District HQ Police Station", "HD1 2NJ", "west-yorkshire"),
    # Sheffield
    ("Snig Hill Police Station", "S3 8LY", "south-yorkshire"),
    ("Rotherham Police Station", "S60 1QY", "south-yorkshire"),
    ("Barnsley Police Station", "S70 2DL", "south-yorkshire"),
    ("Doncaster Police Station", "DN1 3HX", "south-yorkshire"),
    # Liverpool
    ("St Annes Street Police Station", "L3 3HJ", "merseyside"),
    ("Birkenhead Police Station", "CH41 5EU", "merseyside"),
    ("Huyton Police Station", "L36 9XU", "merseyside"),
    ("St Helens Police Station", "WA10 1TG", "merseyside"),
    ("Southport Police Station", "PR9 0LL", "merseyside"),
    ("Admiral Street Police Station", "L8 8JN", "merseyside"),
    ("Wallasey Police Station", "CH44 1DA", "merseyside"),
    ("Kirkby Police Station", "L32 8RF", "merseyside"),
    ("Newton-Le-Willows Police Station", "WA12 9BW", "merseyside"),
    ("Marsh Lane Police Station", "L20 5BW", "merseyside")
]

OUTPUT_FILE = "../data/shape/police_stations.csv"

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["station", "postcode", "police_force","latitude", "longitude"])

    for name, postcode, police_force in stations:
        url = f"https://api.postcodes.io/postcodes/{postcode}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()["result"]
            latitude = data["latitude"]
            longitude = data["longitude"]
            writer.writerow([name, postcode, police_force, latitude, longitude])
        else:
            writer.writerow([name, postcode, police_force, None, None])
        time.sleep(0.2)
    
print(f"\nDataset written to {OUTPUT_FILE}")

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

stations_df = pd.read_csv("police_stations.csv")

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
    ["LSOA21CD", "station", "distance_to_station"]
]
lsoa_station_map.to_csv("../data/shape/lsoa_station_map.csv", index=False)

