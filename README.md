# WeatherGPT 🌦️🤖

WeatherGPT is an enterprise-grade AI-powered conversational weather intelligence mobile application. It provides real-time weather information, forecasts, official severe weather warnings, location-based advisories, multilingual interaction, voice processing, historical climate analysis, and low-bandwidth/offline access.

---

## 🌟 Key Features

1. **Grounded Conversational Intelligence**:
   - Natural language weather queries with **Zero-Hallucination Guardrails**.
   - All weather numbers and facts are directly fetched and grounded from trusted meteorological services (Open-Meteo & NOAA NWS).

2. **Official Warnings vs. AI Recommendations**:
   - Explicit separation between official government meteorological warnings (high-priority red banners) and AI safety advisories.

3. **Low-Bandwidth & Offline Caching**:
   - Compact payload mode for low connectivity environments.
   - Offline cache fallback via encrypted local storage on mobile and Redis in backend.

4. **Security & Clean Architecture**:
   - Zero hardcoded secrets (Pydantic `BaseSettings`).
   - Input sanitization and numerical boundary enforcement for untrusted weather data.
   - Redacted structured logging preventing key leakage.

---

## 📁 Repository Structure

```
app/
├── backend/                  # Python FastAPI Backend Service
│   ├── app/
│   │   ├── api/              # REST Endpoints (/weather, /chat, /alerts, /voice)
│   │   ├── core/             # Database, Redis Cache, Security, Redacted Logger
│   │   ├── models/           # SQLAlchemy DB Models
│   │   ├── schemas/          # Pydantic Schemas
│   │   └── services/         # Weather Provider, Grounded WeatherGPT Engine, Voice
│   ├── tests/                # Pytest Test Suite (100% Passing)
│   └── requirements.txt
├── mobile/                   # Flutter Mobile Client
│   ├── lib/
│   │   ├── core/             # Theme, Constants, Offline Cache
│   │   ├── models/           # Dart Data Models
│   │   ├── services/         # API Service & Weather Repository
│   │   └── presentation/     # Screens (Home, Chat, Alerts) & Custom Widgets
│   └── pubspec.yaml
├── docs/                     # Architectural Specification & Sitemap
│   └── ARCHITECTURE.md
└── docker-compose.yml        # Production Docker Setup (FastAPI, PostGIS, Redis)
```

---

## 🚀 Getting Started

### 1. Run Backend Tests
```bash
cd backend
python -m pytest
```

### 2. Launch Backend Locally
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```
Interactive API documentation: `http://localhost:8000/docs`

### 3. Launch Docker Environment
```bash
docker-compose up --build
```
