import requests
import pandas as pd
import plotly.express as px
import os

# --- Configuration ---
CITY_NAME_FOR_TITLE = "Pithampur (Sector-2)"
CITY_ID_FOR_API = "@10522"
API_KEY = os.environ.get('AQI_API_KEY', 'd71cf8a4a7136a8aa76ca5ab543c206d0ed3925d') 
API_URL = f"https://api.waqi.info/feed/{CITY_ID_FOR_API}/?token={API_KEY}"

# --- Data Acquisition ---
print(f"Fetching data for {CITY_NAME_FOR_TITLE}...")
try:
    response = requests.get(API_URL)
    response.raise_for_status()  # This will raise an error for bad responses (4xx or 5xx)
    data = response.json()

    # --- Data Processing and Cleaning ---
    if data.get("status") == "ok":
        print("Data fetched successfully!")
        forecast_data = data["data"]["forecast"]["daily"]["pm25"]

        df = pd.DataFrame(forecast_data)
        df = df.rename(columns={"day": "date"})
        df = df.rename(columns={"avg": "pm25"})
        df['date'] = pd.to_datetime(df['date'])
        df = df[['date', 'pm25']]

        print("Data cleaned and prepared. Here's a preview:")
        print(df.head())

        # --- Data Visualization ---
        print("Creating visualization...")
        fig = px.line(
            df, 
            x='date', 
            y='pm25', 
            title=f'Forecasted PM2.5 Levels in {CITY_NAME_FOR_TITLE}',
            labels={'date': 'Date', 'pm25': 'PM2.5 Level (µg/m³)'},
            template='plotly_white',
            markers=True
        )

        fig.update_layout(
            title_font_size=24,
            xaxis_title_font_size=16,
            yaxis_title_font_size=16,
            font_family="Arial, sans-serif"
        )
        fig.update_traces(line=dict(width=3))

        # --- Save to HTML ---
        output_file = "dashboard.html"
        fig.write_html(output_file)
        print(f"Chart saved successfully as {output_file}!")

    else:
        print(f"API status was not 'ok'. Please check the station ID: {CITY_ID_FOR_API}")
        print("API Response:", data)

except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching data: {e}")
except KeyError as e:
    print(f"Could not find expected data key in the API response: {e}")
    print("Please check the API's JSON structure.")