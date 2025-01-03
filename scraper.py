import json
import os
import feedparser
import logging
import time
import re
import pandas as pd
import dateutil.parser

from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

chrome_options = Options()
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--ignore-ssl-errors')
# chrome_options.add_argument("--headless")  # Uncomment if you want to run in headless mode
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service("chromedriver.exe")

driver = webdriver.Chrome(service=service, options=chrome_options)


def scrape_memorial(existing_job_links, existing_jobs):
    logging.info("Scraping Memorial University")
    driver.get("https://www.mun.ca/hr/careers/external-job-postings/")

    # List of CSS selectors for job links
    selectors = [
        "#scope-STJ > tbody > tr > td:nth-child(2) > a",
        "#scope-MI > tbody > tr > td:nth-child(2) > a",
        "#scope-MI-IRTP > tbody > tr > td:nth-child(2) > a",
        "#scope-LI > tbody > tr.odd > td:nth-child(2) > a",
        "#scope-GC > tbody > tr > td:nth-child(2) > a"
    ]

    jobs = []

    for selector in selectors:
        logging.info(f"Using selector: {selector}")
        while True:
            try:
                # Wait until job elements are present
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                )
            except TimeoutException:
                logging.warning(f"No job elements found with selector: {selector}")
                break

            job_elements = driver.find_elements(By.CSS_SELECTOR, selector)
            logging.info(f"Found {len(job_elements)} job elements using selector {selector}")

            for element in job_elements:
                title = element.text.strip()
                link = element.get_attribute("href")

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                # Try to scrape the date, if available
                try:
                    # Navigate to the parent <tr> and then to the 4th <td> for the date
                    date_element = element.find_element(By.XPATH, "./ancestor::tr/td[4]")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job is new by comparing the link
                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "Memorial University",
                        "date": date,
                        "link": link,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job: retain the 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "school": "Memorial University",
                        "date": existing_job.get("date", date),
                        "link": link,
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {title}")

                jobs.append(job)

            # Handle pagination: Click the "Next" button if available
            try:
                next_button = driver.find_element(By.LINK_TEXT, 'Next')
                # Check if the "Next" button is disabled or not clickable
                if 'disabled' in next_button.get_attribute('class').lower():
                    logging.info("Next button is disabled. No more pages.")
                    break
                else:
                    next_button.click()
                    logging.info("Clicked Next button. Navigating to the next page.")
                    # Wait for the next page to load by waiting for job elements
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
            except NoSuchElementException:
                logging.info("Next button not found. Assuming no more pages.")
                break
            except Exception as e:
                logging.warning(f"Error clicking Next button: {e}")
                break

    logging.info(f"Found {len(jobs)} jobs at Memorial University")
    return jobs


def scrape_university_of_new_brunswick(existing_job_links, existing_jobs):
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

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                # Try to scrape the date, if available
                try:
                    # Example XPath for date; replace with actual path
                    date_element = element.find_element(By.XPATH, "./ancestor::tr/td[3]")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "University of New Brunswick",
                        "date": date,
                        "link": link,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "school": "University of New Brunswick",
                        "date": existing_job.get("date", date),
                        "link": link,
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping University of New Brunswick: {e}")

    logging.info(f"Found {len(jobs)} jobs at University of New Brunswick")
    return jobs


