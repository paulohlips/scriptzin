import os
import pickle
import random
from time import sleep

from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from constants import MESSAGES

load_dotenv()

username = os.getenv('LINKEDIN_USERNAME')
password = os.getenv('LINKEDIN_PASS')

def format_message(recruiter_name: str, stack: str, lenguage: str) -> str:
    message_template = MESSAGES[stack][lenguage].format(recruiter_name=recruiter_name)
    return message_template

def initialize_driver():
    driver = webdriver.Chrome()
    driver.get('https://www.linkedin.com/login')
    
    if os.path.exists('cookies.pkl'):
        load_cookies(driver, 'cookies.pkl')
        driver.get('https://www.linkedin.com')
    
    return driver

def save_cookies(driver, file_path):
    with open(file_path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, file_path):
    with open(file_path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)

def login(driver, username, password):
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'username'))
    )
    input_username = driver.find_element(By.ID, 'username')
    input_username.send_keys(username)
    input_password = driver.find_element(By.ID, 'password')
    input_password.send_keys(password)
    input_password.send_keys(Keys.RETURN)

def wait_for_page_load():
    sleep(5)

def accept_cookies(driver):
    try:
        accept_cookies_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Accept cookies"]'))
        )
        random_sleep()
        accept_cookies_btn.click()
    except Exception:
        pass

def add_note_and_send_invite(driver, button, recruiter_name):
    button.click()
    random_sleep()

    send_now = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label^="Add a note"]'))
    )
    send_now.click()
    random_sleep()

    try:
        email_input = driver.find_element(By.NAME, "email")
        dismiss_button = driver.find_element(By.CSS_SELECTOR, '[aria-label="Dismiss"]')
        dismiss_button.click()
        random_sleep()
        return False
    except Exception:
        pass

    message_textarea = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, "message"))
    )
    message_textarea.clear()

    message = format_message(recruiter_name, "backend", "EN")
    print(message)
    
    message_textarea.send_keys(message)

    send_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Send invitation"]'))
    )
    send_button.click()
    random_sleep()
    return True

def navigate_and_send_invites(driver, url):
    page_num = 1
    url += f"&page={page_num}"
    invites = 0

    while True:
        if invites == 50: break

        url = url[:url.index("page=")] + f"page={page_num}"
        driver.get(url)

        random_sleep()
        try:
            connect_buttons = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[aria-label^="Invite"]'))
            )
        except Exception as e:
            print(f"Exception: {e}")
            page_num += 1
            continue
        
        for button in connect_buttons:
            try:
                aria_label = button.get_attribute('aria-label')
                recruiter_name = aria_label.replace('Invite ', '').replace(' to connect', '').split()[0]
                success = add_note_and_send_invite(driver, button, recruiter_name)
                if success:
                    invites += 1
            except Exception as e:
                print(f"Exception: {e}")
                continue

        page_num += 1
    
    print(f"Número de convites: #{invites}")

def random_sleep():
    sleep(random.uniform(1, 2))

if __name__ == "__main__":
    driver = initialize_driver()
    try:
        if not os.path.exists('cookies.pkl'):
            login(driver, username, password)
            wait_for_page_load()
            accept_cookies(driver)
            save_cookies(driver, 'cookies.pkl')
        
        linkedin_url = 'https://www.linkedin.com/search/results/people/?activelyHiringForJobTitles=%5B%22-100%22%5D&geoUrn=%5B%22106057199%22%5D&keywords=tech%20recruiter&origin=FACETED_SEARCH&sid=!2N'
        navigate_and_send_invites(driver, linkedin_url)
    finally:
        driver.quit()
