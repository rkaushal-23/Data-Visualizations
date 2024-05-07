import pandas as pd
import os

# Directory containing the folders
directory = os.path.abspath(os.path.join(os.getcwd()))

# Directories containing the files
pm25_directory = os.path.join(directory, 'DataSet/PM2.5/')
ozone_directory = os.path.join(directory, 'DataSet/OZONE/')

# Function to process files in a directory
def process_directory(directory):
    # List all files in the directory
    files = os.listdir(directory)
    dfs = []
    # Iterate over each file
    for file in files:
        if file.endswith('.csv'):  # Process only CSV files
            # Read the CSV file into a DataFrame
            df = pd.read_csv(os.path.join(directory, file))
            dfs.append(df)
    # Concatenate all DataFrames into a single DataFrame
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Convert 'Date (LT)' column to datetime format
    combined_df['Date (LT)'] = pd.to_datetime(combined_df['Date (LT)'])
    
    # Remove duplicate timestamps
    combined_df = combined_df.drop_duplicates(subset='Date (LT)')
    
    # Determine the start and end dates from the dataset
    start_date = combined_df['Date (LT)'].min()
    end_date = combined_df['Date (LT)'].max()
    
    # Create a DatetimeIndex to ensure all hours are accounted for
    date_range = pd.date_range(start=start_date, end=end_date, freq='H')
    
    # Reindex the DataFrame with the complete date range
    combined_df = combined_df.set_index('Date (LT)').reindex(date_range)
    
    # Iterate through each column and fill missing values with previous day's valid values at the same hour
    for column in combined_df.columns:
        for i in range(len(combined_df)):
            if pd.isna(combined_df.iloc[i][column]):
                j = 1
                while True:
                    previous_day_index = combined_df.index[i] - pd.Timedelta(days=j)
                    # Check if the previous day's index is within the range of the DataFrame index
                    if previous_day_index in combined_df.index:
                        previous_value = combined_df.loc[previous_day_index, column]
                        if pd.notna(previous_value):
                            combined_df.at[combined_df.index[i], column] = previous_value
                            break
                    else:
                        # If previous day's index is not within the range, break the loop
                        break
                    j += 1
    
    # Reset index to make Date (LT) a column again
    combined_df = combined_df.reset_index()
    
    return combined_df

# Process PM2.5 directory
pm25_combined_df = process_directory(pm25_directory)

# Process OZONE directory
ozone_combined_df = process_directory(ozone_directory)

# Save the preprocessed DataFrames to new CSV files
pm25_output_file = os.path.join(directory, 'DataSet/preprocessed_combined_pm25.csv')
pm25_combined_df.to_csv(pm25_output_file, index=False)

ozone_output_file = os.path.join(directory, 'DataSet/preprocessed_combined_ozone.csv')
ozone_combined_df.to_csv(ozone_output_file, index=False)
