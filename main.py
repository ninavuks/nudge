import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from data import get_weather_forecast
from agent import analyze_tasks, AVAILABLE_MODELS

load_dotenv()

def print_header():
    print("\n" + "="*50)
    print("        🔔 NUDGE — AI Task Manager")
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


def get_tasks_from_user() -> list:
    """Prima taskove od korisnika kroz terminal."""
    tasks = []
    print("📝 Unesi svoje zadatke (ukucaj 'gotovo' kad završiš):\n")

    while True:
        task_name = input(f"Zadatak {len(tasks)+1}: ").strip()

        if task_name.lower() == 'gotovo':
            if not tasks:
                print("⚠️  Nisi uneo nijedan zadatak. Pokušaj ponovo.\n")
                continue
            break

        if not task_name:
            print("⚠️  Naziv zadatka ne može biti prazan.\n")
            continue

        deadline = input(f"   Rok za '{task_name}' (npr. 2026-12-25) [Enter za preskakanje]: ").strip()
        if deadline:
            try:
                datetime.strptime(deadline, "%Y-%m-%d")
            except ValueError:
                print("   ⚠️  Neispravan format datuma! Zadatak se dodaje bez roka.\n")
                deadline = None
        else:
            deadline = None

        print(f"   Kategorija za '{task_name}':")
        print("   1. Posao  2. Škola  3. Lično  4. Zdravlje  5. Ostalo")
        cat_choice = input("   Izbor (1-5) [Enter za preskakanje]: ").strip()

        categories = {"1": "Posao", "2": "Škola", "3": "Lično", "4": "Zdravlje", "5": "Ostalo"}
        category = categories.get(cat_choice, "")

        tasks.append({
            "name": task_name,
            "deadline": deadline if deadline else None,
            "category": category if category else None
        })

        print(f"   ✅ Dodat: {task_name}\n")

    return tasks


def get_city_from_user() -> str:
    """Prima naziv grada od korisnika."""
    print("\n🌍 Za koji grad da proverim vremensku prognozu?")
    print("Dostupni gradovi: Beograd, Novi Sad, Nis, London, Berlin")
    city = input("Grad [Enter za Beograd]: ").strip()
    return city if city else "beograd"


def save_report(report: str, tasks: list) -> str:
    """Čuva izveštaj u Markdown fajl."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"nudge_report_{timestamp}.md"

    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"# Nudge izveštaj\n")
            f.write(f"*Generisano: {datetime.now().strftime('%d.%m.%Y u %H:%M')}*\n\n")
            f.write(f"**Broj zadataka:** {len(tasks)}\n\n")
            f.write("---\n\n")
            f.write(report)
        return filename
    except IOError as e:
        return f"Greška pri čuvanju: {str(e)}"


def main():
    print_header()

    # Izbor modela
    provider, model = choose_model()

    # Unos zadataka
    tasks = get_tasks_from_user()

    # Izbor grada
    city = get_city_from_user()

    # Vremenska prognoza
    print(f"\n🌤️  Preuzimam vremensku prognozu za {city.capitalize()}...")
    weather_data = get_weather_forecast(city)

    if "error" in weather_data:
        print(f"⚠️  {weather_data['error']} Nastavlja se bez podataka o vremenu.")
    else:
        print(f"✅ Prognoza preuzeta: {weather_data['summary']}\n")

    # AI analiza
    print("🤖 Nudge analizira tvoje zadatke...\n")

    report = analyze_tasks(tasks, weather_data, provider, model)

    # Prikaz izveštaja
    print("\n" + "="*50)
    print(report)
    print("="*50 + "\n")

    # Čuvanje izveštaja
    save_choice = input("💾 Sačuvati izveštaj u fajl? (da/ne): ").strip().lower()
    if save_choice == "da":
        filename = save_report(report, tasks)
        if "Greška" not in filename:
            print(f"✅ Izveštaj sačuvan: {filename}")
        else:
            print(filename)

    print("\n🔔 Hvala što koristiš Nudge! Srećan rad!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Nudge je prekinut. Doviđenja!")
        sys.exit(0)