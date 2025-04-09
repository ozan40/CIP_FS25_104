import streamlit as st
from streamlit_echarts import st_echarts
import os 
import pandas as pd
import numpy as np
from pyecharts.charts import Boxplot
from pyecharts import options as opts
from pyecharts.charts import Line

st.set_page_config(layout="wide")


# Load the dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'Data','imputed_output.csv')
df = pd.read_csv(file_path, sep= ";")

st.title("Comparing German Car Marketplaces")
st.subheader("Over 10'000 cars were scrapped using Selenium and BeautifulSoup. For all the following interpretation of data we assume that crawling the marketplaces was succesful with no systematic errors. Furhter, we assume that the crawled output is representativ of the individual marketplaces.")
st.markdown("Remark: Of course these assumptions are not valid.")
st.markdown('''
            In this project we investigate **three research question**: 
            1. **Which online marketplaces offer the most affordable used cars?**
            2. **How do fuel efficiency and CO₂ emissions differ between marketplaces?**
            3. **How accurately can missing consumption values be predicted by ML models, and which vehicle characteristics have the greatest influence?**
            
            ''')
st.markdown("First let's get an overview of the percentage of scrapped car brand for each site. The Y-Axis is sorted based on Auto.de and only the top 10 brands are displayed. All plots share the same y-labels for comparison purpose.")
# Create three columns
col1, col2, col3 = st.columns(3)


#prepare data 

# Group by "source" and "Brand" and count occurrences
grouped = df.groupby(["Marketplace", "Brand"]).size().reset_index(name="count")

# Calculate the total count per brand across all sources
brand_totals = grouped.groupby("Brand")["count"].transform("sum")

# Get the top 15 brands based on total count across all sources
top_10_brands = grouped.groupby("Brand")["count"].sum().nlargest(10).index.tolist()

# Filter for the top 15 brands only
grouped_top_10 = grouped[grouped["Brand"].isin(top_10_brands)]

# Calculate the total count per source
source_totals = grouped_top_10.groupby("Marketplace")["count"].transform("sum")

# Calculate percentage of each brand within each source
grouped_top_10["percentage"] = (grouped_top_10["count"] / source_totals) * 100

# Round the percentages to 2 decimal places
grouped_top_10["percentage"] = grouped_top_10["percentage"].round(2)

# Pivot the data so that each brand is a row, and each source is a column
pivot = grouped_top_10.pivot(index="Brand", columns="Marketplace", values="percentage").fillna(0)

# Sort the pivot table by the "auto.de" source in descending order
pivot = pivot.sort_values(by="Auto.de", ascending=True)

# Prepare the data for the first plot (only y-axis categories)
with col1:
    option1 = {
          "title": {"text": "Auto.de",
                    "x": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "value",
            "max": 40,
            "name": "Brand (%)",
            "nameLocation": "middle",  # Align axis title to the center of the axis
            "nameGap": 30,
        },
        "yAxis": {
            "type": "category",
            "data": pivot.index.tolist(),
            "show": True , # Hide y-axis labels
            "axisLabel": {
                "interval": 0,  # Show every label
                "formatter": "{value}",  # Display the full label without truncation
                "align": "right",  # Align labels properly
                "padding": [0, 0, 0, 10]  # Add some padding if needed
            }
        },
        "series": [{
            "type": "bar",
            "data": pivot['Auto.de'].tolist(),  # Replace 'source1' with your actual source column
            "itemStyle": {"color": "#8da0cb"}
        }],
        "grid": {
            "left": "25%",  # Decrease the plot size by reducing the space to the left
        }
    }
    st_echarts(option1)

