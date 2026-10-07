# 🏥 MediGuard Senior Care - Voice Health Companion & Interaction Graph

MediGuard Senior Care is a mobile-first, AI-driven healthcare web application designed specifically for senior citizens. It helps elderly individuals manage daily medication schedules, identify critical drug-food interactions (such as Warfarin and Cranberry Juice), scan paper prescriptions using live camera OCR, and interact with a voice-activated assistant (**MediBot**) in English and Hindi.

---

## 🌟 Key Features

### 📱 1. Mobile-Optimized Live Camera OCR
* **Rear-Camera Priority**: Uses mobile `facingMode: { exact: "environment" }` constraints to open the back camera directly for prescription scanning.
* **Aspect-Ratio & Frame Guidance**: Includes custom UI overlays designed specifically for smartphone viewports to keep paper prescriptions aligned during capture.
* **File Fallback**: Supports photo library uploads for older devices or saved images.

### ⚠️ 2. Real-Time Drug-Food Interaction Safety Engine
* **Critical Alerts**: Visual and audible warnings for severe interaction hazards (e.g., *Warfarin + Cranberry Juice* or *Atorvastatin + Grapefruit*).
* **Interactive Knowledge Graph**: Canvas-based graph visualization mapping relationships between medicines, dietary items, and risk levels.

### 🎙️ 3. Bilingual Voice Assistant (MediBot)
* **Web Speech API & Voice Briefings**: Full Text-to-Speech (TTS) narrations and Speech-to-Text (STT) voice commands tailored for elderly users with low tech literacy.
* **Dual Language Support**: Instant toggle between **English** and **Hindi (हिंदी)** across all UI elements, alerts, and speech interfaces.
* **Auto-Briefing Capabilities**: Speaks critical medication warnings and daily updates upon app load.

### 📋 4. Daily Medicine Schedule & Management
* Interactively mark medicines as taken.
* Add custom medication items with timing, pill counts, and specific intake rules.
* View progress tracking bar for daily adherence.

---

## 🛠️ Tech Stack

* **Frontend**: HTML5, Tailwind CSS (CDN), Lucide Icons, HTML5 Canvas API, Web Speech API (`SpeechSynthesis` & `webkitSpeechRecognition`).
* **Backend**: Python / Flask (or FastAPI).
* **Styling & Fonts**: Plus Jakarta Sans typography, Senior-friendly high-contrast color scheme, adaptive touch targets.

---

## 📁 Repository Structure

```text
.
├── app.py                  # Backend server (Flask/FastAPI endpoints)
├── templates/
│   └── index.html          # Mobile-optimized single-page web interface
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
