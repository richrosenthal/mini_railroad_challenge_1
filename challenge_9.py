import csv
import time
import os

import networkx as nx


# ============================================================
# CSV HELPERS
# ============================================================

def load_csv(filename):
    data = []
    with open(filename, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data


def first_existing_key(row, possible_keys, label):
    """Return the first column name that exists in row."""
    for key in possible_keys:
        if key in row:
            return key

    raise KeyError(
        f"Could not find a {label} column. "
        f"Expected one of {possible_keys}. Actual columns: {list(row.keys())}"
    )


# ============================================================
# ROUTING
# ============================================================

def find_fastest_path(rail_graph, start_station, destination_station, verbose=False):
    """Find the fastest path using NetworkX Dijkstra."""
    dispatch_start_time = time.perf_counter()

    try:
        total_time, path = nx.single_source_dijkstra(
            rail_graph,
            source=start_station,
            target=destination_station,
            weight="weight",
        )
        reachable = True

        if verbose:
            print(f"Path found: {' -> '.join(path)}")
            print(f"Total time: {total_time} minutes")

    except (nx.NetworkXNoPath, nx.NodeNotFound):
        total_time = float("inf")
        path = []
        reachable = False

        if verbose:
            print(f"No route: {start_station} -> {destination_station}")

    dispatch_end_time = time.perf_counter()

    return {
        "path": path,
        "total_time": total_time,
        "elapsed_seconds": dispatch_end_time - dispatch_start_time,
        "reachable": reachable,
    }


# ============================================================
# TRAIN STAGING
# ============================================================

def stage_trains(trains):
    """
    Convert CSV train rows into train state objects.

    Every train starts at its original/home station and, after every
    shipment, returns to that same station before it can be dispatched again.
    """
    if not trains:
        return []

    sample = trains[0]

    train_id_key = first_existing_key(
        sample,
        ["train_id", "id", "train_name", "name"],
        "train ID",
    )

    home_station_key = first_existing_key(
        sample,
        [
            "home_station",
            "staging_station",
            "station",
            "starting_station",
            "start_station",
            "current_station",
            "origin_station",
        ],
        "train home/staging station",
    )

    staged = []

    for row in trains:
        staged.append(
            {
                "train_id": row[train_id_key],
                "home_station": row[home_station_key],
                "current_station": row[home_station_key],
                "available_at": 0,
                "shipments_completed": 0,
            }
        )

    return staged


# ============================================================
# DISPATCH SCHEDULER
# ============================================================

def choose_shipment_for_train(rail_graph, train, remaining_shipments):
    """
    Choose a shipment for one available train.

    Rules:
      1. Highest priority first (smaller priority number = higher priority).
      2. Within the same priority, choose the shipment whose ORIGIN is closest
         to this train's HOME station.
      3. shipment_id is used as a stable final tie-breaker.

    Returns (shipment, staging_route_result), or (None, None) if none of the
    remaining shipment origins can be reached from this train's home station.
    """
    candidates = []

    for shipment in remaining_shipments:
        staging_result = find_fastest_path(
            rail_graph,
            train["home_station"],
            shipment["origin_station"],
            verbose=False,
        )

        if not staging_result["reachable"]:
            continue

        candidates.append(
            (
                shipment["priority"],
                staging_result["total_time"],
                shipment["shipment_id"],
                shipment,
                staging_result,
            )
        )

    if not candidates:
        return None, None

    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    _, _, _, shipment, staging_result = candidates[0]
    return shipment, staging_result


def run_train_dispatch(rail_graph, trains, shipments, verbose=False):
    """
    Dispatch staged trains until every reachable shipment is completed.

    Simulation behavior:
      - All trains begin at their original station at simulated minute 0.
      - The next train to become available gets dispatched.
      - That train picks the highest-priority remaining shipment.
      - For equal priorities, it picks the shipment origin closest to its home.
      - Train travels HOME -> shipment origin -> shipment destination -> HOME.
      - Only after returning home is the train available for another shipment.
      - Multiple trains are represented by their independent available_at times.
    """
    staged_trains = stage_trains(trains)
    remaining_shipments = list(shipments)
    dispatch_results = []
    unreachable_shipments = []

    run_start_time = time.perf_counter()

    if not staged_trains:
        return dispatch_results, remaining_shipments, 0.0, staged_trains

    while remaining_shipments:
        # Train that becomes available first gets the next dispatch opportunity.
        staged_trains.sort(key=lambda train: (train["available_at"], train["train_id"]))

        assignment_made = False

        for train in staged_trains:
            shipment, staging_result = choose_shipment_for_train(
                rail_graph, train, remaining_shipments
            )

            if shipment is None:
                continue

            delivery_result = find_fastest_path(
                rail_graph,
                shipment["origin_station"],
                shipment["destination_station"],
                verbose=verbose,
            )

            return_result = find_fastest_path(
                rail_graph,
                shipment["destination_station"],
                train["home_station"],
                verbose=False,
            )

            # A shipment is only considered completable if the train can:
            # reach the pickup, deliver it, and return to its home station.
            if not delivery_result["reachable"] or not return_result["reachable"]:
                continue

            dispatch_time = train["available_at"]
            pickup_time = dispatch_time + staging_result["total_time"]
            delivery_time = pickup_time + delivery_result["total_time"]
            home_time = delivery_time + return_result["total_time"]

            cycle_time = (
                staging_result["total_time"]
                + delivery_result["total_time"]
                + return_result["total_time"]
            )

            dispatch_results.append(
                {
                    "train": dict(train),
                    "shipment": shipment,
                    "staging_result": staging_result,
                    "result": delivery_result,
                    "return_result": return_result,
                    "dispatch_time": dispatch_time,
                    "pickup_time": pickup_time,
                    "delivery_time": delivery_time,
                    "home_time": home_time,
                    "cycle_time": cycle_time,
                }
            )

            # Train is explicitly returned to its original station.
            train["current_station"] = train["home_station"]
            train["available_at"] = home_time
            train["shipments_completed"] += 1

            remaining_shipments.remove(shipment)
            assignment_made = True
            break

        if not assignment_made:
            # None of the trains can complete any remaining shipment.
            unreachable_shipments.extend(remaining_shipments)
            break

    run_end_time = time.perf_counter()
    return (
        dispatch_results,
        unreachable_shipments,
        run_end_time - run_start_time,
        staged_trains,
    )


# ============================================================
# DISPLAY
# ============================================================

def route_to_string(result):
    if not result["reachable"]:
        return "UNREACHABLE"
    return " -> ".join(result["path"])


def print_train_staging(staged_trains):
    print("\nTRAIN STAGING")
    print("=" * 70)
    for train in staged_trains:
        print(
            f"Train {train['train_id']} staged at {train['home_station']} | "
            f"available at minute {train['available_at']}"
        )


def print_dispatch_summary(dispatch_results):
    print("\nDISPATCH SUMMARY")
    print("=" * 120)

    headers = [
        "Train",
        "Shipment",
        "Priority",
        "Home",
        "Pickup",
        "Destination",
        "To Pickup",
        "Delivery",
        "Return",
        "Cycle",
        "Home At",
    ]

    rows = []

    for entry in dispatch_results:
        train = entry["train"]
        shipment = entry["shipment"]

        rows.append(
            [
                str(train["train_id"]),
                str(shipment["shipment_id"]),
                str(shipment["priority"]),
                train["home_station"],
                shipment["origin_station"],
                shipment["destination_station"],
                f"{entry['staging_result']['total_time']} min",
                f"{entry['result']['total_time']} min",
                f"{entry['return_result']['total_time']} min",
                f"{entry['cycle_time']} min",
                f"{entry['home_time']} min",
            ]
        )

    widths = []
    for index, header in enumerate(headers):
        widths.append(max([len(header)] + [len(row[index]) for row in rows]))

    def format_row(values):
        return " | ".join(str(value).ljust(widths[i]) for i, value in enumerate(values))

    print(format_row(headers))
    print("-+-".join("-" * width for width in widths))

    for row in rows:
        print(format_row(row))


def export_dispatch_results_csv(dispatch_results, filename="dispatch_results.csv"):
    fieldnames = [
        "train_id",
        "train_home_station",
        "shipment_id",
        "priority",
        "shipment_type",
        "shipment_origin",
        "shipment_destination",
        "dispatch_time",
        "pickup_time",
        "delivery_time",
        "return_home_time",
        "to_pickup_minutes",
        "delivery_minutes",
        "return_minutes",
        "total_cycle_minutes",
        "to_pickup_path",
        "delivery_path",
        "return_path",
    ]

    with open(filename, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for entry in dispatch_results:
            train = entry["train"]
            shipment = entry["shipment"]

            writer.writerow(
                {
                    "train_id": train["train_id"],
                    "train_home_station": train["home_station"],
                    "shipment_id": shipment["shipment_id"],
                    "priority": shipment["priority"],
                    "shipment_type": shipment["shipment_type"],
                    "shipment_origin": shipment["origin_station"],
                    "shipment_destination": shipment["destination_station"],
                    "dispatch_time": entry["dispatch_time"],
                    "pickup_time": entry["pickup_time"],
                    "delivery_time": entry["delivery_time"],
                    "return_home_time": entry["home_time"],
                    "to_pickup_minutes": entry["staging_result"]["total_time"],
                    "delivery_minutes": entry["result"]["total_time"],
                    "return_minutes": entry["return_result"]["total_time"],
                    "total_cycle_minutes": entry["cycle_time"],
                    "to_pickup_path": " -> ".join(entry["staging_result"]["path"]),
                    "delivery_path": " -> ".join(entry["result"]["path"]),
                    "return_path": " -> ".join(entry["return_result"]["path"]),
                }
            )

    print(f"\nDispatch results exported to: {os.path.abspath(filename)}")


# ============================================================
# LOAD INPUT FILES
# ============================================================

# Change "train.csv" to "trains.csv" here if that is your actual filename.
trains = load_csv("train.csv")
shipment_priorities = load_csv("shipment_priority.csv")
rail_connections = load_csv("rail_network_map.csv")
shipments = load_csv("shipments.csv")

print("Python Rail System")
print("=" * 40)
print(f"Trains loaded: {len(trains)}")
print(f"Shipment priorities loaded: {len(shipment_priorities)}")
print(f"Rail connections loaded: {len(rail_connections)}")
print(f"Shipments loaded: {len(shipments)}")


# ============================================================
# SHIPMENT PRIORITIES
# ============================================================

priority_lookup = {}
for priority_row in shipment_priorities:
    priority_lookup[priority_row["shipment_type"]] = int(priority_row["priority"])

for shipment in shipments:
    shipment["priority"] = priority_lookup[shipment["shipment_type"]]

# This isn't required by the scheduler, but it makes displays deterministic.
shipments.sort(key=lambda shipment: (shipment["priority"], shipment["shipment_id"]))


# ============================================================
# BUILD RAIL GRAPH
# ============================================================

rail_graph = nx.Graph()

for connection in rail_connections:
    origin = connection["start_station"]
    destination = connection["end_station"]
    track_time = int(connection["travel_time_minutes"])
    delay = int(connection["delay_minutes"])
    total_travel_time = track_time + delay

    rail_graph.add_edge(origin, destination, weight=total_travel_time)


# ============================================================
# RUN DISPATCH
# ============================================================

initial_staging = stage_trains(trains)
print_train_staging(initial_staging)

print("\nBEGINNING STAGED-TRAIN DISPATCH")
print("=" * 70)

dispatch_results, unreachable_shipments, runtime, final_train_states = run_train_dispatch(
    rail_graph,
    trains,
    shipments,
    verbose=False,
)

print_dispatch_summary(dispatch_results)

print("\nFINAL TRAIN STATUS")
print("=" * 70)
for train in sorted(final_train_states, key=lambda item: item["train_id"]):
    print(
        f"Train {train['train_id']} | "
        f"Home: {train['home_station']} | "
        f"Current: {train['current_station']} | "
        f"Shipments completed: {train['shipments_completed']} | "
        f"Available again at minute: {train['available_at']}"
    )

print("\nRUN TOTALS")
print("=" * 70)
print(f"Completed shipments: {len(dispatch_results)}")
print(f"Unreachable shipments: {len(unreachable_shipments)}")
print(f"Scheduler execution time: {runtime * 1000:.4f} ms")

if final_train_states:
    simulated_finish_time = max(train["available_at"] for train in final_train_states)
    print(f"Simulated time until all trains are back home: {simulated_finish_time} minutes")

if unreachable_shipments:
    print("\nUNREACHABLE / UNASSIGNED SHIPMENTS")
    print("=" * 70)
    for shipment in unreachable_shipments:
        print(
            f"{shipment['shipment_id']} | Priority {shipment['priority']} | "
            f"{shipment['origin_station']} -> {shipment['destination_station']}"
        )

export_dispatch_results_csv(dispatch_results)