def scrape_mount_allison_university(existing_job_links, existing_jobs):
    logging.info("Scraping Mount Allison University")
    jobs = []
    url = "https://mta.ca/about/work-mta/employment-opportunities-academic"

    driver.get(url)

    try:
        # Define the XPath for job links
        job_link_xpath = "//*[@id='block-mount-allison-content']/div/article/div/div[2]/div/div[1]/div[4]/div/div/div/div/div/ul/li/div[1]/span/a"
        
        # Wait until job elements are present
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, job_link_xpath))
        )

        # Find all job link elements
        job_elements = driver.find_elements(By.XPATH, job_link_xpath)
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for i, element in enumerate(job_elements, start=1):
            try:
                # Scroll the element into view
                driver.execute_script("arguments[0].scrollIntoView(true);", element)

                # Extract job title and link
                title = element.text.strip()
                link = element.get_attribute("href")

                # Extract the job date using the provided XPath
                try:
                    date_element_xpath = f"//*[@id='block-mount-allison-content']/div/article/div/div[2]/div/div[1]/div[4]/div/div/div/div/div/ul/li[{i}]/div[2]/div/time"
                    date_element = driver.find_element(By.XPATH, date_element_xpath)
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                if link not in existing_job_links:
                    # New job, assign 'new_since'
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "Mount Allison University",
                        "date": date,
                        "link": link,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, check if the date has changed
                    existing_date = existing_job.get("date")
                    if existing_date != date:
                        logging.info(f"Updated date for existing job: {title} from '{existing_date}' to '{date}'")
                        job = {
                            "title": existing_job["title"],
                            "school": "Mount Allison University",
                            "date": date,
                            "link": link,
                            "new_since": existing_job.get("new_since", None)
                        }
                    else:
                        # No change in date, retain existing data
                        job = existing_job
                        logging.info(f"No date change for existing job: {title}")

                jobs.append(job)
                logging.info(f"Processed job {i}: {title}, date: {date}")

            except Exception as e:
                logging.warning(f"Could not extract job details for job index {i}: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping Mount Allison University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Mount Allison University")
    return jobs



def scrape_st_thomas_university(existing_job_links, existing_jobs):
    logging.info("Scraping St. Thomas University")
    jobs = []
    url = "https://www.stu.ca/employment/"

    driver.get(url)

    try:
        # Use a flexible selector to find all job listings
        job_elements = driver.find_elements(By.XPATH, "//div[contains(@class, 'content')]//p//a")
        logging.info(f"Found {len(job_elements)} job elements on the page")

        for job_element in job_elements:
            try:
                title = job_element.text.strip()
                link = job_element.get_attribute('href')

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                # Try to scrape the date, if available
                try:
                    # Example XPath for date; replace with actual path
                    date_element = job_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'content')]/p[2]")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "St. Thomas University",
                        "date": date,
                        "link": link,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "school": "St. Thomas University",
                        "date": existing_job.get("date", date),
                        "link": link,
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping St. Thomas University: {e}")

    logging.info(f"Found {len(jobs)} jobs at St. Thomas University")
    return jobs


def scrape_universite_de_moncton(existing_job_links, existing_jobs):
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

                # Try to scrape the date, if available
                try:
                    date_element = row.find_element(By.XPATH, ".//td[3]")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "Université de Moncton",
                        "date": date,
                        "link": link,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "school": "Université de Moncton",
                        "date": existing_job.get("date", date),
                        "link": link,
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

                jobs.append(job)

            except Exception as e:
                logging.warning(f"Could not extract job details: {e}")

    except Exception as e:
        logging.error(f"An error occurred while scraping Université de Moncton: {e}")

    logging.info(f"Found {len(jobs)} jobs at Université de Moncton")
    return jobs


def scrape_acadia_university(existing_job_links, existing_jobs):
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

                # Try to scrape the date, if available
                try:
                    # Example XPath for date; replace with actual path
                    date_element = driver.find_element(By.XPATH, f"/html/body/div[2]/div[2]/div/div/div[1]/div[2]/h4[{h4_index}]/following-sibling::p[1]")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "link": link,
                        "additional_info": additional_info,
                        "school": "Acadia University",
                        "date": date,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "link": link,
                        "additional_info": existing_job.get("additional_info", additional_info),
                        "school": "Acadia University",
                        "date": existing_job.get("date", date),
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

                jobs.append(job)

                # Increment to check the next h4 element
                h4_index += 1

            except NoSuchElementException:
                # Exit loop if there are no more h4 elements
                logging.info("No more job postings found.")
                break
            except Exception as e:
                logging.error(f"Error while scraping Acadia University: {e}")
                break

    except Exception as e:
        logging.error(f"Error while scraping Acadia University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Acadia University")
    return jobs


