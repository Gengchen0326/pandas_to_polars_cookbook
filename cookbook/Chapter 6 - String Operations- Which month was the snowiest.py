# %%
import polars as pl  # Replacing pandas with polars
import matplotlib.pyplot as plt
import numpy as np

# Using ggplot style for plots
plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (15, 3)
plt.rcParams["font.family"] = "sans-serif"


# %%
# We saw earlier that pandas is really good at dealing with dates. It is also amazing with strings! We're going to go back to our weather data from Chapter 5, here.
pl_weather_2012 = pl.read_csv("../data/weather_2012.csv")

pl_weather_2012 = pl_weather_2012.with_columns(
    pl.col("date_time").str.strptime(pl.Datetime, format="%Y-%m-%d %H:%M:%S")
)

print(pl_weather_2012.head(5))

# TODO: load the data using polars and call the data frame pl_wather_2012


# %%
# You'll see that the 'Weather' column has a text description of the weather that was going on each hour. We'll assume it's snowing if the text description contains "Snow".
# Pandas provides vectorized string functions, to make it easy to operate on columns containing text. There are some great examples: "http://pandas.pydata.org/pandas-docs/stable/basics.html#vectorized-string-methods" in the documentation.
weather_description = pl_weather_2012["weather"]

# Check if it contains the word 'Snow'
is_snowing = weather_description.str.contains("Snow").cast(pl.Float64)

# Convert to a Pandas Series for plotting (since Polars doesn't have built-in plotting)
is_snowing_series = is_snowing.to_pandas()

# Plot the snow occurrences
is_snowing_series.plot()
plt.title("Snow Occurrences Over Time")
plt.xlabel("Time")
plt.ylabel("Is Snowing (1 = Yes, 0 = No)")
plt.show()

# TODO: do the same with polars


# %%
# If we wanted the median temperature each month, we could use the `resample()` method like this:
pl_weather_2012 = pl_weather_2012.with_columns(
    pl.col("date_time").dt.strftime("%Y-%m").alias("year_month")
)

# Group by 'year_month' and calculate the median temperature for each group
weather_by_month = pl_weather_2012.groupby("year_month").agg(
    pl.col("temperature_c").median().alias("median_temperature")
)

# Convert to Pandas DataFrame for plotting
weather_by_month_pd = weather_by_month.to_pandas()

# Plot the result as a bar chart
weather_by_month_pd.plot(kind="bar", x="year_month", y="median_temperature")
plt.title("Median Temperature by Month")
plt.xlabel("Year-Month")
plt.ylabel("Median Temperature (°C)")
plt.show()
# Unsurprisingly, July and August are the warmest.

# TODO: and now in Polars


# %%
# So we can think of snowiness as being a bunch of 1s and 0s instead of `True`s and `False`s:

# and then use `resample` to find the percentage of time it was snowing each month
# Assuming `is_snowing` is a boolean column indicating snowiness
is_snowing = pl_weather_2012["weather"].str.contains("Snow").cast(pl.Float32)

# Group by month and calculate the mean snowiness for each month
snowiness_by_month = (
    pl_weather_2012
    .with_columns(pl.col("date_time").dt.strftime("%Y-%m").alias("year_month"))
    .groupby("year_month")
    .agg(is_snowing.mean().alias("snowiness_mean"))
)

# Convert Polars DataFrame to Pandas for easier plotting
snowiness_by_month_pd = snowiness_by_month.to_pandas()

# Plot the result as a bar chart
snowiness_by_month_pd.plot(kind="bar", x="year_month", y="snowiness_mean", legend=False)
plt.title("Snowiness by Month in 2012")
plt.xlabel("Year-Month")
plt.ylabel("Mean Snowiness (0-1)")
plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
plt.tight_layout()  # Adjust layout to fit the labels
plt.show()
# So now we know! In 2012, December was the snowiest month. Also, this graph suggests something that I feel -- it starts snowing pretty abruptly in November, and then tapers off slowly and takes a long time to stop, with the last snow usually being in April or May.

# TODO: please do the same in Polars

# %%
