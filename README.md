# 🐝 AI Asistent za Pčelarstvo

AI agent koji analizira planirane aktivnosti na pčelinjaku (pregled, hranjenje, berba, tretman) i kombinuje ih sa vremenskom prognozom kako bi predložio optimalan plan rada i procenio rizike kašnjenja. Razvijen u skladu sa zahtevima Zadatka 3, tematski povezan sa projektom **Košnica PLUS — Aplikacija za Pčelarstvo**. Koristi LangChain framework i podržava više LLM modela i provajdera.

## Veza sa projektom

Agent je dodatni AI modul za aplikaciju Košnica PLUS (https://github.com/elab-development/internet-tehnologije-2025-vebaplikacijazapcelarstvo_2022_0304). Koristi iste pojmove i podatke kao i glavna aplikacija:

- **Aktivnost** — pregled, hranjenje, berba, tretman (kao u `Aktivnost` modelu aplikacije)
- **Pčelinjak** — lokacija sa geografskim koordinatama (kao `latitude`/`longitude` polja u `Kosnica` modelu)
- **Vremenska prognoza** — Open-Meteo API (ista integracija kao u glavnoj aplikaciji, `/api/weather` ruta)

## Funkcionalnosti

- Unos planiranih aktivnosti na pčelinjaku kroz terminal (naziv, tip, planirani datum)
- Vremenska prognoza po pčelinjaku preko Open-Meteo API-ja (do 14 dana unapred)
- AI analiza i prioritizacija aktivnosti
- Procena rizika kašnjenja po aktivnosti (npr. kasni tretman protiv varoe, propuštena berba)
- Plan rada prilagođen vremenskim uslovima (pčele ne lete po kiši, jakom vetru i hladnom vremenu)
- Čuvanje izveštaja u Markdown fajl
- Podrška za više modela: Ollama (lokalno) i Groq (online)

## Ograničenja

- Vremenska prognoza dostupna je za narednih 14 dana. Za aktivnosti planirane dalje u budućnosti, agent ne može dati preporuku na osnovu vremenskih uslova, već samo na osnovu prioriteta i tipa aktivnosti.
- Trenutno se podaci o aktivnostima i pčelinjacima unose ručno kroz terminal — nije povezano sa bazom podataka glavne aplikacije (mogućnost za unapređenje, vidi ispod).

## Pokretanje

1. Klonirati repozitorijum:

```
git clone https://github.com/ninavuks/nudge.git
```

2. Napraviti virtuelno okruženje:

```
python -m venv venv
source venv/Scripts/activate   # Git Bash na Windows-u
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
🐝 AI ASISTENT ZA PČELARSTVO — Planiranje aktivnosti

📡 Izbor AI modela:
1. Ollama — llama3.2 (lokalno, sporo)
2. Ollama — mistral (lokalno, sporo)
3. Groq — llama3.3-70b (online, brzo, preporučeno)
4. Groq — llama3.1-8b (online, brzo)

Izaberi model (1-4): 3

📝 Unesi planirane aktivnosti na pčelinjaku:
Aktivnost 1 (naziv): Tretman protiv varoe
   Tip aktivnosti: 4 (Tretman)
   Planirani datum: 2026-07-05
Aktivnost 2 (naziv): gotovo

📍 Pčelinjak: avala

🤖 AI asistent analizira aktivnosti na pčelinjaku...
```

## Modeli

| Provider | Model                  | Tip     | Brzina |
| -------- | ---------------------- | ------- | ------ |
| Ollama   | llama3.2               | Lokalno | Sporo  |
| Ollama   | mistral                | Lokalno | Sporo  |
| Groq     | llama3.3-70b-versatile | Online  | Brzo   |
| Groq     | llama3.1-8b-instant    | Online  | Brzo   |

## Pčelinjaci (primer lokacija)

| Ključ       | Naziv                 |
| ----------- | --------------------- |
| avala       | Pčelinjak Avala       |
| fruska gora | Pčelinjak Fruška gora |
| zlatibor    | Pčelinjak Zlatibor    |
| vrsac       | Pčelinjak Vršac       |

## Potrebne biblioteke

- `langchain` — AI framework
- `langchain-community` — Ollama integracija
- `langchain-groq` — Groq integracija
- `langchain-ollama` — Ažurirana Ollama integracija
- `python-dotenv` — upravljanje .env fajlom
- `requests` — HTTP pozivi ka Open Meteo API

## Mogućnosti za unapređenje

- Povezivanje sa stvarnom bazom podataka aplikacije Košnica PLUS (čitanje aktivnosti i košnica direktno preko `/api/activities` i `/api/hives` ruta umesto ručnog unosa)
- Automatsko slanje preporuka agenta kroz postojeći sistem notifikacija aplikacije
- Podrška za prognozu po više pčelinjaka istog korisnika u jednom pokretanju
