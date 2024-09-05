import json
import os
import feedparser
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import logging
import time
import re
from selenium.webdriver.common.by import By
import pandas as pd
from selenium.common.exceptions import TimeoutException



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')

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
            job = {
                "title": title,
                "school": "Athabasca University",
                "date": "No date provided",  # Replaced dynamic date with static "No date provided"
                "link": link
            }
            jobs.append(job)
        
        if not job_elements:
            break
        
        page_number += 1

    logging.info(f"Found {len(jobs)} jobs at Athabasca University")
    return jobs


def scrape_ualberta():
    logging.info("Scraping University of Alberta")
    jobs = []
    url = "https://apps.ualberta.ca/careers/list/all"
    
    driver.get(url)
    
    # Job postings selector
    job_selector = "a.fs-4.stretched-link"
    
    # Extract job postings and store the links
    job_elements = driver.find_elements(By.CSS_SELECTOR, job_selector)
    job_links = []
    
    for element in job_elements:
        relative_link = element.get_attribute("href")
        # Check if the link is relative and prepend the base URL if necessary
        if not relative_link.startswith("http"):
            link = f"https://apps.ualberta.ca{relative_link}"
        else:
            link = relative_link
        job_links.append(link)
    
    logging.info(f"Found {len(job_links)} job links on the page")
    
    for link in job_links:
        try:
            # Navigate to the job posting page
            driver.get(link)
            
            # Extract the title
            try:
                title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
            except Exception as e:
                logging.warning(f"Could not extract job title: {e}")
                title = "Title not provided"
            
            # Extract the posted date (e.g., "Posted date: December 5, 2023")
            try:
                posted_date_element = driver.find_element(By.CSS_SELECTOR, "span[aria-labelledby^='posted-date-label']")
                posted_date = posted_date_element.text.strip()
            except Exception as e:
                logging.warning(f"Could not extract posted date: {e}")
                posted_date = "Date not provided"
            
            job = {
                "title": title, 
                "school": "University of Alberta", 
                "date": posted_date, 
                "link": link
            }
            jobs.append(job)

            # Go back to the main job listings page
            driver.get(url)
            
        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of Alberta")
    return jobs


def scrape_ucalgary():
    logging.info("Scraping University of Calgary")
    jobs = []
    url = "https://careers.ucalgary.ca/search/jobs"
    
    driver.get(url)
    
    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.jobs-section__item")))

    job_elements = driver.find_elements(By.CSS_SELECTOR, "div.jobs-section__item")

    logging.info(f"Found {len(job_elements)} job elements on the page")
    
    for i, element in enumerate(job_elements, start=1):
        try:
            job_link_element = element.find_element(By.CSS_SELECTOR, "h2.heading-3 a")
            title = job_link_element.text
            link = job_link_element.get_attribute("href")

            # Extract the date
            date_element = element.find_element(By.CSS_SELECTOR, "p")
            date_text = date_element.text.split("Updated")[-1].strip()

            job = {"title": title, "school": "University of Calgary", "date": date_text, "link": link}
            jobs.append(job)

        except Exception as e:
            logging.warning(f"Could not extract job details for job {i}: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of Calgary")
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
            job = {
                "title": title,
                "school": "Mount Royal University",
                "date": "No date provided",  # Replaced dynamic date with static "No date provided"
                "link": link
            }
            jobs.append(job)
        
        if not job_elements:
            break
        
        page_number += 1

    logging.info(f"Found {len(jobs)} jobs at Mount Royal University")
    return jobs


def scrape_kwantlen():
    logging.info("Scraping Kwantlen Polytechnic University")
    jobs = []
    url = "https://tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=JT63GS&cws=37"
    
    driver.get(url)
    
    # Scroll down to load all job postings
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Wait for the page to load more content
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Locate all job postings after scrolling
    job_items = driver.find_elements(By.CSS_SELECTOR, "div.oracletaleocwsv2-accordion-head-info h4.oracletaleocwsv2-head-title")
    logging.info(f"Found {len(job_items)} job items on the page")

    for job_item in job_items:
        try:
            # Extract the job title
            title = job_item.text
            
            # The unique part of the job URL is the rid, which seems to be part of a link
            parent_element = job_item.find_element(By.XPATH, "..")
            link_element = parent_element.find_element(By.XPATH, ".//a[contains(@href, 'viewRequisition')]")
            link_partial = link_element.get_attribute("href")
            
            # Correctly format the full link
            if link_partial.startswith("https://"):
                link_full = link_partial
            else:
                link_full = f"https://tre.tbe.taleo.net{link_partial}"

            # Since no dates are provided on this page, we'll log a placeholder
            posting_date = "Date not provided"

            # Store the job data
            job = {
                "title": title,
                "school": "Kwantlen Polytechnic University",
                "date": posting_date,
                "link": link_full
            }
            jobs.append(job)
            logging.info(f"Added job: {title}, no date provided")

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at Kwantlen Polytechnic University")
    return jobs



def scrape_capilano():
    logging.info("Scraping Capilano University")
    jobs = []
    url = "https://jobs-capilanou.peopleadmin.com/postings/search"
    
    driver.get(url)
    
    # Locate all job postings
    job_items = driver.find_elements(By.CSS_SELECTOR, "div.job-item.job-item-posting")
    logging.info(f"Found {len(job_items)} job items on the page")

    for index, job_item in enumerate(job_items):
        try:
            # Extract the job title and link
            title_element = job_item.find_element(By.CSS_SELECTOR, "div.job-title a")
            title = title_element.text
            link = title_element.get_attribute("href")

            # Visit the job page to get the open date
            driver.get(link)
            try:
                # Check for 'Job Open Date'
                date_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'Job Open Date')]/following-sibling::td"))
                )
                open_date = date_element.text.strip()
            except:
                try:
                    # Check for 'Post Date' if 'Job Open Date' is not found
                    date_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//th[contains(text(),'Post Date')]/following-sibling::td"))
                    )
                    open_date = date_element.text.strip()
                except Exception as e:
                    open_date = "Date not provided"
                    logging.warning(f"Could not extract date for job {title}: {e}")

            # Store the job data
            job = {
                "title": title,
                "school": "Capilano University",
                "date": open_date,
                "link": link
            }
            jobs.append(job)
            logging.info(f"Added job: {title}, date {open_date}")

            # Go back to the listing page
            driver.back()

            # Re-find the job items since the page was refreshed
            job_items = driver.find_elements(By.CSS_SELECTOR, "div.job-item.job-item-posting")

        except Exception as e:
            logging.warning(f"Could not extract job details for job {index + 1}: {e}")

    logging.info(f"Found {len(jobs)} jobs at Capilano University")
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
                job = {
                    "title": title,
                    "school": "Memorial University",
                    "date": "No date provided",  # Replaced date with "No date provided"
                    "link": link
                }
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

def scrape_sfu():
    logging.info("Scraping Simon Fraser University")
    jobs = []
    url = "https://tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=SIMOFRAS&cws=37"
    
    driver = webdriver.Chrome()
    driver.get(url)
    
    # Scroll down to load all jobs
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # wait for the page to load
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Locate all job postings
    job_items = driver.find_elements(By.CSS_SELECTOR, "div.oracletaleocwsv2-accordion-head-info")
    logging.info(f"Found {len(job_items)} job items on the page")

    for job_item in job_items:
        try:
            # Extract the job title and link
            title_element = job_item.find_element(By.CSS_SELECTOR, "a.viewJobLink")
            title = title_element.text
            link = title_element.get_attribute("href")
            
            # Correct the link if necessary
            if "https://tre.tbe.taleo.nethttps" in link:
                link = link.replace("https://tre.tbe.taleo.nethttps", "https://tre.tbe.taleo.net")

            # Store the job data
            job = {
                "title": title,
                "school": "Simon Fraser University",
                "date": "Date not provided",  # No date found in the sample
                "link": link
            }
            jobs.append(job)
            logging.info(f"Added job: {title}")

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at Simon Fraser University")
    driver.quit()
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

def scrape_royal_roads():
    logging.info("Scraping Royal Roads University")
    jobs = []
    url = "https://royalroads.mua.hrdepartment.com/hr/ats/JobSearch/viewAll/jobSearchPaginationExternal_pageSize:100/jobSearchPaginationExternal_page:1"
    
    driver.get(url)
    
    # Wait for the table containing job postings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.datatable.table.table-fixed-header"))
    )
    
    # Locate all job postings
    job_items = driver.find_elements(By.CSS_SELECTOR, "table.datatable.table.table-fixed-header tbody tr")
    logging.info(f"Found {len(job_items)} job items on the page")

    for job_item in job_items:
        try:
            # Extract the job title, date, and link
            title_element = job_item.find_element(By.CSS_SELECTOR, "a")
            title = title_element.text
            link = title_element.get_attribute("href")

            date_element = job_item.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
            posting_date = date_element.text.strip()

            # Store the job data
            job = {
                "title": title,
                "school": "Royal Roads University",
                "date": posting_date,
                "link": link
            }
            jobs.append(job)
            logging.info(f"Added job: {title}, posted on {posting_date}")

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at Royal Roads University")
    return jobs

def scrape_ubc_jobs():
    logging.info(f"Scraping UBC Careers Pages")
    jobs = []

    # URLs for the different UBC job pages
    urls = {
        "UBC Student Jobs": "https://ubc.wd10.myworkdayjobs.com/en-US/ubcstudentjob",
        "UBC Staff Jobs": "https://ubc.wd10.myworkdayjobs.com/en-US/ubcstaffjobs",
        "UBC Faculty Jobs": "https://ubc.wd10.myworkdayjobs.com/en-US/ubcfacultyjobs"
    }

    # Base URL for constructing the full job link
    base_url = "https://ubc.wd10.myworkdayjobs.com"

    for school_name, url in urls.items():
        driver.get(url)

        while True:
            # Wait for job listings to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-automation-id='jobTitle']"))
            )

            # Locate all job postings
            job_items = driver.find_elements(By.CSS_SELECTOR, "li[class*='css-1q2dra3']")

            logging.info(f"Found {len(job_items)} job items on this page")

            for index, job_item in enumerate(job_items, start=1):
                try:
                    # Extract job title
                    title_element = job_item.find_element(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
                    title = title_element.text

                    # Extract the relative link and create the full URL
                    relative_link = title_element.get_attribute("href")
                    full_link = base_url + relative_link

                    # Extract the posting date using the provided XPath
                    date_xpath = f"/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[{index}]/div[3]/div/div/dl/dd"
                    date_element = driver.find_element(By.XPATH, date_xpath)
                    posting_date = date_element.text.strip()

                    # Store the job data
                    job = {
                        "school": "University of British Columbia (UBC)",
                        "title": title,
                        "date": posting_date,
                        "link": full_link,
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}, posted on {posting_date}, school: {school_name}, link: {full_link}")

                except Exception as e:
                    logging.warning(f"Could not extract job details: {e}")

            # Check if there is a "Next" button and click it using the specific selector
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div.css-uvpbop > section > div.css-3z7fsk > nav > div > button:nth-child(3)")
                
                if next_button.is_enabled():
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    driver.execute_script("arguments[0].click();", next_button)
                    logging.info("Clicked the 'Next' button and waiting for the next page to load...")
                    
                    # Wait for the page to load by waiting for the job listings to refresh
                    WebDriverWait(driver, 10).until(
                        EC.staleness_of(job_items[0])
                    )
                    time.sleep(2)  # Add a small delay to ensure the page loads fully
                else:
                    logging.info("Next button is disabled or not found. Ending pagination.")
                    break  # Exit loop if there are no more pages
            except Exception as e:
                logging.info("No 'Next' button found on this page. Ending pagination.")
                break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs


def scrape_unbc_jobs():
    logging.info("Scraping University of Northern British Columbia Careers Pages")
    jobs = []

    # URLs for the different UNBC job pages
    urls = {
        "Faculty Jobs": "https://www.unbc.ca/career-opportunities/current-unbc-faculty-job-postings",
        "Staff Jobs": "https://www.unbc.ca/career-opportunities/current-unbc-staff-job-postings"
    }

    driver = webdriver.Chrome()

    for job_type, url in urls.items():
        driver.get(url)

        # Wait for the job listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "article"))
        )

        # Locate all job postings
        job_items = driver.find_elements(By.CSS_SELECTOR, "article")

        logging.info(f"Found {len(job_items)} job items on the {job_type} page")

        for job_item in job_items:
            try:
                # Extract the job title and link
                title_element = job_item.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text
                link = title_element.get_attribute("href")

                # Extract the posting date
                posting_date_element = job_item.find_element(By.CSS_SELECTOR, "div.field--name-field-date-range time")
                posting_date = posting_date_element.text.strip()

                # Store the job data
                job = {
                    "school": "University of Northern British Columbia",
                    "title": title,
                    "date": posting_date,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Added job: {title}, posted on {posting_date}")

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Total jobs found: {len(jobs)}")
    driver.quit()
    return jobs

def scrape_ufv_jobs():
    logging.info("Scraping University of the Fraser Valley")
    jobs = []
    url = "https://ufv.njoyn.com/CL3/xweb/xweb.asp?tbtoken=Z1FaSh9YDVB6E3JyMSElFE86dRVQaVVecCdMIV9%2FDnlbLUUfUTYecWF2AkUYGhBUSHRgF3U%3D&chk=ZVpaShM%3D&page=joblisting&CLID=56144"

    driver.get(url)

    try:
        # Explicitly wait for the job title elements to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "//h2[contains(@class, 'ui-accordion-header')]"))
        )

        job_elements = driver.find_elements(By.XPATH, "//h2[contains(@class, 'ui-accordion-header')]")
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for index in range(len(job_elements)):
            try:
                # Re-locate job elements since the DOM might change after each interaction
                job_elements = driver.find_elements(By.XPATH, "//h2[contains(@class, 'ui-accordion-header')]")
                job_element = job_elements[index]

                # Get the link to the job details page
                link_element = job_element.find_element(By.XPATH, "following-sibling::div[1]/div[3]/a")
                job_link = link_element.get_attribute("href")

                # Navigate to the job details page
                driver.get(job_link)

                # Wait for the job details to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div[2]/h1"))
                )

                # Extract job title
                title_element = driver.find_elements(By.XPATH, "/html/body/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div[2]/h1")
                if title_element:
                    title = title_element[0].text.strip()
                else:
                    logging.warning(f"Title element not found for element {index}")
                    continue

                # Extract job date
                date_element = driver.find_elements(By.XPATH, "/html/body/div[3]/div/div[2]/div/div[2]/div/form/div[1]/div[2]/span[2]/strong")
                if date_element:
                    date_text = date_element[0].text.strip()
                else:
                    logging.warning(f"Date element not found for element {index}")
                    date_text = "Date not available"

                # Store the job information
                job = {"title": title, "school": "University of the Fraser Valley", "date": date_text, "link": job_link}
                jobs.append(job)

                # Navigate back to the job listing page
                driver.back()

                # Wait for the job listing to reload
                WebDriverWait(driver, 20).until(
                    EC.presence_of_all_elements_located((By.XPATH, "//h2[contains(@class, 'ui-accordion-header')]"))
                )

            except Exception as e:
                logging.warning(f"Could not extract job details for element {index}: {e}")

    except Exception as e:
        logging.error(f"Error while scraping UFV: {e}")

    logging.info(f"Found {len(jobs)} jobs at the University of the Fraser Valley")
    return jobs

