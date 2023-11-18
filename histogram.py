import os
import pandas as pd
import matplotlib.pyplot as plt


def analyze_insulin(df, periods, bucket_size):
    df.drop(columns=['event_type', 'glucose_value_(mg/dl)', 'carb_value_(grams)', 'duration_(hh:mm:ss)'], inplace=True, errors='ignore')
    df.rename(columns={"event_subtype": "type", "insulin_value_(u)": "units"}, inplace=True)
    df['count'] = 1

    # The date does not matter here, since we just grab `.time`
    dti = pd.date_range('1970-1-1', periods=periods, freq=bucket_size).time

    # ------ LONG ACTING ------
    long_acting = df.loc[df.type == "Long-Acting"].copy()
    long_acting.drop(columns=['type'], inplace=True)
    long = long_acting.groupby(long_acting['datetime'].dt.floor(bucket_size).dt.time)['count'].sum().reindex(dti, fill_value=0)

    long_plot = long.plot.bar(x="datetime", y="index", title="Frequency of Long Acting Insulin Dose Time", color=['red'])
    plt.title("Frequency of Long Acting Insulin Dose Time", fontsize = 24)
    long_plot.set_xlabel("Time", fontsize=16)
    long_plot.set_ylabel("Count", fontsize=16)

    # plt.show(block=True)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.savefig('out/long_acting_hist.png', dpi=100)
    plt.clf()

    # ------ FAST ACTING ------
    fast_acting = df.loc[df.type == "Fast-Acting"].copy()
    # Excludes single unit doses, which are likely correction doses
    # fast_acting = fast_acting.loc[fast_acting.units >= 2.0]
    fast_acting.drop(columns=['type'], inplace=True)
    fast = fast_acting.groupby(fast_acting['datetime'].dt.floor(bucket_size).dt.time)['count'].sum().reindex(dti, fill_value=0)

    fast_plot = fast.plot.bar(x="datetime", y="index", title="Frequency of Fast Acting Insulin Dose Time", color=['blue'])
    plt.title("Frequency of Fast Acting Insulin Dose Time", fontsize = 24)
    fast_plot.set_xlabel("Time", fontsize=16)
    fast_plot.set_ylabel("Count", fontsize=16)

    # plt.show(block=True)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.savefig('out/fast_acting_hist.png', dpi=100)
    plt.clf()


def analyze_carbs(df, periods, bucket_size):
    df.reset_index(drop=True, inplace=True)
    df.drop(columns=['event_type', 'event_subtype', 'glucose_value_(mg/dl)', 'insulin_value_(u)', 'duration_(hh:mm:ss)'], inplace=True, errors='ignore')
    df.rename(columns={"carb_value_(grams)": "carbs"}, inplace=True)
    df['count'] = 1

    # The date does not matter here, since we just grab `.time`
    dti = pd.date_range('1970-1-1', periods=periods, freq=bucket_size).time

    # Excludes small amounts of carbs, which are likely snacks/corrections that are not paired with insulin
    df = df.loc[df.carbs >= 5.0]

    carbs = df.groupby(df['datetime'].dt.floor(bucket_size).dt.time)['count'].sum().reindex(dti, fill_value=0)
    carbs_plot = carbs.plot.bar(x="datetime", y="index", title="Frequency of Meal or Snack Time", color=['green'])
    plt.title("Frequency of Meal or Snack Time", fontsize = 24)
    carbs_plot.set_xlabel("Time", fontsize=16)
    carbs_plot.set_ylabel("Count", fontsize=16)

    # plt.show(block=True)
    fig = plt.gcf()
    fig.set_size_inches(18.5, 10.5)
    fig.savefig('out/meal_hist.png', dpi=100)
    plt.clf()


def main():
    outdir = './out'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

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

    # Create new dataframes with different types of events
    insulin_events = df.loc[df.event_type == "Insulin"].copy()
    carb_events = df.loc[df.event_type == "Carbs"].copy()

    # Create plots
    analyze_insulin(insulin_events, 48, '30T')
    analyze_carbs(carb_events, 48, '30T')


if __name__ == "__main__":
    main()
