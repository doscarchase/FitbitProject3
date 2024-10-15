import fitbit_data
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# To run: streamlit run fitbit_dashboard.py

st.title("Devon's Fitbit Dashboard")

'''
Figure 1:

Step count for a 30-day period
'''

# Current date for demo purposes
today = datetime.now()

year = today.year
month = str(today.month).rjust(2, '0')  # Ensure 2 digits for month
day = str(today.day).rjust(2, '0')      # Ensure 2 digits for day

# Construct date string and retrieve step count
date = f'{year}-{month}-{day}'
df_steps = fitbit_data.get_user_steps(date)

# Check if df_steps is None or does not contain expected columns
if df_steps is not None and 'Steps' in df_steps.columns:
    # Plot step count data in a horizontal bar plot, and show average value
    fig1 = plt.figure()
    ax = sns.barplot(data=df_steps, x='Steps', y='Date', orient='h', color='blue', alpha=0.6)
    avg_steps = df_steps['Steps'].mean()
    ax.axvline(x=avg_steps, linewidth=2, color='orange', ls=':')
    st.subheader('Step count from last 30 days')
    st.pyplot(fig1)
else:
    st.write("No step count data available.")

st.markdown('---')

'''
Figure 2:

Heart rate data for selected day
'''

# Input to select the day
day = st.date_input(label='Select a day:')
st.write(day)

# Fetch HR data for the selected day
df_hr = fitbit_data.get_hr_per_min(day)

# Check if df_hr is None or does not contain 'HR' column
if df_hr is not None and 'HR' in df_hr.columns:
    # Compute 10-minute rolling average
    df_hr['HR_10_min_avg'] = df_hr['HR'].rolling(window=10).mean()

    # Create line plot of averaged 10-minute data, showing mean HR for the day
    fig2 = plt.figure()
    st.subheader(f'Heart rate for {day} (10-minute average).')

    # Reduce label clutter and improve readability
    sns.set(font_scale=0.7)
    df_hr['time'] = df_hr['time'].str.slice(0, 5)  # Slice time string to HH:MM
    plot_ = sns.lineplot(data=df_hr, x='time', y='HR_10_min_avg')
    avg_hr = df_hr['HR_10_min_avg'].mean()

    # Show average heart rate as a horizontal line
    plot_.axhline(y=avg_hr, linewidth=2, color='orange', ls=':')

    # Reduce density of x-label ticks for readability
    for ind, label in enumerate(plot_.get_xticklabels()):
        if ind % 120 == 0:  # Keep every 120th label
            label.set_visible(True)
        else:
            label.set_visible(False)

    # Display tick marks vertically
    plt.xticks(rotation=90)
    st.pyplot(fig2)

else:
    st.write("No intraday heart rate data available for the selected day.")

st.markdown('---')

'''
Figure 3:

Activity zone minutes for the past 30 days
'''

# Fetch zone data for the last 30 days ending with the selected day
df_zones = fitbit_data.get_user_zone(day)

# Display the zone DataFrame in Streamlit
if df_zones is not None:
    st.subheader('Activity Zone Minutes (Last 30 Days)')
    st.dataframe(df_zones)

    # Create a multi-line plot for all zones
    fig3, ax = plt.subplots()

    sns.lineplot(data=df_zones, x='date', y='active', ax=ax, label='Active Zone', color='blue')
    sns.lineplot(data=df_zones, x='date', y='fat_burning', ax=ax, label='Fat Burning Zone', color='green')
    sns.lineplot(data=df_zones, x='date', y='cardio', ax=ax, label='Cardio Zone', color='orange')
    sns.lineplot(data=df_zones, x='date', y='peak', ax=ax, label='Peak Zone', color='red')

    # Customize the plot for better readability
    plt.xticks(rotation=90)
    plt.xlabel('Date')
    plt.ylabel('Minutes')
    plt.title('Active Zone Minutes Over Last 30 Days')
    plt.legend()

    # Display the plot in Streamlit
    st.pyplot(fig3)

else:
    st.write("Failed to fetch activity zone data.")
