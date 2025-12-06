import streamlit as st
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def get_driver():
    options = Options()
    options.add_argument("--headless=new")  # run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_page(driver, url):
    driver.get(url)
    time.sleep(2)

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

def get_total_pages(driver, base_url):
    driver.get(base_url)
    time.sleep(2)
    pages = driver.find_elements(By.CSS_SELECTOR, "a.srpgn")
    nums = []
    for p in pages:
        try:
            nums.append(int(p.text))
        except:
            pass
    return max(nums) if nums else 1

def full_scrape(base_url):
    driver = get_driver()
    total_pages = get_total_pages(driver, base_url)
    all_data = []

    for i in range(1, total_pages + 1):
        st.info(f"Scraping page {i} of {total_pages}...")
        page_url = base_url.replace(".html", f"/{i}.html")
        all_data.extend(scrape_page(driver, page_url))

    driver.quit()
    df = pd.DataFrame(all_data, columns=["User", "Time", "Message"])
    df.drop_duplicates(inplace=True)
    return df

# -----------------------------
# STREAMLIT APP
# -----------------------------

st.title("MoneyControl Forum Scraper")
st.markdown("Paste the forum URL of any company (e.g., IRCTC, Tata) to scrape posts.")

url_input = st.text_input("Enter MoneyControl Forum URL:")

if st.button("Scrape Forum"):
    if url_input.strip() == "":
        st.warning("Please enter a valid URL!")
    else:
        with st.spinner("Scraping forum… This may take a few minutes depending on pages…"):
            df = full_scrape(url_input.strip())
        st.success(f"Scraping completed! Total posts: {len(df)}")
        st.dataframe(df)

        csv_file = "forum_data.csv"
        df.to_csv(csv_file, index=False)
        st.download_button(
            label="Download CSV",
            data=open(csv_file, "rb").read(),
            file_name="forum_data.csv",
            mime="text/csv"
        )
