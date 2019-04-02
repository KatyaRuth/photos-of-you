import argparse, os, time, json
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from dateutil.parser import parse
from datetime import datetime
from datetime import timedelta


if os.path.exists('tagged.json'):
    os.remove('tagged.json')


def check_for_chromedriver():
    command = 'chromedriver'
    has_chromedriver = any(
        os.access(os.path.join(path, command), os.X_OK) for path in
        os.environ["PATH"].split(os.pathsep))
    if not has_chromedriver:
        print("\nError: Could not find chromedriver. Please make sure you have "
              "chromedriver (http://chromedriver.chromium.org/) installed and "
              "on your PATH. Aborting.\n")
        sys.exit()


def start_session(username, password):
    print("Opening Browser...")
    wd_options = Options()
    wd_options.add_argument("--disable-notifications")
    wd_options.add_argument("--disable-infobars")
    wd_options.add_argument("--mute-audio")
    wd_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(chrome_options=wd_options)

    # Login
    driver.get("https://www.facebook.com/")
    print("Logging In...")
    email_id = driver.find_element_by_id("email")
    pass_id = driver.find_element_by_id("pass")
    email_id.send_keys(username)
    pass_id.send_keys(password)
    driver.find_element_by_id("loginbutton").click()

    return driver


def parse_date(doc):
    if doc['fb_date'] == "Today":
        doc['fb_date'] = datetime.today().strftime('%Y-%m-%d')
    elif doc['fb_date'] == "Yesterday":
        filename_date = datetime.today() - timedelta(days=1)
        doc['fb_date'] = filename_date.strftime('%Y-%m-%d')
    else:
        doc['fb_date'] = parse(doc['fb_date']).strftime("%Y-%m-%d")


def index_photos():
    # Set waits (go higher if slow internet)
    wait = WebDriverWait(driver, 10)
    main_wait = 2

    # Nav to photos I'm tagged in page
    print("Navigating to photos of you...")
    profile_url = driver.find_elements_by_css_selector('[data-type="type_user"] a:nth-child(2)')[0].get_attribute("href")
    photos_url = 'https://www.facebook.com' + profile_url.split('com')[1].split('?')[0] + "/photos_of"
    driver.get(photos_url)
    print("Scanning Photos...")
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "uiMediaThumbImg")))
    driver.find_elements_by_css_selector(".uiMediaThumbImg")[0].click()
    time.sleep(4)

    counter = 1
    current_year = 2025

    while True:
        if counter > 1500:
            main_wait = 3
        time.sleep(main_wait)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".snowliftPager.next"))).click()
        try:
            user = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="fbPhotoSnowliftAuthorName"]//a')))
            media_url = wait.until(EC.presence_of_element_located((By.XPATH,
                                                                   "//img[@class='spotlight']"))).get_attribute('src')
            is_video = "showVideo" in driver.find_element_by_css_selector(".stageWrapper").get_attribute("class")
        except (exceptions.StaleElementReferenceException, exceptions.TimeoutException):
            print('*' * 20)
            print("Received an exception")
            continue

        doc = {
            'fb_url': driver.current_url,
            'fb_date': wait.until(EC.presence_of_element_located((By.CLASS_NAME, "timestampContent"))).text,
            'fb_caption': wait.until(EC.presence_of_element_located((By.XPATH,
                                                                     '//*[@id="fbPhotoSnowliftCaption"]'))).text,
            'media_url': media_url,
            'media_type': 'video' if is_video else 'image',
        }

        parse_date(doc)
        if int(doc['fb_date'][0:4]) <= current_year:
            current_year = doc['fb_date']
        if int(doc['fb_date'][0:4]) > current_year:
            print("We have done a full loop of the photos, breaking...")
            break

        # Log to save file as we go, close when done to save
        with open('tagged.json', 'a') as f:
            f.write(json.dumps(doc) + '\n')
        f.close()

        # Log to stdout and move on
        print("%s) %s // %s" % (counter, doc['fb_date'], doc['media_url']))
        counter += 1


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Facebook Scraper')
    parser.add_argument('-u', type=str, help='FB Username')
    parser.add_argument('-p', type=str, help='FB Password')
    args = parser.parse_args()
    try:
        check_for_chromedriver()
        driver = start_session(args.u, args.p)
        index_photos()
    except KeyboardInterrupt:
        print('\nQuitting the task because your interrupted me!')
        pass
