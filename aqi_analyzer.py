import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuration ---
CITY_NAME_FOR_TITLE = "Pithampur (Sector-2)"
CITY_ID_FOR_API = "@10522"
# The script will first try to get the API key from a GitHub Secret, 
# then fall back to the key you provide here.
API_KEY = os.environ.get('AQI_API_KEY', 'd71cf8a4a7136a8aa76ca5ab543c206d0ed3925d') 
API_URL = f"https://api.waqi.info/feed/{CITY_ID_FOR_API}/?token={API_KEY}"

# --- Data Acquisition & Processing ---
print(f"Fetching data for {CITY_NAME_FOR_TITLE}...")
try:
    response = requests.get(API_URL)
    response.raise_for_status()
    data = response.json()

    if data.get("status") == "ok":
        print("Data fetched successfully!")
        
        # --- Extract Different Data Points ---
        # 1. Current AQI
        current_aqi = data['data']['aqi']
        
        # 2. Individual Pollutant Forecasts (PM2.5)
        pm25_forecast_data = data['data']['forecast']['daily']['pm25']
        df_forecast = pd.DataFrame(pm25_forecast_data)
        df_forecast = df_forecast.rename(columns={"day": "date", "avg": "pm25"})
        df_forecast['date'] = pd.to_datetime(df_forecast['date'])
        
        # 3. Current Individual Pollutant Levels
        iaqi_data = data['data']['iaqi']
        pollutants = {key: iaqi_data[key]['v'] for key in ['pm25', 'pm10', 'o3', 'no2', 'so2', 'co'] if key in iaqi_data}
        df_pollutants = pd.DataFrame(list(pollutants.items()), columns=['Pollutant', 'Value'])

        # --- Create Visualizations ---
        print("Creating visualizations...")
        
        # Figure 1: Gauge Chart for Current AQI
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = current_aqi,
            title = {'text': f"Current AQI in {CITY_NAME_FOR_TITLE}"},
            gauge = {
                'axis': {'range': [0, 300]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': 'green'},
                    {'range': [51, 100], 'color': 'yellow'},
                    {'range': [101, 150], 'color': 'orange'},
                    {'range': [151, 200], 'color': 'red'},
                    {'range': [201, 300], 'color': 'purple'}
                ],
            }
        ))

        # Figure 2: Bar Chart for Current Pollutant Levels
        fig_bar = px.bar(
            df_pollutants, 
            x='Pollutant', 
            y='Value',
            title='Current Pollutant Levels',
            template='plotly_white'
        )
        
        # Figure 3: Line Chart for PM2.5 Forecast
        fig_line = px.line(
            df_forecast, 
            x='date', 
            y='pm25', 
            title='7-Day PM2.5 Forecast',
            template='plotly_white',
            markers=True
        )

        # --- Combine into a single HTML file ---
        print("Combining charts into a single HTML file...")
        with open('index.html', 'w') as f:
            f.write(f"<html><head><title>AQI Dashboard for {CITY_NAME_FOR_TITLE}</title></head><body>")
            f.write(f"<h1 style='text-align:center;'>Air Quality Dashboard: {CITY_NAME_FOR_TITLE}</h1>")
            # Convert figures to HTML and write to file
            f.write(fig_gauge.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write(fig_bar.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write(fig_line.to_html(full_html=False, include_plotlyjs='cdn'))
            f.write("</body></html>")

        print("Dashboard saved successfully as index.html!")

    else:
        print(f"API status was not 'ok'. Response: {data}")

except Exception as e:
    print(f"An error occurred: {e}")