import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from data import get_weather_forecast, APIARY_LOCATIONS
from agent import analyze_tasks, AVAILABLE_MODELS

load_dotenv()

def print_header():
    print("\n" + "="*50)
    print("   🐝 AI ASISTENT ZA PČELARSTVO — Planiranje aktivnosti")
    print("="*50 + "\n")

def choose_model() -> tuple:
    """Korisnik bira provider i model."""
    print("📡 Izbor AI modela:\n")
    print("1. Ollama — llama3.2 (lokalno, sporo ~5-10min)")
    print("2. Ollama — mistral (lokalno, sporo ~5-10min)")
    print("3. Groq — llama3.3-70b (online, brzo, preporučeno)")
    print("4. Groq — llama3.1-8b (online, brzo)\n")

    choice = input("Izaberi model (1-4) [Enter za opciju 3]: ").strip()

    options = {
        "1": ("ollama", "llama3.2"),
        "2": ("ollama", "mistral"),
        "3": ("groq", "llama-3.3-70b-versatile"),
        "4": ("groq", "llama-3.1-8b-instant"),
    }

    if choice in options:
        return options[choice]
    return ("groq", "llama-3.3-70b-versatile")


def get_activities_from_user() -> list:
    """Prima planirane aktivnosti na pčelinjaku od korisnika kroz terminal."""
    activities = []
    print("📝 Unesi planirane aktivnosti na pčelinjaku (ukucaj 'gotovo' kad završiš):\n")

    activity_types = {"1": "pregled", "2": "hranjenje", "3": "berba", "4": "tretman"}

    while True:
        activity_name = input(f"Aktivnost {len(activities)+1} (naziv): ").strip()

        if activity_name.lower() == 'gotovo':
            if not activities:
                print("⚠️  Nisi uneo nijednu aktivnost. Pokušaj ponovo.\n")
                continue
            break

        if not activity_name:
            print("⚠️  Naziv aktivnosti ne može biti prazan.\n")
            continue

        print(f"   Tip aktivnosti za '{activity_name}':")
        print("   1. Pregled  2. Hranjenje  3. Berba  4. Tretman")
        type_choice = input("   Izbor (1-4) [Enter za 'pregled']: ").strip()
        activity_type = activity_types.get(type_choice, "pregled")

        deadline = input(f"   Planirani datum za '{activity_name}' (npr. 2026-06-28) [Enter za preskakanje]: ").strip()
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                print("   ⚠️  Neispravan format datuma! Aktivnost se dodaje bez datuma.\n")
                deadline = None
        else:
            deadline = None

        activities.append({
            "name": activity_name,
            "type": activity_type,
            "deadline": deadline
        })

        print(f"   ✅ Dodato: {activity_name} ({activity_type})\n")

    return activities


def get_apiary_from_user() -> str:
    """Prima izbor pčelinjaka (lokacije) od korisnika."""
    print("\n📍 Za koji pčelinjak da proverim vremensku prognozu?")
    print("Dostupni pčelinjaci:")
    for key, val in APIARY_LOCATIONS.items():
        print(f"  - {val['naziv']} (ukucaj: {key})")
    location = input("Pčelinjak [Enter za Avala]: ").strip()
    return location if location else "avala"


def save_report(report: str, activities: list) -> str:
    """Čuva izveštaj u Markdown fajl."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"pcelinjak_izvestaj_{timestamp}.md"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Izveštaj — Plan rada na pčelinjaku\n")
            f.write(f"*Generisano: {datetime.now().strftime('%d.%m.%Y u %H:%M')}*\n\n")
            f.write(f"**Broj aktivnosti:** {len(activities)}\n\n")
            f.write("---\n\n")
            f.write(report)
        return filename
    except IOError as e:
        return f"Greška pri čuvanju: {str(e)}"


def main():
    print_header()

    # Izbor modela
    provider, model = choose_model()

    # Unos aktivnosti
    activities = get_activities_from_user()

    # Izbor pčelinjaka
    apiary = get_apiary_from_user()

    # Vremenska prognoza
    print(f"\n🌤️  Preuzimam vremensku prognozu...")
    weather_data = get_weather_forecast(apiary)

    if "error" in weather_data:
        print(f"⚠️  {weather_data['error']} Nastavlja se bez podataka o vremenu.")
    else:
        if weather_data.get("warning"):
            print(f"⚠️  {weather_data['warning']}")
        print(f"✅ Prognoza preuzeta: {weather_data['summary']}\n")
    # AI analiza
    print("🤖 AI asistent analizira aktivnosti na pčelinjaku...\n")

    report = analyze_tasks(activities, weather_data, provider, model)

    # Prikaz izveštaja
    print("\n" + "="*50)
    print(report)
    print("="*50 + "\n")

    # Čuvanje izveštaja
    save_choice = input("💾 Sačuvati izveštaj u fajl? (da/ne): ").strip().lower()
    if save_choice == "da":
        filename = save_report(report, activities)
        if "Greška" not in filename:
            print(f"✅ Izveštaj sačuvan: {filename}")
        else:
            print(filename)

    print("\n🐝 Hvala što koristiš AI asistenta za pčelarstvo! Srećan rad na pčelinjaku!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program je prekinut. Doviđenja!")
        sys.exit(0)