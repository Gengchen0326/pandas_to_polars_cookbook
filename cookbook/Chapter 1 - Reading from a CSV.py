import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

# %%
# Reading data from a csv file
# You can read data from a CSV file using the `read_csv` function. By default, it assumes that the fields are comma-separated.

# We're going to be looking at some cyclist data from Montréal. Here's the [original page](http://donnees.ville.montreal.qc.ca/dataset/velos-comptage) (in French), but it's already included in this repository. We're using the data from 2012.

# This dataset is a list of how many people were on 7 different bike paths in Montreal, each day.

pl_broken_df = pl.read_csv('/Users/shiyi/Desktop/Term 1/D100 Fundamentals of Data Science/pandas to polar notebook/pandas_to_polars_cookbook/data/bikes.csv', encoding="ISO-8859-1")

# %%
# Look at the first 3 rows
pl_broken_df.head(3)

# %%
# You'll notice that this is totally broken! `read_csv` has a bunch of options that will let us fix that, though. Here we'll

# * change the column separator to a `;`
# * Set the encoding to `'latin1'` (the default is `'utf8'`)
# * Parse the dates in the 'Date' column
# * Tell it that our dates have the day first instead of the month first
# * Set the index to be the 'Date' column

pl_fixed_df = pl.read_csv(
    '/Users/shiyi/Desktop/Term 1/D100 Fundamentals of Data Science/pandas to polar notebook/pandas_to_polars_cookbook/data/bikes.csv',
    separator=";",
    encoding="latin1",
        infer_schema_length=10000,
)

pl_fixed_df = pl_fixed_df.with_columns(pl.col('Date').str.strptime(pl.Date, '%d/%m/%Y').alias('Date'))

pl_fixed_df.head(3)

# %%
# Selecting a column
pl_fixed_df.select("Berri 1")

# %%
# Plotting is quite easy in Polars using Matplotlib and Seaborn
sns.lineplot(data=pl_fixed_df.to_pandas(), x="Date", y="Berri 1")
plt.show()

# %%
# We can also plot all the columns just as easily. We'll make it a little bigger, too.
pl_fixed_df_pd = pl_fixed_df.to_pandas()
pl_fixed_df_pd.plot(figsize=(15, 10))
plt.show()