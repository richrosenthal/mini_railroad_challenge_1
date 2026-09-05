# Graph terminology for this project:
#
#     Graph Term       |    Railroad Meaning
#     Vertex(Node)     |    Train Station
#     Edge             |    Railroad Track time
#     Weight           |    Travel Time
#     Path             |    Route
#     Neighbor         |    Connected Station
import csv
def load_csv(filename):
    data = []
    with open(filename, newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            data.append(row)
        return data

rail_graph = {}

with open("rail_network.csv", newline="") as file:
    reader = csv.DictReader(file)
    for row in reader:
        origin = row["start_station"]
        destination = row["end_station"]

        #read the track time and delay from the CSV
        track_time =int(row["travel_time_minutes"])
        delay=int(row["delay_minutes"])

        total_travel_time = track_time + delay

        #Add the stations if they are not already in the graph
        if origin not in rail_graph:
            rail_graph[origin] = {}

        if destination not in rail_graph:
            rail_graph[destination] = {}

        #Add the connection in both directions
        rail_graph[origin][destination] = total_travel_time
        rail_graph[destination][origin] = total_travel_time
print(rail_graph)