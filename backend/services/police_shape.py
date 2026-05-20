import requests
import csv
import time
import requests
import csv
import time
from pathlib import Path

stations = [
    ("Acton Police Station", "W3 9BH"),
    ("Barking Learning Centre", "IG11 7NB"),
    ("Bethnal Green Police Station", "E2 9NZ"),
    ("Bexleyheath Police Station", "DA7 4QS"),
    ("Brixton Police Station", "SW9 7DD"),
    ("Bromley Police Station", "BR1 1ER"),
    ("Charing Cross Police Station", "WC2N 4JP"),
    ("Chingford Police Station", "E4 7EA"),
    ("Colindale Police Station", "NW9 5TW"),
    ("Croydon Police Station", "CR9 1BP"),
    ("Dagenham Police Station", "RM10 7TU"),
    ("Edmonton Police Station", "N9 0PW"),
    ("Forest Gate Police Station", "E7 8BS"),
    ("Hammersmith Police Station", "W6 7NX"),
    ("Harrow Police Station", "HA2 0DN"),
    ("Hayes Police Station", "UB4 8HU"),
    ("Hounslow Police Station", "TW3 1LB"),
    ("Ilford Police Station", "IG1 1GT"),
    ("Islington Police Station", "N1 0YY"),
    ("Kensington Police Station", "W8 6EQ"),
    ("Kentish Town Police Station", "NW5 3AE"),
    ("Kingston Police Station", "KT1 1LB"),
    ("Lavender Hill Police Station", "SW11 1JX"),
    ("Lewisham Police Station", "SE13 5JZ"),
    ("Mitcham Police Station", "CR4 4LA"),
    ("Plumstead Police Station", "SE18 1JY"),
    ("Romford Police Station", "RM1 3BJ"),
    ("Stoke Newington Police Station", "N16 8DS"),
    ("Sutton Police Station", "SM1 4RF"),
    ("Tottenham Police Station", "N17 9ES"),
    ("Twickenham Police Station", "TW1 3SY"),
    ("Walworth Police Station", "SE17 3BB"),
    ("Wembley Police Station", "HA0 2HH"),
    ("Wimbledon Police Station", "SW19 8NN")
]

Path("../data/shape").mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = "../data/shape/metropolitan_police_stations.csv"

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