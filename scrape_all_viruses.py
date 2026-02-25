import requests
from bs4 import BeautifulSoup
import csv
import time
import concurrent.futures

BASE_URL = "https://gd.eppo.int"
VIRUS_LIST_URL = "https://gd.eppo.int/photos/virus"
OUTPUT_FILE = "all_viruses_distribution.csv"

def get_soup(url):
    """Fetches a URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_viruses():
    """Extracts the list of viruses and their EPPO codes."""
    print(f"Fetching virus list from: {VIRUS_LIST_URL}")
    soup = get_soup(VIRUS_LIST_URL)
    if not soup:
        print("Failed to load virus list.")
        return []

    virus_list = []
    ul = soup.find('ul', id='listg')
    if not ul:
        print("Could not find the virus list (ul#listg).")
        return []

    items = ul.find_all('li')
    for item in items:
        a_tag = item.find('a')
        if a_tag:
            virus_name = a_tag.get_text(strip=True)
            url_part = a_tag['href']  # e.g., /taxon/SCRV00/photos
            # Extract just the code from the URL, assuming /taxon/CODE/...
            parts = url_part.split('/')
            if len(parts) >= 3:
                eppo_code = parts[2]
                virus_list.append((virus_name, eppo_code))
                
    return virus_list

def extract_first_recorded(detail_url):
    """Extracts 'First recorded in' year from the detail page."""
    soup = get_soup(detail_url)
    if not soup:
        return "Error"
    
    # Look for the specific structure: <b><u>First recorded in:</u></b> 2018
    b_tags = soup.find_all('b')
    for b in b_tags:
        u = b.find('u')
        if u and "First recorded in" in u.get_text():
            next_node = b.next_sibling
            if next_node:
                return next_node.strip()
            
    return "Not available"

def process_virus(virus_data):
    """Processes a single virus to extract its distribution."""
    virus_name, eppo_code = virus_data
    distribution_url = f"{BASE_URL}/taxon/{eppo_code}/distribution"
    print(f"Processing {virus_name}...")
    
    soup = get_soup(distribution_url)
    if not soup:
        return []

    table = soup.find('table', id='dttable')
    if not table:
        print(f"  No distribution table found for {virus_name}.")
        return []

    data = []
    tbody = table.find('tbody')
    if not tbody:
         return []
         
    rows = tbody.find_all('tr')
    
    # We delay to avoid spamming the detail pages if there are many rows
    for i, row in enumerate(rows):
        cols = row.find_all('td')
        if len(cols) < 5:
            continue
        
        continent = cols[0].get_text(strip=True)
        country = cols[1].get_text(strip=True)
        state = cols[2].get_text(strip=True)
        status = cols[3].get_text(strip=True)
        
        view_link = cols[4].find('a', href=True)
        first_recorded = "Not available"
        
        if view_link:
            relative_url = view_link['href']
            detail_url = BASE_URL + relative_url
            first_recorded = extract_first_recorded(detail_url)
            time.sleep(0.5) # Be polite when hitting detail pages
            
        data.append([virus_name, continent, country, state, status, first_recorded])

    print(f"  Finished {virus_name}: found {len(data)} records.")
    return data

def main():
    start_time = time.time()
    viruses = extract_viruses()
    print(f"Found {len(viruses)} viruses to process.")
    
    all_data = []
    headers = ["Virus", "Continent", "Country", "State", "Status", "First Recorded In"]
    
    # Using ThreadPoolExecutor to process viruses concurrently
    # Keep max_workers low to be polite to the server
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_virus = {executor.submit(process_virus, virus): virus for virus in viruses}
        
        for future in concurrent.futures.as_completed(future_to_virus):
            try:
                data = future.result()
                all_data.extend(data)
            except Exception as exc:
                virus = future_to_virus[future]
                print(f"{virus[0]} generated an exception: {exc}")

    print(f"Extraction complete. Total records: {len(all_data)}. Saving to {OUTPUT_FILE}...")
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(all_data)
        
    duration = time.time() - start_time
    print(f"Done! Took {duration:.2f} seconds.")

if __name__ == "__main__":
    main()