def scrape_cape_breton_university(existing_job_links, existing_jobs):
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

                # Try to scrape the date, if available
                try:
                    # Example XPath for date; replace with actual path
                    date_element = driver.find_element(By.XPATH, f"/html/body/main/div/div[3]/div[1]/div[{div_index}]/div/div/p[1]")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "Cape Breton University",
                        "date": date,
                        "link": link,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "school": "Cape Breton University",
                        "link": link,
                        "date": existing_job.get("date", date),
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

                jobs.append(job)

                # Increment to check the next div
                div_index += 1

            except Exception as e:
                logging.info("No more job postings found or encountered an issue")
                break

    except Exception as e:
        logging.error(f"An error occurred while scraping Cape Breton University: {e}")

    logging.info(f"Found {len(jobs)} jobs at Cape Breton University")
    return jobs


def scrape_dalhousie_university(existing_job_links, existing_jobs):
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

                    # Check if the job already exists
                    existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                    # Try to scrape the date, if available
                    try:
                        # Example XPath for date; replace with actual path
                        date_element = job_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'job-title')]/following-sibling::div[contains(@class, 'job-date')]/span")
                        date_text = date_element.text.strip()
                        date = format_date(date_text)
                    except NoSuchElementException:
                        date = None  # No date found
                    except Exception as e:
                        logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                        date = None

                    if link not in existing_job_links:
                        new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        job = {
                            "title": title,
                            "school": "Dalhousie University",
                            "date": date,
                            "link": link,
                            "new_since": new_since
                        }
                        logging.info(f"Added new job: {title}, new_since: {new_since}")
                    else:
                        # Existing job, retain 'new_since' and 'date'
                        job = {
                            "title": existing_job["title"],
                            "school": "Dalhousie University",
                            "link": link,
                            "date": existing_job.get("date", date),
                            "new_since": existing_job.get("new_since", None)
                        }
                        logging.info(f"Job already exists: {existing_job['title']}")

                    jobs.append(job)

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


def scrape_nscad_university(existing_job_links, existing_jobs):
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

            # Try to scrape the date, if available
            try:
                # Example XPath for date; replace with actual path
                date_element = driver.find_element(By.XPATH, f"/html/body/article/section/div/section/section/div[1]/section[2]/article/table/tbody/tr[{index}]/td[2]/span")
                date_text = date_element.text.strip()
                date = format_date(date_text)
            except NoSuchElementException:
                date = None  # No date found
            except Exception as e:
                logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                date = None

            # Check if the job already exists
            existing_job = next((job for job in existing_jobs if job["link"] == link), None)

            if link not in existing_job_links:
                new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                job = {
                    "title": title,
                    "school": "NSCAD University",
                    "link": link,
                    "date": date,
                    "new_since": new_since
                }
                logging.info(f"Added new job: {title}, new_since: {new_since}")
            else:
                # Existing job, retain 'new_since' and 'date'
                job = {
                    "title": existing_job["title"],
                    "school": "NSCAD University",
                    "link": link,
                    "date": existing_job.get("date", date),
                    "new_since": existing_job.get("new_since", None)
                }
                logging.info(f"Job already exists: {existing_job['title']}")

            jobs.append(job)
            logging.info(f"Added job {index}: {title}")

        except Exception as e:
            logging.warning(f"Could not extract details for job {index}: {e}")

    logging.info(f"Scraping complete. Found {len(jobs)} jobs at NSCAD University.")
    return jobs


