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
            model = model or "llama3-8b-8192"
            return ChatGroq(
                groq_api_key=api_key,
                model_name=model
            )
        else:
            raise ValueError(f"Nepoznat provider: {provider}. Koristi 'ollama' ili 'groq'.")
    except Exception as e:
        raise RuntimeError(f"Greška pri učitavanju modela: {str(e)}")


def build_prompt(tasks: list, weather_data: dict) -> str:
    """Gradi strukturisan prompt za analizu taskova."""
    
    task_list = ""
    for i, task in enumerate(tasks, 1):
        task_list += f"{i}. {task['name']}"
        if task.get('deadline'):
            task_list += f" (rok: {task['deadline']})"
        if task.get('category'):
            task_list += f" [kategorija: {task['category']}]"
        task_list += "\n"

    weather_summary = weather_data.get("summary", "Nema podataka o vremenu.")
    city = weather_data.get("city", "Beograd")
    
    forecast_text = ""
    for day in weather_data.get("forecast", [])[:5]:
        forecast_text += f"- {day['day_name']} ({day['date']}): {day['condition']}, {day['max_temp']}°C, padavine: {day['precipitation_mm']}mm\n"

    template = PromptTemplate(
        input_variables=["task_list", "weather_summary", "city", "forecast_text"],
        template="""Ti si Nudge — pametni AI asistent za upravljanje zadacima i produktivnost.

## Tvoja uloga:
Analiziraj listu zadataka korisnika i vremensku prognozu za {city}, 
pa predloži optimalan plan rada sa procenom rizika.

## Zadaci korisnika:
{task_list}

## Vremenska prognoza za {city}:
{weather_summary}

Detalji po danima:
{forecast_text}

## Tvoj zadatak:
1. Analiziraj svaki zadatak i dodeli mu prioritet (Visok/Srednji/Nizak)
2. Proceni rizike ako se zadatak ne završi na vreme
3. Predloži koji zadaci se mogu raditi u kišne dane (kod kuće)
4. Predloži koji zadaci zahtevaju izlazak napolje i kada je najbolje vreme
5. Napiši konkretan plan za narednih 7 dana

## Format odgovora (koristi tačno ovaj Markdown format):

# Nudge — Analiza zadataka

## Prioritizovani zadaci
| Zadatak | Prioritet | Rok | Rizik kašnjenja |
|---------|-----------|-----|-----------------|
[popuni tabelu]

## Procena rizika
[za svaki zadatak navedi rizik i posledice kašnjenja]

## Plan prema vremenu
[predloži kada raditi koji zadatak prema prognozi]

## Preporučeni plan za 7 dana
[konkretan dnevni plan]

## Nudge preporuke
[3-5 konkretnih saveta za produktivnost]
"""
    )
    
    return template.format(
        task_list=task_list,
        weather_summary=weather_summary,
        city=city,
        forecast_text=forecast_text
    )


def analyze_tasks(tasks: list, weather_data: dict, provider: str = None, model: str = None) -> str:
    """Glavna funkcija — analizira taskove i vraća izveštaj."""
    
    if not tasks:
        return "Greška: Lista zadataka je prazna."
    
    if "error" in weather_data:
        weather_data = {
            "city": "Beograd",
            "summary": "Podaci o vremenu nisu dostupni.",
            "forecast": []
        }
    
    try:
        llm = get_llm(provider, model)
        prompt = build_prompt(tasks, weather_data)
        
        response = llm.invoke(prompt)
            
        if hasattr(response, 'content'):
            return response.content
        return str(response)
        
    except RuntimeError as e:
        return f"Greška sa modelom: {str(e)}"
    except Exception as e:
        return f"Neočekivana greška: {str(e)}"