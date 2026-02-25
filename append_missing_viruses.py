import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

VIRUS_LIST_URL = "https://gd.eppo.int/photos/virus"
OUTPUT_FILE = "all_viruses_distribution.csv"

def get_soup(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return BeautifulSoup(response.content, 'html.parser')

def extract_viruses():
    soup = get_soup(VIRUS_LIST_URL)
    virus_list = []
    ul = soup.find('ul', id='listg')
    items = ul.find_all('li')
    for item in items:
        a_tag = item.find('a')
        if a_tag:
            virus_name = a_tag.get_text(strip=True)
            url_part = a_tag['href']
            parts = url_part.split('/')
            if len(parts) >= 3:
                eppo_code = parts[2]
                virus_list.append((virus_name, eppo_code))
    return virus_list

def main():
    viruses = extract_viruses()
    
    # Read existing dataset to find which ones are present
    df = pd.read_csv(OUTPUT_FILE)
    scraped_viruses = df['Virus'].unique()
    
    missing = []
    for virus_name, code in viruses:
        if virus_name not in scraped_viruses:
            missing.append(virus_name)
            
    print(f"Found {len(missing)} viruses not in the CSV.")
    
    # Append to the CSV
    with open(OUTPUT_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for virus_name in missing:
            writer.writerow([virus_name, "Not available", "Not available", "Not available", "Not available", "Not available"])
            
    print(f"Successfully appended {len(missing)} missing viruses to {OUTPUT_FILE}.")

if __name__ == "__main__":
    main()