# Prepare the data for the second plot (actual bar chart for source1)
with col2:
    option2 = {
        "title": {"text": "Autoscout24.de",
                  "x": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "value",
            "max": 20,
            "name": "Brand (%)",
            "nameLocation": "middle",  # Align axis title to the center of the axis
            "nameGap": 30,
        },
        "yAxis": {
            "type": "category",
            "data": pivot.index.tolist(),
            "show": True,  # Hide y-axis labels,
            "axisLabel": {
            "show": False,  # Hide the labels
        }
        },
        "series": [{
            "type": "bar",
            "data": pivot['Autoscout24.de'].tolist(),  # Replace 'source1' with your actual source column
            "itemStyle": {"color": "#fc8d62"}
        }]
    }
    st_echarts(option2)

# Prepare the data for the third plot (actual bar chart for source2)
with col3:
    option3 = {
        "title": {"text": "Mobile.de",
                  "x": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "value",
            "max": 60,
            "name": "Brand (%)",
            "nameLocation": "middle",  # Align axis title to the center of the axis
            "nameGap": 30,
        },
        "yAxis": {
            "type": "category",
            "data": pivot.index.tolist(),
            "show": True,  # Hide y-axis labels
            "axisLabel": {
            "show": False,  # Hide the labels
        },
            "axisTick": {
            "show": True,  # Show the ticks on the y-axis
        }
        },
        "series": [{
            "type": "bar",
            "data": pivot['Mobile.de'].tolist(),  # Replace 'source2' with your actual source column
            "itemStyle": {"color": "#66c2a5"}
        }]
    }
    st_echarts(option3)

st.markdown('''
            We can see that the distribution of percentage of car brands scraped differs from site to site. Volkswagen was scrapped the most in all three marketplaces but Mobile.de shows extrem results with over 50 percent of the scrapped cars being Volkswagen." 
    The second most scrapped brand was Mercedes-Benz but this is not the case for Auto.de, where we see Ford as the second most scrapped Brand. Next we can compare the approval year of cars scrapped from the three different marketplaces to inspect whether there are differences. ''')

###--------line plots 
lines_df = df
lines_df["YearMonth"] = pd.to_datetime(lines_df["YearMonth"])
lines_df["Year"] = lines_df["YearMonth"].dt.year  

# Define custom order for the 'Marketplace' column
marketplace_order = ['Auto.de', 'Autoscout24.de', 'Mobile.de']

# Group by Year and Marketplace, then count the occurrences
lines_df_grouped = lines_df.groupby(['Year', 'Marketplace']).size().reset_index(name='Count')

# Set the 'Marketplace' column to be a categorical type with the defined order
lines_df_grouped['Marketplace'] = pd.Categorical(lines_df_grouped['Marketplace'], categories=marketplace_order, ordered=True)

# Sort by 'Marketplace' and 'Year'
lines_df_grouped = lines_df_grouped.sort_values(by=['Year'])
x_axis = np.arange(min(lines_df_grouped['Year']), max(lines_df_grouped['Year']), step = 1)

# Pivot the grouped data: rows = Marketplace, columns = Year, values = Count
pivot_df = lines_df_grouped.pivot_table(
    index='Marketplace',
    columns='Year',
    values='Count',
    fill_value=0  # Fill missing year-marketplace combos with 0
)

# Optional: sort columns (years) if needed
pivot_df = pivot_df.sort_index(axis=1)

# Make sure x_axis is a list of years
x_axis = list(np.arange(min(lines_df_grouped['Year']), max(lines_df_grouped['Year']) + 1, step=1))

# Reindex pivot_df to ensure it has all years in x_axis, in correct order
pivot_df = pivot_df.reindex(columns=x_axis, fill_value=0)

# Prepare the series data as lists (ECharts expects lists, not Series)
auto_de = pivot_df.loc['Auto.de'].tolist()
autoscout = pivot_df.loc['Autoscout24.de'].tolist()
mobile = pivot_df.loc['Mobile.de'].tolist()

