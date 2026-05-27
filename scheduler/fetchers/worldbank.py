import requests
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

WB_BASE = "https://api.worldbank.org/v2/country"

WB_INDICATORS = {
    "gdp_current_usd": "NY.GDP.MKTP.CD",
    "gdp_growth": "NY.GDP.MKTP.KD.ZG",
    "inflation_cpi": "FP.CPI.TOTL.ZG",
    "unemployment": "SL.UEM.TOTL.ZS",
    "current_account": "BN.CAB.XOKA.CD"
}

COUNTRIES = ["US", "GB", "DE", "JP", "CN", "IN", "BR", "FR"]

def fetch_indicator(country, indicator_code, start_year=1960):
    url = f"{WB_BASE}/{country}/indicator/{indicator_code}"
    params = {
        "format": "json",
        "date": f"{start_year}:2026",
        "per_page": 100
    }
    response = requests.get(url, params=params)
    data = response.json()
    if len(data) < 2:
        return []
    results = []
    for entry in data[1]:
        if entry["value"] is not None:
            results.append({
                "country": country,
                "year": entry["date"],
                "value": entry["value"]
            })
    return results

def fetch_all_world_bank():
    all_data = {}
    for ind_name, ind_code in WB_INDICATORS.items():
        all_data[ind_name] = []
        for country in COUNTRIES:
            print(f"Fetching World Bank: {ind_name} for {country}")
            try:
                results = fetch_indicator(country, ind_code)
                all_data[ind_name].extend(results)
            except Exception as e:
                print(f"Failed {ind_name} {country}: {e}")
    return all_data
