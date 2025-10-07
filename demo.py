from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Define synthetic polygon data for East African FIRs and upper traffic zones (sample expanded)
fir_polygons = {
    "Kenya FIR": {
        "coords": [[5.0, 34.0], [5.0, 42.0], [-1.0, 42.0], [-1.0, 34.0], [5.0, 34.0]],
        "color": "rgba(255, 0, 0, 0.2)"
    },
    "Uganda FIR": {
        "coords": [[1.5, 29.0], [1.5, 35.5], [-2.5, 35.5], [-2.5, 29.0], [1.5, 29.0]],
        "color": "rgba(0, 255, 0, 0.2)"
    },
    "Tanzania FIR": {
        "coords": [[-1.0, 34.0], [-1.0, 40.0], [-7.0, 40.0], [-7.0, 34.0], [-1.0, 34.0]],
        "color": "rgba(0, 0, 255, 0.2)"
    },
    "Upper Traffic Zone": {
        "coords": [[-2.0, 33.0], [4.0, 43.0], [10.0, 43.0], [10.0, 33.0], [-2.0, 33.0]],
        "color": "rgba(255, 255, 0, 0.15)"
    }
}

# Airport data sample (integrated from cell gEJz7Wj1igqN)
airport_data = [
    {'country': 'Uganda', 'city': 'Entebbe', 'name': 'Entebbe International', 'iata': 'EBB', 'lat': 0.042386, 'lon': 32.443503},
    {'country': 'Rwanda', 'city': 'Kigali', 'name': 'Kigali International', 'iata': 'KGL', 'lat': -1.968629, 'lon': 30.139492},
    {'country': 'Kenya', 'city': 'Nairobi', 'name': 'Jomo Kenyatta International', 'iata': 'NBO', 'lat': -1.319167, 'lon': 36.927500},
    {'country': 'Kenya', 'city': 'Mombasa', 'name': 'Moi International', 'iata': 'MBA', 'lat': -4.034833, 'lon': 39.594250},
    {'country': 'Kenya', 'city': 'Nairobi', 'name': 'Wilson Airport', 'iata': 'WIL', 'lat': -1.321889, 'lon': 36.814833},
    {'country': 'Kenya', 'city': 'Eldoret', 'name': 'Eldoret International', 'iata': 'EDL', 'lat': 0.404457, 'lon': 35.238886},
    {'country': 'Tanzania', 'city': 'Dar es Salaam', 'name': 'Julius Nyerere International', 'iata': 'DAR', 'lat': -6.878111, 'lon': 39.202625},
    {'country': 'Tanzania', 'city': 'Kilimanjaro', 'name': 'Kilimanjaro International', 'iata': 'JRO', 'lat': -3.429406, 'lon': 37.074461},
    {'country': 'Tanzania', 'city': 'Zanzibar', 'name': 'Abeid Amani Karume Intl', 'iata': 'ZNZ', 'lat': -6.221978, 'lon': 39.224911},
    {'country': 'Burundi', 'city': 'Bujumbura', 'name': 'Bujumbura International', 'iata': 'BJM', 'lat': -3.324019, 'lon': 29.318519},
    {'country': 'D.R. Congo', 'city': 'Kinshasa', 'name': "N’djili International", 'iata': 'FIH', 'lat': -4.385751, 'lon': 15.444600},
    {'country': 'D.R. Congo', 'city': 'Goma', 'name': 'Goma International', 'iata': 'GOM', 'lat': -1.670814, 'lon': 29.238472},
    {'country': 'D.R. Congo', 'city': 'Lubumbashi', 'name': 'Lubumbashi International', 'iata': 'FBM', 'lat': -11.591514, 'lon': 27.530107},
    {'country': 'South Sudan', 'city': 'Juba', 'name': 'Juba International', 'iata': 'JUB', 'lat': 4.872006, 'lon': 31.601117},
    {'country': 'Somalia', 'city': 'Mogadishu', 'name': 'Aden Adde International', 'iata': 'MGQ', 'lat': 2.014547, 'lon': 45.304698},
    {'country': 'Somalia', 'city': 'Berbera', 'name': 'Berbera International', 'iata': 'BBO', 'lat': 10.389167, 'lon': 44.941111},
    {'country': 'Somalia', 'city': 'Hargeisa', 'name': 'Egal International', 'iata': 'HGA', 'lat': 9.519917, 'lon': 44.088806},
    {'country': 'Somalia', 'city': 'Garowe', 'name': 'Garowe Airport', 'iata': 'GGR', 'lat': 8.460556, 'lon': 48.484444},
]


