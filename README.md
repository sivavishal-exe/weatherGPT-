<p align="center">
  <img src="docs/logo.png" alt="WeatherGPT Logo" width="130" height="130" style="border-radius: 24px; box-shadow: 0 10px 30px rgba(2, 132, 199, 0.4);" />
</p>

<h1 align="center">WeatherGPT Intelligence</h1>

<p align="center">
  <strong>Enterprise-Grade Conversational Weather Intelligence, Real-Time Doppler Radar & Grounded Meteorological Safety System</strong>
</p>

<p align="center">
  <a href="https://flutter.dev/"><img src="https://img.shields.io/badge/Mobile-Flutter_3.x-02569B.svg?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/Backend-FastAPI_v0.110-009688.svg?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Container-Docker-2496ED.svg?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License" /></a>
  <img src="https://img.shields.io/badge/SIH-2026_Hackathon-FF9933.svg?style=for-the-badge" alt="SIH 2026" />
</p>

---

## 📖 Executive Summary

**WeatherGPT Intelligence** is a production-grade, AI-driven meteorological companion engineered for the **Smart India Hackathon (SIH) 2026**. Built to bridge the critical gap between complex meteorological sensor data and everyday civilian actionability, WeatherGPT combines:

1. **Grounded Conversational AI**: Zero-hallucination natural language answers backed by strict factual verification against authorized meteorological services (IMD, Open-Meteo, NOAA NWS).
2. **Interactive Doppler Weather Radar**: Real-time simulated 360° radar sweep scope with dynamic precipitation reflectivity (dBZ), thermal contours, and wind vector streamlines.
3. **Transparent WMO Hazard Risk Assessment**: An explainable 0–100 impact scoring algorithm adhering to World Meteorological Organization protocols.
4. **Emergency Low-Bandwidth & Offline Resilience**: Compressed JSON payloads and multi-tier local encrypted caching for disaster situations and rural connectivity.
5. **Cross-Platform Mobile Application**: Crafted with Flutter featuring custom branding, bundled Roboto typography, dynamic GPS synchronization, and 10+ modular screens.

---

## 📱 Mobile Application Showcase

<table align="center" width="100%">
  <tr>
    <td width="33%" align="center">
      <strong>Home Dashboard</strong><br>
      <em>Live GPS, Conditions & Metrics</em><br><br>
      <img src="docs/screenshots/home_dashboard.png" width="260" alt="Home Dashboard" />
    </td>
    <td width="33%" align="center">
      <strong>Interactive Doppler Radar</strong><br>
      <em>360° Sweep & Multi-Layer dBZ</em><br><br>
      <img src="docs/screenshots/weather_radar.png" width="260" alt="Doppler Radar" />
    </td>
    <td width="33%" align="center">
      <strong>Grounded AI Assistant</strong><br>
      <em>Zero-Hallucination Verified Facts</em><br><br>
      <img src="docs/screenshots/ai_assistant.png" width="260" alt="WeatherGPT AI Chat" />
    </td>
  </tr>
  <tr>
    <td width="33%" align="center">
      <strong>Navigation Drawer</strong><br>
      <em>10+ Modular Screen Destinations</em><br><br>
      <img src="docs/screenshots/navigation_drawer.png" width="260" alt="Navigation Drawer" />
    </td>
    <td width="33%" align="center">
      <strong>7-Day Forecast</strong><br>
      <em>Precipitation Probabilities & Temps</em><br><br>
      <img src="docs/screenshots/forecast_view.png" width="260" alt="7-Day Forecast" />
    </td>
    <td width="33%" align="center">
      <strong>Brand Identity & Launch</strong><br>
      <em>Custom Glowing Logo & Splash</em><br><br>
      <img src="docs/logo.png" width="180" alt="Brand Logo" />
    </td>
  </tr>
</table>

---

## 🏛️ System Architecture

