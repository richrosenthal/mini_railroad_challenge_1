##9-3-26

print("Welcome to the Railroad Dispatch System! \n")


# Define Functions
def announce_arrival(station):
    print(f" Train arriving at {station}...")


def announce_departure(station):
    print(f" Train departing to: {station}...")


def announce_continuing(station):
    print(f" Leaving {station} and continuing to the next station...")


def announce_destination(station):
    print(f" Final Destination Reached: {station}!")

def travel_route(departure_station, destination_station, stations):
    departure_station = departure_station
    destination_station = destination_station

    for station in stations:
        announce_arrival(station)

        if station == departure_station:
            announce_departure(station)

        if station == destination_station:
            announce_destination(station)

        else:
            announce_continuing(station)
        print("--------------------")

def calculate_travel_time(track_time, delay):
    return track_time + delay

def travel_route(train_name, stations, departure_station, destination_station, track_time, delay):
    total_time = calculate_travel_time(track_time, delay)

    print(f"\n===={train_name}======")
    print(f"Estimated Travel Time: {total_time} minutes\n")

    for station in stations:
        announce_arrival(station)

        if station == departure_station:
            announce_departure(station)

        if station == destination_station:
            announce_destination(station)

        else:
            announce_continuing(station)
        print("--------------------")




#Train Routes

train_a = [
    "Estes Park"
    "Denver"
    "Castle Rock"
    "Colorado Springs"
    "Pueblo"
    "Trinidad"
]

train_b = [
    "Denver",
    "Boulder",
    "Fort Collins",
    "Cheyenne"
]

train_c = [
    "Denver",
    "Golden",
    "Idaho Springs",
    "Georgetown",
    "Breckenridge",
    "Vail",
    "Aspen",
    "Grand Junction"
]

travel_route(
    train_name="Train A",
    stations=train_a,
    departure_station="Estes Park",
    destination_station="Trinidad",
    track_time=48,
    delay=27
)

travel_route(
    train_name="Train B",
    stations=train_b,
    departure_station="Denver",
    destination_station="Cheyenne",
    track_time=35,
    delay=12
)

travel_route(
    train_name="Train C",
    stations=train_c,
    departure_station="Denver",
    destination_station="Grand Junction",
    track_time=41,
    delay=15
)

print("\n All trains have completed their routes!")


print("\n Train Dispatch Complete!")
