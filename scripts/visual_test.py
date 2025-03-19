import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

car_df = pd.read_csv('../Data/transformed_output.csv', sep =";")
print(car_df.head())
print(car_df.columns)

# Preisvergleich nach Marke & Modell
# Vergleicht die Preise unterschiedlicher Modelle je Marke mit einem Balkendiagramm.
plt.figure(figsize=(12, 6))
sns.barplot(x="Brand", y="Price_per_km", hue="Model", data=car_df)
plt.title("Price comparison in EUR")
plt.xlabel("Brand")
plt.ylabel("Price (€)")
plt.legend(title="Modell")
plt.show()

# Kraftstoffverbrauch vs. Leistung nach Marke
# Vergleicht den Verbrauch (l/100 km) mit der Motorleistung (kW).
plt.figure(figsize=(12, 6))
sns.scatterplot(x="Power_PS", y="Annual_Fuel_Cost", hue="Gear_Type", size="Price_per_km", data=car_df, sizes=(50, 500))
plt.title("Kraftstoffverbrauch vs. Leistung nach Marke")
plt.xlabel("Leistung (kW)")
plt.ylabel("Verbrauch (l/100 km)")
plt.legend(title="Marke")
plt.show()

# CO₂-Emissionen nach Marke & Kraftstoffart
# Zeigt, wie sich die CO₂-Emissionen nach Marke & Kraftstoffart unterscheiden.
plt.figure(figsize=(12, 6))
sns.boxplot(x="Fuel_Type", y="CO2_per_year", hue="Fuel_Type", data=car_df)
plt.title("CO₂-Emissionen nach Marke & Kraftstoffart")
plt.xlabel("Marke")
plt.ylabel("CO₂-Emissionen (g/km)")
plt.legend(title="Kraftstoffart")
plt.show()


##################################################################################################
##################################################################################################
# Here are more specific visuals
# Focus analysis on Top 10 brands for readability
top_brands = car_df['Brand'].value_counts().nlargest(10).index
filtered_df = car_df[car_df['Brand'].isin(top_brands)]

# Set visualization style
sns.set(style="whitegrid")

# Research Question 1: Price comparison between brands
# Using boxplot for better insight into price spread
plt.figure(figsize=(12, 6))
sns.boxplot(data=filtered_df, x="Brand", y="cleaned_Price", hue = "Brand")
plt.title("Price Distribution per Brand (Top 10)")
plt.ylabel("Price (€)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Reasoning: Boxplots show median, spread, and outliers, ideal for comparing price variation across brands

# Research Question 1 (cont.): Price per km efficiency
# Violin plot shows distribution and density
plt.figure(figsize=(12, 6))
sns.violinplot(data=filtered_df, x="Brand", y="Price_per_km", inner="quartile", hue = "Brand")
plt.title("Price per km Distribution per Brand (Top 10)")
plt.ylabel("Price per km (€)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Research Question 2: Fuel Consumption vs CO2 Emissions
# Scatter plot to highlight correlation
plt.figure(figsize=(10, 6))
sns.scatterplot(data=filtered_df, x="Consumption", y="CO2_g_km", hue="Brand", palette="tab10")
plt.title("Fuel Consumption vs CO2 Emissions")
plt.xlabel("Consumption (L/100km)")
plt.ylabel("CO2 Emissions (g/km)")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Reasoning: Highlights relationship between fuel efficiency and environmental impact

# Research Question 3: Fuel Cost vs Horsepower by Gear Type
# Bubble chart to show multi-dimensional insights
plt.figure(figsize=(12, 6))
sns.scatterplot(
    data=filtered_df,
    x="Power_PS", y="Annual_Fuel_Cost",
    hue="Gear_Type", size="Price_per_km", sizes=(40, 400), alpha=0.7
)
plt.title("Annual Fuel Cost vs Horsepower by Gear Type")
plt.xlabel("Horsepower (PS)")
plt.ylabel("Annual Fuel Cost (€)")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

# Reasoning: Compares performance vs cost-efficiency, enhanced by gear type and price per km bubble size