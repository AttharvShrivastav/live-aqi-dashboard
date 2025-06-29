import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- Configuration ---
CITY_NAME_FOR_TITLE = "Pithampur (Sector-2)"
CITY_ID_FOR_API = "@10522"
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

        # --- Extract Data Points ---
        current_aqi = data['data']['aqi']
        pm25_forecast_data = data['data']['forecast']['daily']['pm25']
        df_forecast = pd.DataFrame(pm25_forecast_data)
        df_forecast = df_forecast.rename(columns={"day": "date", "avg": "pm25"})
        df_forecast['date'] = pd.to_datetime(df_forecast['date'])
        iaqi_data = data['data']['iaqi']
        pollutants = {key.upper(): iaqi_data[key]['v'] for key in ['pm25', 'pm10', 'o3', 'no2'] if key in iaqi_data}
        df_pollutants = pd.DataFrame(list(pollutants.items()), columns=['Pollutant', 'Value'])

        # --- Create Visualizations ---
        print("Creating visualizations...")

        # Figure 1: Gauge Chart
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number", value = current_aqi,
            title = {'text': "Current Overall AQI", 'font': {'size': 24}},
            gauge = {'axis': {'range': [0, 300], 'tickwidth': 1, 'tickcolor': "darkblue"},
                     'bar': {'color': "rgba(0,0,0,0)"}, # Invisible bar to show colors underneath
                     'steps': [{'range': [0, 50], 'color': '#4CAF50'}, {'range': [51, 100], 'color': '#FFEB3B'},
                               {'range': [101, 150], 'color': '#FF9800'}, {'range': [151, 200], 'color': '#F44336'},
                               {'range': [201, 300], 'color': '#9C27B0'}]}
        ))
        fig_gauge.update_layout(height=400)


        # Figure 2: Bar Chart
        fig_bar = px.bar(df_pollutants, x='Pollutant', y='Value', title='Current Pollutant Levels', template='plotly_white')
        fig_bar.update_layout(title_font_size=24)

        # Figure 3: Line Chart
        fig_line = px.line(df_forecast, x='date', y='pm25', title='7-Day PM2.5 Forecast', template='plotly_white', markers=True)
        fig_line.update_layout(title_font_size=24)

        # --- NEW: Generate HTML with Bento Grid Layout ---
        print("Generating dashboard with Bento Grid layout...")

        # Convert each figure to an HTML div
        # We set include_plotlyjs=False because we will include it once in the head
        chart_div_gauge = fig_gauge.to_html(full_html=False, include_plotlyjs=False)
        chart_div_bar = fig_bar.to_html(full_html=False, include_plotlyjs=False)
        chart_div_line = fig_line.to_html(full_html=False, include_plotlyjs=False)

        # Define the HTML structure with CSS for the Bento Grid
        html_template = f"""
        <html>
        <head>
            <title>AQI Dashboard: {CITY_NAME_FOR_TITLE}</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
                    margin: 0;
                    padding: 0;
                    background-color: #f0f2f5;
                }}
                .header {{
                    background-color: white;
                    padding: 20px;
                    text-align: center;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    font-size: 2em;
                    color: #333;
                }}
                .bento-grid {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 20px;
                    padding: 20px;
                    max-width: 1200px;
                    margin: auto;
                }}
                .grid-item {{
                    background-color: white;
                    border-radius: 16px;
                    padding: 20px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                    transition: transform 0.2s ease-in-out;
                }}
                .grid-item:hover {{
                    transform: translateY(-5px);
                }}
                .wide {{
                    grid-column: span 2; /* This makes the gauge chart span both columns */
                }}
            </style>
        </head>
        <body>
            <div class="header">Air Quality Dashboard: {CITY_NAME_FOR_TITLE}</div>
            <div class="bento-grid">
                <div class="grid-item wide">{chart_div_gauge}</div>
                <div class="grid-item">{chart_div_bar}</div>
                <div class="grid-item">{chart_div_line}</div>
            </div>
        </body>
        </html>
        """

        # Write the final HTML to the file
        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(html_template)

        print("Dashboard saved successfully as index.html!")

    else:
        print(f"API status was not 'ok'. Response: {data}")

except Exception as e:
    print(f"An error occurred: {e}")