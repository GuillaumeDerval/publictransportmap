import csv
import json
#import geojson
from geojson import dump


with open("data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt", newline='') as csvfile:
    reader = csv.DictReader(csvfile, delimiter='|')
    with open("data/tiny_data/TU_CENSUS_2011_COMMUTERS_MUNTY.txt", mode='w') as out:
        writer = csv.DictWriter(out, fieldnames=reader.fieldnames, delimiter='|')
        writer.writeheader()
        idx = 0
        refnis = []
        for row in reader:
            resid = row["TX_ADM_DSTR_WORK_DESCR_FR"]
            work = row["TX_ADM_DSTR_RESIDENCE_DESCR_FR"]
            if resid == "Arrondissement de Charleroi" and work == "Arrondissement de Charleroi":
                writer.writerow(row)
                refnisRsd = row["CD_MUNTY_REFNIS_RESIDENCE"]
                refnisWork = row["CD_MUNTY_REFNIS_WORK"]
                if refnisRsd not in refnis: refnis.append(refnisRsd)
                if refnisWork not in refnis: refnis.append(refnisWork)





#travel for nivelles
#extract_travel_tiny
data = json.load(open("out_dir/travel_user.json"))
cities = data["cities"]
travel = data["travel"]
small_cities = []
for city in cities:
    if str(city[1]) in refnis:
        small_cities.append(city)
print(small_cities)
small_travel = []
for t in travel:
    if t["residence"] in small_cities and t["work"] in small_cities:
        small_travel.append(t)
small = {"cities": small_cities, "travel": small_travel}
json.dump(small, open("data/tiny_data/travel_user.json", "w"))




#geojson
with open("data/sh_statbel_statistical_sectors.geojson") as f:

    features = json.load(f)["features"]
    feature_collection = []  # key = refnis
    for elem in features:
        refn = str(elem["properties"]["CD_MUNTY_REFNIS"])
        if refn in refnis:
            feature_collection.append(elem)

out = {
        'type': 'FeatureCollection',
        "features": feature_collection
    }
with open('data/tiny_data/sh_statbel_statistical_sectors.geojson', 'w') as w:
    dump(out, w)


