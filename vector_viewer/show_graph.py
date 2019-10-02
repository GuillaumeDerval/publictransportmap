import orjson

def show(inf, outf, only_sncb=False):
    data = orjson.loads(open(inf).read())
    out = {
        'type': 'FeatureCollection',
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        data[x]["lon"],
                        data[x]["lat"]
                    ]
                },
                "properties": {
                    "name": data[x]["name"],
                    "idx": x
                }
            }
            for x in data
            if (not only_sncb or x.startswith("sncb"))
        ]
    }
    with open(outf, 'wb') as geojson_distfile:
        geojson_distfile.write(orjson.dumps(out))

show("../produce/train_bus_simplified.json", "../produce/stations_loc.json", True)