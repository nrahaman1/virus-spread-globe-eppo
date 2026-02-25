# Global Virus Pathogen Visualization

This project provides a comprehensive database and 3D interactive visualization tool for tracking the global spread of various plant viruses over time. 

The data is scraped directly from the [EPPO Global Database](https://gd.eppo.int/), and the frontend uses [Mapbox GL JS](https://www.mapbox.com/) to render a stunning 3D interactive globe.

🌍 **Live Dashboard:** [View the Interactive Map](https://github.com/nrahaman1)

![Visualization Screenshot](https://img.shields.io/badge/Visualization-3D_Globe-00f2fe?style=for-the-badge) ![Python](https://img.shields.io/badge/Python-Scraping-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## Features

- **Comprehensive Database**: Contains distribution, status, and first recorded years for 120+ plant viruses.
- **Geocoded Data**: All locations (Country/State levels) are geocoded with specific Latitude and Longitude coordinates.
- **Interactive 3D Globe**: Built with Mapbox GL JS (`projection: 'globe'`) with a premium dark mode aesthetic, space/atmosphere effects, and neon glowing markers.
- **Timeline Animation**: A slider UI allows users to dynamically animate the spread of a selected virus across the globe over its recorded history.
- **Auto-Rotation**: Graceful, automatic camera rotation around the Earth.

## Repository Structure

- `index.html`: The main web application file. It loads the UI, Mapbox globe, and parses the CSV data locally via PapaParse.
- `all_viruses_distribution.csv`: The complete, consolidated database generated from the EPPO website, including all geographic coordinates.
- `scrape_all_viruses.py`: The primary Python web scraper that iterates through the EPPO database to fetch the distribution tables for every recorded virus.
- `add_lat_long.py`: Python script utilizing `geopy` and the Nominatim API to geocode the raw scraped locations.
- `globe_app.html`: (Legacy) The original local version of the `index.html` file.
- `check_viruses.py` & `append_missing_viruses.py`: Internal utility scripts used to verify data completeness.

## Getting Started Locally

If you wish to run the app on your local machine rather than the live link:

1. Clone or download this repository.
2. Since the app fetches a local CSV file (`all_viruses_distribution.csv`), it must be served through a local HTTP server to avoid CORS (Cross-Origin Resource Sharing) blockages by your browser.
3. Open your terminal in the directory and run:
   ```bash
   python -m http.server 8000
   ```
4. Open your web browser and go to `http://localhost:8000/index.html`.

## Data Source

All pathogen distribution data is sourced from the [EPPO Global Database](https://gd.eppo.int/). Coordinates were derived using open-source OpenStreetMap Nominatim data.

## Technologies Used

- **Frontend**: HTML, CSS (Glassmorphism), JavaScript
- **Mapping**: Mapbox GL JS v3
- **Data Parsing**: PapaParse
- **Backend/Scraping**: Python 3 (`requests`, `beautifulsoup4`, `pandas`, `geopy`)
