import csv # import the csv library



def load_csv(filename):
    data = []
    with open(filename, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(row)
        return data

trains = load_csv("train.csv")
shipments = load_csv("shipments.csv")
shipment_priorities = load_csv("shipment_priority.csv")
rail_connections = load_csv("rail_network.csv")

#Display the loaded data
print("Python Rail Systems")
print("___________________")
print(f"Trains loaded: {len(trains)}")
print(f"Shipments loaded: {len(shipments)}")
print(f"Shipment priorities loaded: {len(shipment_priorities)}")
print(f"Rail connections loaded: {len(rail_connections)}")
print()
print("READY FOR ROUTE PLANNING")