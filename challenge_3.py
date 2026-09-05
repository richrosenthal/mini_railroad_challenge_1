import csv # import the csv library

shipments = [] # initialize an empty list to store each shipment from the csv file

with open("shipments.csv") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        shipments.append(row)

for shipment in shipments:
    print(
        f"Shipment {shipment['shipment_id']}: "
        f"{shipment['shipment_type']} travels from "
        f"{shipment['origin_station']} to {shipment['destination_station']}. "
    )
