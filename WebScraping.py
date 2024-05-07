import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from datetime import datetime

# Initializing ChromeDriverManager to get the appropriate driver version
service = Service(ChromeDriverManager().install())

# Setting Chrome options
options = webdriver.ChromeOptions()
#options.add_argument("--headless")  # Running in headless mode to speed up scraping 
options.add_argument("--incognito")
options.add_argument("--disable-dev-shm-usage")

# Initializing WebDriver with service and options
driver = webdriver.Chrome(service=service, options=options)

# Initializing range of dates for data scraping
start_date = '2017-01-01'
end_date = '2024-03-31'

# Create a CSV file and write headers
csv_file = 'DataSet/weather_data.csv'
with open(csv_file, 'w') as f:
   f.write('Time,Temperature,Dew Point,Humidity,Wind,Wind Speed,Wind Gust,Pressure,Precipitation,Condition\n')

date_range = pd.date_range(start=start_date, end=end_date, freq='D')
for date in date_range:
    formatted_date = date.strftime('%Y-%m-%d')
    print(f"Scraping data for {formatted_date}......")
    
    url = f"https://www.wunderground.com/history/daily/np/kathmandu/VNKT/date/{formatted_date}"
    
    # Retry up to 3 times if timeout occurs
    retries = 0
    while retries < 3:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-dateString mat-column-dateString ng-star-inserted"]')))
            break  # If elements are found, break out of the loop
        except TimeoutException:
            retries += 1
            print(f"Timeout occurred. Retrying... Attempt {retries}")
            # If all retries exhausted, move to the next date
            if retries == 3:
                print(f"Failed to scrape data for {formatted_date}. Moving to the next date...")
                break
        except WebDriverException as e:
            print(f"An error occurred: {e.msg}")
            break  # Move to the next date if WebDriverException occurs

    # Extracting weather data (if elements found)
    if retries < 3:
        time_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-dateString mat-column-dateString ng-star-inserted"]')]
        temp_data = [elem.text.split(' ')[0] for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-temperature mat-column-temperature ng-star-inserted"]')]
        dew_data = [elem.text.split(' ')[0] for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-dewPoint mat-column-dewPoint ng-star-inserted"]')]
        humidity_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-humidity mat-column-humidity ng-star-inserted"]')]
        wind_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-windcardinal mat-column-windcardinal ng-star-inserted"]')]
        wind_speed_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-windSpeed mat-column-windSpeed ng-star-inserted"]')]
        wind_gust_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-windGust mat-column-windGust ng-star-inserted"]')]
        pressure_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-pressure mat-column-pressure ng-star-inserted"]')]
        precip_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-precipRate mat-column-precipRate ng-star-inserted"]')]
        condition_data = [elem.text for elem in driver.find_elements(By.XPATH, '//td[@class="mat-cell cdk-cell cdk-column-condition mat-column-condition ng-star-inserted"]')]

        # Combine date and time
        full_time_data = [datetime.strptime(f"{formatted_date} {time}", "%Y-%m-%d %I:%M %p").strftime("%Y-%m-%d %H:%M") for time in time_data]

        # Creating DataFrame
        df = pd.DataFrame({
            'Time': full_time_data,
            'Temperature': temp_data,
            'Dew Point': dew_data,
            'Humidity': humidity_data,
            'Wind': wind_data,
            'Wind Speed': wind_speed_data,
            'Wind Gust': wind_gust_data,
            'Pressure': pressure_data,
            'Precipitation': precip_data,
            'Condition': condition_data
        })

        # Append data to CSV file
        df.to_csv(csv_file, mode='a', index=False, header=False)
        print(f"    Data for {formatted_date} written to file...")

# Closing the WebDriver
driver.quit()

print("Web Scraping Completed!\nData saved to 'weather_data.csv'.")