def scrape_uvic():
    logging.info("Scraping University of Victoria")
    jobs = []
    url = "https://www.uvic.ca/ecs/ece/faculty-and-staff/home/job-postings/index.php"

    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Explicitly wait for the job elements to be present
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.XPATH, "/html/body/div[1]/div[4]/div[1]/div[1]/div[2]/div[2]/ul/li/a"))
        )

        job_elements = driver.find_elements(By.XPATH, "/html/body/div[1]/div[4]/div[1]/div[1]/div[2]/div[2]/ul/li/a")
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for element in job_elements:
            try:
                # Extract the job title directly from the element's text
                title = element.get_attribute("textContent").strip()

                # Get the link to the job details
                link = element.get_attribute("href")
                
                job = {"title": title, "school": "University of Victoria", "link": link}
                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"Error while scraping UVic: {e}")

    finally:
        driver.quit()

    logging.info(f"Found {len(jobs)} jobs at the University of Victoria")
    return jobs

def scrape_vancouver_island_university():
    logging.info("Scraping Vancouver Island University")
    jobs = []
    url = "https://careers.viu.ca/vacancies.html#filter=p_web_site_id%3D100017%26p_published_to%3DWWW%26p_language%3DDEFAULT%26p_direct%3DY%26p_format%3DMOBILE%26p_include_exclude_from_list%3DN%26p_search%3D"

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    try:
        # Wait until job cards are present
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "jobCard"))
        )

        # Find all job cards
        job_cards = driver.find_elements(By.CLASS_NAME, "jobCard")
        logging.info(f"Found {len(job_cards)} job elements on the page")

        for i in range(len(job_cards)):
            try:
                # Re-find job cards to avoid stale element references after each iteration
                job_cards = driver.find_elements(By.CLASS_NAME, "jobCard")
                job_card = job_cards[i]

                # Extract job link
                link_element = job_card.find_element(By.CSS_SELECTOR, "h2 a")
                job_link = link_element.get_attribute("href")

                # Navigate to the job detail page
                driver.get(job_link)

                # Wait for the job title and date to load
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div/div[2]/div[6]/section/div/div/div/div/div/div/div[1]/div/div/div/h1"))
                )

                # Extract job title
                title_element = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[6]/section/div/div/div/div/div/div/div[1]/div/div/div/h1")
                title = title_element.text.strip()

                # Extract posted date
                date_element = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[2]/div[6]/section/div/div/div/div/div/div/div[2]/div/div/div/div/div/div/div/div/div[1]/div[2]/div[17]/div[2]")
                date_posted = date_element.text.strip()

                job = {"title": title, "school": "Vancouver Island University", "link": job_link, "date_posted": date_posted}
                jobs.append(job)

                # Navigate back to the job listing page
                driver.back()

            except Exception as e:
                logging.warning(f"Could not extract job details for job card {i}: {e}")
                # Re-navigate back to listing page in case of failure
                driver.back()

    except Exception as e:
        logging.error(f"Error while scraping Vancouver Island University: {e}")

    finally:
        driver.quit()

    logging.info(f"Found {len(jobs)} jobs at Vancouver Island University")
    return jobs

import logging
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def scrape_manitoba():
    logging.info("Scraping University of Manitoba")
    jobs = []
    url = "https://viprecprod.ad.umanitoba.ca/default"
    
    driver.get(url)
    
    page_number = 1
    
    while True:
        try:
            # Ensure page is fully loaded
            WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.XPATH, "//tr[contains(@class, 'gonly')]"))
            )
            
            # Extract job rows
            job_elements = driver.find_elements(By.XPATH, "//tr[contains(@class, 'gonly')]")
            logging.info(f"Found {len(job_elements)} job elements on page {page_number}")
            
            for job_element in job_elements:
                try:
                    # Extract job title
                    title_element = job_element.find_element(By.XPATH, ".//span[contains(@class, 'txt-wrap')]")
                    title = title_element.text.strip()
                    
                    # Extract date
                    date_element = job_element.find_element(By.XPATH, ".//td[3]//input")
                    date_posted = date_element.get_attribute("value").strip()
                    
                    # Create a pseudo-link using the job title
                    job_link = f"{url}#job{title.replace(' ', '_')}"
                    
                    job = {
                        "title": title,
                        "school": "University of Manitoba",
                        "date": date_posted,
                        "link": job_link,
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}, posted on {date_posted}")

                except Exception as e:
                    logging.warning(f"Could not extract job details: {e}")

            # Scroll to the bottom to ensure all elements are visible
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Allow time for any UI changes
            
            try:
                next_button = driver.find_element(By.XPATH, "//img[contains(@id, 'bdr_29') and not(@disabled)]")
                if next_button.is_displayed() and next_button.is_enabled():
                    logging.info(f"Found 'Next' button on page {page_number}. Attempting to click...")

                    # Scroll the element into view and click using JavaScript
                    driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                    driver.execute_script("arguments[0].click();", next_button)
                    
                    # Wait for the new page to load by waiting for the elements to go stale
                    WebDriverWait(driver, 30).until(
                        EC.staleness_of(job_elements[0])
                    )
                    time.sleep(3)  # Small delay to ensure the next page loads completely

                    page_number += 1
                else:
                    logging.info("Next button is not visible or not enabled. Ending pagination.")
                    break

            except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
                logging.info(f"No 'Next' button found or pagination finished. Ending scraping. Exception: {e}")
                break

        except TimeoutException:
            logging.error("Timeout waiting for job elements. Check XPath or increase wait time.")
            break
        except Exception as e:
            logging.error(f"An error occurred during scraping: {e}")
            break
    
    logging.info(f"Found {len(jobs)} jobs at University of Manitoba")
    return jobs




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException, WebDriverException
import logging
import time

def scrape_brandon():
    logging.info("Scraping Brandon University")
    jobs = []
    url = "https://www.brandonu.ca/jobs/"
    
    driver.get(url)
    
    try:
        # List of base XPaths to locate each section
        base_xpaths = [
            "/html/body/div[2]/div[1]/div/ul[1]/li",
            "/html/body/div[2]/div[1]/div/ul[2]/li",
            "/html/body/div[2]/div[1]/div/ul[3]/li",
            "/html/body/div[2]/div[1]/div/ul[4]/li",
            "/html/body/div[2]/div[1]/div/ul[5]/li"
        ]
        
        for base_xpath in base_xpaths:
            try:
                # Wait for the elements to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_all_elements_located((By.XPATH, base_xpath))
                )
                
                # Extract all job links within the current section
                job_links = driver.find_elements(By.XPATH, f"{base_xpath}/a")
                logging.info(f"Found {len(job_links)} job elements for xpath {base_xpath}")
                
                for job_link in job_links:
                    title = job_link.text.strip()
                    link = job_link.get_attribute("href")
                    
                    job = {
                        "title": title,
                        "link": link,
                        "school": "Brandon University",
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}, link: {link}")
            except Exception as e:
                logging.warning(f"Could not extract job details for xpath {base_xpath}: {e}")

    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    
    logging.info(f"Found {len(jobs)} jobs at Brandon University")
    return jobs

def scrape_cmu():
    logging.info("Scraping Canadian Mennonite University")
    jobs = []
    url = "https://www.cmu.ca/about/employment"

    driver.get(url)

    try:
        # List of XPaths to locate each job title and link
        base_xpath = "//div[@class='hr']/preceding-sibling::h3/a"

        # Wait for the job elements to be present
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, base_xpath))
        )

        # Extract all job links within the current section
        job_links = driver.find_elements(By.XPATH, base_xpath)
        logging.info(f"Found {len(job_links)} job elements on the page")
        
        for job_link in job_links:
            title = job_link.text.strip()
            link = job_link.get_attribute("href")
            if not link.startswith("http"):
                link = "https://www.cmu.ca" + link  # Ensure the full URL is formed

            job = {
                "title": title,
                "link": link,
                "school": "Canadian Mennonite University",
            }
            jobs.append(job)
            logging.info(f"Added job: {title}, link: {link}")

    except Exception as e:
        logging.error(f"An error occurred during scraping: {e}")
    
    logging.info(f"Found {len(jobs)} jobs at Canadian Mennonite University")
    return jobs

def scrape_stpauls():
    logging.info("Scraping St. Paul's College")
    jobs = []
    url = "https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=e0deecb0-63b7-464a-a5d7-36704316a883&ccId=9200974135815_2&lang=en_CA"
    
    driver.get(url)
    
    # Wait for job elements to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".current-openings-list > div"))
    )

    job_elements = driver.find_elements(By.CSS_SELECTOR, ".current-openings-item")
    logging.info(f"Found {len(job_elements)} job elements on the page")

    for index, element in enumerate(job_elements):
        try:
            # Re-locate elements to avoid stale element reference errors
            job_elements = driver.find_elements(By.CSS_SELECTOR, ".current-openings-item")
            element = job_elements[index]
            
            # Extract job title
            title_element = element.find_element(By.CSS_SELECTOR, ".current-opening-title")
            title = title_element.text.strip()

            # Extract the date
            date_text = element.find_element(By.CSS_SELECTOR, ".current-opening-post-date").text.strip()

            # Extract job ID from the span's ID attribute
            job_id = title_element.get_attribute("id").split("_")[1]  # Assuming the job ID is the second part

            # Construct the full job URL manually
            link = f"https://workforcenow.adp.com/mascsr/default/mdf/recruitment/recruitment.html?cid=e0deecb0-63b7-464a-a5d7-36704316a883&ccId=9200974135815_2&lang=en_CA&selectedMenuKey=CareerCenter&jobId={job_id}"

            # Store the job details
            job = {"title": title, "school": "St. Paul's College", "date": date_text, "link": link}
            jobs.append(job)
            logging.info(f"Added job: {title}, link: {link}, date: {date_text}")

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at St. Paul's College")
    return jobs

def scrape_university_of_saint_boniface():
    logging.info("Scraping Université de Saint-Boniface")
    jobs = []
    url = "https://carrieres.ustboniface.ca/offres/offres.php#postes"
    
    driver.get(url)
    
    # Wait for the job postings to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, '.job-listing'))
    )

    job_elements = driver.find_elements(By.CSS_SELECTOR, '.job-listing')
    logging.info(f"Found {len(job_elements)} job elements on the page")

    for element in job_elements:
        try:
            # Attempt to extract the job date using multiple XPaths
            try:
                date_text = element.find_element(By.XPATH, 'div/div[1]/p[2]').text.strip()
            except Exception:
                try:
                    date_text = element.find_element(By.XPATH, 'div/div[2]/div[1]/p[2]').text.strip()
                except Exception:
                    date_text = element.find_element(By.XPATH, 'div/div[3]/div[1]/p[2]').text.strip()

            # Extract the job title
            title = element.find_element(By.CSS_SELECTOR, 'p:nth-child(2)').text.strip()
            
            # Extract the link
            link = element.find_element(By.CSS_SELECTOR, 'a.btn-outline').get_attribute('href')

            # Store the job details
            job = {"title": title, "school": "Université de Saint-Boniface", "date": date_text, "link": link}
            jobs.append(job)
            logging.info(f"Added job: {title}, link: {link}, date: {date_text}")

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at Université de Saint-Boniface")
    return jobs

