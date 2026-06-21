# 🔔 Nudge: AI Task Manager

Nudge je inteligentni AI agent koji analizira tvoje zadatke i kombinuje ih sa vremenskom prognozom kako bi predložio optimalan plan rada i procenio rizike kašnjenja. Koristi LangChain framework i podržava više LLM modela i provajdera.

## Funkcionalnosti

- Unos zadataka kroz terminal sa rokovima i kategorijama
- Vremenska prognoza sa Open Meteo API 
- AI analiza i prioritizacija zadataka
- Procena rizika kašnjenja po zadatku
- Plan rada prilagođen vremenskim uslovima
- Čuvanje izveštaja u Markdown fajl
- Podrška za više modela: Ollama (lokalno) i Groq (online)

## Pokretanje

1. Klonirati repozitorijum:
```
git clone https://github.com/tvojeime/nudge.git
```
2. Napraviti virtuelno okruženje:
```
python -m venv venv
venv\Scripts\activate
```
3. Instalirati biblioteke:
```
pip install -r requirements.txt
```
4. Napraviti `.env` fajl:
```
GROQ_API_KEY=groq API kljuc
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_PROVIDER=groq
DEFAULT_MODEL=llama-3.3-70b-versatile
```
5. Pokretanje
```
python main.py
```

## Primer korišćenja

```
🔔 NUDGE — AI Task Manager

📡 Izbor AI modela:
1. Ollama — llama3.2 (lokalno, sporo)
2. Ollama — mistral (lokalno, sporo)
3. Groq — llama3.3-70b (online, brzo, preporučeno)
4. Groq — llama3.1-8b (online, brzo)

Izaberi model (1-4): 3

📝 Unesi svoje zadatke:
Zadatak 1: Završiti seminarski rad
   Rok: 2026-06-28
   Kategorija: 2 (Škola)
Zadatak 2: gotovo

🌍 Grad: Beograd

🤖 Nudge analizira tvoje zadatke...


## Modeli

| Provider | Model | Tip | Brzina |
|----------|-------|-----|--------|
| Ollama | llama3.2 | Lokalno | Sporo |
| Ollama | mistral | Lokalno | Sporo |
| Groq | llama3.3-70b-versatile | Online | Brzo |
| Groq | llama3.1-8b-instant | Online | Brzo |

## Potrebne biblioteke

- `langchain` — AI framework
- `langchain-community` — Ollama integracija
- `langchain-groq` — Groq integracija
- `langchain-ollama` — Ažurirana Ollama integracija
- `python-dotenv` — upravljanje .env fajlom
- `requests` — HTTP pozivi ka Open Meteo API