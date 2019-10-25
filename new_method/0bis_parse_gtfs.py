import csv
import datetime
import json
import os

"""####################################################################################################################
Convert the data with format GTFS into a json with the form :
{
        "id_train": {
             name: "name of the stop",
             lat: 0.0
             lon: 0.0
             nei: [
                 ["id_dest_1", departure_time_1, arrival_time_1},
                 ["id_dest_2", departure_time_2, arrival_time_2},
                 ...
             ]
         }
     }
          
departure_time and arrival_time are given in seconds   
            
Time : update the date  


in  : ../gts/*

    Localisation of data :  put respectively the GTFS sncb,stib,tec, delijn 
                        in the folder ../gtfs/sncb, ../gtfs/stib, ../gtfs/tec, ../gtfs/delijn

out :   ../produce/train_only.json
        ../produce/bus_only.json
        ../produce/train_bus.json  
#######################################################################################################################                                               
"""





"""
Return a list of the service_ids done at given date 
"""
def get_service_ids(folder, date):
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    str_format = date.isoformat().replace("-", "")
    int_format = int(str_format)

    out = set()

    if os.path.exists(os.path.join(folder, "calendar.txt")):
        with open(os.path.join(folder, "calendar.txt"), newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if int(row["start_date"]) <= int_format <= int(row["end_date"]):
                    if row[weekdays[date.weekday()]] == "1":
                        out.add(row["service_id"])

    with open(os.path.join(folder, "calendar_dates.txt"), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["date"] == str_format:
                if row["exception_type"] == "1":
                    out.add(row["service_id"])
                elif row["service_id"] in out:
                    out.remove(row["service_id"])

    return out



"""
Return a list of trip_ids done by the TC contained in the seviceId list
"""
def get_trip_ids(folder, services_id):
    services_id = set(services_id)
    with open(os.path.join(folder, "trips.txt"), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["service_id"] in services_id:
                yield (row["trip_id"], row["route_id"])


"""
Return  out      : list of  n°stop_id   parent_station      if parent station
                            n°stop_id   { name , lat ,lon}
        resolver : list of  n°stop_id   stop_id   
"""
def get_stops(folder):
    out = {}
    resolver = {}
    with open(os.path.join(folder, "stops.txt"), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if "parent_station" in row and row["parent_station"] != "":
                resolver[row["stop_id"]] = row["parent_station"]
            else:
                resolver[row["stop_id"]] = row["stop_id"]
                out[row["stop_id"]] = {"name": row["stop_name"],
                                       "lat": float(row["stop_lat"]),
                                       "lon": float(row["stop_lon"])}
    return out, resolver


"""
return : n°trip_ids    a list of [n°stop_sequence stop_id, arrival_time, departure_time ]    
"""
def get_trip_contents(folder, trip_ids, stop_id_resolver):
    trip_ids = set(trip_ids)
    out = {}
    with open(os.path.join(folder, "stop_times.txt"), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row["trip_id"] in trip_ids:
                if row["trip_id"] not in out:
                    out[row["trip_id"]] = {}
                out[row["trip_id"]][int(row["stop_sequence"])] = (stop_id_resolver[row["stop_id"]], row["arrival_time"], row["departure_time"])
    out = {x: [z[1] for z in sorted(y.items())] for x, y in out.items()}
    return out






"""
transform hh:mm:ss into a time givent in second
"""
def time_str_to_int(time):
    a, b, c = [int(x) for x in time.split(":")]
    return ((a*60)+b)*60+c


def generate_output_for_gtfs(folder, prefix, date):
    # The output is in the form:
    # {
    #     "id": {
    #         name: "name of the stop",
    #         lat: 0.0
    #         lon: 0.0
    #         nei: [
    #             ["id_dest_1", departure_time_1, arrival_time_1},
    #             ["id_dest_2", departure_time_2, arrival_time_2},
    #             ...
    #         ]
    #     }
    # }
    service_ids = list(get_service_ids(folder, date))
    print("service id,  ", service_ids)
    trip_ids = list(get_trip_ids(folder, service_ids))
    print([x[0] for x in trip_ids if x[1] == "X9150-16922"])
    stops, stop_id_resolver = get_stops(folder)
    trip_contents = get_trip_contents(folder, [x[0] for x in trip_ids], stop_id_resolver)


    minimal = 1000

    for idx in stops:
        stops[idx]["nei"] = []
    for trip_id in trip_contents:
        for idx in range(0, len(trip_contents[trip_id])-1):
            cur_stop_id, pre_arrival, departure = trip_contents[trip_id][idx]
            next_stop_id, arrival, _ = trip_contents[trip_id][idx+1]

            minimal = min(minimal, time_str_to_int(arrival)-time_str_to_int(departure))

            # note: it is possible that departure == arrival.
            stops[cur_stop_id]["nei"].append([prefix + next_stop_id, time_str_to_int(departure), time_str_to_int(arrival)])
    for idx in stops:
        stops[idx]["nei"] = sorted(stops[idx]["nei"], key=lambda x: x[1])

    print("minimum stop duration {}".format(minimal))
    stops = {prefix+x: y for x, y in stops.items()}
    print(len(stops))
    return stops



date = datetime.date(2019, 10, 8)



#produce the json format for each kind of transport in belgium
print("SNCB")
stops_train = generate_output_for_gtfs("../gtfs/sncb", "sncb", date)


stops = {}
""" print("MIVB")
stops.update(generate_output_for_gtfs("../gtfs/stib", "stib", date))
print("TEC")
stops.update(generate_output_for_gtfs("../gtfs/tec", "tec", date))
print("DE LIJN")
stops.update(generate_output_for_gtfs("../gtfs/delijn", "delijn", date))
print("SAVING")
"""
json.dump(stops_train, open("../produce/train_only.json", "w"))
json.dump(stops, open("../produce/bus_only.json", "w"))
stops.update(stops_train)
json.dump(stops, open("../produce/train_bus.json", "w"))
