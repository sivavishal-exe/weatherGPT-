# WeatherGPT Intelligence 🌦️🤖

> **Enterprise-Grade AI Conversational Weather Intelligence & Real-Time Meteorological Safety System**

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_v0.110.0-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Flutter](https://img.shields.io/badge/Mobile-Flutter_3.x-02569B.svg?style=flat&logo=flutter)](https://flutter.dev/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)]()

---

## 📖 Overview

**WeatherGPT Intelligence** is a state-of-the-art, AI-powered conversational weather mobile & backend platform designed for Smart India Hackathon (SIH) 2026. It integrates real-time meteorological data, grounded multi-lingual conversational AI, transparent risk evaluation engines, severe weather safety alerts, and low-bandwidth/offline fallback capability.

---

## 🌟 Key Features

### 🤖 1. Grounded Conversational Weather AI
- Natural language query interface powered by **Fine-Tuned LLMs** (Gemini / QLoRA adapters).
- **Zero-Hallucination Guardrails**: All weather facts, numerical data, and precipitation metrics are strictly grounded against verified meteorological providers.
- Supports multi-lingual advisory generation in **English, Hindi, Tamil, Telugu, and more**.

### ⚠️ 2. Transparent Severe Weather Risk Assessment Engine
- Implements an explainable **0–100 Weather Impact Score** adhering to WMO (World Meteorological Organization) standards.
- Evaluates rainfall rate (`mm/h`), wind speed, heat indices, convective hazards, and official government warnings.
- Explicitly separates **Official Government Warnings** (High-Priority Banners) from **AI Safety Recommendations**.

### 📍 3. Live GPS Location Tracking & Travel Sync
- Real-time GPS location tracking using `Geolocator`.
- Dynamically updates weather metrics, 7-day forecasts, severe alerts, and AI advisory contexts as you move or travel across regions.

### 📶 4. Low-Bandwidth Mode & Offline Synchronization
- Features a **Low-Bandwidth Mode** returning ultra-compressed payload JSON for low-connectivity rural or emergency areas.
- Automatic multi-tier caching (Redis backend cache & encrypted local mobile cache) ensuring offline access during network outages.

### 🛡️ 5. Enterprise Security & Clean Architecture
- Clean layered architecture separating Presentation, Repositories, API Routers, and Services.
- Input sanitization, SQL injection prevention, prompt-injection defense mechanisms, and zero hardcoded secrets (`Pydantic BaseSettings`).

---

## 📁 Repository Structure

```text
app/
├── backend/                  # Python FastAPI Backend Service
│   ├── alembic/              # Database Schema Migration Scripts
│   ├── app/
│   │   ├── api/              # REST Endpoints (/weather, /chat, /alerts, /voice, /climate)
│   │   ├── core/             # Database, Redis Cache, Security, Redacted Logger
│   │   ├── models/           # SQLAlchemy DB Models (Weather, Alerts, Metadata)
│   │   ├── schemas/          # Pydantic Request/Response Schemas
│   │   └── services/         # Weather Providers, Risk Engine, LLM Grounding, Voice
│   ├── tests/                # Comprehensive Pytest Suite
│   └── requirements.txt      # Python Dependencies
├── mobile/                   # Flutter Cross-Platform Mobile Application
│   ├── android/              # Native Android Wrapper & Gradle Build System
│   ├── lib/
│   │   ├── core/             # Theme Tokens, Constants, Offline Cache Manager
│   │   ├── models/           # Dart Data Models
│   │   ├── presentation/     # Screens (Home, Forecast, Alerts, Chat, Radar, Voice)
│   │   └── services/         # API Service, Location Service, Weather Repository
│   └── pubspec.yaml          # Flutter Dependencies & Assets
├── docs/                     # Architectural Specification & Site Diagrams
├── WeatherGPT.apk            # Pre-compiled Android Application Package
└── docker-compose.yml        # Production Docker Setup (FastAPI, PostGIS, Redis)
```

---

## 🔑 Environment & API Key Configuration

Create a `.env` file in `app/backend/`:

```env
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=your-secure-secret-key

# LLM Conversational Intelligence Key (Gemini / OpenAI)
LLM_PROVIDER=gemini
LLM_API_KEY=your-llm-api-key

# Weather Meteorological Provider Key (Visual Crossing)
VISUAL_CROSSING_API_KEY=your-visual-crossing-key

# Caching & Database
CACHE_TTL_SECONDS=600
DATABASE_URL=sqlite+aiosqlite:///./weathergpt.db
```

---

## 🚀 Quick Start Guide

### 1. Backend Setup & Run

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run pytest test suite
python -m pytest

# Start Uvicorn development server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
* Interactive API Documentation (Swagger): `http://localhost:8000/docs`

### 2. Deploy to Connected Mobile Device

Connect your phone via USB with USB Debugging enabled, then execute:

```powershell
# Set up ADB reverse port forwarding for USB debugging
adb reverse tcp:8000 tcp:8000

# Install APK directly onto connected phone
android run --apks="mobile/build/app/outputs/apk/debug/app-debug.apk"
```

### 3. Production Docker Deployment

```bash
docker-compose up --build -d
```

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy, Pydantic v2, Alembic
- **Mobile Client**: Flutter 3.x, Dart, Geolocator, Shared Preferences
- **AI & ML**: Fine-tuned LLMs (Gemini / QLoRA), Grounded Fact Evaluator, WMO Risk Scoring Engine
- **Databases & Cache**: SQLite (Development), PostGIS/PostgreSQL (Production), Redis
- **Tooling & Orchestration**: Android CLI, Gradle 9, Docker & Docker Compose

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
