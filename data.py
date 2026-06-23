import requests
from datetime import datetime, timedelta

# Primer lokacija pčelinjaka (u stvarnoj aplikaciji ovo bi dolazilo iz
# Kosnica.latitude / Kosnica.longitude iz baze podataka)
APIARY_LOCATIONS = {
    "avala": {"latitude": 44.6892, "longitude": 20.5142, "naziv": "Pčelinjak Avala"},
    "fruska gora": {"latitude": 45.1548, "longitude": 19.8556, "naziv": "Pčelinjak Fruška gora"},
    "zlatibor": {"latitude": 43.7286, "longitude": 19.7062, "naziv": "Pčelinjak Zlatibor"},
    "vrsac": {"latitude": 45.1206, "longitude": 21.3034, "naziv": "Pčelinjak Vršac"},
}

def get_weather_forecast(location: str = "avala", days: int = 14) -> dict:
    """Vuče vremensku prognozu za lokaciju pčelinjaka (lat/lon)."""
    location_lower = location.lower()

    warning = None
    if location_lower in APIARY_LOCATIONS:
        apiary = APIARY_LOCATIONS[location_lower]
    else:
        apiary = APIARY_LOCATIONS["avala"]
        warning = (
            f"Pčelinjak '{location}' nije pronađen u listi poznatih lokacija. "
            f"Korišćena je prognoza za {apiary['naziv']} kao default."
        )

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": apiary["latitude"],
        "longitude": apiary["longitude"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "weathercode", "windspeed_10m_max"],
        "timezone": "Europe/Belgrade",
        "forecast_days": days
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        raw_data = response.json()
        result = process_weather_data(raw_data, apiary["naziv"])
        if warning:
            result["warning"] = warning
        return result
    except requests.exceptions.Timeout:
        return {"error": "Vreme čekanja na API isteklo. Pokušaj ponovo."}
    except requests.exceptions.ConnectionError:
        return {"error": "Nema internet konekcije."}
    except requests.exceptions.RequestException as e:
        return {"error": f"API greška: {str(e)}"}


def process_weather_data(raw_data: dict, naziv_pcelinjaka: str) -> dict:
    """Obrađuje sirove podatke sa API-ja i procenjuje pogodnost dana za rad sa košnicama."""
    daily = raw_data.get("daily", {})
    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    precipitation = daily.get("precipitation_sum", [])
    weathercodes = daily.get("weathercode", [])
    windspeeds = daily.get("windspeed_10m_max", [])

    forecast_days = []
    for i in range(len(dates)):
        date_obj = datetime.strptime(dates[i], "%Y-%m-%d")
        day_name = get_day_name(date_obj)
        condition = interpret_weathercode(weathercodes[i] if i < len(weathercodes) else 0)
        rain = precipitation[i] if i < len(precipitation) else 0
        wind = windspeeds[i] if i < len(windspeeds) else 0
        max_t = max_temps[i] if i < len(max_temps) else 20

        # Pčele ne lete dobro po kiši, jakom vetru ili hladnom vremenu (< 12°C)
        good_for_beekeeping = rain < 2 and wind < 25 and max_t > 12

        forecast_days.append({
            "date": dates[i],
            "day_name": day_name,
            "max_temp": max_t,
            "min_temp": min_temps[i] if i < len(min_temps) else None,
            "precipitation_mm": rain,
            "wind_kmh": wind,
            "condition": condition,
            "good_for_beekeeping": good_for_beekeeping
        })

    return {
        "pcelinjak": naziv_pcelinjaka,
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
    """Generiše kratak tekstualni rezime prognoze za rad sa košnicama."""
    if not forecast_days:
        return "Nema podataka o vremenu."

    losi_dani = [d["day_name"] for d in forecast_days if not d["good_for_beekeeping"]]
    dobri_dani = [d["day_name"] for d in forecast_days if d["good_for_beekeeping"]]

    summary = f"Prognoza za {len(forecast_days)} dana: "

    if dobri_dani:
        summary += f"Dobri dani za rad sa košnicama: {', '.join(dobri_dani[:3])}. "
    else:
        summary += "Nema povoljnih dana u narednom periodu. "

    if losi_dani:
        summary += f"Izbegavati: {', '.join(losi_dani[:3])} (kiša/vetar/hladno)."

    return summary