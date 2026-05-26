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
    ("Acton Police Station", "W3 9BH"),
    ("Bethnal Green Police Station", "E2 9NZ"),
    ("Brixton Police Station", "SW9 7DD"),
    ("Bromley Police Station", "BR1 1ER"),
    ("Charing Cross Police Station", "WC2N 4JP"),
    ("Chingford Police Station", "E4 7EA"),
    ("Colindale Police Station", "NW9 5TW"),
    ("Croydon Police Station", "CR9 1BP"),
    ("Dagenham Police Station", "RM10 7TU"),
    ("Edmonton Police Station", "N9 0PW"),
    ("Hammersmith Police Station", "W6 7NX"),
    ("Hayes Police Station", "UB4 8HU"),
    ("Islington Police Station", "N1 0YY"),
    ("Lavender Hill Police Station", "SW11 1JX"),
    ("Lewisham Police Station", "SE13 5JZ"),
    ("Plumstead Police Station", "SE18 1JY"),
    ("Stoke Newington Police Station", "N16 8DS"),
    ("Sutton Police Station", "SM1 4RF"),
    ("Stratford Police Station", "E15 4SG"),
    ("Twickenham Police Station", "TW1 3SY"),
    ("Walworth Police Station", "SE17 3BB"),
    ("Wembley Police Station", "HA0 2HH"),
    # Birmingham
    ("Bournville Police Station", "B30 1QX"),
    ("Stechford Police Station", "B33 8RR"),
    ("Sutton Coldfield Police Station", "B74 2NR"),
    ("Coventry Central Police Station", "CV1 2JX"),
    ("Brierley Hill Police Station", "DY5 3DH"),
    ("West Bromwich Police Station", "B70 8HS"),
    ("Solihull Police Station", "B91 3QL"),
    ("Bloxwich Police Station", "WS3 2PD"),
    ("Wolverhampton Police Station", "WV1 3AA"),
    # Leeds
    ("Leeds District HQ Police Station", "LS11 8BU"),
    ("Wakefield District HQ Police Station", "WF6 1FD"),
    ("Bradford District HQ Police Station", "BD5 0DZ"),
    ("Halifax District HQ Police Station", "HX1 5TW"),
    ("Kirklees District HQ Police Station", "HD1 2NJ"),
    # Sheffield
    ("Snig Hill Police Station", "S3 8LY"),
    ("Rotherham Police Station", "S60 1QY"),
    ("Barnsley Police Station", "S70 2DL"),
    ("Doncaster Police Station", "DN1 3HX"),
    # Liverpool
    ("St Annes Street Police Station", "L3 3HJ"),
    ("Birkenhead Police Station", "CH41 5EU"),
    ("Huyton Police Station", "L36 9XU"),
    ("St Helens Police Station", "WA10 1TG"),
    ("Southport Police Station", "PR9 0LL"),
    ("Admiral Street Police Station", "L8 8JN"),
    ("Wallasey Police Station", "CH44 1DA"),
    ("Kirkby Police Station", "L32 8RF"),
    ("Newton-Le-Willows Police Station", "WA12 9BW"),
    ("Marsh Lane Police Station", "L20 5BW")
]

OUTPUT_FILE = "police_stations.csv"

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["station", "postcode", "latitude", "longitude"])

    for name, postcode in stations:
        url = f"https://api.postcodes.io/postcodes/{postcode}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()["result"]
            latitude = data["latitude"]
            longitude = data["longitude"]
            writer.writerow([name, postcode, latitude, longitude])
        else:
            writer.writerow([name, postcode, None, None])
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