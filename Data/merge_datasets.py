import pandas as pd


columns_to_read = [
            "Brand", "Model", "YearMonth", "cleaned_Price", "Price_Eval", 
            "Kilometer", "Gear_Type", "Fuel_Type", "Power_PS",
            "Consumption", "CO2_g_km"
        ]

df_autoscout = pd.read_csv("Data/imputed_output.csv", sep=";", usecols=columns_to_read)
df_auto_de = pd.read_csv("Data/transformed_Auto.de.csv", sep = ";", usecols=columns_to_read)

df_auto_de['cleaned_Price'] = df_auto_de['cleaned_Price'].astype(str).str.replace('.', '', regex=False).astype(int)

df_mobile_de = pd.read_csv("Data/car_mobile.csv", sep = ",")


df_mobile_de = df_mobile_de.rename(columns={
    "brand": "Brand",
    "model": "Model",  
    "price":"cleaned_Price",
    "price_evaluation":"Price_Eval",
    "kilometer":"Kilometer" ,
    "gear":"Gear_Type",
    "date":"YearMonth",
    "fuel":"Fuel_Type",
    "power":"Power_PS",
    "consumption":"Consumption",
    "co2":"CO2_g_km",
    })

df_mobile_de = df_mobile_de.drop(['car_info','user_text'], axis=1)


#-------Date---------

def keep_year(dataframe, date_col, date_format):
    """
    Turns date character into date format but only keeps year as we make the assumption most important information is keep in the year
    """
    dataframe[date_col] = pd.to_datetime(dataframe[date_col], format = date_format).dt.year
    
    return dataframe

#-------Add source---------

def add_source(dataset, name):
    dataset["source"] = name





if __name__ == "__main__":
    df_auto_de = keep_year(df_auto_de, "YearMonth", "%d-%m-%Y" )
    df_autoscout = keep_year(df_autoscout, "YearMonth", "%Y-%m-%d")
    df_mobile_de = keep_year(df_mobile_de, "YearMonth", "%m/%Y")

    add_source(df_auto_de,"Auto.de")
    add_source(df_autoscout, "Autoscout.de")
    add_source(df_mobile_de, "Mobile.de")

    df_autoscout.columns = df_autoscout.columns.str.strip()  # Remove any extra spaces
    df_mobile_de.columns = df_mobile_de.columns.str.strip()
    df_combined = pd.concat([df_auto_de, df_autoscout, df_mobile_de], ignore_index=True)


    df_combined.to_csv('./Data/merged_datasets.csv', index=False)