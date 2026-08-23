#Author: Ricky Rosenthal
#Date: 8-23-26
#Preparation for Algorithm and analysis

train_stations = ["Lynchburg", "DC", "Pittsburgh", "NYC", "Detroit", "Chicago"]
departure_station = "Lynchburg"
destination_station = "NYC"

for station in train_stations:
    if station == departure_station:
        print(f"You just departed {departure_station}")
    elif station == destination_station:
        print(f"You just arrived {destination_station}")
        break
    else:
        print(f"Arrived at {station}. Continue to the next station")