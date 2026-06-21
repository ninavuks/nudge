# Nudge — AI Task Manager

Nudge je AI agent koji analizira tvoje zadatke i kombinuje ih sa vremenskom 
prognozom kako bi predložio optimalan plan rada i procenio rizike.

## Funkcionalnosti

- Unos zadataka kroz terminal sa rokovima i kategorijama
- Vremenska prognoza sa Open Meteo API (besplatno, bez registracije)
- AI analiza i prioritizacija zadataka
- Procena rizika kašnjenja
- Plan rada prema vremenskim uslovima
- Čuvanje izveštaja u Markdown fajl
- Podrška za više modela: Ollama (lokalno) i Groq (online)


## Primer korišćenja

```
NUDGE — AI Task Manager

Izbor AI modela:
1. Ollama — llama3.2 (lokalno)
> Izaberi model: 1

Unesi svoje zadatke:
Zadatak 1: Završiti seminarski rad
Rok: 2024-12-20
Kategorija: 2 (Škola)

Zadatak 2: gotovo

Grad: Beograd

Nudge analizira tvoje zadatke...
```

## Struktura projekta

```
nudge/
├── main.py          # Ulazna tačka, terminal interfejs
├── agent.py         # LangChain AI logika
├── data.py          # Open Meteo API integracija
├── .env             # API ključevi
├── requirements.txt # Biblioteke
└── README.md        # Dokumentacija
```

## Potrebne biblioteke

- `langchain` — AI framework
- `langchain-community` — Ollama integracija
- `langchain-groq` — Groq integracija
- `python-dotenv` — upravljanje .env fajlom
- `requests` — HTTP pozivi ka Open Meteo API

## Modeli

| Provider | Model | Tip |
|----------|-------|-----|
| Ollama | llama3.2 | Lokalno |
| Ollama | mistral | Lokalno |
| Groq | llama3 | Online |
| Groq | mixtral | Online |