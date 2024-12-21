import pandas as pd

# Define the chunk size
chunksize = 1000000

# Create a chunk generator
chunk_reader = pd.read_csv("../Databases/mimic-iv-3.1/mimic-iv-3.1/icu/chartevents.csv", chunksize=chunksize)

# Iterate over the chunks
for chunk in chunk_reader:
    print(chunk)  # Print the first few rows of the current chunk
