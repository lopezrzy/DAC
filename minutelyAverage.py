import pandas as pd

# Function to calculate the minutely average
def calculate_minutely_average(dataframe):
    print(dataframe.columns)
    dataframe['Date'] = pd.to_datetime(dataframe['Date'] + ' ' + dataframe['Time'])
    print('_')
    print(dataframe.columns)
    dataframe = dataframe.set_index('Date')
    dataframe = dataframe.drop(columns=['Date', 'Time'])
    minutely_avg = dataframe.resample('1T').mean()
    return minutely_avg

# Input path for the CSV file
input_path = input("Enter the path to the input CSV file: ")

# Read the CSV file
try:
    df = pd.read_csv(input_path)
except FileNotFoundError:
    print("File not found. Please provide a valid file path.")
    exit(1)

# Calculate minutely averages
minutely_avg_df = calculate_minutely_average(df)

# Create a new CSV file with minutely averages
output_path = input_path.replace('.csv', '_minutely.csv')
minutely_avg_df.to_csv(output_path)

print(f"Minutely averages saved to {output_path}")
