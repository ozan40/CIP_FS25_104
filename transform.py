import transform


import pandas as pd



if __name__ == "__main__":

    # Autoscout.de part
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
    print("########################### Autoscout.de Transformation Part ###########################\n")
    print(missing_val)
    print(msno_visual)
    print(outlier_information)
    print(enriched_df.dtypes)


    # Auto.de part
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

    print("########################### Auto.de Transformation Part ###########################\n")
    print(missing_val_auto)
    print(msno_visual_auto)
    print(outlier_information_auto)
    print(enriched_df_auto_de.dtypes)



    # Mobile.de Part
    # Load Data
    df_mobile_de = pd.read_csv("Data/car_mobile.csv", sep=",")
    # df_mobile_de['Marketplace'] = 'Mobile.de'
    # df_mobile_de = df_mobile_de.rename(columns={
    #     "brand": "Brand",
    #     "model": "Model",
    #     "price": "cleaned_Price",
    #     "price_evaluation": "Price_Eval",
    #     "kilometer": "Kilometer",
    #     "gear": "Gear_Type",
    #     "date": "YearMonth",
    #     "fuel": "Fuel_Type",
    #     "power": "Power_PS",
    #     "consumption": "Consumption",
    #     "co2": "CO2_g_km",
    # })

    # clean Data
    cleaner_mobile_de = transform.DataCleaner(df_mobile_de)
    cleaned_df_mobile = cleaner_mobile_de.cleaned_categorical_values()
    missing_val_mobile, msno_visual_mobile = cleaner_mobile_de.missing_values(cleaned_df_mobile)
    outlier_information_mobile = cleaner_mobile_de.detect_outliers()

    # enrich Data
    enricher_mobile_de = transform.DataEnricher(df_mobile_de)
    enriched_df_mobile_de = enricher_mobile_de.categorize_cols()

    print("########################### Mobile.de Transformation Part ###########################\n")
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
    combined_data.to_csv("Data/transformed_output.csv", sep=";")