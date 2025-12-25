# 🌍 Multi-Agent Travel Planning System

### 🤖 Powered by CrewAI

---

## 🧭 Overview

This project is a **Multi-Agent System (MAS)** designed for **automated travel planning** using **CrewAI**. It uses **four intelligent agents**, each handling a part of the travel planning process.

### 🧠 Agents:

- ✈️ **Flight Search Agent**  
  _Searches flights via the **Amadeus API**. Returns flight costs in **Euros (€)**._

- 🏨 **Hotel Search Agent**  
  _Searches hotels via **RapidAPI**. Returns hotel costs in **USD ($)**._

- 🎡 **Activity Search Agent**  
  _Recommends activities using **DuckDuckGo Search Tool**._

- 🧾 **Final Aggregation Agent**  
  _Combines all results into a **budget-friendly travel plan**._

---

## ✨ Features

- 🔍 **Flight Search** – Based on source, destination, date, and budget  
- 🛏️ **Hotel Search** – Based on location, preferences, and budget  
- 🎯 **Activity Search** – Based on destination and interests  
- 💸 **Budget Optimization** – Aggregates all data into a cost-effective plan

---

## 📦 Tech Stack

- CrewAI  
- Amadeus API  
- Booking.com via RapidAPI  
- DuckDuckGo Search Tool

---

## 🚀 Usage

1. Clone the repository  
2. Install dependencies  
3. Set your API keys in `.env`  
4. Run the app, using main.py file (uvicorn main:app --host 0.0.0.0 --port 8000 --reload)
5. Input travel preferences and get a full plan!
6. I have created react UI : You can inference working of this agent there
---

## 📝 Notes

- Hotel costs are in USD, flight costs in EUR.
- Be mindful of API quotas on RapidAPI and Amadeus.

---

