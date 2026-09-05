import requests 
from bs4 import BeautifulSoup
import time

def fetch_linkedin_jobs(job_title, location, page):
    
    base_url = "https://linkedin.com"
    
    params = { 
        "keywords": job_title,
        "location": location,   
        "start": page * 25
    }
    
    headers = { 
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    response = requests.get(base_url, params=params, headers=headers)

    if response.status_code != 200:
        print(f"Failed to fetch jobs from LinkedIn. Status code: {response.status_code}")
        return [] 

    soup = BeautifulSoup(response.text, 'html.parser')
    job_cards = soup.find_all('li')
    jobs = [] 

    for card in job_cards:
        try:
            title_element = card.find('h3', class_='base-search-card__title')    
            company_element = card.find('h4', class_='base-search-card__subtitle')
            location_element = card.find('span', class_='job-search-card__location')
            link_element = card.find('a', class_='base-card__full-link')

            if title_element and company_element and location_element and link_element:
                job_data = { 
                    "title": title_element.get_text(strip=True),
                    "company": company_element.get_text(strip=True),
                    "location": location_element.get_text(strip=True),
                    "link": link_element['href'].split('?')[0]
                }
                jobs.append(job_data)
        except Exception as e:
            print(f"Error occurred while processing job cards: {e}")
            
    return jobs

if __name__ == "__main__":
    print("searching for jobs...")
    found_jobs = fetch_linkedin_jobs("Automation Engineer", "Bangalore, Karnataka", page=0)

    for idx, job in enumerate(found_jobs, 1):
        print(f"{idx}. {job['title']} at {job['company']} ({job['location']})")
        print(f"   URL: {job['link']}\n")