def scrape_smu_jobs(existing_job_links, existing_jobs):
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

            # Try to scrape the date, if available
            try:
                # Example XPath for date; replace with actual path
                date_element = driver.find_element(By.XPATH, f"/html/body/div[2]/div[2]/div[1]/div[1]/div/table/tbody/tr[{row_index}]/td[2]/span")
                date_text = date_element.text.strip()
                date = format_date(date_text)
            except NoSuchElementException:
                date = None  # No date found
            except Exception as e:
                logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                date = None

            # Check if the job already exists
            existing_job = next((job for job in existing_jobs if job["link"] == link), None)

            if link not in existing_job_links:
                new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                job = {
                    "title": title,
                    "school": "Saint Mary’s University",
                    "link": link,
                    "date": date,
                    "new_since": new_since
                }
                logging.info(f"Added new job: {title}, new_since: {new_since}")
            else:
                # Existing job, retain 'new_since' and 'date'
                job = {
                    "title": existing_job["title"],
                    "school": "Saint Mary’s University",
                    "link": link,
                    "date": existing_job.get("date", date),
                    "new_since": existing_job.get("new_since", None)
                }
                logging.info(f"Job already exists: {existing_job['title']}")

            jobs.append(job)
            logging.info(f"Added job {row_index}: {title}")

            # Increment row index to process the next job
            row_index += 1

        except NoSuchElementException:
            logging.warning(f"Could not find job listing at row {row_index}. Assuming no more jobs.")
            break
        except Exception as e:
            logging.warning(f"Could not find more job listings. Last processed row: {row_index - 1}. Error: {e}")
            break

    logging.info(f"Scraping complete. Found {len(jobs)} jobs at Saint Mary’s University.")
    return jobs


def scrape_universite_sainte_anne(existing_job_links, existing_jobs):
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

                # Try to scrape the date, if available
                try:
                    # Example XPath for date; replace with actual path
                    date_element = driver.find_element(By.XPATH, f"/html/body/main/div[1]/div[1]/div[1]/div/div/div/form/table/tbody/tr[{row_index}]/td[2]/span")
                    date_text = date_element.text.strip()
                    date = format_date(date_text)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "title": title,
                        "school": "Université Sainte-Anne",
                        "link": link,
                        "date": date,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "title": existing_job["title"],
                        "school": "Université Sainte-Anne",
                        "link": link,
                        "date": existing_job.get("date", date),
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

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


def scrape_university_of_kings_college(existing_job_links, existing_jobs):
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
            title = job_element.get_attribute("title").strip()
            link = job_element.get_attribute("href")

            # Try to scrape the date, if available
            try:
                # Example XPath for date; replace with actual path
                date_element = driver.find_element(By.XPATH, f"/html/body/section[2]/div/div[{div_index}]/a/following-sibling::span")
                date_text = date_element.text.strip()
                date = format_date(date_text)
            except NoSuchElementException:
                date = None  # No date found
            except Exception as e:
                logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                date = None

            # Check if the job already exists
            existing_job = next((job for job in existing_jobs if job["link"] == link), None)

            if link not in existing_job_links:
                new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                job = {
                    "title": title,
                    "school": "University of King's College",
                    "date": date,
                    "link": link,
                    "new_since": new_since
                }
                logging.info(f"Added new job: {title}, new_since: {new_since}")
            else:
                # Existing job, retain 'new_since' and 'date'
                job = {
                    "title": existing_job["title"],
                    "school": "University of King's College",
                    "date": existing_job.get("date", date),
                    "link": link,
                    "new_since": existing_job.get("new_since", None)
                }
                logging.info(f"Job already exists: {existing_job['title']}")

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


def scrape_upei(existing_job_links, existing_jobs):
    logging.info("Scraping University of Prince Edward Island job postings")
    jobs = []

    url = "https://www.upei.ca/hr/competitions"
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
                try:
                    date_element = driver.find_element(By.XPATH, date_xpath)
                    closing_date = date_element.text.strip()
                    date = format_date(closing_date)
                except NoSuchElementException:
                    date = None  # No date found
                except Exception as e:
                    logging.warning(f"Unexpected error when extracting date for job '{title}': {e}")
                    date = None

                # Check if the job already exists
                existing_job = next((job for job in existing_jobs if job["link"] == link), None)

                if link not in existing_job_links:
                    new_since = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    job = {
                        "school": "University of Prince Edward Island",
                        "title": title,
                        "link": link,
                        "date": f"Closing date: {date}" if date else None,
                        "new_since": new_since
                    }
                    logging.info(f"Added new job: {title}, new_since: {new_since}")
                else:
                    # Existing job, retain 'new_since' and 'date'
                    job = {
                        "school": "University of Prince Edward Island",
                        "title": existing_job["title"],
                        "link": link,
                        "date": existing_job.get("date", f"Closing date: {date}" if date else None),
                        "new_since": existing_job.get("new_since", None)
                    }
                    logging.info(f"Job already exists: {existing_job['title']}")

                jobs.append(job)
                logging.info(f"Found job: {title} - Closing date: {date}")

                job_index += 1
            except NoSuchElementException:
                logging.info(f"No more jobs found after {job_index - 1} listings.")
                break
            except Exception as e:
                logging.error(f"Error occurred while scraping UPEI: {e}")
                break

    except Exception as e:
        logging.error(f"Error occurred: {e}")

    logging.info(f"Scraped {len(jobs)} jobs from UPEI")
    return jobs


