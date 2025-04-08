import transform

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":

    print("########################### Autoscout.de Transformation Part ###########################\n")
    # load data
    autoscout_df = pd.read_csv("Data/autoscout_data.csv", sep=";")

    # clean Data
    cleaner = transform.DataCleaner(autoscout_df)
    cleaned_df = cleaner.cleaned_categorical_values()
    missing_val, msno_visual = cleaner.missing_values(cleaned_df)
    outlier_information = cleaner.detect_outliers()

    # enrich Data
    enricher = transform.DataEnricher(cleaned_df)
    enriched_df = enricher.categorize_cols()

    print(missing_val)
    print(msno_visual)
    print(outlier_information)
    print(enriched_df.dtypes)

    print("########################### Auto.de Transformation Part ###########################\n")
    # Load Data
    auto_de_df = pd.read_csv("Data/Auto_de_Data.csv", sep = ",")

    # clean Data
    cleaner_auto_de = transform.DataCleaner(auto_de_df)
    cleaned_df_auto = cleaner_auto_de.cleaned_categorical_values()
    missing_val_auto, msno_visual_auto = cleaner_auto_de.missing_values(cleaned_df_auto)
    outlier_information_auto = cleaner_auto_de.detect_outliers()

    # enrich Data
    enricher_auto_de = transform.DataEnricher(cleaned_df_auto)
    enriched_df_auto_de = enricher_auto_de.categorize_cols()

    print(missing_val_auto)
    print(msno_visual_auto)
    print(outlier_information_auto)
    print(enriched_df_auto_de.dtypes)

    print("########################### Mobile.de Transformation Part ###########################\n")
    # Mobile.de Part
    # Load Data
    df_mobile_de = pd.read_csv("Data/car_mobile.csv", sep=",")

    # clean Data
    cleaner_mobile_de = transform.DataCleaner(df_mobile_de)
    cleaned_df_mobile = cleaner_mobile_de.cleaned_categorical_values()
    missing_val_mobile, msno_visual_mobile = cleaner_mobile_de.missing_values(cleaned_df_mobile)
    outlier_information_mobile = cleaner_mobile_de.detect_outliers()

    # enrich Data
    enricher_mobile_de = transform.DataEnricher(df_mobile_de)
    enriched_df_mobile_de = enricher_mobile_de.categorize_cols()


    print(missing_val_mobile)
    print(msno_visual_mobile)
    print(outlier_information_mobile)
    print(enriched_df_mobile_de.dtypes)

    # Combine Data
    combined_data = pd.concat([enriched_df, enriched_df_auto_de, enriched_df_mobile_de], ignore_index=True)
    print("########################### Combined Data ###########################\n")
    print("✅ Combined Dataset Shape:", combined_data.shape)
    print("✅ Preview:\n", combined_data.head())
    #


    # skewness check
    # Remove rows with NaN or infinite values in 'cleaned_Price' or 'Price_per_km'
    df_clean = combined_data.dropna(subset=['cleaned_Price', 'CO2_g_km'])  # Remove NaN values
    df_clean = df_clean[np.isfinite(df_clean['cleaned_Price'])]  # Remove infinite values
    df_clean = df_clean[np.isfinite(df_clean['CO2_g_km'])]  # Remove infinite values

    # Plot 1: Distribution of Cleaned Price
    plt.figure(figsize=(14, 6))
    sns.histplot(df_clean['cleaned_Price'], kde=True)
    plt.title('Distribution of Cleaned Price')
    plt.tight_layout()
    plt.show()

    # Plot 2: Distribution of CO2_Emission
    plt.figure(figsize=(14, 6))
    sns.histplot(df_clean['CO2_g_km'], kde=True)
    plt.title('Distribution of CO2_g_km')
    plt.tight_layout()
    plt.show()

    # Apply logarithm to cleaned price and Price_per_km (add a small constant to avoid issues with zero values)
    combined_data['log_cleaned_price'] = np.log1p(combined_data['cleaned_Price'])  # log1p is log(1 + x), which handles zero and small values
    combined_data['log_price_per_km'] = np.log1p(combined_data['Price_per_km'])
    combined_data['log_CO2_Emission'] = np.log1p(combined_data['CO2_g_km'])  # log1p handles zero and small values
    combined_data['log_CO2_per_year'] = np.log1p(combined_data['CO2_per_year'])

    # Plot the transformed CO2_Emission distribution
    sns.histplot(combined_data['log_CO2_Emission'], kde=True)
    plt.title('Distribution of Log-transformed CO2 Emissions')

    # Plot the transformed cleaned proce distribution
    sns.histplot(combined_data['log_cleaned_price'], kde=True)
    plt.title('Distribution of Log-transformed cleaned Price')

    plt.tight_layout()
    plt.show()

    combined_data.to_csv("Data/transformed_output.csv", sep=";")