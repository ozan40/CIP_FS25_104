import csv


class CrawledCar():
    # Konstruktur initialisieren und brand, model, description, price, kilometer, gear, year, fuel, hp, etc. übergeben
    def __init__(self, brand = None, model= None, car_info= None, user_text= None, price= None, price_evaluation= None,
                 km= None, gear= None, date= None, fuel= None, power= None,
                 consumption= None, co2= None):
        self.brand = brand
        self.model = model
        self.car_info = car_info
        self.user_text = user_text
        self.price = price
        self.price_evaluation = price_evaluation
        self.kilometer = km
        self.gear = gear
        self.date = date
        self.fuel = fuel
        self.power = power
        self.consumption = consumption
        self.co2 = co2

    # Methode zur Speicherung aller CrawledCar-Instanzen als CSV-Datei
    @staticmethod
    def file_maker(cars_list, filename="Data/crawled_output.csv", marketplace_name="Autoscout24.de"):
        """Erstellt eine CSV-Datei mit `;`-getrennten Werten aus einer Liste von CrawledCar-Objekten."""

        # CSV-Spalten definieren
        headers = [
            "Brand", "Model", "Car_Info", "User_Desc", "Price", "Price_Eval",
            "Kilometer", "Gear_Type", "YearMonth", "Fuel_Type", "Horsepower",
            "Consumption", "CO2_Emission", "Marketplace"  # Marketplace hinzugefügt
        ]

        # Datei schreiben
        # https: // docs.python.org / 3 / library / csv.html  # csv.writer
        with open(filename, mode="w", newline="", encoding="utf-8") as writefile:
            writer = csv.writer(writefile, delimiter=";")  # Semikolon als Trennzeichen setzen
            writer.writerow(headers)  # Kopfzeile schreiben

            # Jedes CrawledCar-Objekt in eine Zeile umwandeln
            for car in cars_list:
                car.marketplace = marketplace_name  # Setze den Marktplatznamen für jedes Objekt
                writer.writerow([
                    car.brand, car.model, car.car_info, car.user_text, car.price, car.price_evaluation,
                    car.kilometer, car.gear, car.date, car.fuel, car.power, car.consumption, car.co2,
                    car.marketplace  # Marketplace-Wert hinzufügen
                ])

        print(f"CSV-Datei erfolgreich erstellt: {filename}")
