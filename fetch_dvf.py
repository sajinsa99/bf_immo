#!/usr/bin/env python3
"""
Fetch DVF (Demandes de Valeurs Foncières) data for Rue Brossolette, 92400 Courbevoie
and calculate price per square meter for years 2020-2025.

Note: This script downloads ~350MB of government data. First run may take 5-10 minutes.
"""

import os
import json
import zipfile
import io
import requests
import csv
from typing import Dict, List
from datetime import datetime, timedelta
import random

# DVF dataset URLs from data.gouv.fr
DVF_URLS = {
    "2020_H2": "https://www.data.gouv.fr/api/1/datasets/r/8d771135-57c8-480f-a853-3d1d00ea0b69",
    "2021": "https://www.data.gouv.fr/api/1/datasets/r/e117fe7d-f7fb-4c52-8089-231e755d19d3",
    "2022": "https://www.data.gouv.fr/api/1/datasets/r/8c8abe23-2a82-4b95-8174-1c1e0734c921",
    "2023": "https://www.data.gouv.fr/api/1/datasets/r/cc8a50e4-c8d1-4ac2-8de2-c1e4b3c44c86",
    "2024": "https://www.data.gouv.fr/api/1/datasets/r/af812b0e-a898-4226-8cc8-5a570b257326",
    "2025_H1": "https://www.data.gouv.fr/api/1/datasets/r/4d741143-8331-4b59-95c2-3b24a7bdbe3c",
}

def download_dvf_file(url: str, year: str) -> List[Dict]:
    """Download and extract DVF ZIP file, return as list of dicts."""
    print(f"Downloading DVF data for {year}... (this may take a few minutes)")
    try:
        response = requests.get(url, timeout=300, stream=True)
        response.raise_for_status()
        
        # Extract ZIP file
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            # Find the .txt file in the ZIP
            file_list = zip_ref.namelist()
            txt_file = [f for f in file_list if f.endswith('.txt')][0]
            
            # Read the file with pipe delimiter
            with zip_ref.open(txt_file) as f:
                # Decode and parse CSV with pipe delimiter
                text = f.read().decode('utf-8', errors='ignore')
                lines = text.splitlines()
                reader = csv.DictReader(lines, delimiter='|')
                
                # Process rows as we read them to save memory
                result = []
                for i, row in enumerate(reader):
                    result.append(row)
                    if (i + 1) % 500000 == 0:
                        print(f"  - Processed {i + 1} rows...")
                
                print(f"  - Read {len(result)} total rows")
                return result
                
    except requests.exceptions.RequestException as e:
        print(f"Network error downloading {year}: {e}")
        print(f"Please try again, or visit https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres")
        return []
    except Exception as e:
        print(f"Error processing {year}: {e}")
        return []

def process_transactions(rows: List[Dict], year: str) -> List[Dict]:
    """Filter and process transactions for Rue Brossolette, 92400."""
    results = []
    
    for row in rows:
        try:
            # Filter for postal code 92400 and street containing "BROSSOLETTE"
            postal_code = row.get('code_postal', '').strip()
            street = row.get('adresse_nom_voie', '').upper() if row.get('adresse_nom_voie') else ''
            
            if postal_code != '92400' or 'BROSSOLETTE' not in street:
                continue
            
            # Get transaction details
            valeur_str = row.get('valeur_fonciere', '').strip()
            surface_str = row.get('surface_reelle_bati', '').strip()
            
            if not valeur_str or not surface_str:
                continue
            
            try:
                valeur = float(valeur_str.replace(',', '.'))
                surface = float(surface_str.replace(',', '.'))
            except ValueError:
                continue
            
            # Calculate price per m²
            if surface > 0:
                price_per_m2 = valeur / surface
                
                results.append({
                    "year": year,
                    "date": str(row.get('date_mutation', ''))[:10] if row.get('date_mutation') else None,
                    "address": f"{row.get('adresse_numero', '')} {row.get('adresse_nom_voie', '')}, {postal_code}",
                    "price": int(valeur),
                    "surface_m2": int(surface),
                    "price_per_m2": round(price_per_m2, 2),
                    "property_type": str(row.get('type_local', '')) if row.get('type_local') else "Unknown"
                })
        except Exception:
            continue
    
    return results

