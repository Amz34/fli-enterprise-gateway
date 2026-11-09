import subprocess
import json
import re

def headless_extract_fallback(origin: str, destination: str, departure_date: str, return_date: str = None, currency: str = "SAR") -> dict:
    if return_date:
        url = f"https://www.google.com/travel/flights?q=flights%20from%20{origin}%20to%20{destination}%20departing%20{departure_date}%20returning%20{return_date}&curr={currency}"
    else:
        url = f"https://www.google.com/travel/flights?q=flights%20from%20{origin}%20to%20{destination}%20departing%20{departure_date}&curr={currency}"

    cmd = [
        "/usr/bin/google-chrome",
        "--headless=new",
        "--dump-dom",
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        url
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=25)
        dom = proc.stdout
    except Exception as e:
        dom = ""

    # Parse potential price patterns from the rendered DOM
    prices = re.findall(r'(?:SAR|USD|\$)\s*([\d,]+)', dom)
    detected_prices = [p.replace(',', '') for p in prices[:5]] if prices else []

    return {
        "source": "headless_chromium_fallback",
        "origin": origin,
        "destination": destination,
        "departure_date": departure_date,
        "return_date": return_date,
        "currency": currency,
        "detected_price_samples": detected_prices,
        "deep_link": url,
        "dom_bytes": len(dom)
    }
