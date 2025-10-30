# Description: Python simulation of a Smart-City Feedback & Optimisation Engine.
#              Now pulls *real* traffic data when possible (TomTom Freemium).

import pandas as pd
import random
import requests                         # NEW – for live traffic
from textblob import TextBlob
import folium
import webbrowser
import os
from datetime import datetime, timedelta

# --------------------------------------------------
# 1. CONFIGURATION & SETUP
# --------------------------------------------------
# --------------------------------------------------
# 1. CONFIGURATION & SETUP  (expanded metros)
# --------------------------------------------------
# --------------------------------------------------
# 1. CONFIGURATION & SETUP  (pan-India metros)
# --------------------------------------------------
CITY_LOCATIONS = {
    # ----- NORTH -----
    "Delhi": {"lat": 28.7041, "lon": 77.1025},
    "New Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Gurugram": {"lat": 28.4595, "lon": 77.0266},
    "Noida": {"lat": 28.5355, "lon": 77.3910},
    "Ghaziabad": {"lat": 28.6673, "lon": 77.4483},
    "Faridabad": {"lat": 28.4089, "lon": 77.3172},
    "Chandigarh": {"lat": 30.7333, "lon": 76.7794},
    "Jaipur": {"lat": 26.9124, "lon": 75.7873},
    "Lucknow": {"lat": 26.8467, "lon": 80.9462},
    "Kanpur": {"lat": 26.4499, "lon": 80.3319},
    "Agra": {"lat": 27.1767, "lon": 78.0081},

    # ----- WEST -----
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "Pune": {"lat": 18.5204, "lon": 73.8567},
    "Navi Mumbai": {"lat": 19.0330, "lon": 73.0297},
    "Thane": {"lat": 19.2183, "lon": 72.9781},
    "Ahmedabad": {"lat": 23.0225, "lon": 72.5714},
    "Surat": {"lat": 21.1702, "lon": 72.8311},
    "Vadodara": {"lat": 22.3072, "lon": 73.1812},
    "Nagpur": {"lat": 21.1458, "lon": 79.0882},
    "Indore": {"lat": 22.7196, "lon": 75.8577},
    "Bhopal": {"lat": 23.2599, "lon": 77.4126},

    # ----- SOUTH -----
    "Bengaluru": {"lat": 12.9716, "lon": 77.5946},
    "Hyderabad": {"lat": 17.3850, "lon": 78.4867},
    "Chennai": {"lat": 13.0827, "lon": 80.2707},
    "Coimbatore": {"lat": 11.0168, "lon": 76.9558},
    "Kochi": {"lat": 9.9312, "lon": 76.2673},
    "Thiruvananthapuram": {"lat": 8.5241, "lon": 76.9366},
    "Visakhapatnam": {"lat": 17.6868, "lon": 83.2185},
    "Mysuru": {"lat": 12.2958, "lon": 76.6394},
    "Mangaluru": {"lat": 12.9141, "lon": 74.8560},

    # ----- EAST -----
    "Kolkata": {"lat": 22.5726, "lon": 88.3639},
    "Howrah": {"lat": 22.5958, "lon": 88.2636},
    "Bhubaneswar": {"lat": 20.2961, "lon": 85.8245},
    "Guwahati": {"lat": 26.1445, "lon": 91.7362},

    # ----- CENTRAL -----
    "Raipur": {"lat": 21.2514, "lon": 81.6296},
    "Jabalpur": {"lat": 23.1815, "lon": 79.9864}
}

# Centre map on India’s geographic middle
CITY_CENTER = [22.0, 77.5]
NUM_FEEDBACK_ENTRIES = 50
NUM_TRAFFIC_RECORDS_PER_LOCATION = 1

TOMTOM_KEY = "O2nlZSRVKXsuHW3a2qfO6Jb7mDz6p6Bk"   # <── your key
if not TOMTOM_KEY:
    print("⚠️  No TomTom key found – falling back to simulated traffic.")

