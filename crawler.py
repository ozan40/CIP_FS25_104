import crawler

fetcher = crawler.CarsFetcher()

crawled_car = []
for car in fetcher.fetch():
    crawled_car.append(
        crawler.CrawledCar(
            car.brand, car.model, car.car_info, car.user_text, car.price, car.price_evaluation, car.kilometer,
            car.gear, car.date, car.fuel, car.power, car.consumption, car.co2
        )
    )
crawler.CrawledCar.file_maker(crawled_car, filename="Data/autoscout_data.csv", marketplace_name="Autoscout24.de")

# Close the driver
fetcher.close()

