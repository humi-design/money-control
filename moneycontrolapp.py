import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_URL = "https://mmb.moneycontrol.com/forum-topics/stocks/irctc-511034.html"
OUTPUT_FILE = "forum_data.csv"
CHROMEDRIVER_PATH = " /Users/somilupadhyay/Downloads/chrome-mac-arm64"  # <-- your downloaded path
SLEEP_TIME = 3

# -----------------------------
# SETUP SELENIUM DRIVER
# -----------------------------
def get_driver():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--headless=new")  # comment out if you want to see browser
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# -----------------------------
# SCRAPE SINGLE PAGE
# -----------------------------
def scrape_page(driver, url):
    driver.get(url)
    time.sleep(SLEEP_TIME)

    posts = driver.find_elements(By.CSS_SELECTOR, ".FL.pr.bseForumData")
    data = []

    for post in posts:
        try:
            user = post.find_element(By.CSS_SELECTOR, ".gry").text.strip()
            time_posted = post.find_element(By.CSS_SELECTOR, ".PT15").text.strip()
            msg = post.find_element(By.CSS_SELECTOR, ".FL.wid652").text.strip()
            data.append([user, time_posted, msg])
        except:
            pass

    return data

# -----------------------------
# GET TOTAL PAGES
# -----------------------------
def get_total_pages(driver):
    driver.get(BASE_URL)
    time.sleep(SLEEP_TIME)
    pages = driver.find_elements(By.CSS_SELECTOR, "a.srpgn")
    nums = []

    for p in pages:
        try:
            nums.append(int(p.text))
        except:
            pass

    return max(nums) if nums else 1

# -----------------------------
# FULL SCRAPE (ALL PAGES)
# -----------------------------
def full_scrape():
    driver = get_driver()
    total = get_total_pages(driver)
    print(f"Total pages found: {total}")

    all_data = []

    for i in range(1, total + 1):
        print(f"Scraping page {i} ...")
        page_url = BASE_URL.replace(".html", f"/{i}.html")
        all_data.extend(scrape_page(driver, page_url))

    driver.quit()

    df = pd.DataFrame(all_data, columns=["User", "Time", "Message"])
    df.drop_duplicates(inplace=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\nFull scrape complete → Saved to {OUTPUT_FILE}")

# -----------------------------
# INCREMENTAL UPDATE (NEW POSTS ONLY)
# -----------------------------
def incremental_update():
    try:
        old_df = pd.read_csv(OUTPUT_FILE)
    except:
        print("No existing CSV found → performing full scrape.")
        return full_scrape()

    driver = get_driver()
    print("Checking new posts on Page 1 ...")
    new_data = scrape_page(driver, BASE_URL)
    driver.quit()

    new_df = pd.DataFrame(new_data, columns=["User", "Time", "Message"])
    combined = pd.concat([old_df, new_df])
    combined.drop_duplicates(inplace=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print("\nIncremental update completed. CSV updated with new posts.")

# -----------------------------
# MAIN EXECUTION
# -----------------------------
if __name__ == "__main__":
    print("1. Full scrape (all pages)")
    print("2. Incremental update (only new posts)")
    choice = input("Select option (1/2): ")

    if choice == "1":
        full_scrape()
    elif choice == "2":
        incremental_update()
    else:
        print("Invalid choice. Exiting.")