import re

def scrape_university_of_winnipeg():
    logging.info("Scraping University of Winnipeg")
    jobs = []
    url = "https://www.northstarats.com/University-of-Winnipeg"
    
    driver.get(url)
    
    try:
        # Explicitly wait for the job elements to be present
        job_link_xpath = "/html/body/form/div[4]/div/div[1]/div/div/div[2]/p[1]/a"
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, job_link_xpath))
        )

        # Find job elements using XPath
        job_elements = driver.find_elements(By.XPATH, job_link_xpath)
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for element in job_elements:
            try:
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                
                # Extract the job title
                title = element.text.strip()
                
                # Extract the href and parse the actual link from the JavaScript PopUp function
                href = element.get_attribute("href")
                link_match = re.search(r"PopUp\('(.+?)'\)", href)
                
                if link_match:
                    link = link_match.group(1)
                else:
                    link = "Link not found"
                
                # Since there's no date available, we set it to "Date not available"
                date_text = "Date not available"
                
                job = {"title": title, "school": "University of Winnipeg", "date": date_text, "link": link}
                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping University of Winnipeg: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of Winnipeg")
    return jobs

def scrape_university_of_new_brunswick():
    logging.info("Scraping University of New Brunswick")
    jobs = []
    url = "https://www.unb.ca/hr/careers/support-staff.php"
    
    try:
        driver.get(url)
        
        # Wait for job elements to be present
        job_link_xpath = "/html/body/div[3]/div/div[3]/div[1]/div/table/tbody/tr/td[1]/strong/a"
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, job_link_xpath))
        )
        
        # Find all job elements using the XPath provided
        job_elements = driver.find_elements(By.XPATH, job_link_xpath)
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for element in job_elements:
            try:
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                
                # Extract the job title
                title = element.text.strip()
                
                # Extract the job link
                link = element.get_attribute("href")
                
                # Since there's no date available, we set it to "Date not available"
                date_text = "Date not available"
                
                # Store the job data
                job = {"title": title, "school": "University of New Brunswick", "date": date_text, "link": link}
                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping University of New Brunswick: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of New Brunswick")
    return jobs

def scrape_mount_allison_university():
    logging.info("Scraping Mount Allison University")
    jobs = []
    url = "https://mta.ca/about/work-mta/employment-opportunities-academic"
    
    driver.get(url)
    
    try:
        # Wait for the job elements to be present
        job_link_xpath = "/html/body/div[3]/div/main/div[2]/div/div/div/div/div/article/div/div[2]/div/div[1]/div[4]/div/div/div/div/div/ul/li/div[1]/span/a"
        job_date_xpath = "/html/body/div[3]/div/main/div[2]/div/div/div/div/div/article/div/div[2]/div/div[1]/div[4]/div/div/div/div/div/ul/li/div[2]/div/time"
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, job_link_xpath))
        )

        # Find job elements using XPath
        job_elements = driver.find_elements(By.XPATH, job_link_xpath)
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for i, element in enumerate(job_elements, start=1):
            try:
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                
                # Extract the job title and link
                title = element.text.strip()
                link = element.get_attribute("href")
                
                # Extract the job date
                date_element = driver.find_element(By.XPATH, f"/html/body/div[3]/div/main/div[2]/div/div/div/div/div/article/div/div[2]/div/div[1]/div[4]/div/div/div/div/div/ul/li[{i}]/div[2]/div/time")
                date_text = date_element.text.strip()

                # Store job data
                job = {"title": title, "school": "Mount Allison University", "date": date_text, "link": link}
                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping Mount Allison University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Mount Allison University")
    return jobs

def scrape_st_thomas_university():
    logging.info("Scraping St. Thomas University")
    jobs = []
    url = "https://www.stu.ca/employment/"
    
    driver.get(url)

    try:
        # Use a more flexible selector to find all job listings
        job_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'content')]//p//a")
        logging.info(f"Found {len(job_elements)} job elements on the page")
        
        for job_element in job_elements:
            try:
                title = job_element.text.strip()
                link = job_element.get_attribute('href')

                # Since the date is available on the page, we note that here
                date_text = "Closing date is available on the page"

                job = {"title": title, "school": "St. Thomas University", "date": date_text, "link": link}
                jobs.append(job)
                logging.info(f"Added job: {title}, link: {link}")

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping St. Thomas University: {e}")

    logging.info(f"Found {len(jobs)} jobs at St. Thomas University")
    return jobs

def scrape_universite_de_moncton():
    logging.info("Scraping Université de Moncton")
    jobs = []
    url = "https://www.umoncton.ca/emploi/?case=4&Type=0"
    
    driver.get(url)
    
    try:
        # Wait for the job listings to load
        job_table_xpath = "/html/body/div/div[1]/div[10]/div[2]/div/div/div[3]/div[3]/div/table/tbody/tr"
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, job_table_xpath))
        )

        # Find all job rows
        job_rows = driver.find_elements(By.XPATH, job_table_xpath)
        logging.info(f"Found {len(job_rows)} job rows")

        for row in job_rows:
            try:
                # Extract job title and link
                job_element = row.find_element(By.XPATH, ".//td[1]/a")
                title = job_element.text.strip()
                link = job_element.get_attribute("href")

                # Since no date is available, set it to "Date not provided"
                date_text = "Date not provided"

                job = {"title": title, "school": "Université de Moncton", "date": date_text, "link": link}
                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping Université de Moncton: {e}")

    logging.info(f"Found {len(jobs)} jobs at Université de Moncton")
    return jobs

def scrape_acadia_university():
    logging.info("Scraping Acadia University")
    jobs = []
    url = "https://www2.acadiau.ca/about-acadia/leadership/vice-president-academic-671/faculty-librarian-offerings.html?_gl=1*68bgkf*_ga*MTk0OTI2NjAzNC4xNzI1NDYzNDE3*_ga_ER6057ZV8N*MTcyNTQ2MzQxNi4xLjEuMTcyNTQ2MzQ0NC4zMi4wLjA."

    driver.get(url)

    try:
        # Start from the second h4 element and iterate through all job postings
        h4_index = 2  # Adjust this starting point as needed
        while True:
            try:
                # XPaths for each job title and link
                job_title_xpath = f"/html/body/div[2]/div[2]/div/div/div[1]/div[2]/h4[{h4_index}]/a"
                additional_xpath = f"/html/body/div[2]/div[2]/div/div/div[1]/div[2]/h4[{h4_index}]"

                # Locate job title and link
                title_element = driver.find_element(By.XPATH, job_title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute("href")

                # Get any additional information (if necessary)
                additional_info_element = driver.find_element(By.XPATH, additional_xpath)
                additional_info = additional_info_element.text.strip()

                # Append to jobs list
                job = {
                    "title": title,
                    "link": link,
                    "additional_info": additional_info,
                    "school": "Acadia University",
                    "date": "Date not available"  # No dates found in HTML
                }
                jobs.append(job)

                logging.info(f"Extracted job: {title} with link: {link}")

                # Increment to check the next h4 element
                h4_index += 1

            except NoSuchElementException:
                # Exit loop if there are no more h4 elements
                logging.info("No more job postings found.")
                break
    except Exception as e:
        logging.error(f"Error while scraping Acadia University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Acadia University")
    return jobs

def scrape_cape_breton_university():
    logging.info("Scraping Cape Breton University")
    jobs = []
    url = "https://www.cbu.ca/current-students/career-services/student-job-opportunities/"

    driver.get(url)

    try:
        # Wait for the job elements to be visible
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/main/div/div[3]/div[1]/div[1]/div/div/h1"))
        )

        div_index = 1
        while True:
            try:
                # Construct the dynamic XPath for job title and link
                name_xpath = f"/html/body/main/div/div[3]/div[1]/div[{div_index}]/div/div/h1"
                link_xpath = f"/html/body/main/div/div[3]/div[1]/div[{div_index}]/div/a"

                # Extract the job title
                title_element = driver.find_element(By.XPATH, name_xpath)
                title = title_element.text.strip()

                # Extract the link
                link_element = driver.find_element(By.XPATH, link_xpath)
                link = link_element.get_attribute("href")

                # Add job details to the list
                job = {
                    "title": title,
                    "school": "Cape Breton University",
                    "date": "No date available",
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Added job: {title}")

                # Increment to check the next div
                div_index += 1

            except Exception as e:
                logging.info("No more job postings found or encountered an issue")
                break

    except Exception as e:
        logging.error(f"An error occurred while scraping Cape Breton University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Cape Breton University")
    return jobs

def scrape_dalhousie_university():
    logging.info("Scraping Dalhousie University")
    jobs = []
    url = "https://dal.peopleadmin.ca/postings/search"
    
    driver.get(url)

    try:
        # Wait for the job listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".job-title.job-title-text-wrap h3 a"))
        )

        page_num = 1
        while True:
            logging.info(f"Scraping page {page_num}")
            job_elements = driver.find_elements(By.CSS_SELECTOR, ".job-title.job-title-text-wrap h3 a")

            for job_element in job_elements:
                try:
                    # Extract the title and link
                    title = job_element.text.strip()
                    link = job_element.get_attribute("href")

                    # Add the job details to the list
                    job = {
                        "title": title,
                        "school": "Dalhousie University",
                        "date": "No date available",
                        "link": link
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}")

                except Exception as e:
                    logging.warning(f"Could not extract job details: {e}")

            # Check for pagination and click "Next" if available
            try:
                next_page = driver.find_element(By.LINK_TEXT, "Next")
                next_page.click()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".job-title.job-title-text-wrap h3 a"))
                )
                logging.info("Moving to the next page")
                page_num += 1
            except Exception as e:
                logging.info("No more pages found or error navigating to next page")
                break

    except Exception as e:
        logging.error(f"An error occurred while scraping Dalhousie University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Dalhousie University")
    return jobs

def scrape_nscad_university():
    logging.info("Scraping NSCAD University job listings")
    jobs = []
    url = "https://jobs.careerbeacon.com/employer-profile/nscad-university"
    
    driver.get(url)
    
    # Wait for the job listings to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//tbody/tr/td/a"))
    )
    
    # Count the number of rows in the table to handle all jobs dynamically
    rows = driver.find_elements(By.XPATH, "//tbody/tr")
    logging.info(f"Found {len(rows)} job elements on the page")
    
    # Loop through each row in the table and extract title and link
    for index, row in enumerate(rows, start=1):
        try:
            # Extract title and link using dynamic XPath
            job_element = driver.find_element(By.XPATH, f"/html/body/article/section/div/section/section/div[1]/section[2]/article/table/tbody/tr[{index}]/td[1]/a")
            title = job_element.text.strip()
            link = job_element.get_attribute('href')
            
            # Store the job details
            job = {
                "title": title,
                "school": "NSCAD University",
                "link": link,
                "date": "No date available"  # No date provided
            }
            jobs.append(job)
            logging.info(f"Added job {index}: {title}")
            
        except Exception as e:
            logging.warning(f"Could not extract details for job {index}: {e}")
    
    logging.info(f"Scraping complete. Found {len(jobs)} jobs at NSCAD University.")
    return jobs


def scrape_smu_jobs():
    logging.info("Scraping Saint Mary’s University (Staff Employment Opportunities)")
    jobs = []
    url = "https://www.smu.ca/about/staff-employment-opportunities.html"
    
    driver.get(url)
    
    # Wait for the job listings to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//table/tbody/tr"))
    )
    
    # Initialize row index (tr) for XPath
    row_index = 1
    
    while True:
        try:
            # Define XPath for the job title and link using the row index
            job_xpath = f"/html/body/div[2]/div[2]/div[1]/div[1]/div/table/tbody/tr[{row_index}]/td[1]/strong/a"
            
            # Find the job title and link
            job_element = driver.find_element(By.XPATH, job_xpath)
            title = job_element.text.strip()
            link = job_element.get_attribute('href')
            
            # Store the job details
            job = {
                "title": title,
                "school": "Saint Mary’s University",
                "link": link,
                "date": "No date available"  # No date provided on the page
            }
            jobs.append(job)
            logging.info(f"Added job {row_index}: {title}")
            
            # Increment row index to process the next job
            row_index += 1
            
        except Exception as e:
            logging.warning(f"Could not find more job listings. Last processed row: {row_index-1}.")
            break
    
    logging.info(f"Scraping complete. Found {len(jobs)} jobs at Saint Mary’s University.")
    return jobs

