from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
import time
import csv
import random
import os
from pathlib import Path
import subprocess

def extract_cafe_details(driver):
    """Extract name, address, and phone from the details panel with direct extraction"""
    cafe_details = {
        'name': 'N/A',
        'address': 'N/A',
        'phone': 'N/A'
    }
    
   
    wait = WebDriverWait(driver, 10)
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.fontBodyMedium")))
        
      
        try:
            name_elements = driver.find_elements(By.CSS_SELECTOR, "h1.fontHeadlineLarge, h1.DUwDvf, h1.fontHeadlineMedium")
            if name_elements:
                cafe_details['name'] = name_elements[0].text.strip()
            
          
            if cafe_details['name'] == 'N/A':
                name_elements = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc, span.a5H0ec")
                for elem in name_elements:
                    if elem.get_attribute("aria-label"):
                        cafe_details['name'] = elem.get_attribute("aria-label").strip()
                        break
                    elif elem.text.strip():
                        cafe_details['name'] = elem.text.strip()
                        break
        except Exception as e:
            print(f"Error extracting name: {e}")
        
    
        try:
            print("Looking for address and phone elements...")
            info_divs = driver.find_elements(By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc")
            
            for div in info_divs:
                try:
                    text = div.text.strip()
                    if not text:
                        continue
                        
                
                    digits = ''.join(filter(str.isdigit, text))
                    if len(digits) >= 10 and len(digits) / len(text) > 0.5:
                        if cafe_details['phone'] == 'N/A':
                            cafe_details['phone'] = text
                            print(f"Successfully extracted phone: {text}")
                    
                  
                    elif any(indicator in text.lower() for indicator in [
                        'street', 'road', 'avenue', 'temple', 'colony', 'nagar', 'maharashtra', 
                        'delhi', 'backside', 'behind', 'opposite', 'above', 'floor'
                    ]):
                        if cafe_details['address'] == 'N/A':
                            cafe_details['address'] = text
                            print(f"Successfully extracted address: {text}")
                except StaleElementReferenceException:
                    continue
        
            if cafe_details['address'] == 'N/A':
                address_elements = driver.find_elements(By.CSS_SELECTOR, "div.Io6YTe.fontBodyMedium")
                for elem in address_elements:
                    try:
                        text = elem.text.strip()
                        if any(indicator in text.lower() for indicator in [
                            'street', 'road', 'avenue', 'temple', 'colony', 'nagar', 'maharashtra', 
                            'delhi', 'backside', 'behind', 'opposite', 'above', 'floor'
                        ]):
                            cafe_details['address'] = text
                            print(f"Extracted address from fallback: {text}")
                            break
                    except StaleElementReferenceException:
                        continue
       
            if cafe_details['phone'] == 'N/A':
            
                try:
                    phone_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-item-id^='phone:tel:']")
                    for button in phone_buttons:
                        data_id = button.get_attribute("data-item-id")
                        if data_id and "phone:tel:" in data_id:
                            phone = data_id.replace("phone:tel:", "")
                            if len(phone) >= 10:
                                cafe_details['phone'] = phone
                                print(f"Extracted phone from data-item-id: {phone}")
                                break
                except Exception as e:
                    print(f"Error extracting phone: {e}")
                    
            
                try:
                    phone_buttons = driver.find_elements(By.CSS_SELECTOR, "button.CsEnBe")
                    for button in phone_buttons:
                        aria_label = button.get_attribute("aria-label")
                        if aria_label and "Phone:" in aria_label:
                            phone = aria_label.replace("Phone:", "").strip()
                            cafe_details['phone'] = phone
                            print(f"Extracted phone from aria-label: {phone}")
                            break
                except Exception as e:
                    print(f"Error extracting phone via aria-label: {e}")
                
        except Exception as e:
            print(f"Error extracting info: {e}")
            
    except Exception as e:
        print(f"Error waiting for details panel: {e}")
        
    return cafe_details

def find_chrome():
    """Find Chrome executable on Linux Mint"""
    possible_paths = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
  
    try:
        chrome_path = subprocess.check_output(["which", "google-chrome"], text=True).strip()
        if chrome_path:
            return chrome_path
    except:
        pass
    
    try:
        chromium_path = subprocess.check_output(["which", "chromium-browser"], text=True).strip()
        if chromium_path:
            return chromium_path
    except:
        pass
        
 
    return None

def find_chromedriver():
    """Find chromedriver executable on Linux Mint"""
    try:
        driver_path = subprocess.check_output(["which", "chromedriver"], text=True).strip()
        if driver_path and os.path.exists(driver_path):
            return driver_path
    except:
        pass
        

    possible_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
  
    return None

