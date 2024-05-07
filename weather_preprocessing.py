import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('DataSet/weather_data.csv')

# Convert 'Time' column to datetime
df['Time'] = pd.to_datetime(df['Time'])

# Filter data starting from 2017-01-01 and up to 3/17/2024
df = df[(df['Time'] >= '2017-01-01') & (df['Time'] <= '2024-03-18')]

# Convert time to Nepal time by adding 5 hours and 45 minutes
df['Time'] = df['Time'] + pd.DateOffset(hours=5, minutes=45)

# Adjust date if necessary when crossing midnight
df['Time'] = df.apply(lambda row: row['Time'] - pd.DateOffset(days=1) if row['Time'].hour < 5 else row['Time'], axis=1)

# Round the values of the 'Time' column to the closest hour mark
df['Time'] = df['Time'].dt.round('H')

# Drop duplicate timestamps
df = df.drop_duplicates(subset=['Time'])

# Resample the DataFrame to hourly frequency and interpolate missing values
df = df.set_index('Time').resample('H').interpolate(method='time').reset_index()

print(df.shape)
print(df.head())

# Save the DataFrame to a new CSV file
df.to_csv('DataSet/preprocessed_weather_data.csv', index=False)

# Confirm the file has been saved
print("Preprocessed data saved to 'preprocessed_weather_data.csv'")