def scrape_universite_sainte_anne():
    logging.info("Scraping Université Sainte-Anne")
    jobs = []
    url = "https://www.usainteanne.ca/offres-demploi"

    driver.get(url)

    try:
        # Wait for the job listings to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/main/div[1]/div[1]/div[1]/div/div/div/form/table/tbody/tr[1]/th/a"))
        )

        row_index = 1
        while True:
            try:
                # Construct dynamic XPath for each row's title and link
                title_xpath = f"/html/body/main/div[1]/div[1]/div[1]/div/div/div/form/table/tbody/tr[{row_index}]/th/a"
                title_element = driver.find_element(By.XPATH, title_xpath)
                
                # Extract title and link
                title = title_element.text.strip()
                link = title_element.get_attribute("href")
                
                # Store the job details
                job = {
                    "title": title,
                    "link": link,
                    "school": "Université Sainte-Anne",
                    "date": "No date available"  # No dates available on the page
                }
                jobs.append(job)
                logging.info(f"Added job {row_index}: {title}")

                # Increment row index to check the next row
                row_index += 1

            except NoSuchElementException:
                logging.info("No more job postings found.")
                break

    except Exception as e:
        logging.error(f"Error while scraping Université Sainte-Anne: {e}")

    logging.info(f"Found {len(jobs)} jobs at Université Sainte-Anne")
    return jobs

def scrape_university_of_kings_college():
    logging.info("Scraping University of King's College")
    jobs = []
    url = "https://ukings.ca/campus-community/employment/"
    driver.get(url)

    div_index = 1
    
    while True:
        try:
            # Construct the dynamic XPath for job title and link
            job_xpath = f"/html/body/section[2]/div/div[{div_index}]/a"
            job_element = driver.find_element(By.XPATH, job_xpath)
            
            # Extract the job title (using 'title' attribute) and link (using 'href')
            title = job_element.get_attribute("title")
            link = job_element.get_attribute("href")

            # Add job details to the list
            job = {
                "title": title,
                "school": "University of King's College",
                "date": "No date provided",  # No date available on the page
                "link": link
            }
            jobs.append(job)
            logging.info(f"Added job {div_index}: {title}")

            # Increment index to process the next job listing
            div_index += 1

        except NoSuchElementException:
            logging.info("No more job postings found.")
            break
        except Exception as e:
            logging.error(f"Error while scraping University of King's College: {e}")
            break
    
    logging.info(f"Found {len(jobs)} jobs at University of King's College")
    return jobs


def scrape_lethbridge():
    logging.info("Scraping University of Lethbridge")
    jobs = []
    url = "https://uleth.peopleadmin.ca/postings/search?utf8=✓&query=&query_v0_posted_at_date=&query_position_type_id=3&285&commit=Search"
    
    driver.get(url)
    
    # Explicitly wait for the job elements to be present
    job_element_selector = "h3 a"  # Selector for job title and link
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, job_element_selector))
    )

    job_elements = driver.find_elements(By.CSS_SELECTOR, job_element_selector)
    logging.info(f"Found {len(job_elements)} job elements on the page")
    
    for element in job_elements:
        try:
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Extract the job title and link
            title = driver.execute_script("return arguments[0].textContent;", element).strip()
            link = element.get_attribute("href")
            
            # Extract job posting date by locating the sibling elements
            parent_div = element.find_element(By.XPATH, "..")
            try:
                date_element = parent_div.find_element(By.XPATH, "following-sibling::div[@class='posting-info']/div")
                date_text = date_element.text.strip()
            except Exception:
                date_text = "Date not found"

            # Add job data to the list
            job = {"title": title, "school": "University of Lethbridge", "date": date_text, "link": link}
            jobs.append(job)

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of Lethbridge")
    return jobs

def scrape_brock_university():
    logging.info("Scraping Brock University Careers Page")
    jobs = []
    url = "https://brocku.wd3.myworkdayjobs.com/brocku_careers"
    
    driver.get(url)

    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li"))
    )

    while True:
        try:
            index = 1
            # Dynamically iterate through the job listings using the changing li[index] in the XPath
            while True:
                try:
                    # Dynamic XPaths for job title, link, and date
                    title_xpath = f"/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[{index}]/div[1]/div/div/h3/a"
                    date_xpath = f"/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[{index}]/div[3]/div/div/dl/dd"
                    
                    # Extract job title and link
                    title_element = driver.find_element(By.XPATH, title_xpath)
                    title = title_element.text
                    link = title_element.get_attribute("href")  # Use the relative link directly
                    
                    # Extract job date
                    date_element = driver.find_element(By.XPATH, date_xpath)
                    posting_date = date_element.text.strip()

                    # Append job data
                    job = {
                        "school": "Brock University",
                        "title": title,
                        "date": posting_date,
                        "link": link,  # Use the correct link
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}, posted on {posting_date}, link: {link}")

                    # Increment index to move to the next job listing
                    index += 1

                except Exception as e:
                    logging.warning(f"No more job listings found at index {index}: {e}")
                    break

            # Check for pagination (next button)
            try:
                # Wait for and click the next button using the updated selector
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.css-14gl3ze"))
                )
                
                # Scroll the next button into view and click
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                
                logging.info("Clicked the 'Next' button, waiting for the next page to load...")
                
                # Wait for the next page to load by waiting for a new job title to appear
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(driver.find_element(By.XPATH, title_xpath))
                )
                
                # Reset index for the new page
                index = 1

            except Exception as e:
                logging.info("No 'Next' button found or pagination ended. Exiting pagination.")
                break

        except Exception as e:
            logging.error(f"Error occurred during scraping: {e}")
            break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs

def scrape_carleton_university():
    logging.info("Scraping Carleton University Career Opportunities")
    jobs = []
    url = "https://carleton.njoyn.com/CL2/xweb/xweb.asp?CLID=53443&page=joblisting&lang=1"
    
    driver.get(url)

    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div[3]/div/div[1]/table/tbody/tr[1]/td[2]/a"))
    )

    # Start an index counter for dynamic XPath creation
    index = 1

    while True:
        try:
            # Dynamically iterate through the job listings using the changing tr[index] in the XPath
            while True:
                try:
                    # Dynamic XPaths for job title, link, and date
                    title_xpath = f"/html/body/div[5]/div/div[3]/div/div[1]/table/tbody/tr[{index}]/td[2]/a"
                    date_xpath = f"/html/body/div[5]/div/div[3]/div/div[1]/table/tbody/tr[{index}]/td[5]"
                    
                    # Extract job title and link
                    title_element = driver.find_element(By.XPATH, title_xpath)
                    title = title_element.text
                    link = title_element.get_attribute("href")
                    
                    # Extract job posting date
                    date_element = driver.find_element(By.XPATH, date_xpath)
                    posting_date = date_element.text.strip()

                    # Append job data
                    job = {
                        "school": "Carleton University",
                        "title": title,
                        "date": posting_date,
                        "link": link,
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}, posted on {posting_date}, link: {link}")

                    # Increment index to move to the next job listing
                    index += 1

                except Exception as e:
                    logging.warning(f"No more job listings found at index {index}: {e}")
                    break

            # Exit loop when no more job listings are found
            break

        except Exception as e:
            logging.error(f"Error occurred during scraping: {e}")
            break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs

def scrape_huron_university():
    logging.info("Scraping Huron University Careers Page")
    jobs = []
    url = "https://huron.wd1.myworkdayjobs.com/en-US/huroncareers"
    
    driver.get(url)

    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-automation-id='jobTitle']"))
    )

    while True:
        # Locate all job postings
        job_items = driver.find_elements(By.CSS_SELECTOR, "li[class*='css-1q2dra3']")
        logging.info(f"Found {len(job_items)} job items on this page")

        for index, job_item in enumerate(job_items, start=1):
            try:
                # Extract job title
                title_element = job_item.find_element(By.CSS_SELECTOR, "a[data-automation-id='jobTitle']")
                title = title_element.text

                # Extract the link (relative_link is already a complete URL, so no need for base_url)
                full_link = title_element.get_attribute("href")

                # Extract the posting date
                date_xpath = f"/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[{index}]/div[3]/div/div/dl/dd"
                date_element = driver.find_element(By.XPATH, date_xpath)
                posting_date = date_element.text.strip()

                # Store the job data
                job = {
                    "school": "Huron University College",
                    "title": title,
                    "date": posting_date,
                    "link": full_link,
                }
                jobs.append(job)
                logging.info(f"Added job: {title}, posted on {posting_date}, link: {full_link}")

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

        # Check if there is a "Next" button and click it using the specific selector
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='next']")
            if next_button.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                logging.info("Clicked the 'Next' button and waiting for the next page to load...")
                
                # Wait for the page to load by waiting for the job listings to refresh
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(job_items[0])
                )
                time.sleep(2)  # Add a small delay to ensure the page loads fully
            else:
                logging.info("Next button is disabled or not found. Ending pagination.")
                break  # Exit loop if there are no more pages
        except Exception as e:
            logging.info("No 'Next' button found on this page. Ending pagination.")
            break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs

def scrape_kings_university_college():
    logging.info("Scraping King's University College Employment Page")
    jobs = []
    url = "https://www.kings.uwo.ca/current-students/money-matters/employment/employment-opportunities/"
    
    driver.get(url)

    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#maincontent > div > div.col-lg-9.col-lg-push-3.printable > div.mura-object.mura-body-object.mura-async-object > div > ul > li:nth-child(1) > span > span.thumb-info-wrapper > a > span > span"))
    )

    index = 1  # Start index for dynamic CSS selector building

    while True:
        try:
            while True:
                try:
                    # Dynamic CSS Selectors for job title and link
                    name_selector = f"#maincontent > div > div.col-lg-9.col-lg-push-3.printable > div.mura-object.mura-body-object.mura-async-object > div > ul > li:nth-child({index}) > span > span.thumb-info-wrapper > a > span > span"
                    link_selector = f"#maincontent > div > div.col-lg-9.col-lg-push-3.printable > div.mura-object.mura-body-object.mura-async-object > div > ul > li:nth-child({index}) > span > span.thumb-info-wrapper > a"
                    
                    # Extract job title
                    title_element = driver.find_element(By.CSS_SELECTOR, name_selector)
                    title = title_element.text

                    # Extract the job link
                    link_element = driver.find_element(By.CSS_SELECTOR, link_selector)
                    link = link_element.get_attribute("href")

                    # Append job data
                    job = {
                        "school": "King's University College",
                        "title": title,
                        "link": link,
                    }
                    jobs.append(job)
                    logging.info(f"Added job: {title}, link: {link}")

                    # Increment index to move to the next job listing
                    index += 1

                except Exception as e:
                    logging.warning(f"No more job listings found at index {index}: {e}")
                    break

            logging.info("No more job listings found. Ending scraping.")
            break

        except Exception as e:
            logging.error(f"Error occurred during scraping: {e}")
            break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs

def scrape_lakehead_university():
    logging.info("Scraping Lakehead University Faculty Job Listings")
    jobs = []
    url = "https://www.lakeheadu.ca/faculty-and-staff/departments/services/hr/employment-opportunities/faculty"
    
    driver.get(url)

    # Wait for the page to load and the first job element to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[1]/div/div[3]/div/div/div/div/article/div[1]/div/div/div/div[1]/div/div[1]/a"))
    )

    # Define index counters for Thunder Bay and Orillia campuses
    campus_index = 1
    job_index = 1
    section_counter = 0  # Counter to limit the number of sections processed

    while section_counter < 500:  # Limit to 8 sections
        try:
            # Scrape jobs from Thunder Bay Campus
            while section_counter < 500:
                try:
                    # XPaths for job title and link for Thunder Bay Campus
                    title_xpath_thunder_bay = f"/html/body/div/div/div/div[1]/div/div[3]/div/div/div/div/article/div[1]/div/div/div/div[1]/div/div[{job_index}]/a"
                    date_xpath_thunder_bay = f"/html/body/div/div/div/div[1]/div/div[3]/div/div/div/div/article/div[1]/div/div/div/div[1]/div/div[{job_index}]/span"

                    # Extract job title and link
                    job_element = driver.find_element(By.XPATH, title_xpath_thunder_bay)
                    title = job_element.text
                    link = job_element.get_attribute("href")

                    # Extract job posting date
                    date_element = driver.find_element(By.XPATH, date_xpath_thunder_bay)
                    posting_date = date_element.text.strip()

                    jobs.append({
                        "school": "Lakehead University",
                        "title": title,
                        "date": posting_date,
                        "link": link
                    })

                    logging.info(f"Added job: {title}, posted on {posting_date}, link: {link}")
                    job_index += 1
                    section_counter += 1  # Increment section counter

                except Exception as e:
                    logging.warning(f"No more job listings found for Thunder Bay Campus: {e}")
                    break

            # Reset job_index for next campus
            job_index = 1

            # Scrape jobs from Orillia Campus
            while section_counter < 500:
                try:
                    # XPaths for job title and link for Orillia Campus
                    title_xpath_orillia = f"/html/body/div/div/div/div[1]/div/div[3]/div/div/div/div/article/div[1]/div/div/div/div[2]/div/div[{job_index}]/a"
                    date_xpath_orillia = f"/html/body/div/div/div/div[1]/div/div[3]/div/div/div/div/article/div[1]/div/div/div/div[2]/div/div[{job_index}]/span"

                    # Extract job title and link
                    job_element = driver.find_element(By.XPATH, title_xpath_orillia)
                    title = job_element.text
                    link = job_element.get_attribute("href")

                    # Extract job posting date
                    date_element = driver.find_element(By.XPATH, date_xpath_orillia)
                    posting_date = date_element.text.strip()

                    jobs.append({
                        "school": "Lakehead University",
                        "title": title,
                        "date": posting_date,
                        "link": link
                    })

                    logging.info(f"Added job: {title}, posted on {posting_date}, link: {link}")
                    job_index += 1
                    section_counter += 1  # Increment section counter

                except Exception as e:
                    logging.warning(f"No more job listings found for Orillia Campus: {e}")
                    break

            break  # Exit loop after scraping both campuses

        except Exception as e:
            logging.error(f"Error occurred during scraping: {e}")
            break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs

def scrape_nipissing_university():
    logging.info("Scraping Nipissing University")
    jobs = []
    url = "https://www.nipissingu.ca/employment-postings"
    
    driver.get(url)
    
    # Define the base XPaths for each section, handling variations in structure
    section_xpaths = [
        '/html/body/div[2]/div[2]/div[2]/main/div/div/div/div[2]/div/div/div/div[2]/div[2]/ul/li',    # Section 1 - Regular structure
        '/html/body/div[2]/div[2]/div[2]/main/div/div/div/div[2]/div/div/div/div[2]/div[4]/ul/li',    # Section 2 - Regular structure
        '/html/body/div[2]/div[2]/div[2]/main/div/div/div/div[2]/div/div/div/div[2]/div[5]/ul/li',    # Section 3 - Regular structure
        '/html/body/div[2]/div[2]/div[2]/main/div/div/div/div[2]/div/div/div/div[3]/div[1]/div/div/div/ul/li',  # Section 4 - Deeper structure
    ]
    
    # Loop through each section XPath
    for section_xpath in section_xpaths:
        try:
            # Find all job listings within the section by selecting all `li` elements
            job_elements = driver.find_elements(By.XPATH, f"{section_xpath}/div[1]/span/a")
            logging.info(f"Found {len(job_elements)} job listings in section {section_xpath}")
            
            for job_element in job_elements:
                try:
                    # Extract job title and link
                    title = job_element.text.strip()
                    link = job_element.get_attribute("href")

                    # Look for the closing date if available
                    parent_div = job_element.find_element(By.XPATH, "../..")
                    try:
                        date_element = parent_div.find_element(By.CLASS_NAME, 'views-field-field-closing-date')
                        closing_date = date_element.text.strip()
                    except:
                        closing_date = "Open until filled"
                    
                    # Add job details to the jobs list
                    job = {
                        "title": title,
                        "school": "Nipissing University",
                        "date": closing_date,
                        "link": link
                    }
                    jobs.append(job)
                
                except Exception as e:
                    logging.warning(f"Could not extract job details for an element: {e}")
        
        except Exception as e:
            logging.warning(f"Could not find job listings in section {section_xpath}: {e}")

    logging.info(f"Found {len(jobs)} jobs at Nipissing University")
    return jobs

def scrape_ocad_university():
    logging.info("Scraping OCAD University")
    jobs = []
    url = "https://tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=OCADU&cws=37"
    
    driver.get(url)

    # Scroll to the bottom to load all job listings
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Increase the wait time to ensure the new jobs have time to load
        
        # Check if new jobs have loaded
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            # If the height hasn't changed, wait for 2 seconds and try again to ensure all content is loaded
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    # Defining the XPath pattern for job listings
    xpath_pattern = '/html/body/div[3]/section[5]/div/div/div[2]/div/div[{}]/div/div[1]/div[2]/h4/a'

    job_index = 1
    while True:
        try:
            # Try finding job elements by iterating through the index
            job_element = driver.find_element(By.XPATH, xpath_pattern.format(job_index))
            title = job_element.text
            link = job_element.get_attribute("href")

            # Append job details
            job = {
                "title": title,
                "school": "OCAD University",
                "date": "No date provided",
                "link": link
            }
            jobs.append(job)
            job_index += 1

        except Exception as e:
            logging.warning(f"Reached end of job listings or encountered an issue: {e}")
            break

    logging.info(f"Found {len(jobs)} jobs at OCAD University")
    return jobs

def scrape_ontario_tech():
    logging.info("Scraping Ontario Tech University")
    jobs = []
    url = "https://ontariotechu.csod.com/ux/ats/careersite/4/home?c=ontariotechu"
    
    driver.get(url)

    # Scroll down the page to load all jobs
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # Define the XPath patterns for the job elements
    link_xpath_pattern = '/html/body/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[{}]/div/div/div/a'
    title_xpath_pattern = '/html/body/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[{}]/div/div/div/a/p'
    date_xpath_pattern = '/html/body/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[{}]/div/div/div/p[2]'

    # Loop over multiple job listing entries
    div_index = 3  # Initial div index for job listings
    while True:
        try:
            # Get job link and title
            job_link = driver.find_element(By.XPATH, link_xpath_pattern.format(div_index))
            job_title = driver.find_element(By.XPATH, title_xpath_pattern.format(div_index)).text
            job_url = job_link.get_attribute("href")

            # Get job posting date
            job_date = driver.find_element(By.XPATH, date_xpath_pattern.format(div_index)).text

            # Add job details to the list
            job = {
                "title": job_title,
                "school": "Ontario Tech University",
                "date": job_date,
                "link": job_url
            }
            jobs.append(job)
            div_index += 1

        except Exception as e:
            logging.warning(f"Could not extract details for div index {div_index}: {e}")
            break

    logging.info(f"Found {len(jobs)} jobs at Ontario Tech University")
    return jobs


def scrape_queens_university():
    logging.info("Scraping Queen’s University")
    jobs = []
    url = "https://queensu.njoyn.com/cl4/xweb/xweb.asp?tbtoken=YlhaRRtYDVB3FnZ4TF0mFE9McxZbaVVbA1JMWl0Of3kuLEcSWTIbcWJwB0IYGhJWQXJjF3U%3D&chk=ZVpaShM%3D&CLID=74827&page=joblisting&lang=1"
    
    driver.get(url)

    # Looping through job rows in the table
    row_number = 1
    while True:
        try:
            # Construct the XPath dynamically for each row
            link_xpath = f'/html/body/div[3]/div/section/div/div/div/div[2]/div/div/div/div/article/div[1]/div/div/div/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{row_number}]/td[1]/a'
            name_xpath = f'/html/body/div[3]/div/section/div/div/div/div[2]/div/div/div/div/article/div[1]/div/div/div/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{row_number}]/td[2]'
            date_xpath = f'/html/body/div[3]/div/section/div/div/div/div[2]/div/div/div/div/article/div[1]/div/div/div/div/div[2]/div/div[2]/div[1]/table/tbody/tr[{row_number}]/td[6]'

            # Find job details
            job_link_element = driver.find_element(By.XPATH, link_xpath)
            job_name_element = driver.find_element(By.XPATH, name_xpath)
            job_date_element = driver.find_element(By.XPATH, date_xpath)

            # Extract details
            title = job_name_element.text
            link = job_link_element.get_attribute("href")
            closing_date = job_date_element.text.strip()

            # Append job to list
            job = {
                "title": title,
                "school": "Queen’s University",
                "date": closing_date,
                "link": link
            }
            jobs.append(job)
            logging.info(f"Job {row_number}: {title} - {closing_date}")

            # Move to the next row
            row_number += 1
        except Exception as e:
            logging.warning(f"Could not extract details for row {row_number}: {e}")
            break

    logging.info(f"Found {len(jobs)} jobs at Queen’s University")
    return jobs


def scrape_redeemer_university():
    logging.info("Scraping Redeemer University")
    jobs = []
    url = "https://www.redeemer.ca/about/careers/"
    
    driver.get(url)

    # XPath pattern that uses a wildcard (*) for dynamic div indexing
    base_xpath = '/html/body/main/section/div[2]/article/div[3]/div/div/div[*]/div/div[2]/div[1]/a'
    
    try:
        # Locate all job elements dynamically by using the wildcard in the XPath
        job_elements = driver.find_elements(By.XPATH, base_xpath)
        logging.info(f"Found {len(job_elements)} job listings")

        for job_element in job_elements:
            try:
                # Extract job title and link
                title = job_element.text
                link = job_element.get_attribute("href")

                # Add job details to the jobs list
                job = {
                    "title": title,
                    "school": "Redeemer University",
                    "link": link
                }
                jobs.append(job)
            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.warning(f"Could not find job listings: {e}")

    logging.info(f"Found {len(jobs)} jobs at Redeemer University")
    return jobs


def scrape_trent_university():
    logging.info("Scraping Trent University Job Listings")
    jobs = []
    
    # URLs for the two sections
    faculty_url = "https://www.trentu.ca/humanresources/employment-opportunities/full-time-faculty-positions"
    non_academic_url = "https://www.trentu.ca/humanresources/employment-opportunities/non-academic-positions"
    
    # Scraping Full-Time Faculty Positions
    logging.info("Scraping Full-Time Faculty Positions")
    driver.get(faculty_url)

    try:
        # Loop through all the faculty job tables
        table_index = 1
        while True:
            try:
                title_xpath = f"/html/body/div[1]/div[2]/div/main/div/div/div[1]/article/div/div/div/div[3]/div/div/div/table[{table_index}]/tbody/tr/td[1]/a"
                job_element = driver.find_element(By.XPATH, title_xpath)
                
                title = job_element.text
                link = job_element.get_attribute('href')
                
                job = {
                    "title": title,
                    "link": link,
                    "school": "Trent University - Full-Time Faculty"
                }
                jobs.append(job)
                table_index += 1
            except Exception as e:
                logging.warning(f"No more faculty jobs found in table {table_index}: {e}")
                break
    except Exception as e:
        logging.warning(f"Could not scrape job listings for Full-Time Faculty at Trent University: {e}")

    # Scraping Non-Academic Positions
    logging.info("Scraping Non-Academic Positions")
    driver.get(non_academic_url)

    try:
        # Loop through all the non-academic job rows in the table
        row_index = 1
        while True:
            try:
                title_xpath = f"/html/body/div[1]/div[2]/div/main/div/div/div[1]/article/div/div/div/div[2]/div/div/div/table/tbody/tr[{row_index}]/td[1]/a"
                job_element = driver.find_element(By.XPATH, title_xpath)
                
                title = job_element.text
                link = job_element.get_attribute('href')
                
                job = {
                    "title": title,
                    "link": link,
                    "school": "Trent University - Non-Academic Positions"
                }
                jobs.append(job)
                row_index += 1
            except Exception as e:
                logging.warning(f"No more non-academic jobs found in row {row_index}: {e}")
                break
    except Exception as e:
        logging.warning(f"Could not scrape job listings for Non-Academic Positions at Trent University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Trent University")
    return jobs

def scrape_university_of_guelph():
    logging.info("Scraping University of Guelph Faculty, Librarian & Veterinarian positions")
    jobs = []
    url = "https://careers.uoguelph.ca/go/Faculty%2C-Librarian-and-Veterinarian/8665747/"
    
    driver.get(url)

    try:
        # XPath for the job listings, assuming it changes based on the li[#]
        job_count = 11  # Number of job listings visible on the page (you can dynamically calculate this if needed)
        
        for i in range(1, job_count + 1):
            try:
                # Construct XPaths for job names and links
                if i == 4:  # Special case where the structure differs
                    name_xpath = f"/html/body/div[1]/div[3]/div/div/div[7]/div/ul/li[{i}]/div/div/span[1]/div[1]/span[2]/a"
                else:
                    name_xpath = f"/html/body/div[1]/div[3]/div/div/div[7]/div/ul/li[{i}]/div/div/div[2]/div[1]/div/span[2]/a"
                
                # Extract job name (text content)
                name_element = driver.find_element(By.XPATH, name_xpath)
                name = name_element.text.strip()

                # If the name is not found, create a generic name
                if not name:
                    name = f"Job listing {i}"
                
                # Extract job link (href attribute)
                link = name_element.get_attribute('href')

                # Construct job dictionary
                job = {
                    "name": name,
                    "link": link,
                    "school": "University of Guelph"
                }
                jobs.append(job)
            except Exception as e:
                logging.warning(f"Could not extract job details for job listing {i}: {e}")

    except Exception as e:
        logging.warning(f"Could not find job listings on University of Guelph's site: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of Guelph")
    return jobs


