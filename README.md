
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
  </p>

  <p align="center"><em>
    Our submission for Cyberathon – GDGoC 2026
  </em></p>
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
## What We Built

PocketPilot AI is a working end-to-end system that includes:

- A receipt upload pipeline with demo Document AI processing
- Real-time data storage using Firebase
- An interactive analytics dashboard (charts + tables)
- An AI chatbot (Pilot) powered by Gemini AI
- Automatic dashboard refresh after every receipt upload

All features shown in this repository are fully implemented and functional.

---

## Built With

<p align="left">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" width="48" height="48"/>
  <img src="https://raw.githubusercontent.com/simple-icons/simple-icons/develop/icons/gradio.svg" alt="Gradio" width="48" height="48"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/firebase/firebase-plain.svg" alt="Firebase" width="48" height="48"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" alt="Pandas" width="48" height="48"/>
</p>

Python--Gradio--Firebase--Pandas

### AI Components

#### Gemini AI
Gemini AI powers the Pilot chatbot, enabling users to ask finance-related questions and receive contextual responses based on stored receipt data.

#### Document AI (Demo Mode)
Receipt parsing is implemented using a demo Document AI pipeline to simulate OCR and data extraction. This avoids paid API dependencies while maintaining realistic system behavior.

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

## License
MIT License

---

## Team — CyberForge
This project was built and submitted as part of **Cyberathon – GDGoC 2026**.


| Team Member | Role | Contributions |
|------------|------|---------------|
| Komal Harshita | App Deployment & Full Stack | Application deployment, backend integration, Firebase setup, dashboard functionality, AI chatbot integration, end-to-end testing |
| Saie Yadav | Presentation & Documentation | PPT deck creation, architecture slides, submission documentation |
| Pooja Rana| Brand Design & UI Identity | Logo design, PPT, and README |
|team mamber 4| Video & Demo Content | YouTube demo video creation (≤3 minutes), solution walkthrough, feature explanation, final demo presentation |


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

