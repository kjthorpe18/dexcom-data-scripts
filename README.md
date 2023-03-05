# Dexcom CGM Data Histogram Generator

![example histogram](example1.png)

A script that takes a CSV export of Dexcom continuous blood glucose monitor (CGM) data and generates histograms for fast-acting insulin, long-acting insulin, and carbohydrate times.

### Exporting CGM Data

Dexcom allows raw patient CGM data to be exported in CSV format. Follow the [instructions given here](https://www.dexcom.com/en-us/faqs/can-i-export-raw-data) to export data.

### To Run

Add your CSV to the `data/` directory and rename it `export.csv`. A sample CSV is provided, and can be renamed. Run the script from the main directory with:

```sh
python3 histogram.py
```

### Notes

- This script groups data into 30 minute buckets.
- This script excludes carb entries less than 5 grams. This is to exclude small "correction" food that is used to sightly blood glucose when low. The justification for this is to only track more significant meals and snacks. This is adjustable by changing this line in the script:

  ```python
  df = df.loc[df.carbs >= 5.0]
  ```
