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

    # Combine Data
    combined_data = pd.concat([enriched_df, enriched_df_auto_de], ignore_index=True)
    print("########################### Combined Data ###########################\n")
    print("✅ Combined Dataset Shape:", combined_data.shape)
    print("✅ Preview:\n", combined_data.head())

    combined_data.to_csv("Data/transformed_output.csv", sep=";")


