import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

car_df = pd.read_csv('../transformed_output.csv', sep = ";")
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