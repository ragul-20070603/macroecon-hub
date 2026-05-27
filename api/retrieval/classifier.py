import re

TIMESERIES_PATTERNS = [
    r'\b(rate|rates|percentage|percent|%)\b.*\b(in|during|since|from|between|year|decade)\b',
    r'\b(what was|show me|give me|tell me).*(inflation|gdp|growth|unemployment|interest).*(rate|trend|data|history)',
    r'\b(trend|trends|historical|history|over time|since \d{4}|from \d{4})\b',
    r'\b\d{4}\b.*\b(to|till|until|through|and)\b.*\b\d{4}\b',
    r'\b(compare|comparison|versus|vs)\b.*\b(country|countries|nation|us|uk|china|india)\b',
    r'\b(chart|graph|plot|visualize|show)\b'
]

NEWS_PATTERNS = [
    r'\b(today|this week|this month|latest|recent|current|now|breaking|just)\b',
    r'\b(announced|said|stated|reported|decided|cut|raised|hiked)\b',
    r'\b(fed|federal reserve|ecb|rbi|boe)\b.*\b(meeting|decision|rate cut|rate hike)\b',
    r'\b(news|update|happening|development)\b'
]

HISTORICAL_PATTERNS = [
    r'\b(what happened|crisis|crash|recession of|depression|stagflation)\b',
    r'\b(19\d{2}|200[0-9]|201[0-9])\b',
    r'\b(great depression|financial crisis|dot.?com|subprime)\b'
]

def classify_query(query):
    query_lower = query.lower()

    for pattern in TIMESERIES_PATTERNS:
        if re.search(pattern, query_lower):
            return "timeseries"

    for pattern in NEWS_PATTERNS:
        if re.search(pattern, query_lower):
            return "news"

    for pattern in HISTORICAL_PATTERNS:
        if re.search(pattern, query_lower):
            return "historical"

    return "conceptual"

def extract_years(query):
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', query)
    return [int(y) for y in years]

def extract_indicator(query):
    query_lower = query.lower()
    if any(w in query_lower for w in ["inflation", "cpi", "price", "cost"]):
        return "inflation"
    if any(w in query_lower for w in ["gdp", "gross domestic", "economic growth", "economy size"]):
        return "gdp"
    if any(w in query_lower for w in ["interest rate", "federal funds", "fed rate", "borrowing rate"]):
        return "interest_rate"
    if any(w in query_lower for w in ["unemployment", "jobs", "employment", "jobless"]):
        return "unemployment"
    return "inflation"

def extract_country(query):
    query_lower = query.lower()
    country_map = {
        "united states": "US", "us": "US", "usa": "US", "america": "US",
        "united kingdom": "GB", "uk": "GB", "britain": "GB",
        "germany": "DE", "japan": "JP", "china": "CN",
        "india": "IN", "brazil": "BR", "france": "FR"
    }
    for name, code in country_map.items():
        if name in query_lower:
            return code
    return "US"
