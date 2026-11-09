"""
Corporate Group Travel Sync Module
"""
import json
import sys

def build_group_itinerary(destination: str, departure_date: str, return_date: str, origins: list, currency: str = "SAR"):
    results = {
        "event_hub": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "currency": currency,
        "routes": []
    }
    for org in origins:
        results["routes"].append({
            "origin": org.strip(),
            "destination": destination,
            "deep_link": f"https://www.google.com/travel/flights?q=flights%20from%20{org.strip()}%20to%20{destination}%20departing%20{departure_date}%20returning%20{return_date}&curr={currency}"
        })
    return results

if __name__ == "__main__":
    dest = sys.argv[1] if len(sys.argv) > 1 else "DAC"
    dep = sys.argv[2] if len(sys.argv) > 2 else "2027-01-11"
    ret = sys.argv[3] if len(sys.argv) > 3 else "2027-01-25"
    origs = sys.argv[4].split(",") if len(sys.argv) > 4 else ["JED", "RUH", "DMM"]
    curr = "SAR"
    print(json.dumps(build_group_itinerary(dest, dep, ret, origs, curr), indent=2))
