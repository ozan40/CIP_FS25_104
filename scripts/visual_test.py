import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
file_path = "../Data/transformed_output.csv"
df = pd.read_csv(file_path, sep=';')

# Prepare style
sns.set(style="whitegrid")

# Define threshold for grouping less frequent brands
brand_counts = df['Brand'].value_counts()
top_brands = brand_counts[brand_counts > 100].index  # Keep brands with >100 listings
df['Brand_Grouped'] = df['Brand'].apply(lambda x: x if x in top_brands else 'Other')

# -----------------------
# Research Question 1
# -----------------------

# Average price per grouped brand and marketplace
avg_price = (
    df.groupby(['Marketplace', 'Brand_Grouped'])['cleaned_Price']
    .mean()
    .reset_index()
)

# Plot 1: Average Used Car Price
plt.figure(figsize=(14, 6))
sns.barplot(data=avg_price, x='Brand_Grouped', y='cleaned_Price', hue='Marketplace')
plt.title('Average Used Car Price by Brand Group and Marketplace')
plt.ylabel('Average Price (€)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Average price per km
avg_price_per_km = (
    df.groupby(['Marketplace', 'Brand_Grouped'])['Price_per_km']
    .mean()
    .reset_index()
)

# Plot 2: Price per Kilometer
plt.figure(figsize=(14, 6))
sns.barplot(data=avg_price_per_km, x='Brand_Grouped', y='Price_per_km', hue='Marketplace')
plt.title('Average Price per Kilometer by Brand Group and Marketplace')
plt.ylabel('€/km')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# -----------------------
# Research Question 2
# -----------------------

# Average fuel consumption and CO₂ emissions per marketplace
fuel_emissions = (
    df.groupby('Marketplace')[['Consumption', 'CO2_g_km']]
    .mean()
    .reset_index()
)

# Plot 3: Fuel Consumption
plt.figure(figsize=(8, 5))
sns.barplot(data=fuel_emissions, x='Marketplace', y='Consumption')
plt.title('Average Fuel Consumption (L/100km) by Marketplace')
plt.ylabel('Fuel Consumption (L/100km)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Plot 4: CO2 Emissions
plt.figure(figsize=(8, 5))
sns.barplot(data=fuel_emissions, x='Marketplace', y='CO2_g_km')
plt.title('Average CO₂ Emissions (g/km) by Marketplace')
plt.ylabel('CO₂ Emissions (g/km)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
