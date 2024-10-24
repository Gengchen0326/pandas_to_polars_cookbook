# %%
import pandas as pd
import matplotlib.pyplot as plt
import polars as pl

# Make the graphs a bit prettier, and bigger
plt.style.use("ggplot")
plt.rcParams["figure.figsize"] = (15, 5)

# This is necessary to show lots of columns in pandas 0.12.
# Not necessary in pandas 0.13.
pd.set_option("display.width", 5000)
pd.set_option("display.max_columns", 60)

# %%
# Let's continue with our NYC 311 service requests example.
# because of mixed types we specify dtype to prevent any errors
complaints = pd.read_csv("/Users/shiyi/Desktop/Term 1/D100 Fundamentals of Data Science/pandas_to_polars_cookbook/data/311-service-requests.csv", dtype="unicode")

# %%
# TODO: rewrite the above using the polars library (you might have to import it above) and call the data frame pl_complaints
pl_complaints = pl.read_csv("/Users/shiyi/Desktop/Term 1/D100 Fundamentals of Data Science/pandas_to_polars_cookbook/data/311-service-requests.csv", schema_overrides={"*": pl.Utf8}, null_values=["N/A", "77092-2016", "55164-0737"], infer_schema_length=10000, ignore_errors=True)
# %%
# 3.1 Selecting only noise complaints
# I'd like to know which borough has the most noise complaints. First, we'll take a look at the data to see what it looks like:
complaints[:5]
pl_complaints.head(5)
# %%
# TODO: rewrite the above in polars

# %%
# To get the noise complaints, we need to find the rows where the "Complaint Type" column is "Noise - Street/Sidewalk".
noise_complaints = complaints[complaints["Complaint Type"] == "Noise - Street/Sidewalk"]
noise_complaints[:3]

# %%
# TODO: rewrite the above in polars
noise_complaints = pl_complaints.filter(pl_complaints["Complaint Type"] == "Noise - Street/Sidewalk")
noise_complaints.head(3)

# %%
# Combining more than one condition
is_noise = complaints["Complaint Type"] == "Noise - Street/Sidewalk"
in_brooklyn = complaints["Borough"] == "BROOKLYN"
complaints[is_noise & in_brooklyn][:5]

# %%
# TODO: rewrite the above using the Polars library. In polars these conditions are called Expressions.
# Check out the Polars documentation for more info.
is_noise = pl_complaints["Complaint Type"] == "Noise - Street/Sidewalk"
in_brooklyn = pl_complaints["Borough"] == "BROOKLYN"
noise_in_brooklyn = pl_complaints.filter(is_noise & in_brooklyn)
noise_in_brooklyn.head(5)

# %%
# If we just wanted a few columns:
complaints[is_noise & in_brooklyn][
    ["Complaint Type", "Borough", "Created Date", "Descriptor"]
][:10]

# %%
# TODO: rewrite the above using the polars library
selected_columns = noise_in_brooklyn.select(
    ["Complaint Type", "Borough", "Created Date", "Descriptor"]
)
selected_columns.head(10)

# %%
# 3.3 So, which borough has the most noise complaints?
is_noise = complaints["Complaint Type"] == "Noise - Street/Sidewalk"
noise_complaints = complaints[is_noise]
noise_complaints["Borough"].value_counts()

# %%
# TODO: rewrite the above using the polars library
is_noise = pl_complaints["Complaint Type"] == "Noise - Street/Sidewalk"
noise_complaints = pl_complaints.filter(is_noise)
borough_counts = noise_complaints.groupby("Borough").count().sort("count", reverse=True)

# %%
# What if we wanted to divide by the total number of complaints?
noise_complaint_counts = noise_complaints["Borough"].value_counts()
complaint_counts = complaints["Borough"].value_counts()

noise_complaint_counts / complaint_counts.astype(float)

# %%
# TODO: rewrite the above using the polars library
noise_complaint_counts = noise_complaints.groupby("Borough").count().rename({"count": "noise_count"})
complaint_counts = pl_complaints.groupby("Borough").count().rename({"count": "total_count"})
result = noise_complaint_counts.join(complaint_counts, on="Borough")
result = result.with_columns((pl.col("noise_count") / pl.col("total_count")).alias("noise_complaint_ratio"))

# %%
# Plot the results
(noise_complaint_counts / complaint_counts.astype(float)).plot(kind="bar")
plt.title("Noise Complaints by Borough (Normalized)")
plt.xlabel("Borough")
plt.ylabel("Ratio of Noise Complaints to Total Complaints")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# %%
# TODO: rewrite the above using the polars library. NB: polars' plotting method is sometimes unstable. You might need to use seaborn or matplotlib for plotting.