def main():
  
    chrome_path = find_chrome()
    driver_path = find_chromedriver()
    
    if not chrome_path:
        print("Chrome/Chromium browser not found. Please install it first.")
        return
        
    print(f"Using Chrome at: {chrome_path}")
    if driver_path:
        print(f"Using ChromeDriver at: {driver_path}")
    
    
    options = Options()
    
    
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-dev-shm-usage")  
    options.add_argument("--no-sandbox")  
    

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    
   
    options.add_argument("--disable-gpu") 
    
   
    options.add_argument("--start-maximized")
    
   
    user_agents = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
  
    if chrome_path:
        options.binary_location = chrome_path
    
  
    print("Starting Chrome browser...")
    if driver_path:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    try:
        print("Opening Google Maps...")
        driver.get("https://www.google.com/maps")
        time.sleep(5) 
        
        print("Entering search query...")
        try:
            search_box = driver.find_element(By.ID, "searchboxinput")
            search_box.clear()
            
            search_query = input("Enter your search query: ")
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.ENTER)
            
            print(f"Searching for: {search_query}")
            time.sleep(7)  
            
        except Exception as e:
            print(f"Error finding search box: {e}")
            print("Trying alternative method...")
            
         
            try:
                driver.find_element(By.CSS_SELECTOR, "div#searchbox").click()
                time.sleep(1)
                search_box = driver.find_element(By.ID, "searchboxinput")
                search_box.clear()
                
                search_query = input("Enter your search query: ")
                search_box.send_keys(search_query)
                search_box.send_keys(Keys.ENTER)
                
                print(f"Searching for: {search_query}")
                time.sleep(7)
            except Exception as e2:
                print(f"Still can't find search box: {e2}")
                return
        
    
        wait = WebDriverWait(driver, 15)
        try:
            scrollable_div = wait.until(EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]')))
            print("Found results container")
            
           
            print("Scrolling to load more results...")
            for i in range(3):
                driver.execute_script('arguments[0].scrollTop = arguments[0].scrollHeight', scrollable_div)
                time.sleep(2)
                
        except Exception as e:
            print(f"Error finding results container: {e}")
            return
        
        # Process cafes
        cafe_data = []
        max_cafes = 10
        processed = 0
        
        while processed < max_cafes:
            print(f"\n{'='*50}")
            print(f"Processing cafe {processed+1}/{max_cafes}")
            print(f"{'='*50}")
            
          
            if processed > 0:
                delay = random.uniform(1, 3)
                print(f"Waiting {delay:.1f} seconds...")
                time.sleep(delay)
            
            try:
                
                cafe_links = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
                
                if processed >= len(cafe_links):
                    print(f"No more cafes to process. Found {len(cafe_links)} total.")
                    break
                    
              
                print(f"Clicking on cafe {processed+1}...")
                
             
                try:
                 
                    driver.execute_script("arguments[0].click();", cafe_links[processed])
                except:
                  
                    cafe_links[processed].click()
                    
                time.sleep(3)  
                
             
                print(f"Extracting details for cafe {processed+1}...")
                details = extract_cafe_details(driver)
                
                print(f"Cafe {processed+1}:")
                print(f"  Name: {details['name']}")
                print(f"  Address: {details['address']}")
                print(f"  Phone: {details['phone']}")
                
                cafe_data.append(details)
                
             
                print("Going back to results list...")
                try:
                    back_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Back']")
                    if back_buttons:
                        driver.execute_script("arguments[0].click();", back_buttons[0])
                        time.sleep(2)
                    else:
                     
                        driver.back()
                        time.sleep(3)
                        
                 
                    processed += 1
                        
                except Exception as e:
                    print(f"Error navigating back: {e}")
              
                    driver.get("https://www.google.com/maps/search/" + search_query.replace(" ", "+"))
                    time.sleep(5)
            
            except Exception as e:
                print(f"Error processing cafe {processed+1}: {e}")
                processed += 1  
                try:
                    driver.get("https://www.google.com/maps/search/" + search_query.replace(" ", "+"))
                    time.sleep(5)
                except:
                    pass
        
        
        if cafe_data:
            results_file = 'results.csv'
            with open(results_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=['name', 'address', 'phone'])
                writer.writeheader()
                for cafe in cafe_data:
                    writer.writerow(cafe)
            print(f"\nSaved {len(cafe_data)} results to {results_file}")
        else:
            print("\nNo data to save")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        print("\nClosing browser...")
        try:
            driver.quit()
        except:
            print("Browser already closed")

if __name__ == "__main__":
    main()
