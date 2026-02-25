import pandas as pd
import time
import subprocess
import sys
import os

def install_geopy():
    try:
        import geopy
    except ImportError:
        print("Installing geopy...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "geopy"])

install_geopy()

from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def main():
    csv_file = "all_viruses_distribution.csv"
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    print("Loading data...")
    df = pd.read_csv(csv_file)
    
    # Initialize geolocator
    geolocator = Nominatim(user_agent="eppo_virus_geocoder_bot_99")
    # To respect Nominatim usage policy (max 1 request per second)
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1.1, max_retries=2, error_wait_seconds=5.0)
    
    cache = {}
    
    def get_lat_lon(row):
        country = row.get("Country", "Not available")
        state = row.get("State", "Not available")
        
        if pd.isna(country) or country == "Not available":
            return
            
        country_str = str(country).strip()
        state_str = str(state).strip() if not pd.isna(state) else ""
        
        if state_str and state_str != "Not available":
            query = f"{state_str}, {country_str}"
        else:
            query = country_str
            
        if query in cache:
            return
            
        try:
            loc = geocode(query)
            if loc:
                cache[query] = (loc.latitude, loc.longitude)
                print(f"Geocoded: {query} -> {loc.latitude}, {loc.longitude}")
            elif state_str and state_str != "Not available":
                # Fallback to country only
                loc_country = geocode(country_str)
                if loc_country:
                    cache[query] = (loc_country.latitude, loc_country.longitude)
                    print(f"Fallback Geocoded: {country_str} (for {query}) -> {loc_country.latitude}, {loc_country.longitude}")
                else:
                    cache[query] = ("", "")
                    print(f"Could not geocode fallback: {country_str}")
            else:
                cache[query] = ("", "")
                print(f"Could not geocode: {query}")
                
        except Exception as e:
            print(f"Error geocoding {query}: {e}")
            cache[query] = ("", "")

    print("Extracting unique locations to minimize API requests...")
    unique_locations = df[['Country', 'State']].drop_duplicates()
    
    print(f"Found {len(unique_locations)} unique locations to process. This may take a few minutes...")
    for _, row in unique_locations.iterrows():
        get_lat_lon(row)
        
    print("Applying geocoded coordinates to main dataset...")
    def apply_cache(row):
        country = row.get("Country", "Not available")
        state = row.get("State", "Not available")
        
        if pd.isna(country) or country == "Not available":
            return pd.Series(["", ""])
            
        country_str = str(country).strip()
        state_str = str(state).strip() if not pd.isna(state) else ""
        
        if state_str and state_str != "Not available":
            query = f"{state_str}, {country_str}"
        else:
            query = country_str
            
        coords = cache.get(query, ("", ""))
        return pd.Series(coords)
        
    df[['Latitude', 'Longitude']] = df.apply(apply_cache, axis=1)
    
    # Save back to CSV
    df.to_csv(csv_file, index=False)
    print(f"\nDone! Overwritten {csv_file} with Latitude and Longitude columns.")

if __name__ == "__main__":
    main()