def scrape_university_of_ottawa():
    logging.info("Scraping University of Ottawa Career Opportunities")
    jobs = []
    url = "https://uottawa.wd3.myworkdayjobs.com/en-US/uOttawa_External_Career_Site"
    
    driver.get(url)

    # Wait for the job listings to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[1]/div[1]/div/div/h3/a"))
    )

    page_number = 1  # Counter for pagination
    while True:
        logging.info(f"Scraping page {page_number}")
        index = 1  # Reset index for each page
        while True:
            try:
                # Dynamic XPaths for job title, link, and date
                title_xpath = f"/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[{index}]/div[1]/div/div/h3/a"
                date_xpath = f"/html/body/div/div/div/div[3]/div/div/div[2]/section/ul/li[{index}]/div[3]/div/div/dl/dd"
                
                # Extract job title and link
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text
                link = title_element.get_attribute("href")
                
                # Extract job posting date
                date_element = driver.find_element(By.XPATH, date_xpath)
                posting_date = date_element.text.strip()

                # Append job data to the list
                job = {
                    "school": "University of Ottawa",
                    "title": title,
                    "date": posting_date,
                    "link": link,
                }
                jobs.append(job)
                logging.info(f"Added job: {title}, posted on {posting_date}, link: {link}")

                index += 1  # Move to the next job listing
            except Exception as e:
                logging.warning(f"No more job listings found at index {index} on page {page_number}: {e}")
                break

        # Check if there is a "Next" button and click it using the specific selector
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "#mainContent > div > div.css-uvpbop > section > div.css-3z7fsk > nav > div > button:nth-child(3)")
            
            if next_button.is_enabled():
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                logging.info("Clicked the 'Next' button and waiting for the next page to load...")
                
                # Wait for the page to load by waiting for the job listings to refresh
                WebDriverWait(driver, 10).until(
                    EC.staleness_of(title_element)
                )
                time.sleep(2)  # Add a small delay to ensure the page loads fully
                page_number += 1  # Increment page counter
            else:
                logging.info("Next button is disabled or not found. Ending pagination.")
                break  # Exit loop if there are no more pages
        except Exception as e:
            logging.info("No 'Next' button found. Ending pagination.")
            break

    logging.info(f"Total jobs found: {len(jobs)}")
    return jobs

from selenium.common.exceptions import WebDriverException
import time
import logging

def scrape_mcmaster():
    logging.info("Scraping McMaster University job postings")
    jobs = []
    
    url = "https://careers.mcmaster.ca/psp/prcsprd/EMPLOYEE/HRMS/c/HRS_HRAM.HRS_APP_SCHJOB.GBL?Page=HRS_APP_SCHJOB&Action=U&FOCUS=Applicant&SiteId=1001&cmd=uninav&Rnode=HRMS&uninavpath=Root{PORTAL_ROOT_OBJECT}.Portal%20Objects{PORTAL_BASE_DATA}.Navigation%20Collections{CO_NAVIGATION_COLLECTIONS}.Custom%20Tabs{PAPP_CUSTOM_TABS}&customTab=MCM_STAFF_POS&IgnoreParamTempl=customTab"
    
    try:
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

        driver.get(url)

        # Switch to iframe and scrape job listings
        WebDriverWait(driver, 15).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "TargetContent")))
        logging.info("Switched to iframe")
        
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "HRS_AGNT_RSLT_I$scroll$0")))
        logging.info("Job table loaded")

        job_rows = driver.find_elements(By.XPATH, "//tr[starts-with(@id, 'trHRS_AGNT_RSLT_I$')]")
        logging.info(f"Found {len(job_rows)} job rows")
        
        for row in job_rows:
            try:
                title_element = row.find_element(By.XPATH, ".//a[contains(@id, 'POSTINGLINK')]")
                title = title_element.text.strip()

                onclick_value = title_element.get_attribute("href")
                if "submitAction_win0" in onclick_value:
                    job_id = onclick_value.split("HRS_JOB_OPEN_ID_PB.")[1].split("');")[0]
                    link = f"https://hrprd.mcmaster.ca/psc/prhrprd/EMPLOYEE/HRMS/c/HRS_HRAM.HRS_CE.GBL?Page=HRS_CE_JOB_DTL&Action=A&FOCUS=Applicant&SiteId=1001&JobOpeningId={job_id}"
                else:
                    link = "Link not found"
                
                attributes = row.find_element(By.XPATH, ".//div[@class='attributes PSTEXT align:left']").text.strip()
                
                job = {
                    "title": title,
                    "attributes": attributes,
                    "link": link
                }
                jobs.append(job)

            except Exception as e:
                logging.warning(f"Error extracting job details: {e}")
    
    except WebDriverException as e:
        logging.error(f"WebDriver error occurred: {e}")
        logging.info("Retrying after 5 seconds...")
        time.sleep(5)
        return scrape_mcmaster()  # Retry the function in case of connection issues

    except TimeoutException:
        logging.error("Timeout waiting for job listings")
    
    finally:
        logging.info(f"Found {len(jobs)} jobs at McMaster University")
        return jobs



def scrape_st_michaels():
    logging.info("Scraping University of St. Michael’s College job postings")
    jobs = []

    url = "https://stmikes.utoronto.ca/about-us/employment-opportunities"
    driver = webdriver.Chrome()  # Ensure you have the correct path for your webdriver
    driver.get(url)

    try:
        # Wait for the page to load and find the first job listing
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/section/section/article/div[2]/ul/li[1]/h3/a"))
        )
        logging.info("Page loaded, extracting job listings")

        job_index = 1
        while True:
            try:
                # Scroll the page down gradually to load more jobs if necessary
                driver.execute_script("window.scrollBy(0, 500);")
                WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, f"/html/body/section/section/article/div[2]/ul/li[{job_index}]/h3/a"))
                )

                # Construct dynamic XPath for job title and link
                title_xpath = f"/html/body/section/section/article/div[2]/ul/li[{job_index}]/h3/a"
                date_xpath = f"/html/body/section/section/article/div[2]/ul/li[{job_index}]/h3/span"

                # Extract title and link
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')

                # Extract posted date
                date_element = driver.find_element(By.XPATH, date_xpath)
                posting_date = date_element.text.strip()

                # Creating job dictionary with required structure
                job = {
                    "school": "University of St. Michael’s College",
                    "title": title,
                    "date": posting_date,  # Using "date" for the posting date
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {title}, Posted: {posting_date}")

                job_index += 1

            except Exception as e:
                logging.warning(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from University of St. Michael’s College")
        return jobs
    
    
def scrape_u_of_toronto():
    logging.info("Scraping University of Toronto job postings")
    jobs = []

    url = "https://jobs.utoronto.ca/search/?q=&utm_source=CSSearchWidget&startrow=1"
    driver = webdriver.Chrome()  # Ensure you have the correct path for your webdriver
    driver.get(url)

    try:
        # Wait for the page to load and find the job listings
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div/div/div[4]/table/tbody/tr[1]/td[1]/span/a"))
        )
        logging.info("Page loaded, extracting job listings")

        while True:
            job_index = 1
            while True:
                try:
                    # Construct dynamic XPaths for job title and link
                    title_xpath = f"/html/body/div/div[2]/div/div/div[4]/table/tbody/tr[{job_index}]/td[1]/span/a"

                    # Extract title and link
                    title_element = driver.find_element(By.XPATH, title_xpath)
                    title = title_element.text.strip()
                    link = title_element.get_attribute('href')

                    job = {
                        "school": "University of Toronto",
                        "title": title,
                        "link": link,
                    }
                    jobs.append(job)
                    logging.info(f"Found job: {title}")

                    job_index += 1
                except Exception as e:
                    logging.warning(f"No more jobs found on current page after {job_index - 1} listings.")
                    break

            # Check if there is a next page and wait for it to load
            try:
                next_button = driver.find_element(By.XPATH, "//li[@class=' ']/a[@title='Page 2']")
                logging.info("Navigating to next page")
                driver.execute_script("arguments[0].click();", next_button)

                # Explicitly wait for the next page to load
                WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div/div/div[4]/table/tbody/tr[1]/td[1]/span/a"))
                )

            except Exception as e:
                logging.warning("No more pages to navigate.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from University of Toronto")
        return jobs


def scrape_trinity_college():
    logging.info("Scraping Trinity College School job postings")
    jobs = []

    url = "https://www.tcs.on.ca/who-we-are/employment-opportunities"
    driver = webdriver.Chrome()  # Ensure you have the correct path for your webdriver
    driver.get(url)

    try:
        # Wait for the page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div/div/div[1]/div/div[3]/div/article/div/div/div[2]/div/div/div[1]/div[1]/strong/a"))
        )
        logging.info("Page loaded, extracting job listings")

        div_index = 1
        while True:
            try:
                # Construct dynamic XPaths for job title and link based on div structure
                title_xpath = f"/html/body/div[2]/div[2]/div/div/div[1]/div/div[3]/div/article/div/div/div[2]/div/div/div[{div_index}]/div[1]/strong/a"

                # Extract title and link
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')

                job = {
                    "school": "Trinity College School",
                    "title": title,
                    "link": link,
                }
                jobs.append(job)
                logging.info(f"Found job: {title}")

                div_index += 1
            except NoSuchElementException:
                logging.warning(f"No more jobs found after {div_index - 1} listings.")
                break
            except Exception as e:
                logging.error(f"Error occurred: {e}")
                break

    except Exception as e:
        logging.error(f"Error occurred while loading the page: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Trinity College School")
        return jobs



import logging

def scrape_university_of_waterloo():
    logging.info("Scraping University of Waterloo job postings")
    jobs = []
    url = "https://careers-uwaterloo.icims.com/jobs/search?ss=1"
    
    driver = webdriver.Chrome()  # Make sure the driver path is correctly set
    driver.get(url)

    try:
        # Wait for the page to load and locate the first job listing
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.iCIMS_MainWrapper.iCIMS_ListingsPage"))
        )
        logging.info("Page loaded, extracting job listings")

        job_index = 1
        while True:
            try:
                # Construct dynamic CSS selector for job title and link
                title_selector = f"div.container-fluid.iCIMS_JobsTable > div:nth-child({job_index}) > div.col-xs-12.title > a"
                title_element = driver.find_element(By.CSS_SELECTOR, title_selector)

                title = title_element.text.strip()
                link = title_element.get_attribute('href')

                job = {
                    "school": "University of Waterloo",
                    "title": title,
                    "link": link,
                }
                jobs.append(job)
                logging.info(f"Found job: {title}")

                job_index += 1
            except Exception as e:
                logging.warning(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from University of Waterloo")
        return jobs


def scrape_university_of_windsor():
    logging.info("Scraping University of Windsor job postings")
    jobs = []

    url = "https://www.uwindsor.ca/humanresources/employment-opportunities"
    driver = webdriver.Chrome()  # Ensure you have the correct path for your webdriver
    driver.get(url)

    try:
        # Wait for the page to load and find the job listings
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[3]/div/div/div[1]/div[2]/div/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[1]/a"))
        )
        logging.info("Page loaded, extracting job listings")

        div_index = 1
        while True:
            try:
                # Construct dynamic XPaths for job title and link
                title_xpath = f"/html/body/div/div[3]/div/div/div[1]/div[2]/div/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[{div_index}]/a"

                # Extract title and link
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')

                job = {
                    "school": "University of Windsor",
                    "title": title,
                    "link": link,
                }
                jobs.append(job)
                logging.info(f"Found job: {title}")

                div_index += 1
            except NoSuchElementException:
                logging.warning(f"No more jobs found after {div_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from University of Windsor")
        return jobs



def scrape_victoria_university():
    logging.info("Scraping Victoria University job postings")
    jobs = []

    url = "https://can241.dayforcehcm.com/CandidatePortal/en-US/victoriauniversity"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        # Wait for the job listings to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/div/div[1]/main/div[2]/ul/li[1]/div[1]/div[1]/div[1]/h2/a"))
        )
        logging.info("Page loaded, extracting job listings")

        # Initialize the index for <li> element for dynamic path generation
        li_index = 1
        while True:
            try:
                # Construct dynamic XPaths for job title, link, and date
                title_xpath = f"/html/body/div[1]/div/div[1]/main/div[2]/ul/li[{li_index}]/div[1]/div[1]/div[1]/h2/a"
                date_xpath = f"/html/body/div[1]/div/div[1]/main/div[2]/ul/li[{li_index}]/div[1]/div[1]/div[3]"

                # Extract job title, link, and date
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')
                date_element = driver.find_element(By.XPATH, date_xpath)
                date_posted = date_element.text.strip()

                job = {
                    "school": "Victoria University",
                    "title": title,
                    "link": link,
                    "date": date_posted
                }
                jobs.append(job)
                logging.info(f"Found job: {title} - {date_posted}")

                # Increment the li index to move to the next job listing
                li_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {li_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Victoria University")
        return jobs
    
    
def scrape_wilfrid_laurier_university():
    logging.info("Scraping Wilfrid Laurier University job postings")
    jobs = []
    
    url = "https://careers.wlu.ca/go/All-jobs/504947/"
    driver = webdriver.Chrome()  # Ensure you have the correct path for your webdriver
    driver.get(url)

    try:
        # Wait for the page to load and ensure job listings are present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobTitle-link"))
        )
        logging.info("Page loaded, extracting job listings")

        job_index = 1
        while True:
            try:
                # Construct dynamic XPath for job title and link
                title_xpath = f"/html/body/div/div[2]/div/div/div[4]/div[2]/table/tbody/tr[{job_index}]/td[1]/span/a"
                
                # Extract title and link
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')

                job = {
                    "school": "Wilfrid Laurier University",
                    "title": title,
                    "link": link,
                }
                jobs.append(job)
                logging.info(f"Found job: {title}")

                job_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Wilfrid Laurier University")
        return jobs
    
    
