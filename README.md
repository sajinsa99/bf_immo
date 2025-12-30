# Rue Brossolette Price Evolution Dashboard

Real estate price tracking for **Rue Brossolette, 92400 Courbevoie** (2020-2025).

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Fetch data from DVF
```bash
python fetch_dvf.py
```

This script:
- Downloads official DVF (Demandes de Valeurs Foncières) data from data.gouv.fr
- Filters for Rue Brossolette, postal code 92400
- Calculates price per m² for each transaction
- Stores results in `data.json`

### 3. View the dashboard
Open `index.html` in your web browser:
```bash
open index.html
```

Or serve it locally:
```bash
python -m http.server 8000
# Then visit http://localhost:8000
```

## Files

- **`fetch_dvf.py`** - Python script to fetch and process DVF data
- **`index.html`** - Interactive dashboard with Chart.js
- **`data.json`** - Generated JSON database (created after running fetch_dvf.py)
- **`requirements.txt`** - Python dependencies

## Data Structure

The `data.json` file contains:

```json
{
  "location": {
    "street": "Rue Brossolette",
    "postal_code": "92400",
    "city": "Courbevoie",
    "department": "Hauts-de-Seine"
  },
  "yearly_statistics": [
    {
      "year": 2020,
      "avg_price_per_m2": 5500.00,
      "min_price_per_m2": 5000.00,
      "max_price_per_m2": 6000.00,
      "transaction_count": 5
    }
  ],
  "all_transactions": [...]
}
```

## Dashboard Features

- 📊 Line chart showing price evolution from 2020-2025
- 📈 Average, min, and max price/m² per year
- 📋 Detailed statistics table
- 💾 Real transaction data from French tax authority

## Data Source

Data provided by the French government's open data portal:
- **Portal**: https://www.data.gouv.fr
- **Dataset**: Demandes de Valeurs Foncières (DVF)
- **License**: Open License 2.0
- **Last Update**: October 19, 2025

## Requirements

- Python 3.7+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection (first run to download data)

## Notes

- First run takes a few minutes (downloading ~350MB of data)
- Data is stored locally in `data.json`
- Subsequent views load instantly
- To refresh data, delete `data.json` and run the script again