# Helper function to add ordinal suffixes
def ordinal(n):
    if 11 <= (n % 100) <= 13:
        return f'{n}th'
    else:
        return f'{n}{"st" if n % 10 == 1 else "nd" if n % 10 == 2 else "rd" if n % 10 == 3 else "th"}'


# Helper function to format dates nicely
def format_date(date_string):
    if not date_string:
        return None
    try:
        parsed_date = dateutil.parser.parse(date_string)
        return parsed_date.strftime(f'%B {ordinal(parsed_date.day)}, %Y')
    except Exception as e:
        logging.warning(f"Could not parse date '{date_string}': {e}")
        return None  # Return None if parsing fails


logging.info("Starting the scraping process")


# Load existing jobs
def load_existing_jobs():
    if os.path.exists('Beans/job_listings.json'):
        with open('Beans/job_listings.json', 'r') as file:
            try:
                return json.load(file)['jobs']
            except json.JSONDecodeError:
                logging.warning("job_listings.json is corrupted. Starting with an empty list.")
                return []
    return []


logging.info("Loading existing jobs")
existing_jobs = load_existing_jobs()

# Extract the links of existing jobs to check for duplicates
existing_job_links = {job['link'] for job in existing_jobs}

# Combine all scraping functions, passing the existing job links to each function
new_jobs = (
    # scrape_york_university(existing_job_links, existing_jobs) +  # Uncomment and define if needed
    scrape_memorial(existing_job_links, existing_jobs) +  # Updated Memorial scraper
    # scrape_stmarys(existing_job_links, existing_jobs) +  # Uncomment and define if needed
    scrape_university_of_new_brunswick(existing_job_links, existing_jobs) +
    scrape_mount_allison_university(existing_job_links, existing_jobs) +
    scrape_st_thomas_university(existing_job_links, existing_jobs) +
    scrape_universite_de_moncton(existing_job_links, existing_jobs) +
    scrape_acadia_university(existing_job_links, existing_jobs) +
    scrape_cape_breton_university(existing_job_links, existing_jobs) +
    scrape_dalhousie_university(existing_job_links, existing_jobs) +
    scrape_nscad_university(existing_job_links, existing_jobs) +
    scrape_smu_jobs(existing_job_links, existing_jobs) +
    scrape_universite_sainte_anne(existing_job_links, existing_jobs) +
    scrape_university_of_kings_college(existing_job_links, existing_jobs) +
    scrape_upei(existing_job_links, existing_jobs)
)

driver.quit()

current_job_links = {job['link'] for job in new_jobs}

# Determine new and removed jobs based on the link attribute
added_jobs = [job for job in new_jobs if job['link'] not in existing_job_links]
removed_jobs = [job for job in existing_jobs if job['link'] not in current_job_links]

logging.info(f"Added jobs: {len(added_jobs)}")
logging.info(f"Removed jobs: {len(removed_jobs)}")

# Preserve 'new_since' for existing jobs and add 'new_since' for new jobs
for job in new_jobs:
    if job['link'] in existing_job_links:
        # Preserve 'new_since' for existing jobs
        job['new_since'] = next(
            (existing_job.get('new_since', datetime.now().isoformat())
             for existing_job in existing_jobs if existing_job['link'] == job['link']),
            None
        )
    else:
        # For new jobs, assign today's date as 'new_since'
        job['new_since'] = datetime.now().isoformat()

    # If no date is provided, keep it as None
    if "date" not in job or not job["date"]:
        job["date"] = None  # You can choose to keep it as None or set a specific default

# Save the new job listings with 'new_since'
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