def scrape_york_university():
    logging.info("Scraping York University job postings")
    jobs = []
    
    url = "https://jobs-ca.technomedia.com/yorkuniversity/?_4x1F8B08000000000000FF6DCEB10E83201485E1B761341790AB0E0CB6C4C6077036AD250DAD02E16252DFBE0C1D4DCEF6275F0E7DEC71B3DE1C5EABBA559D547C16BC566DD9CC273E0300DB77F73CCD583A17082CA6B058A231DB4DC790F27DADDEE1110365E75FD55B16C47997A76934A790FA3B64D7CDFA5D0B21197D171D93F3B94E8CCA4D6DCC450CD041CF4109893D2AEC1B106DD3A0E1C3157F6C8DE5EFCC000000"
    driver = webdriver.Chrome()  # Ensure you have the correct path for your webdriver
    driver.get(url)
    
    

    try:
        # Wait for the page to load and ensure job listings are present
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//table[@class='table tblGen']"))
        )
        logging.info("Page loaded, extracting job listings")

        job_index = 1
        while True:
            try:
                # Construct dynamic XPaths for job title, link, and date
                title_xpath = f"/html/body/div[2]/section/div/div[1]/div[4]/div/form/div[2]/div[2]/div/div[2]/div[1]/table/tbody/tr[{job_index}]/td[2]/div/a"
                date_xpath = f"/html/body/div[2]/section/div/div[1]/div[4]/div/form/div[2]/div[2]/div/div[2]/div[1]/table/tbody/tr[{job_index}]/td[6]"
                
                # Extract title, link, and date
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')
                
                date_element = driver.find_element(By.XPATH, date_xpath)
                posting_date = date_element.text.strip()

                job = {
                    "school": "York University",
                    "title": title,
                    "link": link,
                    "date": posting_date
                }
                jobs.append(job)
                logging.info(f"Found job: {title} - {posting_date}")

                job_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from York University")
        return jobs
    
    
def scrape_upei():
    logging.info("Scraping University of Prince Edward Island job postings")
    jobs = []
    
    url = "https://www.upei.ca/hr/competitions"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 1
        while True:
            try:
                # XPath for job title/link
                title_xpath = f"/html/body/div[1]/div[2]/main/div[2]/div[1]/div[3]/div/div/div[1]/div/div/div[2]/div/table/tbody/tr[{job_index}]/td[2]/a"
                # XPath for closing date
                date_xpath = f"/html/body/div[1]/div[2]/main/div[2]/div[1]/div[3]/div/div/div[1]/div/div/div[2]/div/table/tbody/tr[{job_index}]/td[4]/time"
                
                # Extract job title and link
                title_element = driver.find_element(By.XPATH, title_xpath)
                title = title_element.text.strip()
                link = title_element.get_attribute('href')
                
                # Extract closing date
                date_element = driver.find_element(By.XPATH, date_xpath)
                closing_date = date_element.text.strip()

                # Append job details to the list with both "Posted on" and "Closing date"
                job = {
                    "school": "University of Prince Edward Island",
                    "title": title,
                    "link": link,
                    "date": f"Closing date: {closing_date}"  # Display both Posted and Closing date
                }
                jobs.append(job)
                logging.info(f"Found job: {title} - Posted on: {closing_date}")

                job_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from UPEI")
        return jobs



def scrape_bishops_university():
    logging.info("Scraping Bishop's University job postings")
    jobs = []
    
    url = "https://jobboard.ubishops.ca/?_gl=1%2A11wlmo%2A_gcl_au%2AMTM0Nzg2NjA5NS4xNzI1NTQ2NjUy%2A_ga%2AMTU0MjI3NjI2My4xNzI1NTQ2NjQ5%2A_ga_V3YHP7673R%2AMTcyNTU0NjY0OC4xLjEuMTcyNTU0NjY1Ni41NS4wLjA."
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 1
        while True:
            try:
                # XPath for job name
                name_xpath = f"/html/body/div[1]/div/div/section[3]/div/div/div/div/ul/li[{job_index}]/div[2]/div[1]/h3"
                # XPath for job link
                link_xpath = f"/html/body/div[1]/div/div/section[3]/div/div/div/div/ul/li[{job_index}]/a"
                
                # Extract job name
                name_element = driver.find_element(By.XPATH, name_xpath)
                name = name_element.text.strip()

                # Extract job link
                link_element = driver.find_element(By.XPATH, link_xpath)
                link = link_element.get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "Bishop's University",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Bishop's University")
        return jobs
    
    
def scrape_ets():
    logging.info("Scraping École de technologie supérieure job postings")
    jobs = []
    
    url = "https://tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=ETS&cws=37"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 2  # Start at 2 based on the provided paths
        while True:
            try:
                # XPath for job name/link
                name_link_xpath = f"/html/body/div/section[6]/div/div/div[{job_index}]/div/div[1]/div[2]/h4/a"
                
                # Extract job name and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "École de technologie supérieure",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from ÉTS")
        return jobs    
    


def scrape_hec_montreal():
    logging.info("Scraping HEC Montréal job postings")
    jobs = []
    
    url = "https://tre.tbe.taleo.net/tre01/ats/careers/v2/searchResults?org=NYQEDG&cws=40"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    # Incrementally scroll to the bottom of the page to load all jobs
    logging.info("Incrementally scrolling to the bottom of the page to load all job postings")
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollBy(0, 1000);")
        time.sleep(1)  # Wait for the page to load new content
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    try:
        job_index = 1  # Initialize job index for iteration
        while True:
            try:
                # Explicitly wait for the job elements to be visible
                name_link_xpath = f"/html/body/div/section[4]/div/div/div[2]/div/div[{job_index}]/div/div[1]/div[2]/h4/a"
                
                # Handle potential variations in the XPath structure
                if job_index == 11:
                    name_link_xpath = f"/html/body/div/section[4]/div/div/div[2]/div/div[11]/div[7]/div/div[1]/div[2]/h4/a"
                elif job_index == 4:
                    name_link_xpath = f"/html/body/div/section[4]/div/div/div[2]/div/div[11]/div[4]/div/div[1]/div[2]/h4/a"
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, name_link_xpath))
                )

                # Extract job name and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "HEC Montréal",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 2  # Increment by 2 as the div index seems to increase by 2 for each listing
            except (NoSuchElementException, TimeoutException):
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from HEC Montréal")
        return jobs


def scrape_polytechnique_montreal():
    logging.info("Scraping Polytechnique Montréal job postings")
    jobs = []
    
    url = "https://www.polymtl.ca/carriere/offres-demploi"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        # Iterate through both sections, changing the XPath based on the section
        for section in range(1, 4, 2):  # Handles both div[1] and div[3]
            job_index = 1  # Reset job index for each section
            while True:
                try:
                    # Construct XPaths for job names and links based on section
                    if section == 3:
                        # Section 2 (div[3])
                        name_link_xpath = f"/html/body/div[4]/div/div/div[2]/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[5]/div/div[3]/ul/li[{job_index}]/a"
                    else:
                        # Section 1 (div[1])
                        name_link_xpath = f"/html/body/div[4]/div/div/div[2]/div[5]/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[5]/div/div[1]/ul/li[{job_index}]/a"

                    # Explicitly wait for the job elements to be visible
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, name_link_xpath))
                    )

                    # Extract job name and link
                    name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                    name = name_link_element.text.strip()
                    link = name_link_element.get_attribute('href')

                    # Append job details to the list
                    job = {
                        "school": "Polytechnique Montréal",
                        "title": name,
                        "link": link
                    }
                    jobs.append(job)
                    logging.info(f"Found job in section {section}: {name}")

                    job_index += 1  # Increment to the next job in the list
                except NoSuchElementException:
                    logging.info(f"No more jobs found in section {section} after {job_index - 1} listings.")
                    break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Polytechnique Montréal")
        return jobs




def scrape_sherbrooke():
    logging.info("Scraping Université de Sherbrooke job postings")
    jobs = []
    
    url = "https://www.usherbrooke.ca/emplois/offres?tx_udesrechercheemplois_list[sort]=DATEDEBUTAFFICHAGE%20desc"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 1  # Initialize job index for iteration
        while True:
            try:
                # XPath for job name and link (with div[#] structure)
                name_link_xpath = f"/html/body/section/div/div/div/div/main/div/div/div/div/div/div/div/section/div/div/div[2]/div/section/div/div[{job_index}]/a"
                
                # Explicitly wait for the job elements to be visible
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, name_link_xpath))
                )

                # Extract job name and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "Université de Sherbrooke",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1  # Increment to the next job in the list
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Université de Sherbrooke")
        return jobs


def scrape_uqam():
    logging.info("Scraping Université du Québec à Montréal (UQAM) job postings with pagination")
    jobs = []
    
    url = "https://rh.uqam.ca/emplois/"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        while True:  # Loop to handle multiple pages
            job_index = 1  # Initialize job index for each page
            while True:
                try:
                    # XPath for job name and link (with li[#] structure)
                    name_link_xpath = f"/html/body/div[1]/div[2]/div[2]/div[1]/div/div/section/main/article/div[2]/div[3]/div/ul[1]/li[{job_index}]/a"
                    
                    # Explicitly wait for the job elements to be visible
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, name_link_xpath))
                    )

                    # Extract job name and link
                    name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                    name = name_link_element.text.strip()
                    link = name_link_element.get_attribute('href')

                    # Append job details to the list
                    job = {
                        "school": "Université du Québec à Montréal (UQAM)",
                        "title": name,
                        "link": link
                    }
                    jobs.append(job)
                    logging.info(f"Found job: {name}")

                    job_index += 1  # Increment to the next job in the list
                except NoSuchElementException:
                    logging.info(f"No more jobs found after {job_index - 1} listings on this page.")
                    break

            # Check for the "Next" button by detecting the available page numbers
            try:
                next_page_number = driver.find_element(By.XPATH, "//a[text()='Suivant' or text()='2']")  # Handling the next page number
                next_page_number.click()
                WebDriverWait(driver, 10).until(EC.staleness_of(next_page_number))  # Wait for the next page to load
            except NoSuchElementException:
                logging.info("No more pages to navigate.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from UQAM")
        return jobs



def scrape_uqac_jobs():
    logging.info("Scraping Université du Québec à Chicoutimi (UQAC) job postings with pagination")
    jobs = []
    
    url = "https://www.uqac.ca/emploi/emplois/"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        while True:  # Loop to handle pagination
            job_index = 1  # Initialize job index for iteration on each page
            while True:
                try:
                    # XPath for job name and link
                    name_link_xpath = f"/html/body/div[1]/div[4]/div/div[1]/div[1]/ol/li[{job_index}]/dl/dd[2]/strong/a"
                    # XPath for date
                    date_xpath = f"/html/body/div[1]/div[4]/div/div[1]/div[1]/ol/li[{job_index}]/dl/dd[4]/strong"
                    
                    # Wait for the job name/link element to be visible
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, name_link_xpath))
                    )

                    # Extract job name and link
                    name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                    name = name_link_element.text.strip()
                    link = name_link_element.get_attribute('href')

                    # Extract job date
                    date_element = driver.find_element(By.XPATH, date_xpath)
                    date = date_element.text.strip()

                    # Append job details to the list
                    job = {
                        "school": "Université du Québec à Chicoutimi (UQAC)",
                        "title": name,
                        "link": link,
                        "date": date
                    }
                    jobs.append(job)
                    logging.info(f"Found job: {name}")

                    job_index += 1  # Increment to the next job in the list
                except NoSuchElementException:
                    logging.info(f"No more jobs found after {job_index - 1} listings on this page.")
                    break

            # Check for the "Next" button and click it
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "a.next.page-numbers")
                next_page_link = next_button.get_attribute('href')
                driver.get(next_page_link)
                logging.info(f"Navigating to the next page: {next_page_link}")
                WebDriverWait(driver, 10).until(EC.staleness_of(next_button))  # Wait for the next page to load
            except NoSuchElementException:
                logging.info("No more pages to navigate.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from UQAC")
        return jobs



