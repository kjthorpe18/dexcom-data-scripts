# import os
import ctypes

import pandas as pd
import altair as alt
import webview
# import matplotlib.pyplot as plt

# Get screen resolution
user32 = ctypes.windll.user32
screen_width, screen_heigth = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def mean_glucose_plot(df: pd.DataFrame):
    df.drop(columns=['event_type', 'event_subtype', 'insulin_value_(u)', 'carb_value_(grams)', 'duration_(hh:mm:ss)'], inplace=True, errors='ignore')
    df.rename(columns={"glucose_value_(mg/dl)": "glucose_value"}, inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Massage the data into the form we want
    df['datetime'] = df['datetime'].dt.date
    # Replace 'Low' values with 45 mg/dL, although it could have been lower
    df['glucose_value'] = df['glucose_value'].replace('Low', 40)
    df['glucose_value'] = df['glucose_value'].astype('int')

    grouped_by_day = df.groupby('datetime', as_index=False)['glucose_value'].mean().reset_index()
    grouped_by_day['datetime'] = pd.to_datetime(grouped_by_day['datetime'])
    grouped_by_day.glucose_value = round(grouped_by_day.glucose_value)
    
    x_domain = [min(pd.DatetimeIndex(grouped_by_day.datetime) - pd.DateOffset(1)), max(pd.DatetimeIndex(grouped_by_day.datetime) + pd.DateOffset(1))]
    y_domain = [min(grouped_by_day.glucose_value) - 10, max(grouped_by_day.glucose_value) + 10]
    
    chart = alt.Chart(grouped_by_day, title=alt.Title("Average Blood Glucose", fontSize=24)).mark_line(point=True).encode(
        x = alt.X('datetime:T',
                  scale=alt.Scale(domain=x_domain),
                  title="Date"
                  ),
        y = alt.Y('glucose_value:Q', 
                  scale=alt.Scale(domain=y_domain),
                  title="Blood Glucose (mg/dL)"
                  ),
        tooltip=[alt.Tooltip('datetime', title='Date'), alt.Tooltip('glucose_value', title='Glucose Value')]
    ).properties(
        width=screen_width-600,
        height=screen_heigth-400,
    ).to_html()

    # mean_glucose_plot = grouped_by_day.plot.scatter(x="datetime", y="glucose_value", grid=True)
    # plt.title("Average Blood Glucose", fontsize = 24)
    # mean_glucose_plot.set_xlabel("Date", fontsize=16)
    # mean_glucose_plot.set_ylabel("Blood Glucose (mg/dL)", fontsize=16)
    # fig = plt.gcf()
    # fig.set_size_inches(24.5, 10.5)
    # fig.savefig('out/mean_glucose.png', dpi=100)
    # plt.clf()
    
    return chart

def main():
    # outdir = './out'
    # if not os.path.exists(outdir):
    #     os.mkdir(outdir)

    # Parse a CSV file into a base dataframe
    try:
        df = pd.read_csv('data/export.csv', index_col=False)
    except FileNotFoundError as e:
         df = pd.read_csv('data/sample.csv', index_col=False)

    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    df.drop(columns=['index', 'patient_info', 'device_info', 'source_device_id', 'glucose_rate_of_change_(mg/dl/min)', 'transmitter_time_(long_integer)', 'transmitter_id'], inplace=True, errors='ignore')
    df.rename(columns = {'timestamp_(yyyy-mm-ddthh:mm:ss)':'datetime'}, inplace = True)
    df['datetime'] = pd.to_datetime(df["datetime"])
    df.sort_values(by='datetime', inplace = True)

    # Create new dataframe with only blood glucose values
    blood_glucose_events = df.loc[df.event_type == "EGV"].copy()

    # Create plots
    chart = mean_glucose_plot(blood_glucose_events)
    
    # Display plot
    webview.create_window('Average Blood Glucose', html=chart, width=screen_width, height=screen_heigth-50)
    webview.start()
    

if __name__ == "__main__":
    main()
