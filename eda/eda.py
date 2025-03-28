#https://github.com/ozan40/CIP_FS25_104/blob/829ab2ee411acabe71ace411b3450694f0e9953b/Data/car_data_Auto.de_v2.csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Load data
path = "C:/Users/thoma/PycharmProjects/CIP_FS25_104/Data/car_data_Auto.de_v2.csv"
df = pd.read_csv(path)
# Change the value of emission free cars to 0 l/Km en 0 Emission before parsing
zero_consumption = df['Fuel'].str.contains('Elektro|Wasserstoff|Erdgas|Autogas', case=False, na=False)
df.loc[zero_consumption, 'l/Km'] = '0'
df.loc[zero_consumption, 'Emission'] = '0'

# Clean numerical values
df['CurrentPrice'] = df['CurrentPrice'] * 1000
df['Kilometers'] = df['Kilometers'].astype(str).str.replace(r'\D', '', regex=True).astype(float)
df['Year'] = df['BuildYear'].astype(str).str.extract(r'(\d{4})').astype(float)
df['Power_kW'] = df['Power'].astype(str).str.extract(r'^(\d+)').astype(float)
df['l_Km'] = pd.to_numeric(df['l/Km'].astype(str).str.extract(r'^([\d.]+)')[0], errors='coerce')
df['Emission_g'] = df['Emission'].astype(str).str.extract(r'^(\d+)').astype(float)

# Categoricals
df['Transmission'] = df['Transmission'].astype('category')
df['Fuel'] = df['Fuel'].astype('category')
df['Brand'] = df['Brand'].astype('category')

# Drop rows with missing data
df = df.dropna(subset=[
    'CurrentPrice', 'Kilometers', 'Year', 'Power_kW',
    'l_Km', 'Emission_g', 'Transmission', 'Fuel', 'Brand'
])

# Debug: check Elektro auto's
print("Aantal auto's per brandstoftype na schoonmaken:")
print(df['Fuel'].value_counts(dropna=False))
print("\nUnieke l/Km voor Elektro:", df[df['Fuel'] == 'Elektro']['l/Km'].unique())
print(df[df['Fuel'] == 'Elektro'][['Model', 'l/Km']].head(10))

# Lineair model
formula = 'CurrentPrice ~ Kilometers + Year + Power_kW + l_Km + Emission_g + Transmission + Fuel + Brand'
model = smf.ols(formula=formula, data=df).fit()
print(model.summary())

# Plot: Kilometers vs Price
plt.figure(figsize=(6, 4))
plt.scatter(df['Kilometers'], df['CurrentPrice'], alpha=0.5)
plt.xlabel("Kilometers")
plt.ylabel("Prijs (in euro)")
plt.title("Prijs vs. Kilometers")
plt.grid(True)
plt.show()

# Plot: Year vs Price
plt.figure(figsize=(6, 4))
plt.scatter(df['Year'], df['CurrentPrice'], alpha=0.5)
plt.xlabel("Bouwjaar")
plt.ylabel("Prijs")
plt.title("Prijs vs. Bouwjaar")
plt.grid(True)
plt.show()

# Boxplots
plt.figure(figsize=(6, 4))
sns.boxplot(x='Transmission', y='CurrentPrice', data=df)
plt.title("Prijs vs Transmissie")
plt.show()

plt.figure(figsize=(8, 6))
df['Fuel'] = df['Fuel'].cat.remove_unused_categories()
sns.boxplot(x='Fuel', y='CurrentPrice', data=df)
plt.title("Prijs vs Brandstof")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Diagnostic plots for the linear model
fig = plt.figure(figsize=(12, 8))
sm.graphics.plot_regress_exog(model, 'Kilometers', fig=fig)
plt.show()

# Log-transform CurrentPrice
df['LogPrice'] = np.log(df['CurrentPrice'])
model_log = smf.ols(
    'LogPrice ~ Kilometers + Year + Power_kW + l_Km + Emission_g + Transmission + Fuel + Brand',
    data=df
).fit()
print(model_log.summary())

# Diagnostic plots for the log model
fig = plt.figure(figsize=(12, 8))
sm.graphics.plot_regress_exog(model_log, 'Kilometers', fig=fig)
plt.show()
