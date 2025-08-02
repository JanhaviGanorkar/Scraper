import yaml
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import re

def init_driver(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(10)
    return driver

def extract_all_business_data_at_once(driver):
    """Extract all business data in one pass without re-finding elements"""
    
    print("🔍 EXTRACTING ALL BUSINESS DATA IN ONE PASS...")
    
    business_data = []
    
    try:
        # Get all business containers using the working pattern
        print("📦 Finding business containers...")
        
        # Use the container pattern that was working
        containers = driver.find_elements(By.XPATH, "//div[starts-with(@id, '9999PX')]")
        
        if not containers:
            print("❌ No containers found with 9999PX pattern, trying alternatives...")
            containers = driver.find_elements(By.XPATH, "//div[contains(@id, '.X721.')]")
        
        print(f"📊 Found {len(containers)} business containers")
        
        # Process all containers at once
        for i, container in enumerate(containers[:15], 1):
            print(f"\n🔍 Processing container {i}/{min(15, len(containers))}...")
            
            try:
                # Extract all data from this container immediately
                business_info = extract_single_business_complete(driver, container, i)
                
                if business_info and business_info.get('name'):
                    business_data.append(business_info)
                    print(f"✅ Added: {business_info['name']}")
                    if business_info.get('contact') != "Not found":
                        print(f"   📞 {business_info['contact']}")
                    if business_info.get('address') != "Not found":
                        print(f"   📍 {business_info['address'][:60]}...")
                else:
                    print("⚠️ No valid business data found")
                    
            except Exception as e:
                print(f"❌ Error processing container {i}: {e}")
                continue
        
    except Exception as e:
        print(f"❌ Error in main extraction: {e}")
    
    return business_data

def extract_single_business_complete(driver, container, index):
    """Extract complete business info from a single container"""
    
    business_info = {
        'name': "Not found",
        'contact': "Not found", 
        'address': "Not found"
    }
    
    try:
        # Get container ID for specific XPath construction
        container_id = container.get_attribute('id')
        
        # Extract name - look for H3 within this container
        try:
            h3_elements = container.find_elements(By.XPATH, ".//h3")
            for h3 in h3_elements:
                text = h3.text.strip()
                if text and len(text) > 3:
                    # Check if it looks like a business name
                    business_keywords = ['hotel', 'shop', 'bar', 'grill', 'food', 'kitchen']
                    text_lower = text.lower()
                    if (any(keyword in text_lower for keyword in business_keywords) or 
                        len(text.split()) >= 2):
                        business_info['name'] = text
                        break
        except Exception as e:
            print(f"   ⚠️ Name extraction error: {e}")
        
        # Extract contact - try multiple methods within this container
        try:
            # Method 1: callcontent class
            callcontent_elements = container.find_elements(By.XPATH, ".//span[contains(@class, 'callcontent')]")
            for el in callcontent_elements:
                text = el.text.strip()
                phone_match = re.search(r'(\d{10,11})', text)
                if phone_match:
                    business_info['contact'] = phone_match.group(1)
                    break
            
            # Method 2: If no callcontent found, try other patterns
            if business_info['contact'] == "Not found":
                phone_patterns = [
                    ".//span[contains(text(), '08')]",  # Numbers starting with 08
                    ".//span[contains(text(), '9')]",
                    ".//span[contains(text(), '8')]", 
                    ".//span[contains(text(), '7')]",
                ]
                
                for pattern in phone_patterns:
                    elements = container.find_elements(By.XPATH, pattern)
                    for el in elements:
                        text = el.text.strip()
                        phone_match = re.search(r'(\d{10,11})', text)
                        if phone_match:
                            business_info['contact'] = phone_match.group(1)
                            break
                    if business_info['contact'] != "Not found":
                        break
                        
        except Exception as e:
            print(f"   ⚠️ Contact extraction error: {e}")
        
        # Extract address - try multiple methods within this container
        try:
            # Method 1: locatcity class (this was working)
            locatcity_elements = container.find_elements(By.XPATH, ".//div[contains(@class, 'locatcity')]")
            for el in locatcity_elements:
                text = el.text.strip()
                if text and len(text) > 10:
                    business_info['address'] = text
                    break
            
            # Method 2: If no locatcity found, try other patterns
            if business_info['address'] == "Not found":
                address_patterns = [
                    ".//*[contains(text(), 'Indore')]",
                    ".//*[contains(text(), 'Road')]",
                    ".//*[contains(text(), 'Area')]",
                    ".//*[contains(text(), 'Nagar')]",
                ]
                
                for pattern in address_patterns:
                    elements = container.find_elements(By.XPATH, pattern)
                    for el in elements:
                        text = el.text.strip()
                        if text and len(text) > 10:
                            # Check if it contains location keywords
                            location_keywords = ['road', 'area', 'street', 'nagar', 'chowk', 'square', 'amravati']
                            if any(keyword in text.lower() for keyword in location_keywords):
                                business_info['address'] = text
                                break
                    if business_info['address'] != "Not found":
                        break
                        
        except Exception as e:
            print(f"   ⚠️ Address extraction error: {e}")
        
    except Exception as e:
        print(f"   ❌ Complete extraction error for container {index}: {e}")
    
    return business_info

def save_to_csv(business_data, filename="allresults.csv"):
    """Save business data to CSV"""
    if not business_data:
        print("❌ No data to save!")
        return
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['name', 'contact', 'address']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for business in business_data:
            writer.writerow(business)
    
    print(f"✅ Saved {len(business_data)} businesses to {filename}")

def main():
    print("🚀 Starting FIXED JustDial Scraper (No Page White Issue)...")
    
    # Load config
    with open("/home/janhavi/Dora_world/Scraper/XPath-Scraper/config.yml", "r") as f:
        config = yaml.safe_load(f)
    
    driver = init_driver(headless=False)
    
    try:
        print(f"🌐 Loading: {config['url']}")
        driver.get(config['url'])
        
        print("⏳ Waiting for page to load completely...")
        sleep(15)  # Give more time for page to load
        
        print(f"📄 Page title: {driver.title}")
        
        # Scroll to load all content ONCE
        print("📜 Loading all content...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        sleep(2)
        
        # Test patterns first
        print("🧪 Testing patterns...")
        callcontent_count = len(driver.find_elements(By.XPATH, "//span[contains(@class, 'callcontent')]"))
        locatcity_count = len(driver.find_elements(By.XPATH, "//div[contains(@class, 'locatcity')]"))
        container_count = len(driver.find_elements(By.XPATH, "//div[starts-with(@id, '9999PX')]"))
        
        print(f"   📞 Found {callcontent_count} phone elements")
        print(f"   📍 Found {locatcity_count} address elements") 
        print(f"   📦 Found {container_count} business containers")
        
        if container_count == 0:
            print("❌ No business containers found!")
            return
        
        # Extract all business data in one pass
        business_data = extract_all_business_data_at_once(driver)
        
        print(f"\n📊 FINAL RESULTS:")
        print(f"Total businesses extracted: {len(business_data)}")
        
        # Show statistics
        complete_entries = sum(1 for b in business_data if b['contact'] != "Not found" and b['address'] != "Not found")
        with_contact = sum(1 for b in business_data if b['contact'] != "Not found")
        with_address = sum(1 for b in business_data if b['address'] != "Not found")
        
        print(f"📊 Complete entries (name + contact + address): {complete_entries}")
        print(f"📞 Entries with contact: {with_contact}")
        print(f"📍 Entries with address: {with_address}")
        
        if business_data:
            print("\n🏢 EXTRACTED BUSINESSES:")
            for i, business in enumerate(business_data, 1):
                print(f"\n{i}. {business['name']}")
                print(f"   📞 {business['contact']}")
                print(f"   📍 {business['address']}")
            
            save_to_csv(business_data)
        else:
            print("❌ No businesses extracted.")
        
        print("\n✅ Scraping completed successfully!")
        input("\n👀 Press Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    main()