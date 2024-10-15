import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

# Load access token from .env file
load_dotenv()
access_token = os.getenv('ACCESS_TOKEN')

# Headers for API request
headers = {'Authorization': f'Bearer eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1BMOUQiLCJzdWIiOiJDODcyRE4iLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJwcm8gcm51dCByc2xlIiwiZXhwIjoxNzI4OTg0NTIxLCJpYXQiOjE3Mjg5NTU3MjF9.cqAy4uMtSPzTll-G7z8aw5tpCQSMA8EwQoeOyB0MLms'}


def get_user_steps(date):
    """Fetches step count data for the last 30 days up to the given date."""
    start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=29)).strftime('%Y-%m-%d')
    url = f"https://api.fitbit.com/1/user/-/activities/steps/date/{start_date}/{date}.json"
    print(f'URL generated for step count data retrieval:\n{url}')

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        steps_data = response.json()
        print("Step count data response:")
        print(steps_data)

        # Extract step data
        steps_list = steps_data['activities-steps']
        df_steps = pd.DataFrame(steps_list)

        # Convert the date column to datetime
        df_steps['dateTime'] = pd.to_datetime(df_steps['dateTime'])

        # Rename columns for clarity
        df_steps.rename(columns={'dateTime': 'Date', 'value': 'Steps'}, inplace=True)

        # Convert Steps to numeric (int) type
        df_steps['Steps'] = pd.to_numeric(df_steps['Steps'], errors='coerce')

        return df_steps
    else:
        print(f"Error: {response.status_code}")
        return None


def get_hr_per_min(day):
    """Fetches intraday heart rate data for a specific day."""
    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{day}/1d.json"
    print(f'URL generated for heart rate data retrieval:\n{url}')

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        hr_data = response.json()
        print("Heart rate data response:")
        print(hr_data)  # Print the full response to debug

        # Check if the 'activities-heart-intraday' key exists
        if 'activities-heart-intraday' in hr_data:
            hr_list = hr_data['activities-heart-intraday']['dataset']
            df_hr = pd.DataFrame(hr_list)

            # Convert 'time' to a more readable format if needed
            df_hr['time'] = pd.to_datetime(df_hr['time'], format='%H:%M:%S').dt.time
            df_hr['HR'] = pd.to_numeric(df_hr['value'], errors='coerce')  # Ensure HR values are numeric

            return df_hr
        else:
            print("No intraday heart rate data available for the selected day.")
            return None
    else:
        print(f"Error: {response.status_code}")
        return None

def get_user_zone(day):
    """Fetches Fitbit activity zone minutes for a 30-day period ending on 'day'."""
    url = f"https://api.fitbit.com/1/user/-/activities/active-zone-minutes/date/{day}/30d.json"
    print(f'URL generated for zone minutes data retrieval:\n{url}')

    # Send the request to the Fitbit API
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Extract JSON response
        zone_data = response.json()

        # Print the full JSON response to see the structure
        print("Zone minutes data response:")
        print(zone_data)

        # Initialize empty arrays to store data for each zone
        dates = []
        active = []
        fat_burning = []
        cardio = []
        peak = []

        # Extract zone minutes for each date in the 30-day period
        for entry in zone_data['activities-active-zone-minutes']:
            dates.append(entry['dateTime'])

            # Extract values, defaulting to 0 if a zone isn't present
            active_minutes = entry['value'].get('activeZoneMinutes', 0)
            fat_burning_minutes = entry['value'].get('fatBurnActiveZoneMinutes', 0)
            cardio_minutes = entry['value'].get('cardioActiveZoneMinutes', 0)
            peak_minutes = entry['value'].get('peakActiveZoneMinutes', 0)

            # Append data for each zone
            active.append(active_minutes)
            fat_burning.append(fat_burning_minutes)
            cardio.append(cardio_minutes)
            peak.append(peak_minutes)

        # Create a DataFrame from the extracted data
        df = pd.DataFrame({
            'date': dates,
            'active': active,
            'fat_burning': fat_burning,
            'cardio': cardio,
            'peak': peak
        })

        # Save the DataFrame to a CSV file
        df.to_csv(f'zone-minutes-{day}.csv', index=False)
        print("Data saved to CSV successfully!")
        return df
    else:
        print(f"Error: {response.status_code}")
        return None


# Example main function to test the implementation
def main():
    day = input('Enter a date (yyyy-mm-dd): ')
    print()

    # Fetch and save zone minutes data
    df_zones = get_user_zone(day)
    if df_zones is not None:
        print(df_zones)
    else:
        print(f"Failed to fetch zone minutes data for {day}.")


if __name__ == '__main__':
    main()
