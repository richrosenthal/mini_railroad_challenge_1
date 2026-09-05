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


for shipment_priority in shipment_priorities:
    print(
        f"{shipment_priority['shipment_type']} has priority "
        f"{shipment_priority['priority']}."
    )

for shipment in shipments:
    print(shipment)

#Priority Lookup
priority_lookup = {}
for priority_row in shipment_priorities:
    shipment_type = priority_row["shipment_type"]
    #int()conversion - cSV data always in as string so convert "1" to 1 to allow numeric sorting
    priority_number = int(priority_row["priority"])
    priority_lookup[shipment_type] = priority_number

#Add Priority to each shipment using lookup
for shipment in shipments:
    shipment_type = shipment["shipment_type"]
    shipment["priority"] = priority_lookup[shipment_type]

#Sorting shipments by priority
shipments.sort(key=lambda shipment: shipment["priority"])

for shipment in shipments:
    print(shipment)