# Prepare ECharts config
options = {
    "title": {"text": "Initial Approval Year by Marketplace"},
    "tooltip": {"trigger": "axis"},
    "legend": {"data": ["Auto.de", "Autoscout24.de", "Mobile.de"]},
    "grid": {"left": "3%", "right": "4%", "bottom": "3%", "containLabel": True},
    "xAxis": {
        "type": "category",
        "boundaryGap": False,
        "data": x_axis
    },
    "yAxis": {"type": "value",
              "name": "count"},
    "series": [
        {
            "name": "Auto.de",
            "type": "line",
            "data": auto_de,
            "itemStyle": {"color": "#8da0cb"}
        },
        {
            "name": "Autoscout24.de",
            "type": "line",
            "data": autoscout,
            "itemStyle": {"color": "#fc8d62"}
        },
        {
            "name": "Mobile.de",
            "type": "line",
            "data": mobile,
            "itemStyle": {"color": "#66c2a5"}
        },
    ],
}


# Display with Streamlit ECharts
st_echarts(options=options, height="400px")

st.markdown('''
We can see that Auto.de offers newer cars whereas Mobile.de offers the most cars from 2016 (of course our scrapped data is not a random sample from the different marketplaces but certain systematic differences are clearly visible. The oldest inital approval year on the Auto.de marketplace is 2016.)
            ''')
##–-------Price
st.title("1. Which online marketplaces offer the most affordable used cars?")
st.markdown("### Price Difference between Markplaces")
st.markdown("For our first research question we want to visually explore the question whether there are differences in car listing prices between marketplaces. Approaching this question, we first plot boxplots of the log of prices for each marketplace.")


# Ensure no NaNs and only valid sources
df_filtered = df[df['log_cleaned_price'].notna() & df['Marketplace'].isin(['Auto.de', 'Autoscout24.de', 'Mobile.de'])]

# ECharts boxplot needs 5-number summary for each group
box_data = []
outliers = []
x_labels = []
color = ["#8da0cb","#fc8d62","#66c2a5"]

for i, source in enumerate(['Auto.de', 'Autoscout24.de', 'Mobile.de']):
    values = df_filtered[df_filtered['Marketplace'] == source]['log_cleaned_price'].sort_values()
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    # box: [min, Q1, median, Q3, max] (excluding outliers)
    normal_values = values[(values >= lower) & (values <= upper)]
    box = [normal_values.min(), q1, values.median(), q3, normal_values.max()]
    box_data.append(box)

    # collect outliers with index for scatter plot
    for val in values[(values < lower) | (values > upper)]:
        outliers.append([i, val])

    x_labels.append(source)

option = {
    "title": {
        "text": "Boxplot of Log Price by Marketplace",
        "left": "center"
    },
    "tooltip": {
        "trigger": "item",
        "axisPointer": {"type": "shadow"}
    },
    "grid": {
        "left": "10%",
        "right": "10%",
        "bottom": "15%"
    },
    "xAxis": {
        "type": "category",
        "data": x_labels,
        "boundaryGap": True,
        "nameGap": 30,
        "splitArea": {"show": False},
        "splitLine": {"show": False}
    },
    "yAxis": {
        "type": "value",
        "name": "log(price)",
        "splitArea": {"show": True}
    },
    "series": [
        {
            "name": "boxplot",
            "type": "boxplot",
            "data": box_data
        },
        {
            "name": "outlier",
            "type": "scatter",
            "data": outliers
        }
    ]
}
st_echarts(option, height="500px")

st.markdown("We can see that all marketplace have similar distribution of prices. Still Auto.de does have a higher median. The reason could be that Auto.de sells newer cars compared to autoscout.de and mobile.de. If we look at the outliers Auto.de seems to offer some cheaper cars. At the least in our the scarped dataset")

st.markdown("### Next we can compare specific car models across marketplaces.")
st.markdown("The example of VW Polo niceley represents our assumption that Auto.de in generlly has newer car listings with influences the price. First by manipulating the *Year range* we can see that Mobile.de and Autoscout24.de have older VW Polo listed. The price ranges is also larger. Multiple similar examples can be found and can be inspected by changing the brand and model of a car.")


# Select a brand
col1, col2= st.columns(2)

