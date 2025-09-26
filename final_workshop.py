import streamlit as st
import re
import math
import json
import base64
import requests # Added for weather API calls
from gtts import gTTS
from io import BytesIO

# --- PAGE CONFIG ---
st.set_page_config(page_title="BusBuddy Chatbot", page_icon="🚌", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main App background */
    .stApp {
        background-color: #E6E6FA; /* Light lavender background */
    }
    
    /* --- Sidebar Styles --- */
    [data-testid="stSidebar"] {
        background-color: #023e8a;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stMarkdown {
        color: white;
    }

    /* Style for the chat messages */
    .stChatMessage {
        border-radius: 10px;
        padding: 1rem;
        width: 80%;
        margin: 0 auto; /* Center the chat messages in the main area */
    }
    .main .stChatInput {
        width: 80%;
        margin: 0 auto; /* Center the chat input */
    }
    
    /* Custom style for sidebar examples */
    .sidebar-text {
        font-size: 1.1em;
        font-weight: bold;
        color: white;
    }
    .sidebar-caption {
        font-size: 0.9em;
        font-style: italic;
        color: #d3d3d3; /* Light grey for caption */
        margin-bottom: 1em; /* Add space between items */
    }

</style>
""", unsafe_allow_html=True)


# --- DATA ---
# Bus route data
bus_routes = {
    "1": ["IBRAHIMPATNAM", "SWATHI", "KUMMARI PALEM", "KR MARKET", "RAILWAY STATION", "BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KAMAYYATHOPU", "SIDDHARTHA", "PORANKI"],
    "1G": ["GOLLAPUDI", "KUMMARI PALEM", "BHAVANI PURAM", "RAILWAY STATION", "BUS STAND", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KANURU", "PORANKI", "KANKIPADU"],
    "2": ["KALESWARARAO MARKET", "KR MARKET", "TUMMALAPALLI KALKSHETRAM", "BUS STAND", "OLD BUS STAND", "BUNGLAW", "LENINE CENTER", "BESENT ROAD", "BANDAR ROAD", "RAMANDIRAM", "VIJAYA TALKIES", "KOTHAVANTENA", "SITARAMPURAM", "CHUTTUGUNTA", "MARUTHINAGAR", "SRR COLLEGE", "ANJANEYA SWAMY TEMPLE", "MACHAVARAM", "PADAVALAREVU", "GUNADALA CHURCH", "GUNADALA", "GUNADALA VANTHENA", "ESI", "POWER OFFICE", "RING ROAD", "RAMAVARAPADU"],
    "2K": ["KALESWARARAO MARKET", "KANURU"],
    "3": ["KABELA", "GOVERNMENT PRESS"],
    "3D": ["MILK PROJECT", "DEVI NAGAR"],
    "5": ["KABELA", "KR MARKET", "TUMMALAPALLI KALKSHETRAM", "BUS STAND", "OLD BUS STAND", "NAKKAL ROAD", "BESENT ROAD", "PUSHPA HOTEL", "RAMESH HOSPITAL", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR"],
    "5G": ["KALESWARARAO MARKET", "KR MARKET", "TUMMALAPALLI KALKSHETRAM", "BUS STAND", "OLD BUS STAND", "NAKKAL ROAD", "BESENT ROAD", "PUSHPA HOTEL", "RAMESH HOSPITAL", "GURUNANAK COLONY", "AUTONAGAR"],
    "5SG": ["RAILWAY STATION", "OLD BUS STAND", "NAKKAL ROAD", "BESANT ROAD", "PUSHPA HOTEL", "RAMESH HOSPITAL", "GURUNANAK COLONY", "AUTONAGAR"],
    "7A": ["KALESWARARAO MARKET", "BUNDAR ROAD", "BESANT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "PEDDA PULI PAKA"],
    "7ST":["RAILWAY STN","BUS STAND","OLD BUS STAND","BESANT ROAD","IGMC STADIUM","PVP","KANDARI","BENZ CIRCLE","NTR CIRCLE","PATAMATA","AUTONAGAR","KAMAYATHOPU","SIDDHARTHA","TADIGADAPA"],
    "7R": ["MILK PROJECT", "KR MARKET", "BUS STAND", "OLD BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "YANAMALA KUDURU"],
    "10": ["RAILWAY STATION", "BUNDAR ROAD", "BESANT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KANURU", "PORANKI", "PENAMALURU"],
    "10K": ["RAILWAY STATION","BUS STAND", "BUNDAR ROAD","IGMC STADIUM", "BESANT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KANURU", "PORANKI", "PENAMALURU"],
    "10C": ["RAILWAY STATION", "BUNDAR ROAD", "BESANT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KANURU", "PORANKI", "CHODAVARAM"],
    "11": ["MILK PROJECT", "KR MARKET", "TUMMALAPALLI KALKSHETRAM", "BUS STAND", "OLD BUS STAND", "BUNGLAW", "LENINE CENTER", "BESENT ROAD", "RAMANDIRAM", "VIJAYA TALKIES", "KOTHAVANTENA", "SITARAMPURAM", "CHUTTUGUNTA", "MARUTHINAGAR", "SRR COLLEGE", "ANJANEYA SWAMY TEMPLE", "MACHAVARAM", "PADAVALAREVU", "GUNADALA CHURCH", "GUNADALA", "GUNADALA VANTHENA", "ESI", "POWER OFFICE", "RING ROAD", "RAMAVARAPADU", "RAMESH HOSPITAL", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR"],
    "11H": ["KABELA", "KR MARKET", "TUMMALAPALLI KALKSHETRAM", "BUS STAND", "OLD BUS STAND", "BUNGLAW", "LENINE CENTER", "BESENT ROAD", "RAMANDIRAM", "VIJAYA TALKIES", "KOTHAVANTENA", "SITARAMPURAM", "CHUTTUGUNTA", "MARUTHINAGAR", "SRR COLLEGE", "ANJANEYA SWAMY TEMPLE", "MACHAVARAM", "PADAVALAREVU", "GUNADALA CHURCH", "GUNADALA", "GUNADALA VANTHENA", "ESI", "POWER OFFICE", "RING ROAD", "RAMAVARAPADU", "RAMESH HOSPITAL", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR"],    
    "14S": ["WAGON WORKSHOP COLONY", "MADHURA NAGAR"],
    "14E": ["ELAPROLU", "SATYANARAYANAPURAM COLONY"],
    "16M": ["VOMBAY COLONY", "GUNADALA"],
    "16R": ["KALESWARARAO MARKET", "NEW RAJA RAJESWARI PET"],
    "20": ["MADHURANAGAR", "MANGALAGIRI"],
    "23H": ["KALESWARARAO MARKET", "KR MARKET", "BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA",
              "AUTONAGAR GATE", "KANURU","SIDDHARTHA", "PORANKI", "PENAMALURU"],
    "23A": ["FOURMEN BUNGLOW", "RAILWAY STN", "BUNDAR ROAD", "BESANT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA",
              "AUTONAGAR GATE", "KANURU","SIDDHARTHA", "PORANKI", "GANGURU"],
    "23K": ["KALESWARARAO MARKET", "KR MARKET", "BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA",
              "AUTONAGAR GATE", "KANURU","SIDDHARTHA", "PORANKI", "KESARANENI VARI PALEM"],
    "26H": ["HB COLONY", "KR MARKET", "BUS STAND", "BUNDAR ROAD", "BESANT ROAD", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA",
              "AUTONAGAR"],
    "28B": ["PANJA", "RAILWAY STATION", "BUNGLOW", "PWD GROUNDS", "BENZ CIRCLE", "RAMESH HOSPITAL", "VINAYAK THEATRE",
              "NTR HEALTH UNIV", "RAMAVARAPADU RING", "MARUTHI NAGAR", "VIJAYA TALKIES", "RAILWAY STATION", "PANJA"],
    "28E": ["PANJA", "RAILWAY STATION", "VIJAYA TALKIES", "MARUTHI NAGAR", "RAMAVARAPADU RING", "VINAYAK THEATRE",
              "RAMESH HOSPITAL", "BENZ CIRCLE", "PWD GROUNDS", "RAILWAY STN", "PANJA"],
    "29": ["KALESWARARAO MARKET", "AUTONAGAR"],
    "31": ["MILK PROJECT", "KR MARKET", "BUS STAND", "OLD BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM",
             "BENZ CIRCLE", "PATAMATA", "AUTONAGAR"],
    "31A": ["MILK PROJECT", "KR MARKET", "BUS STAND", "OLD BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM",
              "BENZ CIRCLE", "PATAMATA", "AUTONAGAR", "KAMAYYATHOPU", "SIDDHARTHA", "TADIGADAPA"],
    "31H": ["HB COLONY", "KR MARKET", "BUS STAND", "OLD BUS STAND", "BUNDAR ROAD", "BESENT ROAD", "IGMC STADIUM",
              "BENZ CIRCLE", "PATAMATA", "AUTONAGAR"],
    "41V": ["VOMBAY COLONY", "AUTONAGAR"],
    "47H": ["RAILWAY STATION", "BUS STAND", "VARADHI", "MANIPAL HOSPITAL", "MANGALAGIRI", "CHINNA KAKANI"],
    "47N": ["KALESWARARAO MARKET", "BUS STAND", "VARADHI", "MANIPAL HOSPITAL", "MANGALAGIRI", "NRI HOSPITAL"],
    "47V": ["RAILWAY STATION", "BUS STAND", "VARADHI", "MANIPAL HOSPITAL", "MANGALAGIRI"],
    "48K": ["NSB NAGAR", "AUTO NAGAR"],
    "48": ["AUTONAGAR", "BANDAR ROAD","BESANT ROAD","BUNGLAW","LENIN CENTER","RAILWAY STATION","AYODHYA NAGAR","SINGHNAGAR", "NUNNA"],
    "48V": ["AUTONAGAR", "BANDAR ROAD","AYODHYA NAGAR","SINGHNAGAR", "VOMBAY COLONY"],
    "49": ["KALESWARARAO MARKET", "BUS STAND","AYODHYA NAGAR","SINGHNAGAR", "NUNNA"],
    "49M": ["KALESWARARAO MARKET", "MANAGALAPURAM"],
    "49P": ["KALESWARARAO MARKET", "BUS STAND", "KUNDA VARI KANDRIKA"],
    "54": ["RAILWAY STATION", "VIJAYA TALKIES", "MARUTHI NAGAR", "RAMAVARAPADU RING", "VINAYAK THEATRE", "RAMESH HOSPITAL", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR"],
    "55": ["KALESWARARAO MARKET", "KANURU", "PWD GROUNDS", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR TERMINAL", "KAMAYYATHOPU", "KANURU"],
    "55S": ["RAILWAY STATION", "KANURU", "PWD GROUNDS", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR TERMINAL", "KAMAYYATHOPU", "KANURU"],
    "77": ["KALESWARARAO MARKET", "BUS STAND", "ELURU ROAD", "RAMAVARAPADU"],
    "77S": ["RAILWAY STATION", "RAMAVARAPADU", "ELURU ROAD"],
    "79E": ["WHOLESALE MARKET", "BUS STAND", "ELURU ROAD", "PORANKI"],
    "79B": ["WHOLESALE MARKET", "BUS STAND", "BANDAR ROAD", "PORANKI"],
    "112A": ["KALESWARARAO MARKET", "MUSTHABADH"],
    "116": ["KALESWARARAO MARKET", "BUS STAND","IGMC STADIUM","BENZ CIRCLE","RAMAVARAPADU RING", "NIDAMANURU", "GANNAVARAM"],
    "116K": ["KALESWARARAO MARKET", "KR MARKET", "RAILWAY STATION","BUS STAND","IGMC STADIUM","BENZ CIRCLE", "KG PADU"],
    "121": ["RAILWAY STATION", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KAMAYYATHOPU", "SIDDHARTHA", "PORANKI", "MADDURU"],
    "122": ["KALESWARARAO MARKET", "RAILWAY STN", "BUS STAND", "IGMC STADIUM", "BENZ CIRCLE", "PATAMATA", "AUTONAGAR GATE", "KAMAYYATHOPU", "SIDDHARTHA", "PORANKI", "MADDURU"],
    "123": ["SHABADH", "BENZ CIRCLE", "KANKIPADU"],
    "140": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "SIDDHARTHA", "UPPULURU"],
    "141": ["KALESWARARAO MARKET", "RAILWAY STN", "BUS STAND", "BANDAR ROAD", "SIDDHARTHA", "UPPULURU"],
    "144": ["KONDAPALLI", "BUS STAND", "BANDAR ROAD", "BENZ CIRCLE", "AUTONAGAR"],
    "145": ["KONDAPALLI", "BUS STAND", "ELURU ROAD", "NIDAMANURU"],
    "150": ["KONDAPALLI", "BUS STAND", "BANDAR ROAD", "BENZ CIRCLE", "SIDDHARTHA", "KANKIPADU"],
    "152": ["RAILWAY STN", "KAVULURU"],
    "154": ["KALESWARARAO MARKET", "KR MARKET", "BANDAR ROAD", "KANKIPADU"],
    "188": ["KONDAPALLI", "ELURU ROAD", "GANNAVARAM"],
    "201C": ["KALESWARARAO MARKET", "BUS STAND", "PEDDAOUTPALLI"],
    "201T": ["KALESWARARAO MARKET", "BUS STAND", "TELAPROLU"],
    "201O": ["KALESWARARAO MARKET", "ORUGALLA"],
    "203C": ["KALESWARARAO MARKET", "PODDUTURU"],
    "203K": ["KALESWARARAO MARKET", "KONDURU"],
    "203T": ["KALESWARARAO MARKET", "TTENNERU"],
    "208": ["KALESWARARAO MARKET", "AGIRAPALLI"],
    "209": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "VALLURU PALEM"],
    "209A": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "ROYYURU"],
    "209T": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "THOTLAVALLURU"],
    "211": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "KOLLVENU"],
    "212": ["KALESWARARAO MARKET", "CHIKKAVARAM"],
    "212P": ["KALESWARARAO MARKET", "GANNAVARAM (VIA P PATNAM)"],
    "212S": ["KALESWARARAO MARKET", "GANNAVARAM (VIA S.GUDEM)"],
    "212M": ["KALESWARARAO MARKET", "MUDIRAJU PALEM"],
    "215S": ["RAILWAY STATION", "NUTAKKI"],
    "218M": ["BUS STAND", "MAILAVARAM"],
    "220": ["KALESWARARAO MARKET", "TENNARU"],
    "222": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "VYUYURU"],
    "223M": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "MANIKONDA"],
    "226": ["BUS STAND", "CHIRAVURU"],
    "239": ["KALESWARARAO MARKET", "KANASANEPALLI"],
    "241": ["KANKIPADU", "GANNAVARAM"],
    "248": ["AGIRAPALLI", "BANDAR ROAD", "KANKIPADU"],
    "250V": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "PORANKI", "VEMANDA"],
    "252": ["KALESWARARAO MARKET", "BUS STAND", "RAMAVARAPADU RING", "GANNAVARAM", "HANUMAN JUNCTION"],
    "252B": ["KALESWARARAO MARKET", "BUS STAND", "BANDAR ROAD", "BENZ CIRCLE", "RAMAVARAPADU RING", "GANNAVARAM", "HANUMAN JUNCTION"],
    "257": ["RAILWAY STATION", "PWD GROUND", "BANDAR ROAD", "PEDDA OGIRALA"],
    "266": ["VIJAYAWADA", "KANCHIKA CHARLA"],
    "305M": ["VIJAYAWADA", "MOGHULURU", "VEERULAPADU"],
    "308": ["VIJAYAWADA", "NUNNA", "CHINOUTPALLI", "NUZIVIDU"],
    "309": ["IBRAHIMPATNAM", "VIJAYAWADA", "JAMALAPURAM"],
    "309R": ["IBRAHIMPATNAM", "KANCHIKACHARLA", "JAMALAPURAM", "MILAVARAM", "VIJAYAWADA"],
    "333": ["KALESWARARAO MARKET", "PAMARRU"],
    "350": ["VIJAYAWADA", "MILAVARAM"],
    "99": ["RAILWAY STATION", "SATYANARANA PURAM", "BRTS ROAD", "RAMAVARAPADU RING", "BENZ CIRCLE", "PORANKI", "KANKIPADU"]
}

# Dictionary of stop coordinates (Lat, Lon) for straight-line distance calculation
stop_coordinates = {
    "Railway Station": (16.5165, 80.6277),
    "Bus Stand": (16.5161, 80.6277),
    "Benz Circle": (16.5159, 80.6558),
    "Poranki": (16.4716, 80.7061),
    "Kaleswararao Market": (16.5173, 80.6273),
    "Ramavarapadu Ring": (16.5444, 80.6698),
    "Gunadala": (16.5262, 80.6483),
    "Autonagar": (16.4862, 80.6725),
    "Kanuru": (16.4891, 80.6865),
    "Patamata": (16.5053, 80.6599),
    # Additional stops with mock data for calculation fallback
    "Ibrahimpatnam": (16.431, 80.641),
    "Swathi": (16.435, 80.645),
    "Kummari Palem": (16.438, 80.638),
    "Kr Market": (16.509, 80.616),
    "Bundar Road": (16.513, 80.635),
    "IGMC Stadium": (16.515, 80.630),
    "Benz Circle":(16.5159,80.6558),
    "Patamata":(16.5053,80.6599),
    "Autonagar Gate": (16.534, 80.623),
    "Siddhartha": (16.4853, 80.6916),
    "Kankipadu": (16.822, 80.734),
}

# Hardcoded road distances (more accurate than straight-line)
road_distances = {
    ("Railway Station", "Benz Circle"): 7.1,
    ("Kanuru", "Patamata"): 4.5,
    ("Benz Circle", "Patamata"): 1.8,
    ("Railway Station", "Bus Stand"): 0.5,
    ("Benz Circle","Siddhartha"):6.1,
    ("Benz Circle","Patamata"):2.3,
    ("Patamata","Siddhartha"):4.2,
    ("Kaleswararao Market", "Bus Stand"): 1.0,
    ("Kanuru", "Poranki"): 2.5,
    ("Bus Stand", "Ramavarapadu Ring"): 8.5,
    ("Kaleswararao Market", "Poranki"): 10.2
}

# Added: API key for OpenWeatherMap (Dummy key)
appid = 'e7b16ebe3fbe47e6b97f6821cff80e5d'

# --- HELPER FUNCTIONS ---
# Normalize stop names
for bus, stops in bus_routes.items():
    bus_routes[bus] = [stop.title() for stop in stops]
all_stops = set(stop.title() for stops in bus_routes.values() for stop in stops)

def text_to_speech(text, lang):
    """Converts text to speech using gTTS and returns audio bytes."""
    if not text or not text.strip():
        return None
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        return audio_fp.read()
    except Exception as e:
        print(f"Error in gTTS for lang={lang}: {e}")
        return None

def find_buses_between(src, dst):
    results = []
    for bus, stops in bus_routes.items():
        if src in stops and dst in stops and stops.index(src) < stops.index(dst):
            results.append(bus)
    return results

def route_of_bus(bus_number):
    bus_number = bus_number.upper()
    if bus_number in bus_routes:
        return " → ".join(bus_routes[bus_number])
    return None

def get_weather(city_name, api_key):
    city_name_lower = city_name.lower()

    # --- MOCK DATA for testing the travel suggestion feature reliably ---
    if "mumbai" in city_name_lower or "bombay" in city_name_lower:
        return {
            'main': {'temp': 28.5, 'feels_like': 32.0},
            'weather': [{'description': 'light rain'}],
            'name': city_name
        }
    elif "delhi" in city_name_lower:
        return {
            'main': {'temp': 35.1, 'feels_like': 34.0},
            'weather': [{'description': 'clear sky'}],
            'name': city_name
        }
    elif "vijayawada" in city_name_lower:
        return {
            'main': {'temp': 30.0, 'feels_like': 31.5},
            'weather': [{'description': 'scattered clouds'}],
            'name': city_name
        }
    
    # --- Fallback to external API for other cities (Requires valid API key) ---
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"
    }
    try:
        # Use a short timeout for the external request
        response = requests.get(base_url, params=params, timeout=5) 
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass # If API call fails (network or key issue), we return None below
    
    return None

def find_alternative_route(src, dst):
    for bus1, stops1 in bus_routes.items():
        if src in stops1:
            for transfer in stops1:
                if transfer == src: continue
                for bus2, stops2 in bus_routes.items():
                    if bus2 != bus1 and transfer in stops2 and dst in stops2:
                        eng_response = f"No direct bus found. Alternative: Take bus {bus1} from {src} to {transfer}, then switch to bus {bus2} to get to {dst}."
                        tel_response = f"నేరుగా బస్సు లేదు. ప్రత్యామ్నాయం: {src} నుండి {transfer} వరకు బస్సు {bus1} తీసుకోండి, ఆపై {dst}కి చేరుకోవడానికి బస్సు {bus2}కి మారండి."
                        return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
    eng_response = "No direct bus or alternative route found."
    tel_response = "నేరుగా బస్సు లేదా ప్రత్యామ్నాయ మార్గం ఏదీ కనుగొనబడలేదు."
    return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"

def buses_at_stop(stop):
    return [bus for bus, stops in bus_routes.items() if stop in stops]

# Haversine formula for calculating straight-line distance using coordinates
def calculate_distance(coords1, coords2):
    R = 6371  # Radius of Earth in kilometers
    lat1, lon1 = math.radians(coords1[0]), math.radians(coords1[1])
    lat2, lon2 = math.radians(coords2[0]), math.radians(coords2[1])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2)*2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)*2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def call_gemini_api(user_query, known_info):
    # This is a mock function, as actual API calls are restricted in this environment.
    eng = "I'm still learning about new routes and places. You can ask me about specific routes like 'bus from Benz Circle to Poranki' or bus numbers like 'route of 7ST'."
    tel = "నేను ఇంకా కొత్త మార్గాలు మరియు స్థలాల గురించి నేర్చుకుంటున్నాను. మీరు 'బెంజ్ సర్కిల్ నుండి పోరంకికి బస్సు' వంటి నిర్దిష్ట మార్గాల గురించి లేదా '7ST మార్గం' వంటి బస్సు నంబర్ల గురించి నన్ను అడగవచ్చు."
    return f"English: {eng}\n\n*తెలుగు:* {tel}"


# --- CHATBOT BRAIN ---
def get_chatbot_response(query):
    query_lower = query.lower().strip()

    # Handle weather queries and add travel suggestion logic
    match = re.search(r'weather in\s+([a-zA-Z\s]+)', query_lower)
    if match:
        city = match.group(1).strip().title()
        weather_data = get_weather(city, appid)
        
        if weather_data and weather_data.get('main'):
            temp = weather_data['main']['temp']
            desc = weather_data['weather'][0]['description']
            desc_title = desc.title()
            
            # --- Travel Suggestion Logic ---
            travel_suggestion_eng, travel_suggestion_tel = "", ""
            desc_lower = desc.lower()

            if 'rain' in desc_lower or 'thunderstorm' in desc_lower or 'snow' in desc_lower or 'mist' in desc_lower:
                travel_suggestion_eng = "\n\n*Travel Tip (English):* It looks like the weather is rough. We strongly recommend taking a Bus for a safe and comfortable journey!"
                travel_suggestion_tel = "\n\n*ప్రయాణ సూచన (తెలుగు):* వాతావరణం అనుకూలంగా లేదు. సురక్షితమైన మరియు సౌకర్యవంతమైన ప్రయాణం కోసం *బస్సు*లో వెళ్లాలని మేము గట్టిగా సూచిస్తున్నాము!"
            elif temp > 35:
                travel_suggestion_eng = "\n\n*Travel Tip (English):* It's quite hot! For a more comfortable trip, consider traveling by an AC Bus or AC private vehicle."
                travel_suggestion_tel = "\n\n*ప్రయాణ సూచన (తెలుగు):* వాతావరణం చాలా వేడిగా ఉంది! మరింత సౌకర్యవంతమైన ప్రయాణం కోసం, AC బస్సు లేదా *AC ప్రైవేట్ వాహనం*లో ప్రయాణించడానికి ఆలోచించండి."
            elif 'clear sky' in desc_lower or 'few clouds' in desc_lower or temp < 20:
                travel_suggestion_eng = "\n\n*Travel Tip (English):* The weather seems pleasant! You might enjoy driving your personal vehicle."
                travel_suggestion_tel = "\n\n*ప్రయాణ సూచన (తెలుగు):* వాతావరణం ఆహ్లాదకరంగా ఉంది! మీరు మీ వ్యక్తిగత వాహనం నడపడం ఆనందించవచ్చు."
            else:
                travel_suggestion_eng = "\n\n*Travel Tip (English):* The weather is moderate. Both Bus and private vehicle are good options."
                travel_suggestion_tel = "\n\n*ప్రయాణ సూచన (తెలుగు):* వాతావరణం మధ్యస్తంగా ఉంది. బస్సు మరియు ప్రైవేట్ వాహనం రెండూ మంచి ఎంపికలు."
            # --- End Travel Suggestion Logic ---
            
            eng_response = f"The current weather in {city} is {temp}°C with {desc_title}."
            tel_response = f"ప్రస్తుతం {city}లో వాతావరణం **{temp}°C ఉంది మరియు *{desc_title}*గా ఉంది."
            
            return f"English: {eng_response} {travel_suggestion_eng}\n\n*తెలుగు:* {tel_response} {travel_suggestion_tel}"
        else:
            eng_response = f"Sorry, I couldn't retrieve the weather for '{city}'. Please check the city name."
            tel_response = f"క్షమించండి, '{city}' కోసం వాతావరణ సమాచారం పొందలేకపోయాను. దయచేసి నగరం పేరును తనిఖీ చేయండి."
            return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"

    # Logic to handle distance calculation using both hardcoded road_distances AND lat/long coordinates
    if any(word in query_lower for word in ["distance", "km", "how far", "kilometers", "దూరం"]):
        src, dst = None, None
        
        match = re.search(r'from\s+([a-zA-Z\s]+)\s+to\s+([a-zA-Z\s]+)', query_lower)
        if match:
            src = match.group(1).strip().title()
            dst = match.group(2).strip().title()
        elif st.session_state.get('last_src') and st.session_state.get('last_dst'):
            src = st.session_state.last_src
            dst = st.session_state.last_dst
        
        if src and dst:
            distance = None
            # 1. Check for hardcoded road distance (more accurate)
            if (src, dst) in road_distances:
                distance = road_distances[(src, dst)]
                eng_response = f"The approximate road distance between {src} and {dst} is {distance:.2f} km."
                tel_response = f"{src} మరియు {dst} మధ్య సుమారు రోడ్డు దూరం {distance:.2f} కి.మీ."
            elif (dst, src) in road_distances:
                distance = road_distances[(dst, src)]
                eng_response = f"The approximate road distance between {src} and {dst} is {distance:.2f} km."
                tel_response = f"{src} మరియు {dst} మధ్య సుమారు రోడ్డు దూరం {distance:.2f} కి.మీ."
            
            # 2. Fallback to straight-line distance using coordinates (less accurate, but uses lat/long)
            elif src in stop_coordinates and dst in stop_coordinates:
                src_coords = stop_coordinates[src]
                dst_coords = stop_coordinates[dst]
                distance = calculate_distance(src_coords, dst_coords)
                eng_response = f"The approximate straight-line distance between {src} and {dst} is {distance:.2f} km. (This is calculated using coordinates and does not account for roads and is not the actual driving distance)."
                tel_response = f"{src} మరియు {dst} మధ్య సుమారు నేరుగా దూరం {distance:.2f} కి.మీ. (ఇది కోఆర్డినేట్‌లను ఉపయోగించి లెక్కించబడింది మరియు రోడ్లను పరిగణనలోకి తీసుకోదు, ఇది అసలు డ్రైవింగ్ దూరం కాదు)."
            
            if distance:
                return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
            else:
                eng_response = f"Sorry, I don't have location data for '{src}' or '{dst}'. Please choose from major stops like Benz Circle, Railway Station, or Poranki."
                tel_response = f"క్షమించండి, '{src}' లేదా '{dst}' కోసం నా వద్ద స్థాన డేటా లేదు. దయచేసి బెంజ్ సర్కిల్, రైల్వే స్టేషన్ లేదా పోరంకి వంటి ప్రధాన స్టాప్‌ల నుండి ఎంచుకోండి."
                return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
        else:
            eng_response = "To calculate the distance, please tell me the source and destination. For example, 'What's the distance from Railway Station to Benz Circle?'"
            tel_response = "దూరాన్ని లెక్కించడానికి, దయచేసి మూలం మరియు గమ్యస్థానం చెప్పండి. ఉదాహరణకు, 'రైల్వే స్టేషన్ నుండి బెంజ్ సర్కిల్‌కు దూరం ఎంత?'"
            return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"


    if any(word in query_lower for word in ["bye", "goodbye", "see you", "cya", "వీడ్కోలు"]):
        eng_response = "Goodbye! Have a great day."
        tel_response = "వీడ్కోలు! మీకు మంచి రోజు కావాలి."
        return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"

    if query_lower.upper() in bus_routes:
        route = route_of_bus(query_lower)
        eng_response = f"Route for Bus {query_lower.upper()}:\n\n{route}"
        tel_response = f"బస్సు {query_lower.upper()} మార్గం:\n\n{route}"
        return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"

    if any(word in query_lower for word in ["hi", "hello", "hey", "namaste", "నమస్కారం", "namaskaram"]):
        return "Hello! How can I help you today? \n\nనమస్కారం! ఈరోజు మీకు బస్సుల గురించి ఎలా సహాయం చేయగలను?"

    if any(word in query_lower for word in ["pass", "student", "application", "ప్యాస్", "విద్యార్థి"]):
        return """
        #### How to get a Student Bus Pass (విద్యార్థి బస్ పాస్ పొందడం ఎలా)

        English Steps:
        1.  Application Form: Fill out the official Bus Pass Application Form.
        2.  College Verification: Get the form signed and stamped by your College Administration.
        3.  Bus Stand Visit: Go to the City Bus Stand. First, get your documents checked at Platform 1.
        4.  Final Issuance: After verification, go to the 1st Floor of the Main Bus Stand building to have your pass issued.
        
        Remember to carry your College ID!

        ---
        
        తెలుగు దశలు (Telugu Steps):
        1.  అప్లికేషన్ ఫారం (Application Form): అధికారిక బస్ పాస్ అప్లికేషన్ ఫారంను పూరించండి.
        2.  కళాశాల ధృవీకరణ (College Verification): మీ కళాశాల పరిపాలనతో ఫారంపై సంతకం చేసి, స్టాంప్ వేయించుకోండి.
        3.  బస్ స్టాండ్‌ను సందర్శించండి (Visit Bus Stand): సిటీ బస్ స్టాండ్‌కు వెళ్లండి. ముందుగా, ప్లాట్‌ఫారమ్ 1 వద్ద మీ పత్రాలను తనిఖీ చేయించుకోండి.
        4.  ఫైనల్ ఇష్యూ (Final Issuance): ధృవీకరణ తర్వాత, మీ పాస్‌ను జారీ చేయడానికి మెయిన్ బస్ స్టాండ్ భవనం యొక్క 1వ అంతస్తుకు వెళ్లండి.
        
        మీ కాలేజీ IDని తీసుకెళ్లడం మర్చిపోవద్దు!
        """

    match_from_to = re.search(r'bus(es)?\s+from\s+([a-zA-Z\s]+)\s+to\s+([a-zA-Z\s]+)', query_lower)
    if match_from_to:
        src = match_from_to.group(2).strip().title()
        dst = match_from_to.group(3).strip().title()
        
        if src in all_stops and dst in all_stops:
            st.session_state.last_src = src
            st.session_state.last_dst = dst
            
            buses = find_buses_between(src, dst)
            if buses:
                eng_response = f"The following buses go directly from {src} to {dst}: {', '.join(buses)}."
                tel_response = f"{src} నుండి {dst} వరకు నేరుగా వెళ్లే బస్సులు: {', '.join(buses)}."
                return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
            else:
                return find_alternative_route(src, dst)
        else:
            eng_response = f"Sorry, I couldn't recognize the bus stops '{src}' or '{dst}'. Please check the names and try again."
            tel_response = f"క్షమించండి, నేను '{src}' లేదా '{dst}' అనే బస్ స్టాప్‌లను గుర్తించలేకపోయాను. దయచేసి పేర్లను తనిఖీ చేసి, మళ్ళీ ప్రయత్నించండి."
            return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
            
    bus_number_candidates = re.findall(r'\b([a-zA-Z0-9]+)\b', query_lower)
    if any(word in query_lower for word in ["route", "about", "stops", "మార్గం"]):
        for candidate in bus_number_candidates:
            if candidate.upper() in bus_routes:
                route = route_of_bus(candidate)
                eng_response = f"Route for Bus {candidate.upper()}:\n\n{route}"
                tel_response = f"బస్సు {candidate.upper()} మార్గం:\n\n{route}"
                return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"

    destination_keywords = ["go to", "take me to", "for", "going to", "వెళ్లాలి", "చేరాలి"]
    found_dst = None
    
    for keyword in destination_keywords:
        if keyword in query_lower:
            parts = query_lower.split(keyword)
            if len(parts) > 1:
                potential_dst = parts[1].strip()
                for stop in sorted(list(all_stops), key=len, reverse=True):
                    if stop.lower().startswith(potential_dst):
                        found_dst = stop
                        break
            if found_dst:
                break

    if not found_dst:
        sorted_stops = sorted(list(all_stops), key=len, reverse=True)
        for stop in sorted_stops:
            if re.search(r'\b' + re.escape(stop.lower()) + r'\b', query_lower):
                found_dst = stop
                break

    if found_dst:
        buses = buses_at_stop(found_dst)
        if buses:
            eng_response = f"Buses that go to {found_dst} are: {', '.join(buses)}."
            tel_response = f"{found_dst}కు వెళ్లే బస్సులు: {', '.join(buses)}."
            return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
        else:
            eng_response = f"Sorry, I couldn't find any buses for the stop '{found_dst}'."
            tel_response = f"క్షమించండి, '{found_dst}' స్టాప్ కోసం నేను బస్సులను కనుగొనలేకపోయాను."
            return f"English: {eng_response}\n\n*తెలుగు:* {tel_response}"
            
    known_info = {
        'bus_routes': list(bus_routes.keys()),
        'all_stops': list(all_stops),
        'road_distances': [f"{k[0]} to {k[1]}" for k in road_distances.keys()]
    }
    return call_gemini_api(query, known_info)


# --- SIDEBAR UI ---
st.sidebar.title("🚌 BusBuddy")
st.sidebar.markdown("Your Smart Travel Assistant - Find Buses Anytime, Anywhere")
st.sidebar.write("---")

st.sidebar.markdown("""
<p style="color:white; font-size: 1.1em;">Examples / ఉదాహరణలు</p>

<p class="sidebar-text">Bus Query / బస్సు గురించి</p>
<p class="sidebar-caption">e.g., 'route of 23H'</p>

<p class="sidebar-text">Source/Destination Route Search / గమ్యస్థానం కోసం వెతకండి</p>
<p class="sidebar-caption">e.g., 'bus from Benz Circle to Poranki'</p>

<p class="sidebar-text">Distance Calculation / దూరం లెక్కించడం</p>
<p class="sidebar-caption">e.g., 'distance from Railway Station to Benz Circle'</p>

<p class="sidebar-text">Student Bus Pass Process / విద్యార్థి బస్ పాస్ ప్రక్రియ</p>
<p class="sidebar-caption">e.g., 'how to get a student pass'</p>

<p class="sidebar-text">Check Weather / వాతావరణం తనిఖీ చేయండి</p>
<p class="sidebar-caption">e.g., 'weather in Mumbai' (to see the rain tip) or 'weather in Delhi' (to see the heat tip)</p>
""", unsafe_allow_html=True)

st.sidebar.write("---")


# --- MAIN CHAT UI ---
st.title("BusBuddy Chatbot")
st.markdown("Your Smart Travel Assistant for Vijayawada buses. (Responses are now in English and Telugu!)")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How can I help you with the bus routes today? \n\nనమస్కారం! ఈరోజు మీకు బస్సుల గురించి ఎలా సహాయం చేయగలను?"}]
    st.session_state.last_src = None
    st.session_state.last_dst = None

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask about bus routes... / బస్సు మార్గాల గురించి అడగండి..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = get_chatbot_response(prompt)
        st.markdown(response)


        # --- NEW: Text-to-Speech Generation ---
        # Parse the response to find English and Telugu parts
        eng_text, tel_text = None, None
        if "English:" in response and "తెలుగు:" in response:
            try:
                parts = response.split("తెలుగు:")
                eng_text = parts[0].replace("English:", "").strip()
                tel_text = parts[1].strip()
            except Exception:
                eng_text = response # Fallback to full response if parsing fails
        else:
            eng_text = response # If not bilingual, assume it's English

        # Generate audio for each part
        eng_audio = text_to_speech(eng_text, lang='en')
        tel_audio = text_to_speech(tel_text, lang='te')

        # Display audio players in columns
        if eng_audio or tel_audio:
            col1, col2 = st.columns(2)
            with col1:
                if eng_audio:
                    st.write("Listen in English:")
                    st.audio(eng_audio, format='audio/mp3')
            with col2:
                if tel_audio:
                    st.write("తెలుగులో వినండి (Listen in Telugu):")
                    st.audio(tel_audio, format='audio/mp3')
        
        st.session_state.messages.append({"role": "assistant", "content": response})