```mermaid
flowchart TB
    subgraph MobileClient["📱 Mobile Client (Flutter 3.x)"]
        UI["Modern UI / Roboto Typography Engine"]
        HomeView["Home Weather Dashboard"]
        RadarView["Interactive Doppler Radar (CustomPaint 60 FPS)"]
        ChatView["WeatherGPT Conversational Assistant"]
        VoiceView["Voice Assistant Studio (STT)"]
        LocService["GPS Location Engine (Geolocator + TTL Cache)"]
        CacheMgr["Local SQLite / Encrypted SharedPreferences"]
    end

    subgraph ReverseBridge["🔌 Connection Bridge"]
        ADB["ADB Reverse TCP Bridge (tcp:8000 -> tcp:8000)"]
    end

    subgraph BackendGateway["⚡ Backend Microservices (FastAPI)"]
        Router["FastAPI REST Router (/api/v1)"]
        SecMiddleware["Security & Input Sanitization Middleware"]
        CacheLayer["Redis In-Memory Key-Value Cache"]
        RiskEngine["WMO Impact & Risk Assessment Engine (0-100 Score)"]
        LLMGrounding["LLM Verification & Grounding Guardrails"]
    end

    subgraph MeteorologicalProviders["🌐 Meteorological & AI Backbones"]
        IMD["Open-Meteo & IMD Doppler Radar APIs"]
        NOAA["NOAA National Weather Service"]
        Gemini["Fine-Tuned LLM (Gemini / QLoRA Reasoning)"]
    end

    MobileClient <--> ADB <--> BackendGateway
    Router <--> CacheLayer
    Router <--> RiskEngine
    Router <--> LLMGrounding
    RiskEngine <--> IMD
    RiskEngine <--> NOAA
    LLMGrounding <--> Gemini
```

---

## 🌟 Core Modules & Engineering Highlights

### 1. 🤖 Grounded Conversational Intelligence (`/api/v1/chat`)
- **Strict Verification Guardrails**: Every LLM response synthesizes verified meteorological facts before text generation. The model cannot hallucinate precipitation rates, wind speeds, or safety advisories.
- **Multilingual Support**: Real-time natural language query answering in English, Hindi, Tamil, and regional Indian languages.
- **Source Transparency**: Every conversational answer displays an explicit citation badge indicating the verifying meteorological agency.

### 2. 📡 Interactive Doppler Weather Radar (`map_screen.dart`)
- **60 FPS Vector Sweep**: Rendered using Flutter's `CustomPaint` with a real-time rotating sweep beam, fading scan gradient, range rings (50 km – 200 km), and cardinal axes.
- **Layer Switching**: Instantly toggle between **Precipitation Reflectivity (dBZ)**, **Temperature Heatmap (°C)**, **Wind Vectors (km/h)**, and **Satellite Cloud Depth (%)**.
- **Live Station Telemetry**: Dynamic station metadata, elevation angle scan status, and GPS-anchored positioning.

### 3. ⚠️ WMO Hazard Risk Assessment Engine (`risk_engine.py`)
- Standardized algorithmic scoring from **0 to 100** evaluating:
  - Extreme Rainfall intensity (`mm/hr` threshold tracking)
  - Severe Gale/Wind velocities & Gust indices
  - Wet Bulb Temperature & Heat Vulnerability Index
- Unambiguously bifurcates **Official Government Alerts** (high-priority alerts) from **AI Safety Recommendations**.

### 4. 📶 Low-Bandwidth & Disaster Resilience Mode
- **Ultra-Compact Payloads**: Minified JSON structure stripping non-essential telemetry in low-connectivity areas.
- **Instant Cache Hydration**: Mobile app pre-loads local cached weather state instantaneously on cold startup to eliminate blank loading screens.
- **In-Memory GPS De-Duplication**: Prevents repeated device sensor polling, saving battery and preventing mobile thermal throttling.

### 5. 🎨 Typography & Design Integrity
- **Embedded Roboto Typography**: Solves custom OEM font corruption (such as cursive phone themes) by bundling Google's official Roboto font family directly into app assets.
- **Accessible Hamburger Navigation**: Dedicated drawer button enabling seamless access to 10+ sub-screens without conflicting with system edge-swipe gestures.

---

## 📁 Repository Structure

