# Rue Pierre Brossolette - Real Estate Price Evolution Dashboard

Interactive dashboard tracking real estate prices for **Rue Pierre Brossolette, 92400 Courbevoie** using data from LePrixImmo.fr (based on DVF - Demandes de Valeurs Foncières).

## Quick Start

### 1. Start the dashboard

```bash
./bf_immo.sh start
```

Then visit: **http://localhost:8888**

The dashboard will:
- Fetch real estate price data from LePrixImmo.fr
- Create an interactive chart showing price evolution
- Display yearly price/m² statistics
- Auto-generate data.json

### 2. Advanced Usage

#### Specify year range:
```bash
./bf_immo.sh start 2020-2025    # Fetch years 2020-2025 (default)
./bf_immo.sh start 2023-2025    # Fetch recent years only
./bf_immo.sh start 2025-2030    # Future years (estimates)
```

#### Other commands:
```bash
./bf_immo.sh status             # Check if server is running
./bf_immo.sh stop               # Stop the server
```

## Files

- **`bf_immo.sh`** - Control script (start/stop/status with year range support)
- **`fetch_lepriximmo.py`** - Scraper to fetch data from LePrixImmo.fr
- **`index.html`** - Interactive dashboard with Chart.js
- **`data.json`** - Generated JSON data (auto-created)
- **`requirements.txt`** - Python dependencies

## Data Structure

The `data.json` file contains yearly price/m² data:

```json
{
  "location": {
    "street": "Rue Pierre Brossolette",
    "postal_code": "92400",
    "city": "Courbevoie",
    "department": "Hauts-de-Seine"
  },
  "yearly_statistics": [
    {
      "year": 2020,
      "price_per_m2": 4800
    },
    {
      "year": 2025,
      "price_per_m2": 5005
    }
  ],
  "data_source": "LePrixImmo.fr (based on DVF)",
  "last_updated": "2025-12-30T20:24:44"
}
```

## Dashboard Features

- 📊 Interactive line chart showing price evolution
- 📈 Year-over-year price per m² display
- 📋 Simple statistics table (Year | Price/m²)
- 🔄 Auto-refresh with custom year ranges
- 💾 Real data from French real estate registry (DVF)
- 🌐 Responsive design with gradient UI

## Data Source

Real estate data sourced from:
- **Website**: https://www.lepriximmo.fr
- **Data**: Based on DVF (Demandes de Valeurs Foncières)
- **Publisher**: French Tax Authority (DGFiP)
- **License**: Open License 2.0
- **Updates**: Annual

### Data Availability

- 2023, 2025: Real data from LePrixImmo.fr
- 2020-2024: Mix of scraped and estimated values
- Future years: Estimates based on market trends

## Installation

### Prerequisites
- Python 3.7+
- bash/zsh shell
- Internet connection

### Setup
```bash
# Clone/download the repository
cd bf_immo

# Make script executable
chmod +x bf_immo.sh

# Start the dashboard
./bf_immo.sh start
```

## How It Works

1. **Script execution** (`./bf_immo.sh start`):
   - Creates Python virtual environment
   - Installs dependencies (requests, beautifulsoup4)
   - Runs `fetch_lepriximmo.py`

2. **Data fetching** (`fetch_lepriximmo.py`):
   - Scrapes LePrixImmo.fr for each year in the range
   - Extracts price/m² from the Rue Brossolette table row
   - Uses fallback estimates for missing years
   - Generates `data.json`

3. **Dashboard** (`index.html`):
   - Loads data from `data.json`
   - Displays chart and statistics
   - Responsive layout with modern styling

## Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (to fetch data from LePrixImmo.fr)

## Troubleshooting

### "No data found" error
- Run: `./bf_immo.sh start 2020-2025` to force data fetch
- Check internet connection

### Server won't start
- Verify port 8888 is not in use: `lsof -i :8888`
- Stop existing server: `./bf_immo.sh stop`

### Delete cached data
```bash
rm data.json
./bf_immo.sh start
```

## Notes

- First run installs Python dependencies (~30 seconds)
- Data fetching takes ~5-10 seconds per year (respects site limits)
- Subsequent starts are instant if data exists
- Server logs available in `/tmp/bf_immo_server.log`

## License

This project uses publicly available data from:
- LePrixImmo.fr
- French government DVF database (Open License 2.0)