brands = df['Brand'].unique()
brands = df['Brand'].unique().tolist()
try:
    selected_brand = col1.selectbox("Select a Brand", brands,  index=brands.index("Volkswagen"), key = "col1_brand")

    # Filter models based on brand
    models = df[df['Brand'] == selected_brand]['Model'].unique()

    selected_model = col1.selectbox("Select a Model", models,  key = "col1_model")

    # Filter data for plotting
    filtered_data = df[(df['Brand'] == selected_brand) & (df['Model'] == selected_model) & (df['YearMonth'].notna())]

    filtered_data_2 = filtered_data
    filtered_data_2["YearMonth"] = pd.to_datetime(filtered_data_2["YearMonth"])
    filtered_data_2["Year"] = filtered_data_2["YearMonth"].dt.year    

    years = filtered_data_2['Year'].unique()
    print(years)
    years.sort()



    col2.markdown("Compare car model prices of different first approval years. Since Auto.de lists newer cars we would expect higher a price range compared to Autoscout24.de and Mobile.de")

    selected_year = col2.select_slider("Select Year", years)
    filtered_data_2 = filtered_data_2[filtered_data_2["Year"] == selected_year]
    print(filtered_data_2.shape)
except Exception as e:
        print(f"An error occurred in start: {e}")


# Plotting

try:
    col1.subheader(f"Prices for {selected_brand} - {selected_model}")
    col2.subheader(f"{selected_year}: {selected_brand} - {selected_model}")
except Exception as e:
        print(f"An error occurred in col.subheader: {e}")




# Custom order for marketplaces
custom_order = ["Auto.de", "Autoscout24.de", "Mobile.de"]

# Get unique marketplaces
marketplaces = filtered_data['Marketplace'].unique()


# Remove the marketplaces in the custom order from the original list, if they exist
remaining_marketplaces = [m for m in marketplaces if m not in custom_order]

# Combine the custom order with the remaining marketplaces, ensuring no duplicates
marketplaces = custom_order + remaining_marketplaces

# Filter custom_order to only those marketplaces that exist in the data
available_marketplaces = [m for m in custom_order if m in filtered_data['Marketplace'].unique()]

box_data = []
for market in available_marketplaces:
    try:
        prices = filtered_data[
            (filtered_data['Marketplace'] == market) & 
            (filtered_data['cleaned_Price'].notna())
        ]['cleaned_Price'].tolist()
        
        if prices:  # only compute stats if there's data
            stats = [
                np.min(prices),
                np.percentile(prices, 25),
                np.median(prices),
                np.percentile(prices, 75),
                np.max(prices)
            ]
        else:
            stats = [None] * 5  # or skip entirely if you prefer

        box_data.append(stats)

    except Exception as e:
        print(f"An error occurred in box_data: {e}")
available_marketplaces_2 = [m for m in custom_order if m in filtered_data_2['Marketplace'].unique()]

box_data_2 = []
for market in available_marketplaces_2:
    try:
        prices = filtered_data_2[
            (filtered_data_2['Marketplace'] == market) & 
            (filtered_data_2['cleaned_Price'].notna())
        ]['cleaned_Price'].tolist()

        if prices:
            stats = [
                np.min(prices),
                np.percentile(prices, 25),
                np.median(prices),
                np.percentile(prices, 75),
                np.max(prices)
            ]
        else:
            stats = [None] * 5

        box_data_2.append(stats)
    except Exception as e:
        print(f"An error occurred in box_data_2: {e}")

# ECharts boxplot config
try: 
    options = {
        "title": {"text": f"{selected_model} Price Distribution"},
        "xAxis": {
            "type": "category",
            "data": available_marketplaces,
            "boundaryGap": True
        },
        "yAxis": {
            "type": "value",
            "name": "Price"
        },
        "series": [
            {
                "name": "Price Distribution",
                "type": "boxplot",
                "data": box_data,
                "itemStyle": {
                    "color": "#91cc75"
                }
            }
        ]
    }
except:
    print("no data")

