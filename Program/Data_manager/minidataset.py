import csv
import json
#import geojson
from geojson import dump
from Program.Data_manager.main import PATH_BELGIUM, PATH


def reduce_rsd_work(arrondissement):
    with open(PATH_BELGIUM.RSD_WORK, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='|')
        with open(PATH.RSD_WORK, mode='w') as out:
            writer = csv.DictWriter(out, fieldnames=reader.fieldnames, delimiter='|')
            writer.writeheader()
            refnis = []
            for row in reader:
                resid = row["TX_ADM_DSTR_WORK_DESCR_FR"]
                work = row["TX_ADM_DSTR_RESIDENCE_DESCR_FR"]
                if resid == arrondissement and work == arrondissement:
                    writer.writerow(row)
                    refnisRsd = row["CD_MUNTY_REFNIS_RESIDENCE"]
                    refnisWork = row["CD_MUNTY_REFNIS_WORK"]
                    if refnisRsd not in refnis: refnis.append(refnisRsd)
                    if refnisWork not in refnis: refnis.append(refnisWork)

    return refnis



#geojson
def reduce_map(refnis_list):
    with open(PATH_BELGIUM.MAP_SHAPE) as f:

        features = json.load(f)["features"]
        feature_collection = []  # key = refnis
        for elem in features:
            refnis = str(elem["properties"]["CD_MUNTY_REFNIS"])
            if refnis in refnis_list:
                feature_collection.append(elem)

    out = {
            'type': 'FeatureCollection',
            "features": feature_collection
        }
    with open(PATH.MAP_SHAPE, 'w') as w:
        dump(out, w)





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





