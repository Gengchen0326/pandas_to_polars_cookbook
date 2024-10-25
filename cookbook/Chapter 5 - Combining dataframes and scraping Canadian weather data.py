# %%
import polars as pl 
import matplotlib.pyplot as plt
import numpy as np

plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (15, 3)
plt.rcParams["font.family"] = "sans-serif"

# %%
# By the end of this chapter, we're going to have downloaded all of Canada's weather data for 2012, and saved it to a CSV. We'll do this by downloading it one month at a time, and then combining all the months together.
# Here's the temperature every hour for 2012!

# Read the CSV file
weather_2012_final = pl.read_csv("../data/weather_2012.csv")
weather_2012_final = weather_2012_final.with_columns(
    pl.col("date_time").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S")
)

temperature_df = weather_2012_final.select("temperature_c").to_pandas()
temperature_df.plot(figsize=(15, 6))
plt.show()

# TODO: rewrite using Polars

# %%
# Okay, let's start from the beginning.
# We're going to get the data for March 2012, and clean it up
# You can directly download a csv with a URL using Pandas!
# Note, the URL the repo provides is faulty but kindly, someone submitted a PR fixing it. Have a look
# here: https://github.com/jvns/pandas-cookbook/pull/74 and click on "Files changed" and then fix the url.


# This URL has to be fixed first!
url_template = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=5415&Year={year}&Month={month}&timeframe=1&submit=Download+Data"
year = 2012
month = 3
url_march = url_template.format(month=3, year=2012)

weather_mar2012 = pl.read_csv(
    url_march,
    encoding="latin1",
    has_header=True  # Polars assumes there is a header, if there's none, set it to False
)

weather_mar2012 = weather_mar2012.with_columns([
    pl.col("Date/Time (LST)").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S", strict=False)
])
print(weather_mar2012.head())

# TODO: rewrite using Polars. Yes, Polars can handle URLs similarly.


4# %%
# Let's clean up the data a bit.
# You'll notice in the summary above that there are a few columns which are are either entirely empty or only have a few values in them. Let's get rid of all of those with `dropna`.
# The argument `axis=1` to `dropna` means "drop columns", not rows", and `how='any'` means "drop the column if any value is null".
weather_mar2012 = weather_mar2012.drop_nulls()
print(weather_mar2012.head(5))

# This is much better now -- we only have columns with real data.

# TODO: rewrite using Polars


# %%
# Let's get rid of columns that we do not need.
# For example, the year, month, day, time columns are redundant (we have Date/Time (LST) column).
# Let's get rid of those. The `axis=1` argument means "Drop columns", like before. The default for operations like `dropna` and `drop` is always to operate on rows.
weather_mar2012 = weather_mar2012.drop(["Year", "Month", "Day", "Time (LST)"])
print(weather_mar2012.head(5))

# TODO: redo this using polars

# %%
# When you look at the data frame, you see that some column names have some weird characters in them.
# Let's clean this up, too.
# Let's print the column names first:
print(weather_mar2012.columns)

# And now rename the columns to make it easier to work with
new_columns = [col.replace("ï»¿", "").replace("Â", "") for col in weather_mar2012.columns] # Remove the weird characters at the beginning
weather_mar2012 = weather_mar2012.rename(dict(zip(weather_mar2012.columns, new_columns)))
# Remove the weird characters at the
print(weather_mar2012.columns)
# TODO: rewrite using Polars


# %%
# Optionally, you can also rename columns more manually for specific cases:
weather_mar2012 = weather_mar2012.rename({
    'Longitude (x)': 'Longitude',
    'Latitude (y)': 'Latitude',
    'Station Name': 'Station_Name',
    'Climate ID': 'Climate_ID',
    'Temp (°C)': 'Temperature_C',
    'Dew Point Temp (Â°C)': 'Dew_Point_Temp_C',
    'Rel Hum (%)': 'Relative_Humidity',
    'Wind Spd (km/h)': 'Wind_Speed_kmh',
    'Visibility (km)': 'Visibility_km',
    'Stn Press (kPa)': 'Station_Pressure_kPa',
    'Weather': 'Weather'
}, strict=False) 
# Check the new column names

