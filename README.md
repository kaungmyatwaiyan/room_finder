# 🏠 Room Finder

[View Live Dashboard](https://kaungmyatwaiyan.github.io/room_finder/)

## Executive Summary

**The Problem:** Finding an affordable rental property in London with a reasonable commute to a specific workplace (such as Whitfield St) is a time-consuming manual process. It requires constantly monitoring multiple property websites and manually cross-referencing addresses with public transit maps to determine travel times.

**The Solution:** Room Finder is an automated data pipeline that aggregates and processes rental listings into a single, centralized dashboard. Operating on a daily automated schedule, the system:
1. Scans four major UK property platforms (OpenRent, Rightmove, Zoopla, OnTheMarket) for properties meeting specific budget criteria.
2. Identifies and merges duplicate listings across the different platforms.
3. Connects to live public transit data (Transport for London) to calculate exact, door-to-door commute times.
4. Generates a dynamic web dashboard where users can easily filter results by rent, commute time, walking distance, and property type.

**Business Value:** This project demonstrates end-to-end automation, data aggregation, and the ability to transform raw, scattered information into a clean, actionable user interface - all operating with a zero-cost infrastructure model.

---

## Technical Details

This project is a Python-based serverless data engineering pipeline that produces a static frontend dashboard. 

### Architecture & Data Pipeline
- **Scraping Layer:** Concurrently scrapes multiple property portals using a modular, OOP-based architecture.
- **Deduplication:** Implements an $O(N^2)$ algorithm using Haversine geographic distance (matching properties within a 50m radius) combined with price variance checks to identify and merge duplicate cross-platform listings.
- **API Rate Limiting Strategy:** The Transport for London (TfL) API imposes strict rate limits for anonymous usage. To bypass complete system lockouts (`429 Too Many Requests`), the pipeline calculates the direct geographic distance for all scraped properties, sorts them, and only queries the live TfL routing API for the top 50 closest matches. Exponential backoff with jitter is implemented for resilience.
- **Data Validation:** A standalone validation script (`validate_results.py`) acts as a quality gate, enforcing strict price ceilings, schema consistency, and verifying that deduplication rules ran successfully before generating the final dataset.
- **Serverless Automation:** Runs on GitHub Actions via a daily cron job. The CI/CD pipeline installs dependencies, runs offline unit tests and data validation, executes the scraping pipeline, and commits the updated dataset back to the repository.
- **Frontend Generation:** To avoid backend hosting costs, the Python pipeline generates a single-page HTML application and embeds the resulting JSON dataset directly into the DOM. This allows the dashboard to be served entirely statically via GitHub Pages while retaining instant, client-side filtering capabilities using Vanilla JavaScript.

### Tech Stack
- **Language:** Python 3.11+
- **Frontend:** HTML5, CSS3, Vanilla JavaScript (Zero dependencies)
- **CI/CD:** GitHub Actions
- **External APIs:** Transport for London (TfL) Unified API

---

## Local Setup

### Prerequisites
- Python 3.11 or higher
- Git

### Installation
```bash
git clone https://github.com/kaungmyatwaiyan/room_finder.git
cd room_finder
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Running the Pipeline
Run the main scraper (fetches data, handles deduplication/routing, and generates the dashboard):
```bash
python main.py
```

Run the validation script to audit data integrity (verifies schema, price limits, and deduplication logic):
```bash
python validate_results.py
```

Run the test suite:
```bash
python -m unittest tests.test_scrapers.TestScrapersOffline -v
```

---
*This code was written with the help of Antigravity 2.0.*
