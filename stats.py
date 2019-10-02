import json

entries = json.load("produce/train_bus_simplified.json")
print("NB STOPS", len(entries.keys()))
print("NB CONNECTIONS", sum([len(entries[x]['nei']) for x in entries]))