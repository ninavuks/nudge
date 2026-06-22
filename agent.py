from langchain_ollama import OllamaLLM as Ollama
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

AVAILABLE_MODELS = {
    "ollama": {
        "llama3.2": "llama3.2",
        "mistral": "mistral"
    },
    "groq": {
        "llama3.3": "llama-3.3-70b-versatile",
        "llama3.1": "llama-3.1-8b-instant"
    }
}

def get_llm(provider: str = None, model: str = None):
    """Vraća LLM model prema izboru."""
    provider = provider or os.getenv("DEFAULT_PROVIDER", "ollama")

    try:
        if provider == "ollama":
            model = model or os.getenv("DEFAULT_MODEL", "llama3.2")
            return Ollama(
                base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                model=model
            )
        elif provider == "groq":
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY nije postavljen u .env fajlu!")
            model = model or "llama-3.3-70b-versatile"
            return ChatGroq(
                groq_api_key=api_key,
                model_name=model
            )
        else:
            raise ValueError(f"Nepoznat provider: {provider}. Koristi 'ollama' ili 'groq'.")
    except Exception as e:
        raise RuntimeError(f"Greška pri učitavanju modela: {str(e)}")


def build_prompt(activities: list, weather_data: dict) -> str:
    """Gradi strukturisan prompt za analizu pčelarskih aktivnosti."""

    activity_list = ""
    for i, act in enumerate(activities, 1):
        activity_list += f"{i}. {act['name']} [tip: {act['type']}]"
        if act.get('deadline'):
            activity_list += f" (planirani datum: {act['deadline']})"
        activity_list += "\n"

    weather_summary = weather_data.get("summary", "Nema podataka o vremenu.")
    pcelinjak = weather_data.get("pcelinjak", "Pčelinjak")

    forecast_text = ""
    for day in weather_data.get("forecast", [])[:7]:
        forecast_text += (
            f"- {day['day_name']} ({day['date']}): {day['condition']}, "
            f"{day['max_temp']}°C, padavine: {day['precipitation_mm']}mm, "
            f"vetar: {day['wind_kmh']}km/h, "
            f"{'POVOLJNO' if day['good_for_beekeeping'] else 'NEPOVOLJNO'} za rad sa košnicama\n"
        )

    template = PromptTemplate(
        input_variables=["activity_list", "weather_summary", "pcelinjak", "forecast_text"],
        template="""Ti si AI asistent za pčelarstvo — pomažeš pčelaru da organizuje aktivnosti na pčelinjaku
uzimajući u obzir vremenske uslove, jer pčele ne podnose dobro kišu, jak vetar i niske temperature.

## Tvoja uloga:
Analiziraj planirane aktivnosti na pčelinjaku "{pcelinjak}" i vremensku prognozu,
pa predloži optimalan raspored rada sa procenom rizika kašnjenja.

## Planirane aktivnosti (pregled, hranjenje, berba, tretman):
{activity_list}

## Vremenska prognoza za {pcelinjak}:
{weather_summary}

Detalji po danima:
{forecast_text}

## Tvoj zadatak:
1. Analiziraj svaku aktivnost i dodeli joj prioritet (Visok/Srednji/Nizak)
2. Proceni rizik ako se aktivnost ne obavi na vreme (npr. tretman protiv varoe kasni, berba propušta optimalan trenutak)
3. Predloži koje aktivnosti zahtevaju izlazak na pčelinjak i kada je vremenski najbolje (pčele ne lete po kiši/jakom vetru/hladnom)
4. Napiši konkretan plan rada za narednih 7 dana

## Format odgovora (koristi tačno ovaj Markdown format):

# Plan rada na pčelinjaku

## Prioritizovane aktivnosti
| Aktivnost | Tip | Prioritet | Planirani datum | Rizik kašnjenja |
|-----------|-----|-----------|------------------|-----------------|
[popuni tabelu]

## Procena rizika
[za svaku aktivnost navedi rizik i posledice kašnjenja]

## Plan prema vremenskim uslovima
[predloži kada raditi koju aktivnost prema prognozi]

## Preporučeni plan za 7 dana
[konkretan dnevni plan]

## Preporuke za pčelara
[3-5 konkretnih saveta]
"""
    )

    return template.format(
        activity_list=activity_list,
        weather_summary=weather_summary,
        pcelinjak=pcelinjak,
        forecast_text=forecast_text
    )


def analyze_tasks(activities: list, weather_data: dict, provider: str = None, model: str = None) -> str:
    """Glavna funkcija — analizira aktivnosti na pčelinjaku i vraća izveštaj."""

    if not activities:
        return "Greška: Lista aktivnosti je prazna."

    if "error" in weather_data:
        weather_data = {
            "pcelinjak": "Pčelinjak",
            "summary": "Podaci o vremenu nisu dostupni.",
            "forecast": []
        }

    try:
        llm = get_llm(provider, model)
        prompt = build_prompt(activities, weather_data)

        response = llm.invoke(prompt)

        if hasattr(response, 'content'):
            return response.content
        return str(response)

    except RuntimeError as e:
        return f"Greška sa modelom: {str(e)}"
    except Exception as e:
        return f"Neočekivana greška: {str(e)}"