```text
app/
├── backend/                  # Python FastAPI Production Backend
│   ├── alembic/              # Database Schema Migrations
│   ├── app/
│   │   ├── api/              # REST Endpoints (/weather, /chat, /alerts, /radar, /climate)
│   │   ├── core/             # Database Config, Redis, Security & Logging
│   │   ├── models/           # SQLAlchemy Data Models
│   │   ├── schemas/          # Pydantic v2 Request/Response Schemas
│   │   └── services/         # Meteorological Connectors, Risk Engine, LLM Grounding
│   ├── tests/                # Automated Test Suite (Pytest)
│   └── requirements.txt      # Python Dependencies
├── mobile/                   # Flutter Cross-Platform Client
│   ├── android/              # Native Android Wrapper & Gradle Build Config
│   ├── assets/
│   │   ├── fonts/            # Bundled Roboto Font Family (Regular, Medium, Bold)
│   │   └── images/           # Official WeatherGPT Brand Assets
│   ├── lib/
│   │   ├── core/             # App Themes, Color Tokens, Constants, Offline Storage
│   │   ├── models/           # Dart Data Models
│   │   ├── presentation/     # Screens (Home, Forecast, Alerts, Chat, Radar, Voice, Profile)
│   │   └── services/         # API Service, Location Service, Repository
│   └── pubspec.yaml          # Flutter Dependencies & Asset Registrations
├── docs/                     # Visual Documentation & Architecture
│   ├── screenshots/          # High-Resolution Mobile Screenshots
│   └── logo.png              # Official Project Logo
├── docker-compose.yml        # Multi-Container Deployment (FastAPI, Redis, PostGIS)
├── Dockerfile                # Production Container Definition
└── README.md                 # Project Documentation
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: `3.11+`
- **Flutter**: `3.x+` (Dart 3.x)
- **Android SDK**: Platform tools with `adb`
- **Docker** *(optional)*: For production container deployment

---

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run automated tests
python -m pytest

# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`

---

### 2. Mobile App Setup & Device Deployment

```bash
# Navigate to mobile directory
cd mobile

# Fetch Flutter dependencies
flutter pub get

# Connect your phone via USB (with USB Debugging enabled)
# Verify connection:
adb devices

# Configure ADB reverse port forwarding (routes device localhost:8000 to PC backend)
adb reverse tcp:8000 tcp:8000

# Build and install directly onto connected device:
flutter run --debug
```

Or build a standalone APK:

```bash
flutter build apk --debug
# Output: build/app/outputs/flutter-apk/app-debug.apk

# Install via ADB:
adb install -r build/app/outputs/flutter-apk/app-debug.apk
```

---

### 3. Production Docker Deployment

To launch the complete enterprise stack (FastAPI Backend, Redis Cache, PostGIS DB):

```bash
docker-compose up --build -d
```

---

## 🔑 Environment Configuration

Create a `.env` file in `app/backend/`:

```env
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secure-secret-key-32-chars-minimum

# LLM Conversational Intelligence
LLM_PROVIDER=gemini
LLM_API_KEY=your-gemini-or-openai-api-key

# Meteorological Providers
VISUAL_CROSSING_API_KEY=your-api-key-optional

# Cache & Storage
CACHE_TTL_SECONDS=600
DATABASE_URL=sqlite+aiosqlite:///./weathergpt.db
# Production: postgresql+asyncpg://user:password@localhost:5432/weathergpt
```

---

## 📡 REST API Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/weather/current` | Real-time weather conditions by lat/lon or city name |
| `GET` | `/api/v1/weather/forecast` | 7-day multi-tier forecast with precipitation chances |
| `POST` | `/api/v1/chat` | Conversational query with verified meteorological grounding |
| `GET` | `/api/v1/alerts` | Active severe meteorological warnings & risk score |
| `GET` | `/api/v1/climate/historical` | 30-year WMO baseline and decadal climate shift data |
| `GET` | `/health` | Service health, database connection & cache status |

---

## 🏆 Smart India Hackathon (SIH) 2026

- **Domain**: Disaster Management, Agriculture & Citizen Safety
- **Core Impact**: Delivers critical, actionable weather intelligence to vulnerable populations, disaster response agencies, and daily commuters with zero language or connectivity barriers.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

<p align="center">
  <sub>Built with ❤️ for Smart India Hackathon 2026 • Powered by Gemini AI, Flutter & FastAPI</sub>
</p>
