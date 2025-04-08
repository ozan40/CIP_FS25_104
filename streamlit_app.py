import streamlit as st
from streamlit_echarts import st_echarts
import os 
import pandas as pd
import numpy as np
from pyecharts.charts import Boxplot
from pyecharts import options as opts
import altair as alt

st.set_page_config(layout="wide")


# Load the dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, 'Data', 'imputed_output.csv')
df = pd.read_csv(file_path, sep= ";")

st.title("Comparing German Car Marketplaces")
st.subheader("Over 10'000 cars were scrapped using Selenium nad BeautifulSoup. For all the following interpretation of data we asume that crawling the marketplaces was succesful with no systematic errors. Furhter we asume that the crawled output is representativ of the individual marketplace.")

st.markdown('''
            In this project we investigate **three research question**: 
            1. abc
            2. cde
            3. deda
            
            ''')
st.markdown("First lets get an overview of the percentage of scrapped car brand for each site. The Y-Axis is sorted based on Auto.de and only the top 10 brands are displayed. All plots share the same y-labels for comparison.")
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
            "show": False,  # Show the ticks on the y-axis
        }
        },
        "series": [{
            "type": "bar",
            "data": pivot['Mobile.de'].tolist(),  # Replace 'source2' with your actual source column
            "itemStyle": {"color": "#66c2a5"}
        }]
    }
    st_echarts(option3)

st.markdown("We can see that the distribution of percentage of car brands scraped differs from site to site. " 
    "Volkswagen was scrapped the most in all three marketplaces but Mobile.de shows extrem results with over 50'%' of the scrapped cars being Volkswagen." 
    "The second most scrapped brand was Mercedes-Benz but this is not the case for Auto.de, where we see Ford as the second most scrapped Brand.")

st.subheader("Price Difference between Markplaces")
st.markdown("For our first research question we want to visually explore the question whether there are differences in car listing prices between marketplaces. Approaching this question, we first plot boxplots of the log of prices for each marketplace.")

df["price_log"] = np.log(df["cleaned_Price"])
import pandas as pd
import numpy as np

# Ensure no NaNs and only valid sources
df_filtered = df[df['price_log'].notna() & df['Marketplace'].isin(['Auto.de', 'Autoscout24.de', 'Mobile.de'])]

# ECharts boxplot needs 5-number summary for each group
box_data = []
outliers = []
x_labels = []
color = ["#8da0cb","#fc8d62","#66c2a5"]

for i, source in enumerate(['Auto.de', 'Autoscout24.de', 'Mobile.de']):
    values = df_filtered[df_filtered['Marketplace'] == source]['price_log'].sort_values()
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
        "text": "Boxplot of Log Price by Source",
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
st.markdown("")


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



    col2.markdown("Compare car model prices of different first approval years. Since Auto.de lists newer cars we would expect higher price range for Autoscout24.de and Mobile.de")

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