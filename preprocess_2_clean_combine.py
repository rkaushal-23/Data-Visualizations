import pandas as pd

# Define a function to process the data for a given input file
def process_data(input_file):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(input_file)

    # Remove unnecessary columns
    df.drop(columns=['Site', 'Parameter', 'Duration', 'QC Name', 'AQI Category', 'Conc. Unit'], inplace=True)

    # Sort the DataFrame by the 'Hour' column
    df.sort_values(by='Hour', inplace=True)

    # Replace -999 with NaN for easier handling
    df.replace(-999, pd.NA, inplace=True)

    # Define columns to apply EWMA
    cols_to_ewma = ['NowCast Conc.', 'AQI', 'Raw Conc.']

    # Convert specified columns to numeric data type
    df[cols_to_ewma] = df[cols_to_ewma].apply(pd.to_numeric, errors='coerce')

    # Apply EWMA only to missing values in specified columns
    for col in cols_to_ewma:
        df[col] = df[col].mask(df[col].isna(), df[col].ewm(span=10).mean())

    # Sort the DataFrame by the 'index' column
    df.sort_values(by='index', inplace=True)
    
    return df

# Call the function for each input file
pm25_df = process_data('DataSet/preprocessed_combined_pm25.csv')
ozone_df = process_data('DataSet/preprocessed_combined_ozone.csv')

# Merge the DataFrames on the 'index' column
combined_df = pd.merge(pm25_df, ozone_df, on='index', suffixes=('_PM2.5', '_Ozone'))

# Rename columns to match the desired format
combined_df.rename(columns={
    'NowCast Conc._PM2.5': 'PM2.5 - NowCast Conc. (UG/M3)',
    'AQI_PM2.5': 'PM2.5 - AQI (UG/M3)',
    'Raw Conc._PM2.5': 'PM2.5 - Raw Conc. (UG/M3)',
    'NowCast Conc._Ozone': 'Ozone - NowCast Conc. (PPB)',
    'AQI_Ozone': 'Ozone - AQI (PPB)',
    'Raw Conc._Ozone': 'Ozone - Raw Conc. (PPB)',
    'Year_PM2.5': 'Year',
    'Month_PM2.5': 'Month',
    'Day_PM2.5': 'Day',
    'Hour_PM2.5': 'Hour'
}, inplace=True)

# Define bins and labels for PM2.5 AQI category
pm25_bins = [-1, 50, 100, 150, 200, 300, float('inf')]
pm25_labels = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']

# Define bins and labels for Ozone AQI category
ozone_bins = [-1, 50, 100, 150, 200, 300, float('inf')]
ozone_labels = ['Good', 'Moderate', 'Unhealthy for Sensitive Groups', 'Unhealthy', 'Very Unhealthy', 'Hazardous']

# Add 'PM2.5 AQI Category' and 'Ozone AQI Category' columns
combined_df['PM2.5 AQI Category'] = pd.cut(combined_df['PM2.5 - AQI (UG/M3)'], bins=pm25_bins, labels=pm25_labels, right=False)
combined_df['Ozone AQI Category'] = pd.cut(combined_df['Ozone - AQI (PPB)'], bins=ozone_bins, labels=ozone_labels, right=False)

# Rename the 'index' column to 'Time'
combined_df.rename(columns={'index': 'Time'}, inplace=True)

# Reorder columns
combined_df = combined_df[['Time',
                           'PM2.5 - NowCast Conc. (UG/M3)', 'PM2.5 - AQI (UG/M3)', 'PM2.5 - Raw Conc. (UG/M3)',
                           'PM2.5 AQI Category',
                           'Ozone - NowCast Conc. (PPB)', 'Ozone - AQI (PPB)', 'Ozone - Raw Conc. (PPB)', 'Ozone AQI Category']]

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('DataSet/preprocessed_2_cleaned_combined.csv', index=False)
