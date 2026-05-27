import requests
import csv
import time


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
    ("Marsh Lane Police Station", "L20 5BW", "merseyside"),
]


def fetch_stations(output_path: str = "../data/shape/police_stations.csv"):
    with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["station", "postcode", "police_force", "latitude", "longitude"])

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

    print(f"\nDataset written to {output_path}")


if __name__ == "__main__":
    fetch_stations()