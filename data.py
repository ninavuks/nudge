import requests
from datetime import datetime, timedelta

CITY_COORDINATES = {
    "beograd": {"latitude": 44.8176, "longitude": 20.4633},
    "novi sad": {"latitude": 45.2671, "longitude": 19.8335},
    "nis": {"latitude": 43.3209, "longitude": 21.8958},
    "london": {"latitude": 51.5074, "longitude": -0.1278},
    "berlin": {"latitude": 52.5200, "longitude": 13.4050},
}

def get_weather_forecast(city: str = "beograd", days: int = 14) -> dict:
    """Vuče vremensku prognozu za grad."""
    city_lower = city.lower()
    
    if city_lower in CITY_COORDINATES:
        coords = CITY_COORDINATES[city_lower]
    else:
        coords = CITY_COORDINATES["beograd"]
        city = "Beograd"

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weathercode"],
        "timezone": "Europe/Belgrade",
        "forecast_days": days
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        return process_weather_data(raw_data, city)
    except requests.exceptions.Timeout:
        return {"error": "Vreme čekanja na API isteklo. Pokušaj ponovo."}
    except requests.exceptions.ConnectionError:
        return {"error": "Nema internet konekcije."}
    except requests.exceptions.RequestException as e:
        return {"error": f"API greška: {str(e)}"}


def process_weather_data(raw_data: dict, city: str) -> dict:
    """Obrađuje sirove podatke sa API-ja."""
    daily = raw_data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precipitation = daily.get("precipitation_sum", [])
    weathercodes = daily.get("weathercode", [])

    forecast_days = []
    for i in range(len(dates)):
        date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
        day_name = get_day_name(date_obj)
        condition = interpret_weathercode(weathercodes[i] if i < len(weathercodes) else 0)
        rain = precipitation[i] if i < len(precipitation) else 0
        
        forecast_days.append({
            "date": dates[i],
            "day_name": day_name,
            "max_temp": max_temps[i] if i < len(max_temps) else None,
            "min_temp": min_temps[i] if i < len(min_temps) else None,
            "precipitation_mm": rain,
            "condition": condition,
            "good_for_work": rain < 5 and (max_temps[i] if i < len(max_temps) else 20) > 5
        })

    return {
        "city": city,
        "forecast": forecast_days,
        "summary": generate_weather_summary(forecast_days)
    }


def get_day_name(date_obj: datetime) -> str:
    """Vraća naziv dana na srpskom."""
    days = ["Ponedeljak", "Utorak", "Sreda", "Četvrtak", "Petak", "Subota", "Nedelja"]
    return days[date_obj.weekday()]


def interpret_weathercode(code: int) -> str:
    """Pretvara WMO weather code u opis."""
    if code == 0:
        return "Vedro"
    elif code in [1, 2, 3]:
        return "Delimično oblačno"
    elif code in [45, 48]:
        return "Magla"
    elif code in [51, 53, 55]:
        return "Rosulja"
    elif code in [61, 63, 65]:
        return "Kiša"
    elif code in [71, 73, 75]:
        return "Sneg"
    elif code in [80, 81, 82]:
        return "Pljuskovi"
    elif code in [95, 96, 99]:
        return "Grmljavina"
    else:
        return "Promenljivo"


def generate_weather_summary(forecast_days: list) -> str:
    """Generiše kratak tekstualni rezime prognoze."""
    if not forecast_days:
        return "Nema podataka o vremenu."
    
    rainy_days = [d["day_name"] for d in forecast_days if d["precipitation_mm"] > 5]
    good_days = [d["day_name"] for d in forecast_days if d["good_for_work"]]

    summary = f"Prognoza za {len(forecast_days)} dana: "
    
    if rainy_days:
        summary += f"Kišni dani: {', '.join(rainy_days)}. "
    else:
        summary += "Nema kišnih dana. "
    
    if good_days:
        summary += f"Dobri dani za produktivnost: {', '.join(good_days[:3])}."
    
    return summary