# --------------------------------------------------
# 2. DATA SIMULATION MODULE
# --------------------------------------------------
def simulate_citizen_feedback():
    feedback_data = []
    comments = [
        "Huge traffic jam near the flyover, it's been an hour!",
        "The new park is beautiful, great work by the municipality.",
        "Garbage has not been collected for three days on Road No. 12.",
        "Streetlight is not working, it's a safety concern at night.",
        "Water logging after just a little rain is unacceptable.",
        "The metro is so convenient and clean, love it!",
        "Too much noise pollution from construction late at night.",
        "Potholes on this road are damaging our vehicles."
    ]
    for _ in range(NUM_FEEDBACK_ENTRIES):
        location_name = random.choice(list(CITY_LOCATIONS.keys()))
        feedback_data.append({
            "timestamp": datetime.now() - timedelta(minutes=random.randint(5, 120)),
            "location": location_name,
            "feedback_text": random.choice(comments),
            "source": random.choice(["Mobile App", "Twitter"])
        })
    print(f"-> Simulated {len(feedback_data)} citizen feedback entries.")
    return feedback_data


# ----------  NEW: live-traffic helper  ----------
def fetch_live_traffic(lat: float, lon: float) -> dict | None:
    """Return live traffic for a 500 m radius around the point."""
    url = (
        "https://api.tomtom.com/traffic/services/4/flowSegmentData/"
        "absolute/10/json?point={:.5f},{:.5f}&unit=KMPH&openLr=false&key={}"
    ).format(lat, lon, TOMTOM_KEY)
    try:
        r = requests.get(url, timeout=5)
        r.raise_for_status()
        seg = r.json()["flowSegmentData"]
        return {
            "current_speed": seg["currentSpeed"],
            "free_flow": seg["freeFlowSpeed"],
            "confidence": seg["confidence"],
            "closure": seg["roadClosure"]
        }
    except Exception as e:
        # Fail silently so we fall back to simulation
        return None


def simulate_traffic_data():
    """Generate traffic records – live when possible, else fake."""
    traffic_data = []
    for location in CITY_LOCATIONS:
        loc = CITY_LOCATIONS[location]
        live = fetch_live_traffic(loc["lat"], loc["lon"])

        if live and live["confidence"] > 0.7 and not live["closure"]:
            # Use live numbers
            vehicle_count = int(50 + (live["free_flow"] - live["current_speed"]) * 10)
            entry = {
                "timestamp": datetime.now(),
                "location": location,
                "vehicle_count": max(vehicle_count, 10),
                "average_speed_kmh": int(live["current_speed"])
            }
        else:
            # Fall back to original fake generator
            is_congested = location in ["Hitech City", "Gachibowli", "Charminar"] and random.random() > 0.3
            vehicle_count = random.randint(200, 500) if is_congested else random.randint(50, 199)
            avg_speed = random.randint(5, 15) if is_congested else random.randint(16, 40)
            entry = {
                "timestamp": datetime.now() - timedelta(minutes=random.randint(1, 5)),
                "location": location,
                "vehicle_count": vehicle_count,
                "average_speed_kmh": avg_speed
            }
        traffic_data.append(entry)
    print(f"-> Built {len(traffic_data)} traffic records (live when possible).")
    return traffic_data


# --------------------------------------------------
# 3. ANALYSIS ENGINE
# --------------------------------------------------
def analyze_feedback_sentiment(feedback_df):
    feedback_df['sentiment_polarity'] = feedback_df['feedback_text'].apply(
        lambda text: TextBlob(text).sentiment.polarity)
    feedback_df['sentiment_subjectivity'] = feedback_df['feedback_text'].apply(
        lambda text: TextBlob(text).sentiment.subjectivity)
    print("-> Performed sentiment analysis on feedback data.")
    return feedback_df


def process_and_combine_data(feedback_df, traffic_df):
    location_sentiment = feedback_df.groupby('location')['sentiment_polarity'].mean().reset_index()
    location_sentiment.rename(columns={'sentiment_polarity': 'avg_sentiment_polarity'}, inplace=True)

    traffic_df['congestion_score'] = 1 - (traffic_df['average_speed_kmh'] / 50)
    traffic_df['congestion_score'] = traffic_df['congestion_score'].clip(0, 1)

    coords = pd.DataFrame([
        {'location': name, 'lat': data['lat'], 'lon': data['lon']}
        for name, data in CITY_LOCATIONS.items()
    ])
    combined_df = pd.merge(traffic_df, location_sentiment, on='location', how='left')
    combined_df = pd.merge(combined_df, coords, on='location')
    print("-> Combined and aggregated data for all locations.")
    return combined_df


