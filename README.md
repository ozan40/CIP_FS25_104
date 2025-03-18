# Analysis-Online-Car-Marketplaces
This project aims to analyze and compare used car prices, fuel efficiency, and emissions across online marketplaces to identify trends in pricing, cost-effectiveness, and environmental impact. Data from various sources is collected, processed, and analyzed to generate actionable market insights.

## Directory Structure

<pre style="font-size: 10.0pt; font-family: Arial; line-height: 2; letter-spacing: 1.0pt;" >
<b>Directory Structure</b>
|__ <b>.gitignore</b>
|__ <b>requirements.txt</b>
|__ <b>scraping_scripts</b>
    |______ <b>scraping_mobile_de.py</b>
    |______ <b>scraping_auto_de.py</b>
    |______ <b>scraping_autoscout24_de.py</b>
|__ <b>data_folder</b>
</pre>

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


