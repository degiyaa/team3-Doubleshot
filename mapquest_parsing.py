import urllib.parse
import requests


main_api = "https://mapquestapi.com/directions/v2/route?"

while True:

    orig = input("Starting Location: ")

    if orig.lower() == "quit" or orig.lower() == "q":
        break

    dest = input("Destination: ")

    if dest.lower() == "quit" or dest.lower() == "q":
        break

    url = main_api + urllib.parse.urlencode({
        "key": key,
        "from": orig,
        "to": dest
    })

    print("URL: " + url)

    try:
        response = requests.get(url)
        json_data = response.json()

    except requests.exceptions.RequestException:
        print("Error: Unable to connect to MapQuest API.\n")
        continue

    json_status = json_data["info"]["statuscode"]

    if json_status == 0:

        route = json_data["route"]

        print("\nAPI Status: " + str(json_status) +
              " = A successful route call.\n")

        print("=============================================")
        print("Directions from " + orig + " to " + dest)

        print("Trip Duration:   " +
              route["formattedTime"])

        miles = route["distance"]

        print("Miles:           " +
              "{:.2f}".format(miles))

        kilometers = miles * 1.61

        print("Distance (km):   " +
              "{:.2f}".format(kilometers))

        fuel_used = route.get("fuelUsed", None)

        if fuel_used is not None:

            print("Fuel Used (Gal): " +
                  "{:.2f}".format(fuel_used))

            try:

                fuel_price = float(
                    input("Enter fuel price per gallon: ₱")
                )

                fuel_cost = fuel_used * fuel_price

                print("Estimated Fuel Cost: ₱" +
                      "{:.2f}".format(fuel_cost))

                # ROUND TRIP FEATURE
                round_distance = kilometers * 2
                round_fuel = fuel_used * 2
                round_cost = fuel_cost * 2

                print("---------------------------------------------")
                print("ROUND TRIP INFORMATION")

                print("Round Trip Distance: " +
                      "{:.2f} km".format(round_distance))

                print("Round Trip Fuel:     " +
                      "{:.2f} gallons".format(round_fuel))

                print("Round Trip Fuel Cost: ₱" +
                      "{:.2f}".format(round_cost))

            except ValueError:

                print("Invalid fuel price.")

        else:

            print("Fuel Used (Gal): N/A")
            print("Estimated Fuel Cost: N/A")

        print("=============================================")
        print("TURN-BY-TURN DIRECTIONS")

        for each in route["legs"][0]["maneuvers"]:

            distance_km = each["distance"] * 1.61

            print(
                each["narrative"] +
                " (" +
                "{:.2f}".format(distance_km) +
                " km)"
            )

        print("=============================================")

    elif json_status == 402:

        print("**********************************************")
        print(
            "Status Code: " +
            str(json_status) +
            "; Invalid user inputs for one or both locations."
        )
        print("**********************************************\n")

    elif json_status == 611:

        print("**********************************************")
        print(
            "Status Code: " +
            str(json_status) +
            "; Missing an entry for one or both locations."
        )
        print("**********************************************\n")

    else:

        print("************************************************************************")
        print(
            "For Status Code: " +
            str(json_status) +
            "; Refer to:"
        )

        print(
            "https://developer.mapquest.com/documentation/"
            "directions-api/status-codes"
        )

        print("************************************************************************\n")