# Some people also prefer lower case column names.
weather_mar2012 = weather_mar2012.rename({col: col.lower() for col in weather_mar2012.columns})

print(weather_mar2012.columns)

# TODO: redo this using polars

# %%
# Notice how it goes up to 25° C in the middle there? That was a big deal. It was March, and people were wearing shorts outside.
temperature_data = weather_mar2012.select("temperature_c").to_series()

plt.figure(figsize=(15, 5))
plt.plot(temperature_data)
plt.title("Temperature (°C) in March 2012")
plt.xlabel("Time")
plt.ylabel("Temperature (°C)")
plt.show()
# TODO: redo this using polars

# %%
# This one's just for fun -- we've already done this before, using groupby and aggregate! We will learn whether or not it gets colder at night. Well, obviously. But let's do it anyway.
print(weather_mar2012.columns)

temperatures = weather_mar2012.select("temperature_c")

# Extracting the hour from the 'Date/Time (LST)' column and adding it as a new column 'Hour'
weather_mar2012 = weather_mar2012.with_columns([
    pl.col("correct_date_time_column").str.strptime(pl.Datetime, "%Y-%m-%d %H:%M:%S").dt.hour().alias("Hour")
])

# Grouping by 'Hour' and calculating the median of 'temperature_c'
temperature_by_hour = weather_mar2012.groupby("Hour").agg([
    pl.col("temperature_c").median().alias("median_temperature")
])

# Plotting the result
plt.figure(figsize=(15, 5))
plt.plot(temperature_by_hour["Hour"], temperature_by_hour["median_temperature"], marker='o')
plt.title("Median Temperature by Hour")
plt.xlabel("Hour of the Day")
plt.ylabel("Median Temperature (°C)")
plt.grid(True)
plt.show()
# So it looks like the time with the highest median temperature is 2pm. Neat.

# TODO: redo this using polars

# %%4
# Okay, so what if we want the data for the whole year? Ideally the API would just let us download that, but I couldn't figure out a way to do that.
# First, let's put our work from above into a function that gets the weather for a given month.


def clean_data(data):
    # Drop rows with any missing values
    data = data.drop_nulls()

    # Drop specific columns that are redundant
    data = data.drop(["Year", "Month", "Day", "Time (LST)"])

    # Replace unwanted characters in the column names
    columns = [col.replace("ï»¿", "").replace("Â", "") for col in data.columns]

    # Rename columns to meaningful names
    data = data.rename({
        'Longitude (x)': 'Longitude',
        'Latitude (y)': 'Latitude',
        'Station Name': 'Station_Name',
        'Climate ID': 'Climate_ID',
        'Temp (°C)': 'Temperature_C',
        'Dew Point Temp (°C)': 'Dew_Point_Temp_C',
        'Rel Hum (%)': 'Relative_Humidity',
        'Wind Spd (km/h)': 'Wind_Speed_kmh',
        'Visibility (km)': 'Visibility_km',
        'Stn Press (kPa)': 'Station_Pressure_kPa',
        'Weather': 'Weather'
    })

    # Convert column names to lowercase
    data = data.rename({col: col.lower() for col in data.columns})

    return data


def download_weather_month(year, month):
    url_template = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=csv&stationID=51459&Year={year}&Month={month}&Day=1&timeframe=1&submit=Download+Data"
    url = url_template.format(year=year, month=month)
    
    # Use Polars to read the CSV from the URL
    weather_data = pl.read_csv(
        url, 
        parse_dates=True, 
        infer_schema_length=0,  # Infer the schema from the first rows
        encoding="latin1"
    )

    # Clean the data
    weather_data_clean = clean_data(weather_data)

    return weather_data_clean


# TODO: redefine these functions using polars and your code above

# %%
download_weather_month(2012, 1)[:5]
# %%
# Now, let's use a list comprehension to download all our data and then just concatenate these data frames
# This might take a while
data_by_month = [download_weather_month(2012, i) for i in range(1, 13)]
weather_2012 = pl.concat(data_by_month)
print(weather_2012.head())

# TODO: do the same with polars

# %%
# Now, let's save the data.
weather_2012.write_csv("../data/weather_2012.csv")

# TODO: use polars to save the data.

# %%
