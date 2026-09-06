import csv
import heapq
import time
import os
## New Dijkstra
def find_fastest_path(rail_graph, start_station, destination_station, verbose=False):

    distances = {station: float("inf") for station in rail_graph}
    distances[start_station] = 0

    #initialize previous table to store breadcrumbs
    previous = {station: None for station in rail_graph}

    #initialize visited set
    visited = set()

    #initialize the priority queue
    priority_queue = []
    heapq.heappush(priority_queue, (0, start_station))

    #start the dispatch timer
    dispatch_start_time = time.perf_counter()

    #Begin Dijkstra's search
    while priority_queue:
        current_distance, current_station = heapq.heappop(priority_queue)

        #Skip stations we've already processed
        if current_station in visited:
            continue
        #Mark this station as complete
        visited.add(current_station)

        if verbose:
            print()
            print(f"Now exploring: {current_station}")
            print(f"Current travel time: {current_distance} minutes")

        # Explore neighboring stations
        for neighbor, travel_time in rail_graph[current_station].items():
            new_distance = current_distance + travel_time

            if verbose:
                print(f"Neighbor: {neighbor} -> {travel_time} minutes"
                      f"| New Distance: {new_distance} minutes")

            #If the new route is faster than the current
            #best-known route, update our records
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current_station
                heapq.heappush(priority_queue, (new_distance, neighbor))

    #____________________________________________________
    #STOP the dispatch timer
    dispatch_end_time = time.perf_counter()
    elapsed_seconds = dispatch_end_time - dispatch_start_time

    #Reconstruct the path from destination back to start
    path = []
    station = destination_station

    while station is not None:
        path.append(station)
        station = previous.get(station)

    path.reverse()

    reachable = distances.get(destination_station, float("inf")) != float("inf")

    if not reachable:
        path = []

    return {
        "distances": distances,
        "previous": previous,
        "path": path,
        "total_time": distances.get(destination_station, float("inf")),
        "elapsed_seconds": elapsed_seconds,
        "reachable": reachable,
    }

#Function: Print a clean, aligned summary table
def print_summary_table(dispatch_results):
    '''
    Prints the dispatch results as a clean, aligned table using only f-strings (no external table libraries required.
    Clumn widhts are calculated dynamically so it lines up regardless of how long the station names or ids are.
    :param dispatch_results:
    :return:
    '''

    #Build the row datat first (as strings) so we can measure the widest value in each column
    headers = ["Shipment", "Priority", "Type", "Route", "Type", "Search"]
    rows = []

    for entry in dispatch_results:
        shipment = entry["shipment"]
        result = entry["result"]

        route_str = f"{shipment['origin_station']} -> {shipment['destination_station']}"

        if result["reachable"]:
            time_str = f"{result['total_time']} min"
        else:
            time_str = "UNREACHABLE"

        search_str = f"{result['elapsed_seconds'] * 1000:.4f} ms"

        rows.append([
            shipment["shipment_id"],
            str(shipment["priority"]),
            shipment["shipment_type"],
            route_str,
            time_str,
            search_str
        ])

    #Calculate each column's width = the longest value in that column including its header
    column_widths = []

    for col_index, header in enumerate(headers):
        longest_value = len(header)

        for row in rows:
            longest_value = max(longest_value, len(row[col_index]))

        column_widths.append(longest_value)

    #Build a reusable row-formatting function

    def format_row(values):
        cells = [
            value.ljust(column_widths[i]) for i, value in enumerate(values)
        ]
        return ' | '.join(cells)

    divider = "-+-".join("-" * width for width in column_widths)

    #Print the table
    print(format_row(headers))
    print(divider)

    for row in rows:
        print(format_row(row))
#Function: Dispatch every shipment once, in priority order
def run_dispatch(rail_graph, shipments, verbose=False):

    '''
Run find_fatest_path() nce for every shipment in the order they're already sorted (priority order). Returns (dispat_Results, total_run_elapsed)
where total_run_elapsed is the wall-clock time for the whole batch
    '''

    dispatch_results = []
    run_start_time = time.perf_counter()

    for shipment in shipments:
        start_station = shipment["origin_station"]
        destination_station = shipment["destination_station"]

        result = find_fastest_path(
            rail_graph, start_station, destination_station, verbose=verbose
         )

        dispatch_results.append({"shipment": shipment, "result": result})

    run_end_time = time.perf_counter()
    total_run_elapsed = run_end_time - run_start_time

    return dispatch_results, total_run_elapsed

