# Analysis-Online-Car-Marketplaces
This project aims to analyze and compare used car prices, fuel efficiency, and emissions across online marketplaces to identify trends in pricing, cost-effectiveness, and environmental impact. Data from various sources is collected, processed, and analyzed to generate actionable market insights.
A final report is provided as well as an interactive report hosted on the streamlit server: <https://german-marketplace-car-comparison.streamlit.app>

## Directory Structure

<pre style="font-size: 10.0pt; font-family: Arial; line-height: 2; letter-spacing: 1.0pt;" >
<b>Directory Structure</b>
|__ <b>.gitignore</b>
|__ <b>requirements.txt</b>
|__ <b>crawler</b>
    |______ <b>__init__.py</b>
    |______ <b>CarsFetcher.py</b>
    |______ <b>CrawledCar.py</b>
|__ <b>Data</b>
    |______ <b>crawled_output.csv</b>
|__ <b>scripts</b>
    |______ <b>autoscout24_scraper.py</b>
    |______ <b>mobile_scraper.py</b>
    |______ <b>auto_scraper.py</b>
|__ <b>transform</b>
    |______ <b>__init__.py</b>
    |______ <b>DataCleaner.py</b>
    |______ <b>DataEnricher.py</b>

</pre>


## Dataset

| Column Name                  | Data Type   | Description                                  |
|:----------------------------|:------------|:---------------------------------------------|
| Index                       | integer     | Index                                        |
| Brand                       | character   | Brand name of car                            |
| Model                       | character   | Specific model of a car                      |
| YearMonth                   | date          | Date of initial approval                     |
| Kilometer                   | integer     | Miles of a car in km                         |
| Gear_Type                   | character   | Gear type of a car                           |
| Fuel_Type                   | character   | Fuel type of a car                           |
| Consumption                 | float          | Consumption of a car. NA were imputed using a machine learning model|
| CO2_g_km                    | integer           | CO2 emmision of a car                                            |
| Power_PS                    | integer     | Horse power of a car                         |
| Price_per_km                | float           | Price divided by km                                             |
| Fuel_Cost_per_100km         | float           | fuel cost per 100 km                                          |
| Annual_Fuel_Cost            | float           | annual fuel cost                                        |
| CO2_per_year                | float          | CO2 per year                                           |
| CO2_Emission_Category       | Logical           | CO2 Emissions below or above average                                            |
| Marketplace                 | character   | Index for which source cars were scrapped   |
| log_cleanned_price                 | float   | Log of Price  |
| log_price_per_km                 | float   | Log of price per km  |
| log_CO2_Emission                 | float   | Log of CO2   |
| log_CO2_per_year                 | float   | Log of CO2 per year  |
| car_age                 | float   | Age of car calculated up to 2025  |




## Virtual Environment 
Create virtual environment by opening a terminal in project folder and run: 

`python3 -m venv venv`

### Active Venv with the following command: 

Windows: 
`venv\Scripts\activate`

Mac/Linux: 
`source venv/bin/activate`

### Install Requirements 

To install all python packages in your local virtual environment run: 
`pip3 install -r requirements.txt`

Show list of installed packages:
`pip3 list`

### Update requirements.txt

After you install a new packages you can create an updated requirements.txt file and push it to github

`pip3 freeze > requirements.txt`


### Do not Commit Venv to Github
Add it to gitignore file so it doesn't get uploaded

`echo "venv/" >> .gitignore` 

`git add .gitignore`

`git commit -m "Ignore virtual environment"`

### Add .idea (pycharm: project-specific settings, configurations, and metadata) to gitignore
`echo ".idea/" >> .gitignore`

`git add .gitignore`

`git commit -m "Ignore PyCharm settings folder"`