def generate_synthetic_data(numflights=80):
    bounds = {"latmin": -7, "latmax": 10, "lonmin": 29, "lonmax": 43}
    np.random.seed(42)
    flightids = [f"EA{str(i).zfill(3)}" for i in range(1, numflights + 1)]
    latitudes = np.random.uniform(bounds["latmin"], bounds["latmax"], numflights)
    longitudes = np.random.uniform(bounds["lonmin"], bounds["lonmax"], numflights)
    statuses = np.random.choice(["on-time", "delayed", "rerouted"], size=numflights, p=[0.65, 0.25, 0.10])
    congestionlevels = np.random.beta(a=2, b=5, size=numflights)
    airlines = np.random.choice(["AirKenya", "Ethiopian Airlines", "RwandAir", "Precision Air"], size=numflights)
    now = datetime.now()
    flighttimes = [now - timedelta(minutes=int(x)) for x in np.random.randint(0, 180, numflights)]
    origins = np.random.choice([a["iata"] for a in airport_data], size=numflights)
    destinations = np.random.choice([a["iata"] for a in airport_data], size=numflights)
    estimateddelay = np.random.randint(0, 60, numflights)
    emissionssaved = np.round(np.random.uniform(50, 300, numflights), 1)

    # Simulate flight rerouting by creating alternate routes for rerouted flights
    route_lons = []
    route_lats = []

    for status, o, d in zip(statuses, origins, destinations):
        o_coord = next((a for a in airport_data if a["iata"] == o), None)
        d_coord = next((a for a in airport_data if a["iata"] == d), None)
        if o_coord and d_coord:
            if status == "rerouted":
                # Generate a simple reroute via a middle point offset
                mid_lat = (o_coord["lat"] + d_coord["lat"])/2 + np.random.uniform(-0.5, 0.5)
                mid_lon = (o_coord["lon"] + d_coord["lon"])/2 + np.random.uniform(-0.5, 0.5)
                route_lats.append([o_coord["lat"], mid_lat, d_coord["lat"]])
                route_lons.append([o_coord["lon"], mid_lon, d_coord["lon"]])
            else:
                # Straight route
                route_lats.append([o_coord["lat"], d_coord["lat"]])
                route_lons.append([o_coord["lon"], d_coord["lon"]])
        else:
            route_lats.append([0, 0])
            route_lons.append([0, 0])


    df = pd.DataFrame({
        "flight": flightids,
        "lat": latitudes,
        "lon": longitudes,
        "status": statuses,
        "congestion": congestionlevels,
        "airline": airlines,
        "timestamp": flighttimes,
        "origin": origins,
        "destination": destinations,
        "estimateddelay": estimateddelay,
        "emissionssaved": emissionssaved,
        "route_lats": route_lats,
        "route_lons": route_lons,
    })
    return df

app = Dash(__name__)

app.layout = html.Div([
    html.H1("East African Airspace Management Prototype Dashboard"),
    html.Div([
        dcc.Dropdown(
            id='status-filter',
            options=[{'label': s.title(), 'value': s} for s in ["on-time", "delayed", "rerouted"]],
            value="on-time",
            clearable=False,
            style={"width": "180px"}
        ),
        dcc.Dropdown(
            id='airline-filter',
            options=[{'label': a, 'value': a} for a in ["AirKenya", "Ethiopian Airlines", "RwandAir", "Precision Air"]],
            value="AirKenya",
            clearable=False,
            style={"width": "220px", "marginLeft": "20px"}
        ),
        html.Div([ # Wrap the RangeSlider in a Div
            dcc.RangeSlider(
                id='time-range',
                min=0,
                max=180,
                marks={i: f'{i}m ago' for i in range(0, 181, 30)},
                step=5,
                value=[0, 180],
                tooltip={"placement": "bottom", "always_visible": True},
                allowCross=False,
            )
        ], style={"width": "400px", "marginLeft": "20px"}) # Apply style to the wrapping Div
    ], style={"display": "flex", "alignItems": "center", "marginBottom": "20px"}),
    html.Div(id="summary-stats", style={"display": "flex", "justifyContent": "space-around", "marginBottom": "10px"}),
    dcc.Graph(id='map-graph', style={"height": "750px"}),
    html.Div(id='flight-info', style={"marginTop": "20px", "padding": "10px", "border": "1px solid #ccc"})
])

def add_fir_polygons(fig):
    for name, fir in fir_polygons.items():
        lat_c, lon_c = zip(*fir["coords"])
        fig.add_trace(go.Scattermapbox(
            fill="toself",
            lon=lon_c,
            lat=lat_c,
            marker={'size': 0},
            fillcolor=fir["color"],
            line={"color": fir["color"].replace("0.2", "0.8"), "width": 2},
            name=name,
            hoverinfo="text",
            text=name,
            showlegend=True
        ))

