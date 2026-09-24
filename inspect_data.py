import pandas as pd

df = pd.read_csv("loan_data.csv")

print(df.head())

print("\nShape:")
print(df.shape)

print("\nColumns:")
print(df.columns)

print("\nDataset information:")
print(df.info())