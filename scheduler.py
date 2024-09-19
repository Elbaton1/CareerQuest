import subprocess
import time

def run_scraper():
    try:
        # Run the scraping script by calling the Python command in the terminal
        subprocess.run(["python", "C:\\Users\\mobri\\Documents\\School\\mun-job-listings\\scraper.py"], check=True)
        print("Scraper ran successfully.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

def main():
    while True:
        run_scraper()  # Run the scraper function
        print("Waiting for 12 hours before the next run...")
        time.sleep(12 * 60 * 60)  # Wait for 12 hours (12 hours * 60 minutes * 60 seconds)

if __name__ == "__main__":
    main()
