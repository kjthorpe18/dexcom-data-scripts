import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

def mean_glucose_plot(df):
    df.drop(columns=['event_type', 'event_subtype', 'insulin_value_(u)', 'carb_value_(grams)', 'duration_(hh:mm:ss)'], inplace=True, errors='ignore')
    df.rename(columns={"glucose_value_(mg/dl)": "glucose_value"}, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Massage the data into the form we want
    df['datetime'] = df['datetime'].dt.date
    # Replace 'Low' values with 45 mg/dL, although it could have been lower
    df['glucose_value'] = df['glucose_value'].replace('Low', 40)
    df['glucose_value'] = df['glucose_value'].astype('int')

    grouped_by_day = df.groupby('datetime', as_index=False)['glucose_value'].mean().reset_index()

    mean_glucose_plot = grouped_by_day.plot.scatter(x="datetime", y="glucose_value", grid=True)
    plt.title("Average Blood Glucose", fontsize = 24)
    mean_glucose_plot.set_xlabel("Date", fontsize=16)
    mean_glucose_plot.set_ylabel("Blood Glucose (mg/dL)", fontsize=16)

    # plt.show(block=True)
    fig = plt.gcf()
    fig.set_size_inches(24.5, 10.5)
    fig.savefig('out/mean_glucose.png', dpi=100)
    plt.clf()

def main():
    outdir = './out'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # Parse a CSV file into a base dataframe
    df = pd.read_csv('data/export.csv', index_col=False)
    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    df.drop(columns=['index', 'patient_info', 'device_info', 'source_device_id', 'glucose_rate_of_change_(mg/dl/min)', 'transmitter_time_(long_integer)', 'transmitter_id'], inplace=True, errors='ignore')
    df.rename(columns = {'timestamp_(yyyy-mm-ddthh:mm:ss)':'datetime'}, inplace = True)
    df['datetime'] = pd.to_datetime(df["datetime"])
    df.sort_values(by='datetime', inplace = True)

    # Create new dataframe with only blood glucose values
    blood_glucose_events = df.loc[df.event_type == "EGV"].copy()

    # Create plots
    mean_glucose_plot(blood_glucose_events)

if __name__ == "__main__":
    main()