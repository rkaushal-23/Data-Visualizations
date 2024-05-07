import pandas as pd

# Read the preprocessed weather data CSV file
df1 = pd.read_csv('DataSet/preprocessed_weather_data.csv')

# Read the preprocessed_2_cleaned_combined CSV file
df2 = pd.read_csv('DataSet/preprocessed_2_cleaned_combined.csv')

# Merge the two DataFrames on the 'Time' column
combined_df = pd.merge(df1, df2, on='Time', how='inner')

# Print the shape and the first 5 rows of the combined DataFrame
print(combined_df.shape)
print(combined_df.head())

# Save the combined DataFrame to a new CSV file
combined_df.to_csv('DataSet/combined_weather_and_air_quality_data.csv', index=False)

# Confirm the file has been saved
print("Combined data saved to 'combined_weather_and_air_quality_data.csv'")
