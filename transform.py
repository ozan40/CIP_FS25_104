import transform
import pandas as pd


if __name__ == "__main__":
    # load data
    car_df = pd.read_csv("crawled_output.csv", sep=";")

    # clean Data
    cleaner = transform.DataCleaner(car_df)
    cleaned_df = cleaner.cleaned_categorical_values()
    missing_val, msno_visual = cleaner.missing_values(cleaned_df)
    outlier_information = cleaner.detect_outliers()

    # enrich Data
    enricher = transform.DataEnricher(cleaned_df)
    enriched_df = enricher.categorize_cols()
    enriched_missing_val, enriched_msno_visual = cleaner.missing_values(enriched_df)


    print(missing_val)
    print(msno_visual)
    print(outlier_information)
    print(enriched_df.dtypes)
    print(enriched_missing_val)
    print(enriched_msno_visual)
    #enriched_df.to_csv("Data/transformed_output.csv", sep=";")

