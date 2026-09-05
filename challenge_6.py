import csv

#Function: Load a CSV

def load_csv(filename):
    data = []

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Load the CSVs
trains = load_csv("train.csv")
shipment_priorities = load_csv("shipment_priority.csv")
rail_connections = load_csv("rail_network_map.csv")
shipments = load_csv("shipments.csv")

# Display File-Loading Summary
print("Python Rail System")
print("=" * 40)
print(f"Trains loaded: {len(trains)}")
print(f"Shipment priorities loaded: {len(shipment_priorities)}")
print(f"Rail connections loaded: {len(rail_connections)}")
print(f"Shipments loaded: {len(shipments)}")
print()
print("Ready for route planning")

# Create the priority lookup dictionary
#Priority Lookup
priority_lookup = {}
for priority_row in shipment_priorities:
    shipment_type = priority_row["shipment_type"]
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


# Display Shipments after sorting
print("\nShipments sorted by priority")
print("=" * 40)
for shipment in shipments:
    print(
        f"Priority: {shipment['priority']} | "
        f"{shipment['shipment_id']} | "
        f"{shipment['shipment_type']} | "
        f"{shipment['origin_station']} | -> "
        f"{shipment['destination_station']} | "
    )
#Build the graph
rail_graph = {}

for connection in rail_connections:
    origin = connection["start_station"]
    destination = connection["end_station"]

    #Read the track time and delay from csv
    track_time = int(connection["travel_time_minutes"])
    delay = int(connection["delay_minutes"])

    # Calculate the total time for this railroad connection
    total_travel_time = track_time + delay

    #Add the stations if they are not already in the graph
    if origin not in rail_graph:
        rail_graph[origin] = {}

    if destination not in rail_graph:
        rail_graph[destination] = {}
    # Add the connection in both direction
    rail_graph[origin][destination] = total_travel_time
    rail_graph[destination][origin] = total_travel_time

#Display the railroad graph
print("\nRailraod Network")
print("=" * 40)

for station, connections in rail_graph.items():
    print(f"\nStation: {station}")

    for neighbor, travel_time in connections.items():
        print(f" -> {neighbor} -> {travel_time} total minutes")


#Select the Next Shipment for Route Planning
#Beachse the hsipment list is sorted, index 0 contains
# the hsipment with teheihghest priority

if shipments:
    current_shipment = shipments[0]

    start_station = shipments[0]["origin_station"]
    destination_station = current_shipment["destination_station"]

    print("\nNEXT SHIPMENT TO ROUTE")
    print("=" * 40)
    print(f"Shipment ID: {current_shipment['shipment_id']}")
    print(f"Shipment Type: {current_shipment['shipment_type']}")
    print(f"Shipment Priority: {current_shipment['priority']}")
    print(f"Route: {start_station} -> {destination_station}")
else:
    print("\nNo shipmnents are available")