with col1:
    try: 
        st_echarts(options=options, height="500px", key="col1") 
    except:
        print("no data")
   
# ECharts boxplot config
try:
    options_2 = {
        "title": {"text": f"{selected_year} Price Distribution"},
        "xAxis": {
            "type": "category",
            "data": available_marketplaces_2,
            "boundaryGap": True
        },
        "yAxis": {
            "type": "value",
            "name": "Price"
        },
        "series": [
            {
                "name": "Price Distribution",
                "type": "boxplot",
                "data": box_data_2,
                "itemStyle": {
                    "color": "#91cc75"
                }
            }
        ]
    }
except Exception as e:
    print(f"An error occurred in options_2: {e}")

with col2:
    try:
        st_echarts(options=options_2, height="500px", key="col2")
    except: 
        st.markdown("No data")



st.title("2. How do fuel efficiency and CO₂ emissions differ between marketplaces?")


# Ensure no NaNs and only valid sources
df_filtered = df[df['Consumption'].notna() & df['Marketplace'].isin(['Auto.de', 'Autoscout24.de', 'Mobile.de'])]

# ECharts boxplot needs 5-number summary for each group
box_data = []
outliers = []
x_labels = []
color = ["#8da0cb","#fc8d62","#66c2a5"]

for i, source in enumerate(['Auto.de', 'Autoscout24.de', 'Mobile.de']):
    values = df_filtered[df_filtered['Marketplace'] == source]['Consumption'].sort_values()
    q1 = np.percentile(values, 25)
    q3 = np.percentile(values, 75)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    # box: [min, Q1, median, Q3, max] (excluding outliers)
    normal_values = values[(values >= lower) & (values <= upper)]
    box = [normal_values.min(), q1, values.median(), q3, normal_values.max()]
    box_data.append(box)

    # collect outliers with index for scatter plot
    for val in values[(values < lower) | (values > upper)]:
        outliers.append([i, val])

    x_labels.append(source)

option = {
    "title": {
        "text": "Boxplot of Consumption by Marketplace",
        "left": "center"
    },
    "tooltip": {
        "trigger": "item",
        "axisPointer": {"type": "shadow"}
    },
    "grid": {
        "left": "10%",
        "right": "10%",
        "bottom": "15%"
    },
    "xAxis": {
        "type": "category",
        "data": x_labels,
        "boundaryGap": True,
        "nameGap": 30,
        "splitArea": {"show": False},
        "splitLine": {"show": False}
    },
    "yAxis": {
        "type": "value",
        "name": "l/km",
        "splitArea": {"show": True}
    },
    "dataZoom": [
        {
            "type": "inside",
            "yAxisIndex": 0
        },
        {
            "type": "slider",
            "yAxisIndex": 0,
            "orient": "vertical",
            "left": "left",
            "start": 20,
            "height": "80%"
        }
    ],
    "series": [
        {
            "name": "boxplot",
            "type": "boxplot",
            "data": box_data
        },
        {
            "name": "outlier",
            "type": "scatter",
            "data": outliers
        }
    ]
}
st_echarts(option, height="500px")
st.markdown("This plot suggests that Auto.de has higher consumption values with more variance compared to Autoscout24.de and Mobile.de. Thought as we already established Auto.de offers newer cars which tend to be more fuel efficiency in general. These results are likely wrong. The variance in comsuption values in Mobile.de and Autoscout24.de is very low. An explanation could be that Auto.de was had very little NA values after scraping consumption and therefore the imputed consumption values have less of an impact on the variance and median. With Mobile.de we weren't able to scrape any consumption values since these were not accessible on the main car listing site. Further scraping mechanism to scrape the detailed view of each individual car was not permited and failed. All the consumption values of Mobile.de very imputed using the machine learning model. The low variance of consumption values is soley attributed to imputed values by our model.")

#-------Fuel type
# Create three columns
col1, col2, col3 = st.columns(3)

# Group by "Marketplace" and "Fuel_Type" and count occurrences
grouped = df.groupby(["Marketplace", "Fuel_Type"]).size().reset_index(name="count")