def generate_sample_data() -> Dict:
    """Generate realistic sample data for demo purposes."""
    # Base prices that increase over time (realistic market trend)
    base_prices = {
        "2020": {"avg": 5200, "variance": 800},
        "2021": {"avg": 5500, "variance": 850},
        "2022": {"avg": 6100, "variance": 900},
        "2023": {"avg": 6400, "variance": 950},
        "2024": {"avg": 6800, "variance": 1000},
        "2025": {"avg": 7100, "variance": 1100},
    }
    
    yearly_stats = []
    all_transactions = []
    
    for year_str, prices_cfg in base_prices.items():
        year = int(year_str)
        num_transactions = random.randint(3, 8)  # 3-8 transactions per year
        
        year_transactions = []
        for i in range(num_transactions):
            # Generate realistic price variations
            noise = random.gauss(0, prices_cfg["variance"] / 3)
            price_per_m2 = prices_cfg["avg"] + noise
            
            # Realistic property sizes (50-150 m²)
            surface = random.randint(50, 150)
            price = int(price_per_m2 * surface)
            
            # Random date within the year
            date = datetime(year, 1, 1) + timedelta(days=random.randint(0, 365))
            
            transaction = {
                "year": year_str,
                "date": date.strftime("%Y-%m-%d"),
                "address": f"{12 + i} Rue Brossolette, 92400",
                "price": price,
                "surface_m2": surface,
                "price_per_m2": round(price_per_m2, 2),
                "property_type": random.choice(["Apartment", "Studio", "2-room"])
            }
            year_transactions.append(transaction)
            all_transactions.append(transaction)
        
        # Calculate yearly statistics
        prices = [tx["price_per_m2"] for tx in year_transactions]
        yearly_stats.append({
            "year": year,
            "avg_price_per_m2": round(sum(prices) / len(prices), 2),
            "min_price_per_m2": round(min(prices), 2),
            "max_price_per_m2": round(max(prices), 2),
            "transaction_count": len(prices)
        })
    
    return {
        "location": {
            "street": "Rue Brossolette",
            "postal_code": "92400",
            "city": "Courbevoie",
            "department": "Hauts-de-Seine"
        },
        "all_transactions": all_transactions,
        "yearly_statistics": yearly_stats,
        "total_transactions": len(all_transactions),
        "data_source": "Sample data (DVF real data available at https://www.data.gouv.fr)"
    }

def main():
    """Main function to fetch and process DVF data."""
    print("=" * 60)
    print("Fetching DVF data for Rue Brossolette, 92400 Courbevoie")
    print("=" * 60)
    
    all_transactions = []
    downloaded_any = False
    
    # Try to download real data
    for year, url in DVF_URLS.items():
        rows = download_dvf_file(url, year)
        if rows:
            year_clean = year.split('_')[0]  # Extract just the year
            transactions = process_transactions(rows, year_clean)
            all_transactions.extend(transactions)
            print(f"  ✓ Found {len(transactions)} transactions in {year}")
            downloaded_any = True
        else:
            print(f"  ⚠ Skipping {year} (network issue or no data)")
    
    # If no real data was downloaded, use sample data for demo
    if not downloaded_any:
        print("\n⚠ Could not download DVF data. Using realistic sample data for demo.")
        print("To use real data, run this script again or visit:")
        print("https://www.data.gouv.fr/datasets/demandes-de-valeurs-foncieres")
        output = generate_sample_data()
    else:
        # Organize by year for dashboard
        by_year = {}
        for tx in all_transactions:
            year = tx['year']
            if year not in by_year:
                by_year[year] = []
            by_year[year].append(tx)
        
        # Calculate yearly statistics
        yearly_stats = []
        for year in sorted(by_year.keys()):
            prices = [tx['price_per_m2'] for tx in by_year[year] if tx['price_per_m2']]
            if prices:
                yearly_stats.append({
                    "year": int(year),
                    "avg_price_per_m2": round(sum(prices) / len(prices), 2),
                    "min_price_per_m2": round(min(prices), 2),
                    "max_price_per_m2": round(max(prices), 2),
                    "transaction_count": len(prices)
                })
        
        output = {
            "location": {
                "street": "Rue Brossolette",
                "postal_code": "92400",
                "city": "Courbevoie",
                "department": "Hauts-de-Seine"
            },
            "all_transactions": all_transactions,
            "yearly_statistics": yearly_stats,
            "total_transactions": len(all_transactions),
            "data_source": "DVF (data.gouv.fr)"
        }
    
    # Save to JSON
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 60)
    print(f"✓ Data saved to data.json")
    print(f"✓ Total transactions: {output['total_transactions']}")
    print(f"✓ Data source: {output.get('data_source', 'Unknown')}")
    print("=" * 60)
    
    # Print summary
    print("\nYearly Summary (Average Price/m²):")
    print("-" * 40)
    for stat in output['yearly_statistics']:
        print(f"{stat['year']}: €{stat['avg_price_per_m2']:>8.2f}/m² ({stat['transaction_count']} tx)")

if __name__ == "__main__":
    main()
