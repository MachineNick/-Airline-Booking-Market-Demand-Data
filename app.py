from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
load_dotenv()

DATA_FILE = 'flight_data.csv'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    origin = request.form.get('origin')
    destination = request.form.get('destination')
    date = request.form.get('date')

    try:
        df = pd.read_csv(DATA_FILE)
        df_filtered = df[
            (df['departure_iata'] == origin) &
            (df['arrival_iata'] == destination) &
            (df['flight_date'] == date)
        ]

        if df_filtered.empty:
            return jsonify({'error': 'No data found for this route and date'}), 404

        return jsonify({'message': f"{len(df_filtered)} flights found for {origin} to {destination} on {date}."})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/insights', methods=['GET'])
def get_insights():
    try:
        df = pd.read_csv(DATA_FILE)

        # Popular Routes
        popular_routes = df.groupby(['departure_iata', 'arrival_iata']).size().reset_index(name='count')
        popular_routes['route'] = popular_routes['departure_iata'] + ' - ' + popular_routes['arrival_iata']
        popular_routes = popular_routes[['route', 'count']].sort_values(by='count', ascending=False).head(10)

        # Price Trends
        price_trends = df.groupby('flight_date')['price'].mean().reset_index(name='price')
        price_trends = price_trends.sort_values(by='flight_date')

        # Demand Periods (by month)
        df['month'] = pd.to_datetime(df['flight_date']).dt.month
        demand_periods = df.groupby('month').size().reset_index(name='count')

        # In-Air Flights
        in_air_flights = df[df['is_in_air'] == True][
            ['airline_name', 'flight_iata', 'departure_airport', 'arrival_airport', 'flight_date']
        ]
        in_air_flights.rename(columns={
            'airline_name': 'airline',
            'departure_airport': 'departure',
            'arrival_airport': 'arrival'
        }, inplace=True)

        return jsonify({
            'popular_routes': popular_routes.to_dict(orient='records'),
            'price_trends': price_trends.to_dict(orient='records'),
            'demand_periods': demand_periods.to_dict(orient='records'),
            'in_air_flights': in_air_flights.to_dict(orient='records')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
