import csv
from collections import defaultdict
from datetime import datetime

# Function to calculate minute-wise averages
def calculate_minute_averages(input_path):
    data_by_minute = defaultdict(list)

    with open(input_path, mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                date_time_str = f"{row['Date']} {row['Time']}"
                date_time = datetime.strptime(date_time_str, '%m/%d/%Y %H:%M:%S')
                minute = date_time.strftime('%Y-%m-%d %H:%M')

                for key in row:
                    if key != 'Date' and key != 'Time':
                        if row[key]:
                            data_by_minute[minute].append(float(row[key]))
            except ValueError:
                pass

    minute_averages = {}
    for minute, values in data_by_minute.items():
        if values:
            avg = sum(values) / len(values)
            minute_averages[minute] = avg
        else:
            minute_averages[minute] = None

    print (minute_averages)
    return minute_averages



if __name__ == "__main__":
    input_path = input("Enter the pathway of the CSV file: ")
    minute_averages = calculate_minute_averages(input_path)
    
    output_path = "minute_averages.csv"
    #write_minute_averages_to_csv(output_path, minute_averages)
    print(f"Minute-wise averages saved to {output_path}")
