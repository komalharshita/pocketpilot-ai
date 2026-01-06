<!-- Improved compatibility of back to top link -->
<a name="readme-top"></a>

<!-- PROJECT SHIELDS -->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="#">
    <img src="https://github.com/user-attachments/assets/cc1baf9a-7dcf-439e-ba61-af4994290eac" alt="PocketPilot AI Logo" width="300" height= 300"/>
  </a>

  <h3 align="center">PocketPilot AI</h3>

  <p align="center">
    A smart personal finance assistant that turns everyday receipts into real-time spending insights using AI.
    <br />
    <br />
  
  </p>
</div>

---

## About The Project

PocketPilot AI solves a common real-world problem: expense tracking is fragmented, manual, and often ignored.
Receipts are easily lost, financial awareness remains low, and many existing tools are either too complex or require excessive manual input.

PocketPilot AI simplifies this by enabling users to upload receipts and instantly view their spending patterns through a clean, real-time dashboard.
An integrated AI assistant (“Pilot”) helps users understand their finances and ask meaningful questions about their spending behavior.

---

## Problem Statement

Most individuals lack **real-time awareness of their spending habits** because:
- Expense tracking is manual
- Receipts are disorganized
- Financial tools have steep learning curves

This leads to poor budgeting decisions and low financial confidence.

PocketPilot AI solves this by **automating expense capture** and **presenting insights visually and instantly**.

---
### Why PocketPilot AI?
- Reduces friction in everyday expense tracking
- Provides instant, visual financial insights
- Combines automation with AI-powered guidance
- Designed to be simple, fast, and hackathon-ready

---

## Built With
- Python
- Gradio
- Firebase
- Google Gemini AI
- Document AI (Demo Mode)
- Pandas

---

## Key Features (Current Implementation)

- Receipt upload (image/PDF)
- Demo Document AI receipt parsing
- Firebase data storage
- Dashboard showing:
  - Exactly 10 recent receipts
  - Spending by category
  - Spending by merchant
  - Spending over time
- INR (₹)-based summaries
- AI chatbot (“Pilot”) using Gemini AI

---

## Data Flow Diagram

<img width="500" height="700" alt="flow" src="https://github.com/user-attachments/assets/a69944d2-78b8-4b1f-a060-d25f992fcb05" />


---

## Getting Started

### Prerequisites
- Python 3.10+
- Firebase project credentials
- Gemini API key

### Installation
```sh
git clone https://github.com/your_username/pocketpilot-ai.git
cd pocketpilot-ai
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app/main.py
```

---

## Usage
1. Upload a receipt (image or PDF).
2. Receipt data is processed using demo Document AI.
3. Data is stored in Firebase.
4. Dashboard updates instantly with:
   - 10 most recent receipts
   - Spending by category
   - Spending by merchant
   - Spending over time
5. Ask finance questions using Pilot AI chatbot.

---

## Roadmap
- Receipt upload & analytics dashboard
- AI-powered finance chatbot
- Monthly & yearly summaries (planned)
- Exportable reports (planned)

---

## License
MIT License

---

## Team
CyberForge

<!-- MARKDOWN LINKS -->
[contributors-shield]: https://img.shields.io/github/contributors/komalharshita/pocketpilot-ai.svg?style=for-the-badge
[contributors-url]: https://github.com/komalharshita/pocketpilot-ai/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/komalharshita/pocketpilot-ai.svg?style=for-the-badge
[forks-url]: https://github.com/komalharshita/pocketpilot-ai/network/members
[stars-shield]: https://img.shields.io/github/stars/komalharshita/pocketpilot-ai.svg?style=for-the-badge
[stars-url]: https://github.com/komalharshita/pocketpilot-ai/stargazers
[issues-shield]: https://img.shields.io/github/issues/komalharshita/pocketpilot-ai.svg?style=for-the-badge
[issues-url]: https://github.com/komalharshita/pocketpilot-ai/issues
[license-shield]: https://img.shields.io/github/license/komalharshita/pocketpilot-ai.svg?style=for-the-badge
[license-url]: https://github.com/komalharshita/pocketpilot-ai/blob/main/LICENSE