def scrape_uqar_jobs():
    logging.info("Scraping Université du Québec à Rimouski (UQAR) job postings")
    jobs = []
    
    # Hardcoded URLs for the first 10 pages
    urls = [
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/2/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/3/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/4/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/5/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/6/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/7/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/8/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/9/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/10/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/11/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/12/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/13/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/14/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/15/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/16/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/17/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/18/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/19/",
        "https://emploi.uqar.ca/emplois-travail-boulot-postes-ouverts/page/20/"
    ]
    
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver

    try:
        for url in urls:
            logging.info(f"Navigating to: {url}")
            try:
                driver.get(url)
                job_index = 1  # Initialize job index for iteration on each page
                
                while True:
                    try:
                        # XPath for job name and link (with div[#] structure for each listing)
                        name_link_xpath = f"/html/body/section/div/div/main/div/section/div/div/div/div/div/div[1]/div[3]/div/div[{job_index}]/article/div[3]/div[1]/h2/a"
                        
                        # Wait for the job name/link element to be visible
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, name_link_xpath))
                        )

                        # Extract job name and link
                        name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                        name = name_link_element.text.strip()
                        link = name_link_element.get_attribute('href')

                        # Append job details to the list
                        job = {
                            "school": "Université du Québec à Rimouski (UQAR)",
                            "title": name,
                            "link": link
                        }
                        jobs.append(job)
                        logging.info(f"Found job: {name}")

                        job_index += 1  # Increment to the next job in the list
                    except NoSuchElementException:
                        logging.info(f"No more jobs found on page {url}.")
                        break
            except Exception as e:
                logging.error(f"Error occurred on page {url}: {e}")
                
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from UQAR")
        return jobs



def scrape_universite_laval_jobs():
    logging.info("Scraping Université Laval job postings")
    jobs = []
    
    # URL for the job listings page
    url = "https://www.rh.ulaval.ca/emplois-personnel-professionnel"
    
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 1  # Initialize job index for iteration
        
        while True:
            try:
                # XPath for job name and link (with tr[#] structure for each listing)
                name_link_xpath = f"/html/body/div[3]/section/div/div/div[2]/div/div/div/div/article/div[1]/table/tbody/tr[{job_index}]/td[3]/span[2]/a"
                
                # XPath for the job posting date (without `/text()[1]`)
                date_xpath = f"/html/body/div[3]/section/div/div/div[2]/div/div/div/div/article/div[1]/table/tbody/tr[{job_index}]/td[4]/span[2]"

                # Wait for the job name/link element to be visible
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, name_link_xpath))
                )

                # Extract job name and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # Extract job posting date
                date_element = driver.find_element(By.XPATH, date_xpath)
                date_posted = date_element.text.strip()

                # Append job details to the list
                job = {
                    "school": "Université Laval",
                    "title": name,
                    "link": link,
                    "date_posted": date_posted
                }
                jobs.append(job)
                logging.info(f"Found job: {name} (Posted on: {date_posted})")

                job_index += 1  # Increment to the next job in the list
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break
    except Exception as e:
        logging.error(f"Error occurred: {e}")
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Université Laval")
        return jobs
    
    
def scrape_campion_college_jobs():
    logging.info("Scraping Campion College job postings")
    jobs = []
    
    url = "https://urcareers.uregina.ca/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&435=&225=&query_position_type_id%5B%5D=1&commit=Search"
    
    try:
        driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
        driver.get(url)
        
        job_index = 1  # Initialize job index for iteration on each page
        
        while True:
            try:
                # XPath for job name and link (with div[#] structure for each listing)
                name_link_xpath = f"/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div[6]/div[{job_index}]/div/div[1]/div[1]/h3/a"
                
                # Wait for the job name/link element to be visible
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, name_link_xpath))
                )

                # Extract job name and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "Campion College",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1  # Increment to the next job in the list
            except Exception as e:
                logging.error(f"Error or no more jobs found on page: {e}")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from Campion College")
        return jobs



def scrape_fnuniv_jobs():
    logging.info("Scraping First Nations University of Canada job postings")
    jobs = []
    
    url = "https://can241.dayforcehcm.com/CandidatePortal/en-US/Fnuniv"
    
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver

    try:
        driver.get(url)
        job_index = 1  # Initialize job index for iteration on each page
        
        while True:
            try:
                # XPath for job name and link (with li[#] structure for each listing)
                name_link_xpath = f"/html/body/div[1]/div/div[1]/main/div[3]/ul/li[{job_index}]/div[1]/div[1]/div[1]/h2/a"
                
                # Wait for the job name/link element to be visible
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, name_link_xpath))
                )

                # Extract job name and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # XPath for the date (updated to extract the parent element)
                date_xpath = f"/html/body/div[1]/div/div[1]/main/div[3]/ul/li[{job_index}]/div[1]/div[1]/div[3]"

                # Extract the date text from the element
                date_element = driver.find_element(By.XPATH, date_xpath)
                date = date_element.text.strip()

                # Append job details to the list
                job = {
                    "school": "First Nations University of Canada",
                    "title": name,
                    "link": link,
                    "date_posted": date
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1  # Increment to the next job in the list
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")
    
    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from First Nations University of Canada")
        return jobs


def scrape_stm_jobs():
    logging.info("Scraping St. Thomas More College job postings")
    jobs = []

    url = "https://stmcollege.ca/work-here/index.php"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 1
        while True:
            try:
                # XPath pattern for job title (text content) and link
                name_xpath = f"/html/body/div/div/section[2]/div/div/div[2]/div/div/div/p[{job_index}]/a/text()"
                link_xpath = f"/html/body/div/div/section[2]/div/div/div[2]/div/div/div/p[{job_index}]/a"
                
                # Wait for the name element to be present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, link_xpath))
                )

                # Extract job name using JavaScript to get the text node
                name = driver.execute_script("return arguments[0].textContent;", driver.find_element(By.XPATH, link_xpath)).strip()
                
                # Extract the link
                link = driver.find_element(By.XPATH, link_xpath).get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "St. Thomas More College",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1  # Move to the next listing
            except NoSuchElementException:
                logging.info("No more jobs found.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from St. Thomas More College")
        return jobs



def scrape_uofr_jobs():
    logging.info("Scraping University of Regina job postings")
    jobs = []

    url = "https://urcareers.uregina.ca/postings/search?utf8=%E2%9C%93&query=&query_v0_posted_at_date=&435=&225=&1245%5B%5D=7&commit=Search"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        job_index = 1
        while True:
            try:
                # XPath pattern for job title and link
                name_link_xpath = f"/html/body/div[1]/div[2]/div[2]/div[2]/div[1]/div[6]/div[{job_index}]/div/div[1]/div[1]/h3/a"
                
                # Wait for the element to be present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, name_link_xpath))
                )

                # Extract job title and link
                name_link_element = driver.find_element(By.XPATH, name_link_xpath)
                name = name_link_element.text.strip()
                link = name_link_element.get_attribute('href')

                # Append job details to the list
                job = {
                    "school": "University of Regina",
                    "title": name,
                    "link": link
                }
                jobs.append(job)
                logging.info(f"Found job: {name}")

                job_index += 1  # Move to the next listing
            except NoSuchElementException:
                logging.info("No more jobs found.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from University of Regina")
        return jobs




def scrape_uofs_jobs():
    logging.info("Scraping University of Saskatchewan job postings")
    jobs = []

    url = "https://usask.csod.com/ux/ats/careersite/14/home?c=usask&_ga=2.71808829.704237860.1693762691-333734290.1654044175"
    driver = webdriver.Chrome()  # Ensure the correct path to your webdriver
    driver.get(url)

    try:
        while True:  # Loop through pages
            job_index = 3  # Starts from 3 in the div structure
            while True:
                try:
                    # XPath patterns for job title, link, and date
                    name_xpath = f"/html/body/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[{job_index}]/div/div/div/a/p"
                    link_xpath = f"/html/body/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[{job_index}]/div/div/div/a"
                    date_xpath = f"/html/body/div/div/div[2]/div[2]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div/div[{job_index}]/div/div/div/p[2]"
                    
                    # Wait for the elements to be present
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, name_xpath))
                    )

                    # Extract job title, link, and date
                    name = driver.find_element(By.XPATH, name_xpath).text.strip()
                    link = driver.find_element(By.XPATH, link_xpath).get_attribute('href')
                    date_posted = driver.find_element(By.XPATH, date_xpath).text.strip()

                    # Append job details to the list
                    job = {
                        "school": "University of Saskatchewan",
                        "title": name,
                        "link": link,
                        "date_posted": date_posted
                    }
                    jobs.append(job)
                    logging.info(f"Found job: {name} (Posted on: {date_posted})")

                    job_index += 1  # Move to the next listing
                except NoSuchElementException:
                    logging.info("No more jobs found on this page.")
                    break

            # Check for the "Next" button and ensure it is enabled before clicking
            try:
                next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label^='Next Page']")
                if "disabled" not in next_button.get_attribute("class"):
                    driver.execute_script("arguments[0].click();", next_button)  # Click using JavaScript
                    WebDriverWait(driver, 10).until(EC.staleness_of(next_button))  # Wait for the next page to load
                else:
                    logging.info("No more pages to navigate.")
                    break
            except NoSuchElementException:
                logging.info("Next page button not found.")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    finally:
        driver.quit()
        logging.info(f"Scraped {len(jobs)} jobs from University of Saskatchewan")
        return jobs





def scrape_stmarys():
    logging.info("Scraping St. Mary's University")
    jobs = []
    url = "https://stmu.ca/careers/"
    
    driver.get(url)
    
    # Expand each section to reveal job listings (if not expanded)
    sections = driver.find_elements(By.CSS_SELECTOR, ".card-header")
    for section in sections:
        try:
            section.click()
        except Exception as e:
            logging.warning(f"Could not expand section: {e}")

    # Explicitly wait for the job elements to be present
    job_link_selector = ".card-body a"
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, job_link_selector))
    )

    job_elements = driver.find_elements(By.CSS_SELECTOR, job_link_selector)
    logging.info(f"Found {len(job_elements)} job elements on the page")
    
    for element in job_elements:
        try:
            # Scroll the element into view
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            
            # Use JavaScript to extract the text if regular method doesn't work
            title = driver.execute_script("return arguments[0].textContent;", element).strip()
            
            link = element.get_attribute("href")

            # Check if there's a date near the job title (adjust based on actual HTML structure)
            parent_div = element.find_element(By.XPATH, "..")
            try:
                date_element = parent_div.find_element(By.XPATH, "following-sibling::p")
                date_text = date_element.text.strip()
            except Exception:
                date_text = "Date not found"
            
            job = {"title": title, "school": "St. Mary's University", "date": date_text, "link": link}
            jobs.append(job)

        except Exception as e:
            logging.warning(f"Could not extract job details: {e}")

    logging.info(f"Found {len(jobs)} jobs at St. Mary's University")
    return jobs




# Combine all scraping functions, including the new scrape_stmarys function
logging.info("Starting the scraping process")
new_jobs = (
    scrape_york_university() +
    scrape_athabasca() +
    scrape_mtroyal() +
    scrape_memorial() +
    scrape_macewan_rss() +
    scrape_concordia() +
    scrape_stmarys() +
    scrape_ualberta() +
    scrape_ucalgary() +
    scrape_capilano() +
    scrape_kwantlen() +
    scrape_royal_roads() +
    scrape_sfu() +
    scrape_ubc_jobs() +
    scrape_unbc_jobs() +
    scrape_ufv_jobs() +
    scrape_uvic() +
    scrape_vancouver_island_university() +
    scrape_brandon() +
    scrape_cmu() +
    scrape_university_of_saint_boniface() +
    scrape_university_of_new_brunswick() +
    scrape_mount_allison_university() +
    scrape_st_thomas_university() +
    scrape_universite_de_moncton() +
    scrape_acadia_university() +
    scrape_cape_breton_university() +
    scrape_dalhousie_university() +
    scrape_nscad_university() +
    scrape_smu_jobs() +
    scrape_universite_sainte_anne() +
    scrape_university_of_kings_college() +
    scrape_lethbridge() +
    scrape_brock_university() +
    scrape_carleton_university() +
    scrape_huron_university() +
    scrape_kings_university_college() +
    scrape_lakehead_university() +
    scrape_nipissing_university() +
    scrape_ocad_university() +
    scrape_ontario_tech() +
    scrape_queens_university() +
    scrape_redeemer_university() +
    scrape_trent_university() +
    ##scrape_university_of_guelph() +
    scrape_university_of_ottawa() +
    ##scrape_mcmaster() +
    scrape_st_michaels() +
    scrape_u_of_toronto() + 
    scrape_trinity_college() +
    ##scrape_university_of_waterloo() +
    scrape_university_of_windsor() +
    scrape_victoria_university() +
    scrape_wilfrid_laurier_university() +
    scrape_upei() +
    scrape_bishops_university() +
    scrape_ets() +
    scrape_hec_montreal() +
    scrape_polytechnique_montreal() +
    scrape_sherbrooke() +
    scrape_uqam() +
    scrape_uqac_jobs() +
    scrape_uqar_jobs() +
    scrape_universite_laval_jobs() +
    scrape_campion_college_jobs() +
    scrape_fnuniv_jobs() +
    scrape_stm_jobs() +
    scrape_uofr_jobs() +
    scrape_uofs_jobs()
    
    
    
    
    
)
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
