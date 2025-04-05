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
PARENT_DIR = os.path.dirname(BASE_DIR)
file_path = os.path.join(PARENT_DIR, 'Data', 'merged_datasets.csv')
df = pd.read_csv(file_path)

st.title("Comparing German Car Marketplaces")
st.subheader("Over 10'000 cars were scrapped using Selenium nad BeautifulSoup. For all the following interpretation of data we asume that crawling the marketplaces was succesful with no systematic errors. Furhter we asume that the crawled output is representativ of the individual marketplace.")

st.markdown("First lets get an overview of the percentage of scrapped car brand for each site. The Y-Axis is sorted based on Auto.de and only the top 10 brands are displayed. All plots share the same y-labels for comparison.")
# Create three columns
col1, col2, col3 = st.columns(3)


#prepare data 

# Group by "source" and "Brand" and count occurrences
grouped = df.groupby(["source", "Brand"]).size().reset_index(name="count")

# Calculate the total count per brand across all sources
brand_totals = grouped.groupby("Brand")["count"].transform("sum")

# Get the top 15 brands based on total count across all sources
top_15_brands = grouped.groupby("Brand")["count"].sum().nlargest(10).index.tolist()

# Filter for the top 15 brands only
grouped_top_15 = grouped[grouped["Brand"].isin(top_15_brands)]

# Calculate the total count per source
source_totals = grouped_top_15.groupby("source")["count"].transform("sum")

# Calculate percentage of each brand within each source
grouped_top_15["percentage"] = (grouped_top_15["count"] / source_totals) * 100

# Round the percentages to 2 decimal places
grouped_top_15["percentage"] = grouped_top_15["percentage"].round(2)

# Pivot the data so that each brand is a row, and each source is a column
pivot = grouped_top_15.pivot(index="Brand", columns="source", values="percentage").fillna(0)

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
        "title": {"text": "Autoscout.de",
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
            "data": pivot['Autoscout.de'].tolist(),  # Replace 'source1' with your actual source column
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

df["price_log"] = np.log1p(df["cleaned_Price"])
import pandas as pd
import numpy as np

# Ensure no NaNs and only valid sources
df_filtered = df[df['price_log'].notna() & df['source'].isin(['Auto.de', 'Autoscout.de', 'Mobile.de'])]

# ECharts boxplot needs 5-number summary for each group
box_data = []
outliers = []
x_labels = []
color = ["#8da0cb","#fc8d62","#66c2a5"]

for i, source in enumerate(['Auto.de', 'Autoscout.de', 'Mobile.de']):
    values = df_filtered[df_filtered['source'] == source]['price_log'].sort_values()
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

st.markdown("We can see that all marketplace have similar distribution of prices. Still Auto.de does have a higher median. The reason could be that Auto.de sell newer cars compared to autoscout.de and mobile.de. If we look at the outliers Auto.de seems to offer some cheaper cars. At the least in our the scarped dataset")


# -- Multiselect Filters --
sources = df['source'].unique().tolist()
brand_types = df['Brand'].unique().tolist()
model_types = df['Model'].unique().tolist()


selected_sources = st.multiselect("Select sources", sources, default=sources)
selected_brand_types = st.multiselect("Select car types", brand_types, default="Volkswagen")

# -- Filter Data --
filtered_df = df[df['source'].isin(selected_sources) & df['Brand'].isin(selected_brand_types)]

# -- Count car types --
counts = filtered_df['Model'].value_counts().sort_values(ascending=False)
car_type_labels = counts.index.tolist()
car_type_counts = counts.values.tolist()

# -- ECharts Option --
option = {
    "title": {"text": "Car Type Distribution", "left": "center"},
    "tooltip": {},
    "xAxis": {
        "type": "category",
        "data": car_type_labels,
        "axisLabel": {"rotate": 30}
    },
    "yAxis": {"type": "value"},
    "series": [
        {
            "name": "Count",
            "type": "bar",
            "data": car_type_counts,
            "itemStyle": {
                "color": "#5470C6"
            },
        }
    ]
}

st_echarts(option, height="500px")