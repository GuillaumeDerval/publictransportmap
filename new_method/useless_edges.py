import json

data = json.load(open("../train_bus_simplified.json"))
walking_time = json.load(open("../distance_walking.json"))

walking_time = {x: {y: t for t,y in z} for x,z in walking_time.items()}

c = 0
t = 0
for x in data:
    for y, ta, tb in data[x]["nei"]:
        if y in walking_time[x] and tb - ta >= walking_time[x][y]:
            print(x, y, tb-ta, walking_time[x][y])
            c += 1
        t += 1
print(c)
print(t)