@app.callback(
    Output('map-graph', 'figure'),
    Output('summary-stats', 'children'),
    Input('status-filter', 'value'),
    Input('airline-filter', 'value'),
    Input('time-range', 'value')
)
def update_map(status_value, airline_value, time_range):
    df = generate_synthetic_data()
    now = datetime.now()
    lower_time = now - timedelta(minutes=time_range[1])
    upper_time = now - timedelta(minutes=time_range[0])
    filtered_df = df[
        (df['status'] == status_value) &
        (df['airline'] == airline_value) &
        (df['timestamp'] >= lower_time) &
        (df['timestamp'] <= upper_time)
    ].dropna(subset=['congestion']) # Drop rows with NaN congestion

    fig = go.Figure()

    add_fir_polygons(fig)

    # Add airports as orange markers (integrated from cell gEJz7Wj1igqN)
    fig.add_trace(go.Scattermapbox(
        lat=[a['lat'] for a in airport_data],
        lon=[a['lon'] for a in airport_data],
        mode='markers',
        marker=dict(
            size=14,
            color='orange',
            symbol='airport'
        ),
        text=[f"{a['name']} ({a['iata']}) - {a['city']}, {a['country']}" for a in airport_data],
        hoverinfo='text',
        name='Airports'
    ))

    # Add rerouting paths as different color lines
    for _, row in filtered_df.iterrows():
        line_width = 1
        if row["status"] == "rerouted":
            line_color = "blue"
            opacity = 0.7
            line_width = 2
        else:
            line_color = "gray"
            opacity = 0.4

        fig.add_trace(go.Scattermapbox(
            lat=row['route_lats'],
            lon=row['route_lons'],
            mode='lines',
            line=dict(color=line_color, width=line_width),
            opacity=opacity,
            name=f'Route {row["flight"]}',
            hoverinfo='none',
            showlegend=False
        ))

    # Flight markers, colored by congestion to represent congestion heatmap
    if not filtered_df.empty: # Add check for empty DataFrame
        fig.add_trace(go.Scattermapbox(
            lat=filtered_df['lat'],
            lon=filtered_df['lon'],
            mode='markers',
            marker=dict(
                size=12,
                color=filtered_df['congestion'],
                colorscale='OrRd',
                cmin=0,
                cmax=1,
                colorbar=dict(title="Congestion"),

            ),
            text=filtered_df['flight'],
            hoverinfo='text',
            name='Flights'
        ))

    fig.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(
            center=dict(lat=0.5, lon=36),
            zoom=5
        ),
        margin=dict(t=0, b=0, r=0, l=0),
        legend=dict(y=0.99, yanchor="top")
    )

    count = len(filtered_df)
    avg_delay = filtered_df["estimateddelay"].mean() if count > 0 else 0
    total_emissions = filtered_df["emissionssaved"].sum() if count > 0 else 0
    avg_congestion = filtered_df["congestion"].mean() if count > 0 else 0

    stats = [
        html.Div([html.H4("Flights Displayed"), html.P(f"{count}")], style={"width": "24%", "textAlign": "center"}),
        html.Div([html.H4("Avg Delay (min)"), html.P(f"{avg_delay:.1f}")], style={"width": "24%", "textAlign": "center"}),
        html.Div([html.H4("Total Emissions Saved"), html.P(f"{total_emissions:.1f} tons")], style={"width": "24%", "textAlign": "center"}),
        html.Div([html.H4("Avg Congestion"), html.P(f"{avg_congestion:.2f}")], style={"width": "24%", "textAlign": "center"}),
    ]

    return fig, stats

@app.callback(
    Output('flight-info', 'children'),
    Input('map-graph', 'clickData')
)
def show_flight_details(click_data):
    if click_data and "points" in click_data and click_data["points"]:
        point = click_data["points"][0]
        # Check if the clicked point is a flight marker (has 'text' property)
        if 'text' in point:
          flight_id = point['text']
          df = generate_synthetic_data()
          flight = df[df["flight"] == flight_id].iloc[0]
          reroute_text = "Yes" if flight["status"] == "rerouted" else "No"
          return html.Div([
              html.H3(f"Flight {flight['flight']}"),
              html.P(f"Status: {flight['status'].title()}"),
              html.P(f"Airline: {flight['airline']}"),
              html.P(f"Origin: {flight['origin']}"),
              html.P(f"Destination: {flight['destination']}"),
              html.P(f"Estimated Delay: {flight['estimateddelay']} minutes"),
              html.P(f"Emissions Saved: {flight['emissionssaved']} metric tons"),
              html.P(f"Congestion Level: {flight['congestion']:.2f}"),
              html.P(f"Is Rerouted: {reroute_text}"),
              html.P(f"Timestamp: {flight['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
          ])
        else:
             return "Click on a flight marker on the map to see detailed flight information."

    else:
        return "Click on a flight marker on the map to see detailed flight information."

if __name__ == '__main__':
    app.run(debug=True)