#Function: Load a CSV

def load_csv(filename):
    data = []

    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data
def export_dispatch_results_csv(dispatch_results, filename="dispatch_results.csv"):

    full_path = os.path.abspath(filename)
    print(f"\nDispatch results exported to: {filename}")
    print(f"Full file location: {full_path}")

    #function: export performance test results to csv file
def export_performance_results_csv(run_times_ms, filename="performance_results.csv"):

    fieldnames = ["run_number", "elapsed_ms"]

    with open(filename,"w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for run_number, elapsed_ms in enumerate(run_times_ms, start=1):
            writer.writerow({"run_number": run_number,
                             "elapsed_ms": f"{elapsed_ms:.4f}",
                             })
        #Append summary stats as extra rows at the bottom
        average_run_ms = sum(run_times_ms) / len(run_times_ms)
        variance = sum((t - average_run_ms)**2 for t in run_times_ms) / len(run_times_ms)
        std_dev_ms = variance ** 0.5

        writer.writerow({"run_number": "fastest", "elapsed_ms": f"{min(run_times_ms):.4f}"})
        writer.writerow({"run_number": "slowest", "elapsed_ms": f"{max(run_times_ms):.4f}"})
        writer.writerow({"run_number": "average", "elapsed_ms": f"{average_run_ms:.4f}"})
        writer.writerow({"run_number": "std_dev", "elapsed_ms": f"{std_dev_ms:.4f}"})

        full_path = os.path.abspath(filename)
        print(f"Performance results exported to: {filename}")
        print(f"Full file location: {full_path}")


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
    print("\nNo shipmnents are available for route planning")

#Dispatch: Every shipment by priority, one at a time
print("\n" + "=" * 40)
print("BEGINNING FULL DISPATH RUN")
print("=" * 40)

dispatch_results = []
run_start_time = time.perf_counter()

for shipment in shipments:
    start_station = shipment["origin_station"]
    destination_station = shipment["destination_station"]

    #Set verbose=True if you want the full statation-by-station
    #exploration log printed for every shipment
    result = find_fastest_path(rail_graph, start_station, destination_station, verbose=False)

    dispatch_results.append({"shipment": shipment, "result": result})

run_end_time = time.perf_counter()
total_run_elapsed = run_end_time - run_start_time

#Display program Summary details
print("\nDisplay run summary")
print("=" * 40)
print_summary_table(dispatch_results)

print()
print(f"Shipment dispatched: {len(dispatch_results)}")
print(f"Total run time: {total_run_elapsed * 1000:.4f} ms "
      f"){total_run_elapsed:.6f} seconds)")

if dispatch_results:
    average_ms = (
        sum(entry["result"]["elapsed_seconds"] for entry in dispatch_results)
        / len(dispatch_results)
        * 1000
    )
print(f"Average search time per shipment: {average_ms:.4f} ms ")
print("=" * 40)

#Performance Test: Run the full dispatch batch 10 times
#this repeats the entire disptach run (several tiomes back to back)

PERFORMANCE_TEST_RUNS = 10
print("\n" + "=" * 40)
print(f"PERFORMANCE_TEST_RUNS: {PERFORMANCE_TEST_RUNS} RUNS")

run_times_ms = []

for run_number in range(1, PERFORMANCE_TEST_RUNS + 1):
    #Verbose=False her too - we only want timing, not the trace
    _, run_elapsed = run_dispatch(rail_graph, shipments, verbose=False)
    run_elapsed_ms = run_elapsed * 1000
    run_times_ms.append(run_elapsed_ms)

    print(f"Run {run_number:>2}: {run_elapsed_ms:.4f} ns "
          f"({len(shipments)} shipments)")

# Summarize the performance test results
fastest_run_ms = min(run_times_ms)
slowest_run_ms = max(run_times_ms)
average_run_ms = sum(run_times_ms) / len(run_times_ms)

# simple population standard deviation, to show consistency
variance = sum((t - average_run_ms)**2 for t in run_times_ms) / len(run_times_ms)
std_dev_ms = variance ** 0.5

print("_" * 40)
print(f"FASTEST RUN: {fastest_run_ms:.4f} ms ")
print(f"SLOWEST RUN: {slowest_run_ms:.4f} ms ")
print(f"AVG. RUN: {average_run_ms:.4f} ms ")
print(f"STD. RUN: {std_dev_ms:.4f} ms ")


#Export the performance test results to a CSV file
export_performance_results_csv(run_times_ms, filename="performance_results.csv")