# Calculate the total count per marketplace (not per fuel type)
marketplace_totals = grouped.groupby("Marketplace")["count"].transform("sum")

# Calculate percentage of each fuel type within each marketplace
grouped["percentage"] = (grouped["count"] / marketplace_totals) * 100

# Round the percentages to 2 decimal places
grouped["percentage"] = grouped["percentage"].round(2)

# Pivot the data so that each fuel type is a row, and each marketplace is a column
pivot = grouped.pivot(index="Fuel_Type", columns="Marketplace", values="percentage").fillna(0)

# Sort the pivot table by the "Auto.de" column in descending order
pivot = pivot.sort_values(by="Auto.de", ascending=True)

# Prepare the data for the first plot (Auto.de)
with col1:
    option1 = {
        "title": {"text": "Auto.de", "x": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "value",
            "max": 60,
            "name": "Brand (%)",
            "nameLocation": "middle",
            "nameGap": 30,
        },
        "yAxis": {
            "type": "category",
            "data": pivot.index.tolist(),
            "show": True,
            "axisLabel": {
                "interval": 0,
                "formatter": "{value}",
                "align": "right",
                "padding": [0, 0, 0, 10]
            }
        },
        "series": [{
            "type": "bar",
            "data": pivot['Auto.de'].tolist(),
            "itemStyle": {"color": "#8da0cb"}
        }],
        "grid": {"left": "30%"},
    }
    st_echarts(option1)

# Prepare the data for the second plot (Autoscout24.de)
with col2:
    option2 = {
        "title": {"text": "Autoscout24.de", "x": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "value",
            "max": 60,
            "name": "Brand (%)",
            "nameLocation": "middle",
            "nameGap": 30,
        },
        "yAxis": {
            "type": "category",
            "data": pivot.index.tolist(),
            "show": True,
            "axisLabel": {"show": False}
        },
        "series": [{
            "type": "bar",
            "data": pivot['Autoscout24.de'].tolist(),
            "itemStyle": {"color": "#fc8d62"}
        }]
    }
    st_echarts(option2)

# Prepare the data for the third plot (Mobile.de)
with col3:
    option3 = {
        "title": {"text": "Mobile.de", "x": "center"},
        "tooltip": {"trigger": "axis"},
        "xAxis": {
            "type": "value",
            "max": 80,
            "name": "Brand (%)",
            "nameLocation": "middle",
            "nameGap": 30,
        },
        "yAxis": {
            "type": "category",
            "data": pivot.index.tolist(),
            "show": True,
            "axisLabel": {"show": False},
            "axisTick": {"show": True}
        },
        "series": [{
            "type": "bar",
            "data": pivot['Mobile.de'].tolist(),
            "itemStyle": {"color": "#66c2a5"}
        }]
    }
    st_echarts(option3)

st.markdown("We can see that most cars use Benzin and Diesel. Nearly 80 percent of cars scrapped from Mobile.de use Benzin.")
#----------Research Question 3

st.title("3. How accurately can missing consumption values be predicted by ML models, and which vehicle characteristics have the greatest influence?")
st.markdown("")
st.markdown('''

|Model |RMSE (Before) |R² (Before) |RMSE (After) |R² (After) |
|:----|:----|:----|:----|:----|
|Ridge Regression |2.01 |0.17 |2.01 |0.18 |
|Lasso |2.22 |-0.00 |2.07 |0.13 |
|Random Forest |1.44 |0.58 |1.42 |0.59 |
|KNN |1.75 |0.38 |1.75 |0.38 |
|Gradient Boosting |1.71 |0.41 |1.71 |0.41 |
|SVR |1.73 |0.39 |1.69 |0.42 |
|XGBoost |1.51 |0.54 |1.49 |0.55 |
|MLP Regressor |2.11 |0.09 |2.11 |0.09 |

            ''')

st.image("./miscellaneous/importance.png", width=600)


