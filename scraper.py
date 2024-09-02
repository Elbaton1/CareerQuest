import json
import os
import feedparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("chromedriver.exe")

driver = webdriver.Chrome(service=service, options=chrome_options)

def scrape_athabasca():
    logging.info("Scraping Athabasca University")
    jobs = []
    url = "https://athabascau.acquiretm.com/home.aspx"
    selector = "#contentWrapper > div > div > div.inner-page > div > div.inner-content-center > div > div:nth-child(8) > div > table > tbody > tr > td > div > h4 > a:nth-child(3)"
    
    page_number = 1
    
    while True:
        driver.get(url)
        logging.info(f"Fetching page {page_number} of Athabasca University")
        
        # Go to the specific page number
        if page_number > 1:
            try:
                next_page = driver.find_element(By.LINK_TEXT, str(page_number))
                next_page.click()
            except Exception as e:
                logging.warning(f"Page number {page_number} not found: {e}")
                try:
                    next_button = driver.find_element(By.LINK_TEXT, 'Next')
                    next_button.click()
                except Exception as e:
                    logging.warning(f"Next button not found: {e}")
                    break
        
        job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
        logging.info(f"Found {len(job_elements)} job elements on page {page_number}")
        for element in job_elements:
            title = element.text
            link = element.get_attribute("href")
            job = {"title": title, "school": "Athabasca University", "date": datetime.now().strftime("%Y-%m-%d"), "link": link}
            jobs.append(job)
        
        if not job_elements:
            break
        
        page_number += 1

    logging.info(f"Found {len(jobs)} jobs at Athabasca University")
    return jobs

def scrape_mtroyal():
    logging.info("Scraping Mount Royal University")
    jobs = []
    url = "https://mtroyalca.hua.hrsmart.com/hr/ats/JobSearch/search"
    selector = "#jobSearchResultsGrid_table > tbody > tr > td:nth-child(2) > a"
    
    page_number = 1
    
    while True:
        driver.get(url)
        logging.info(f"Fetching page {page_number} of Mount Royal University")
        
        # Go to the specific page number
        if page_number > 1:
            try:
                next_page = driver.find_element(By.LINK_TEXT, str(page_number))
                next_page.click()
            except Exception as e:
                logging.warning(f"Page number {page_number} not found: {e}")
                try:
                    next_button = driver.find_element(By.LINK_TEXT, 'Next')
                    next_button.click()
                except Exception as e:
                    logging.warning(f"Next button not found: {e}")
                    break
        
        job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
        logging.info(f"Found {len(job_elements)} job elements on page {page_number}")
        for element in job_elements:
            title = element.text
            link = element.get_attribute("href")
            job = {"title": title, "school": "Mount Royal University", "date": datetime.now().strftime("%Y-%m-%d"), "link": link}
            jobs.append(job)
        
        if not job_elements:
            break
        
        page_number += 1

    logging.info(f"Found {len(jobs)} jobs at Mount Royal University")
    return jobs

def scrape_memorial():
    logging.info("Scraping Memorial University")
    driver.get("https://www.mun.ca/hr/careers/external-job-postings/")
    selectors = [
        "#scope-STJ > tbody > tr > td:nth-child(2) > a",
        "#scope-MI > tbody > tr > td:nth-child(2) > a",
        "#scope-MI-IRTP > tbody > tr > td:nth-child(2) > a",
        "#scope-LI > tbody > tr.odd > td:nth-child(2) > a",
        "#scope-GC > tbody > tr:nth-child(1) > td:nth-child(2) > a",
        "#scope-GC > tbody > tr:nth-child(2) > td:nth-child(2) > a",
        "#scope-GC > tbody > tr:nth-child(3) > td:nth-child(2) > a",
        "#scope-GC > tbody > tr:nth-child(4) > td:nth-child(2) > a"
    ]
    jobs = []
    for selector in selectors:
        logging.info(f"Using selector: {selector}")
        while True:
            job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            logging.info(f"Found {len(job_elements)} job elements using selector {selector}")
            for element in job_elements:
                title = element.text
                link = element.get_attribute("href")
                job = {"title": title, "school": "Memorial University", "date": datetime.now().strftime("%Y-%m-%d"), "link": link}
                jobs.append(job)
            try:
                next_button = driver.find_element(By.LINK_TEXT, 'Next')
                next_button.click()
            except Exception as e:
                logging.warning(f"Next button not found: {e}")
                break
    logging.info(f"Found {len(jobs)} jobs at Memorial University")
    return jobs


def scrape_macewan_rss():
    logging.info("Scraping MacEwan University via RSS")
    rss_url = "https://www.macewan.ca/rss/index.php?feed=all-careers"
    feed = feedparser.parse(rss_url)
    jobs = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        date = entry.get("published", "No Date Provided")
        job = {"title": title, "school": "MacEwan University", "date": date, "link": link}
        jobs.append(job)
    logging.info(f"Found {len(jobs)} jobs at MacEwan University via RSS")
    return jobs

def scrape_concordia():
    logging.info("Scraping Concordia University of Edmonton via RSS")
    rss_url = 'https://api.startdate.ca/jobs/rss_feed?client=concordiaedmonton'
    feed = feedparser.parse(rss_url)
    jobs = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        date = entry.get("published", "No Date Provided")
        job = {"title": title, "school": "Concordia University of Edmonton", "date": date, "link": link}
        jobs.append(job)
    logging.info(f"Found {len(jobs)} jobs at Concordia University of Edmonton via RSS")
    return jobs

# Combine all scraping functions
logging.info("Starting the scraping process")
new_jobs = scrape_athabasca() + scrape_mtroyal() + scrape_memorial() + scrape_macewan_rss() + scrape_concordia()
driver.quit()

# Load existing jobs
def load_existing_jobs():
    if os.path.exists('Beans/job_listings.json'):
        with open('Beans/job_listings.json', 'r') as file:
            return json.load(file)['jobs']
    return []

logging.info("Loading existing jobs")
existing_jobs = load_existing_jobs()

current_job_links = {job['link'] for job in new_jobs}
existing_job_links = {job['link'] for job in existing_jobs}

# Determine new and removed jobs based on the link attribute
added_jobs = [job for job in new_jobs if job['link'] not in existing_job_links]
removed_jobs = [job for job in existing_jobs if job['link'] not in current_job_links]

logging.info(f"Added jobs: {len(added_jobs)}")
logging.info(f"Removed jobs: {len(removed_jobs)}")

# Save the new job listings
data = {"jobs": new_jobs, "last_updated": datetime.now().isoformat()}
with open("Beans/job_listings.json", "w") as file:
    json.dump(data, file, indent=4)
logging.info("New job listings saved")

# Log scraping details
def log_scraping_details(added_jobs, removed_jobs):
    log_file = 'Beans/scraping_log.json'
    log_data = []
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as file:
                log_data = json.load(file)
                if not isinstance(log_data, list):
                    log_data = []
        except json.JSONDecodeError:
            log_data = []

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "new_jobs_count": len(added_jobs),
        "removed_jobs_count": len(removed_jobs),
        "new_jobs": added_jobs,
        "removed_jobs": removed_jobs
    }

    log_data.append(log_entry)

    with open(log_file, 'w') as file:
        json.dump(log_data, file, indent=4)
    logging.info("Scraping details logged")

log_scraping_details(added_jobs, removed_jobs)
logging.info("Scraper finished")
