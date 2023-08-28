import pandas as pd
import altair as alt
import webview
import pyautogui

screen_width, screen_heigth = pyautogui.size()

def mean_glucose_plot(df: pd.DataFrame) -> alt.Chart:
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
    )
    return chart

def analyze_insulin(df: pd.DataFrame, periods: int, bucket_size: str) -> alt.Chart: 
    df.drop(columns=['event_type', 'glucose_value_(mg/dl)', 'carb_value_(grams)', 'duration_(hh:mm:ss)'], inplace=True, errors='ignore')
    df.rename(columns={"event_subtype": "type", "insulin_value_(u)": "units"}, inplace=True)
    df['count'] = 1

    # The date does not matter here, since we just grab `.time`
    dti = pd.date_range('1970-1-1', periods=periods, freq=bucket_size).time

    # ------ LONG ACTING ------
    long_acting = df.loc[df['type'] == "Long-Acting"].copy()
    long_acting.drop(columns=['type'], inplace=True)
    long = long_acting.groupby(long_acting['datetime'].dt.floor(bucket_size).dt.time)['count'].sum().reindex(dti, fill_value=0)
    long = pd.DataFrame(long).reset_index()
    long['datetime'] = pd.to_datetime(long['datetime'], format='%H:%M:%S')
    
    chart_long = alt.Chart(long, title=alt.Title("Frequency of Long Acting Insulin Dose Time", fontSize=24)).mark_bar().encode(
        x = alt.X('hoursminutes(datetime):O', axis=alt.Axis(labelAngle=-90), title="Time"),
        y = alt.Y('count:Q', title="Count"),
        tooltip=[alt.Tooltip('hoursminutes(datetime):O', title='Time'), alt.Tooltip('count', title='Count')]
    ).properties(
        width=screen_width-600,
        height=screen_heigth-400,
    )

    # ------ FAST ACTING ------
    fast_acting = df.loc[df.type == "Fast-Acting"].copy()
    # Excludes single unit doses, which are likely correction doses
    # fast_acting = fast_acting.loc[fast_acting.units >= 2.0]
    fast_acting.drop(columns=['type'], inplace=True)
    fast = fast_acting.groupby(fast_acting['datetime'].dt.floor(bucket_size).dt.time)['count'].sum().reindex(dti, fill_value=0)
    fast = pd.DataFrame(fast).reset_index()
    fast['datetime'] = pd.to_datetime(fast['datetime'], format='%H:%M:%S')
    
    chart_fast = alt.Chart(fast, title=alt.Title("Frequency of Fast Acting Insulin Dose Time", fontSize=24)).mark_bar().encode(
        x = alt.X('hoursminutes(datetime):O', axis=alt.Axis(labelAngle=-90), title="Time"),
        y = alt.Y('count:Q', title="Count"),
        tooltip=[alt.Tooltip('hoursminutes(datetime):O', title='Time'), alt.Tooltip('count', title='Count')]
    ).properties(
        width=screen_width-600,
        height=screen_heigth-400,
    )

    return chart_long, chart_fast

def analyze_carbs(df: pd.DataFrame, periods: int, bucket_size: str) -> alt.Chart:
    df.reset_index(drop=True, inplace=True)
    df.drop(columns=['event_type', 'event_subtype', 'glucose_value_(mg/dl)', 'insulin_value_(u)', 'duration_(hh:mm:ss)'], inplace=True, errors='ignore')
    df.rename(columns={"carb_value_(grams)": "carbs"}, inplace=True)
    df['count'] = 1

    # The date does not matter here, since we just grab `.time`
    dti = pd.date_range('1970-1-1', periods=periods, freq=bucket_size).time

    # Excludes small amounts of carbs, which are likely snacks/corrections that are not paired with insulin
    df = df.loc[df.carbs >= 5.0]

    carbs = df.groupby(df['datetime'].dt.floor(bucket_size).dt.time)['count'].sum().reindex(dti, fill_value=0)
    carbs = pd.DataFrame(carbs).reset_index()
    carbs['datetime'] = pd.to_datetime(carbs['datetime'], format='%H:%M:%S')
    
    chart_carbs = alt.Chart(carbs, title=alt.Title("Frequency of Meal or Snack Time", fontSize=24)).mark_bar().encode(
        x = alt.X('hoursminutes(datetime):O', axis=alt.Axis(labelAngle=-90), title="Time"),
        y = alt.Y('count:Q', title="Count"),
        tooltip=[alt.Tooltip('hoursminutes(datetime):O', title='Time'), alt.Tooltip('count', title='Count')]
    ).properties(
        width=screen_width-600,
        height=screen_heigth-400,
    )

    return chart_carbs

def main():
    try:
        df = pd.read_csv('data/export.csv', index_col=False)
    except FileNotFoundError as e:
         df = pd.read_csv('data/sample.csv', index_col=False)

    df.columns = [c.lower().replace(' ', '_') for c in df.columns]
    df.drop(columns=['index', 'patient_info', 'device_info', 'source_device_id', 'glucose_rate_of_change_(mg/dl/min)', 'transmitter_time_(long_integer)', 'transmitter_id'], inplace=True, errors='ignore')
    df.rename(columns = {'timestamp_(yyyy-mm-ddthh:mm:ss)':'datetime'}, inplace = True)
    df['datetime'] = pd.to_datetime(df["datetime"])
    df.sort_values(by='datetime', inplace = True)

    # Create new dataframes with different types of events
    insulin_events = df.loc[df.event_type == "Insulin"].copy()
    carb_events = df.loc[df.event_type == "Carbs"].copy()
    blood_glucose_events = df.loc[df.event_type == "EGV"].copy()

    # Create plots
    glucose = mean_glucose_plot(blood_glucose_events)
    long_acting, fast_acting = analyze_insulin(insulin_events, 48, '30T')
    carbs = analyze_carbs(carb_events, 48, '30T')
    
    charts_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-lite@5.8.0"></script>
    <script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
    </head>
    <body>

    <div id="vis1"></div>
    <div id="vis2"></div>
    <div id="vis3"></div>
    <div id="vis4"></div>

    <script type="text/javascript">
    vegaEmbed('#vis1', {glucose.to_json()});
    vegaEmbed('#vis2', {long_acting.to_json()});
    vegaEmbed('#vis3', {fast_acting.to_json()});
    vegaEmbed('#vis4', {carbs.to_json()});
    </script>
    </body>
    </html>
    """
    
    # Display plots
    webview.create_window('Dexcom Data Analysis', html=charts_html, width=screen_width, height=screen_heigth-50)
    webview.start()
        
if __name__ == "__main__":
    main()