# --------------------------------------------------
# 4. OPTIMISATION & RECOMMENDATION ENGINE
# --------------------------------------------------
def generate_recommendations(df):
    recommendations = []
    for _, row in df.iterrows():
        rec_text, priority = "Status: Normal.", "Low"
        if row['congestion_score'] > 0.7 and row['avg_sentiment_polarity'] < -0.2:
            rec_text = "ACTION: High traffic and public frustration detected. Dispatch traffic warden immediately."
            priority = "High"
        elif row['congestion_score'] > 0.8:
            rec_text = "ALERT: Severe traffic congestion. Monitor signals and update public traffic alerts."
            priority = "Medium"
        elif row['avg_sentiment_polarity'] < -0.4:
            rec_text = "ACTION: High negative sentiment detected. Review recent citizen feedback for urgent issues (e.g., sanitation, safety)."
            priority = "High"
        recommendations.append({"location": row['location'], "recommendation": rec_text, "priority": priority})
    print(f"-> Generated {len(recommendations)} recommendations.")
    return pd.DataFrame(recommendations)


# --------------------------------------------------
# 5. VISUALISATION & REPORTING MODULE
# --------------------------------------------------
def create_interactive_dashboard(data_df, rec_df):
    city_map = folium.Map(location=CITY_CENTER, zoom_start=12, tiles="CartoDB positron")
    data_df = pd.merge(data_df, rec_df, on='location')

    for _, row in data_df.iterrows():
        colour = 'red' if row['priority'] == 'High' else 'orange' if row['priority'] == 'Medium' else 'green'
        popup_html = f"""
        <h4><b>{row['location']}</b></h4><hr>
        <b>Priority:</b> <font color='{colour}'>{row['priority']}</font><br>
        <b>Recommendation:</b> {row['recommendation']}<hr>
        <b><u>Live Data:</u></b><br>
        <b>Avg. Sentiment Score:</b> {row['avg_sentiment_polarity']:.2f}<br>
        <b>Congestion Score:</b> {row['congestion_score']:.2f}<br>
        <b>Avg. Speed:</b> {row['average_speed_kmh']} km/h<br>
        <b>Vehicle Count:</b> {row['vehicle_count']}
        """
        iframe = folium.IFrame(popup_html, width=300, height=200)
        popup = folium.Popup(iframe, max_width=300)
        folium.Marker(
            location=[row['lat'], row['lon']],
            popup=popup,
            tooltip=f"{row['location']} ({row['priority']})",
            icon=folium.Icon(color=colour, icon='info-sign')
        ).add_to(city_map)

    output_filename = "smart_city_dashboard.html"
    city_map.save(output_filename)
    print(f"\n-> Interactive dashboard created: '{output_filename}'")
    return output_filename


# --------------------------------------------------
# 6. MAIN EXECUTION
# --------------------------------------------------
if __name__ == "__main__":
    print("--- Smart City Engine Simulation Initializing ---")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    feedback = simulate_citizen_feedback()
    traffic = simulate_traffic_data()

    feedback_df = pd.DataFrame(feedback)
    traffic_df = pd.DataFrame(traffic)

    feedback_df = analyze_feedback_sentiment(feedback_df)
    combined_data_df = process_and_combine_data(feedback_df, traffic_df)

    recommendations_df = generate_recommendations(combined_data_df)
    dashboard_file = create_interactive_dashboard(combined_data_df, recommendations_df)

    print("\n--- Optimization Summary ---")
    print(recommendations_df)
    print("\n--- Simulation Complete ---")
    print("Opening the interactive dashboard in your web browser...")

    try:
        webbrowser.open('file://' + os.path.realpath(dashboard_file))
    except Exception as e:
        print(f"Could not auto-open the file. Please open '{dashboard_file}' manually.")
        print(f"Error: {e}")