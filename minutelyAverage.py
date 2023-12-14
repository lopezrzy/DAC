import pandas as pd
import yagmail
import datetime


def sendData(description, original_data, minutelyAv_data):
    # Set up your yagmail instance
    #email_address = 'dacceakaust@gmail.com '
    #password = 'dac202312'
    #yag = yagmail.SMTP(email_address, password)
    
    email_address = 'bantanalamin@gmail.com'
    password = 'muzomvmpwxiczzmo'
    yag = yagmail.SMTP(email_address, password)
    
    try:
      # Compose the email
      rec = ['zulma.lopezreyes@kaust.edu.sa','wesley.hopwood@kaust.edu.sa']
      today_date = datetime.datetime.now().strftime('%Y-%m-%d')
      today_date2 = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
      subject_ = f'DAC data: {today_date}'      
      body = f'{description} at {today_date2}' 
      yag.send(to=rec, subject=subject_, contents=body, attachments= [original_data, minutelyAv_data])

      print(f'Email sent successfully to {rec}')
    
    except Exception as e:
      # Log the error
      print(f"Error: {e}")
    
    finally:
      # Logout
      yag.close()

# Function to calculate the minutely average
def calculate_minutely_average(dataframe):
    dataframe['Date'] = pd.to_datetime(dataframe['Date'] + ' ' + dataframe['Time'])
    dataframe = dataframe.set_index('Date')
    dataframe = dataframe.drop(columns=['Time'])
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

description = input("Description: ")


# Calculate minutely averages
minutely_avg_df = calculate_minutely_average(df)

# Create a new CSV file with minutely averages
output_path = input_path.replace('.csv', '_minutely.csv')
minutely_avg_df.to_csv(output_path)

sendData(description, input_path, output_path)

print(f"Minutely averages saved to {output_path}")
