"""Test BEA API fetcher as a standalone function for refresh_v2.py"""
import requests
import json
from datetime import datetime, timezone

def fetch_bea():
    """Fetch BEA CAINC1 for Volusia County via API."""
    url = "https://apps.bea.gov/api/data"
    params = {
        "UserID": "49ED5E15-6093-4A4E-ABBC-83E7BC38B324",
        "method": "GetData",
        "datasetname": "Regional",
        "TableName": "CAINC1",
        "GeoFips": "12127",
        "LineCode": "3",
        "Year": "ALL",
        "ResultFormat": "JSON",
    }
    
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    
    error = data.get("BEAAPI", {}).get("Results", {}).get("Error")
    if error:
        return False, f"API Error: {error.get('APIErrorDescription', '')}"
    
    bea_data = data.get("BEAAPI", {}).get("Results", {}).get("Data", [])
    if not bea_data:
        return False, "No data returned"
    
    # Get latest per capita income (line_code 3)
    latest = bea_data[-1]
    per_capita = float(latest["DataValue"])
    year = int(latest["TimePeriod"])
    
    # Also get total income (line 1) and population (line 2) for same year
    total_income = None
    population = None
    for item in bea_data:
        if int(item["TimePeriod"]) == year:
            code = item.get("Code", "").split("-")[-1]
            if code == "1":
                total_income = float(item["DataValue"])
            elif code == "2":
                population = int(float(item["DataValue"]))
    
    result = {
        "per_capita_income": per_capita,
        "year": year,
        "total_income": total_income,
        "population": population,
    }
    return True, result

if __name__ == "__main__":
    ok, result = fetch_bea()
    if ok:
        print(f"BEA OK: {result}")
    else:
        print(f"BEA FAIL: {result}")
