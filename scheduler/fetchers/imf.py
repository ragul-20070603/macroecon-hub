import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

IMF_BASE = "https://www.imf.org/external/datamapper/api/v1"

IMF_INDICATORS = {
    "gdp_growth": "NGDP_RPCH",
    "inflation": "PCPIPCH",
    "unemployment": "LUR",
    "current_account": "BCA_NGDPD"
}

IMF_COUNTRIES = ["USA", "GBR", "DEU", "JPN", "CHN", "IND", "BRA", "FRA", "ITA", "CAN"]

def fetch_imf_indicator(indicator_code):
    url = f"{IMF_BASE}/{indicator_code}"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        results = []
        values = data.get("values", {}).get(indicator_code, {})
        for country_code, year_data in values.items():
            if country_code in IMF_COUNTRIES:
                for year, value in year_data.items():
                    if value is not None:
                        results.append({
                            "country": country_code,
                            "year": year,
                            "value": value,
                            "indicator": indicator_code
                        })
        return results
    except Exception as e:
        print(f"IMF fetch failed for {indicator_code}: {e}")
        return []

def fetch_all_imf():
    all_data = {}
    for name, code in IMF_INDICATORS.items():
        print(f"Fetching IMF: {name}")
        all_data[name] = fetch_imf_indicator(code)
        print(f"Got {len(all_data[name])} records for {name}")
    return all_data
