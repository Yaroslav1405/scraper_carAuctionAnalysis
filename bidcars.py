# Import required modules
from seleniumbase import Driver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time



# Function to extract the data
def extracting_data(MAX_PAGES = 21):
    # Url of website page to log in and scrap
    login_url = 'https://bid.cars/en/login'
    scrape_url = 'https://bid.cars/en/search/archived/results?search-type=filters&type=Automobile&make=BMW&model=3+Series&year-from=2013&year-to=2019&airbags=Intact&order-by=dateDesc'
    
    # Login credentials
    email = 'email'
    password = 'password'
    
    
    # Intitialization of DataFrame to store scraped data
    df = pd.DataFrame(columns=[
                'Name', 'Price', 'Auction Name', 'Date of Sale', 'Condition',
                'VIN', 'Mileage', 'Seller', 'Documents', 'Key', 'Location',
                'Damage', 'Auction Type', 'Transmission'
            ])
    
    # Intitialization of page count
    page_count = 1
    
    # Intitialization of Selenium driver
    driver = Driver(uc=True)
    
    # Connect to login page
    driver.uc_open_with_reconnect(login_url, 10)
    
    # Find login and password fields and send keys
    driver.find_element(By.NAME, 'login').send_keys(email)
    time.sleep(3)
    driver.find_element(By.NAME, 'password').send_keys(password)
    driver.uc_click("button.btn-primary.g-recaptcha")
        
    # Open URL to scrape
    driver.uc_open_with_reconnect(scrape_url, 10)
    
    
    
    # Loop to scrape multiple pages, up to MAX_PAGES
    while page_count < MAX_PAGES:
        
        # Parse the current page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'lxml')
        
        # Extract all car data from the page
        data = soup.find_all('div', class_ = 'item-horizontal lots-search red')
        print(f'Number of cars found on page {page_count}: {len(data)}')

        # Process the last 50 cars on the page
        for car in data[-50:]:
        
            try:   
                # Extract details of the car  
                name = car.find('a', class_='damage-info').text
                price = car.find('div', class_='price-box').text if car.find('div', class_='price-box') else "N/A"
                auction_name = car.find('span', class_='item-seller').text
                sale_date = car.find('div', class_='date no-wrap-text-ellipsis').text
                condition =car.find('strong').text
                mileage = car.find('li', class_='odo_desc no-wrap-text-ellipsis').text
                vin = car.find('span', class_='vin_title').text
                seller = car.find('li', class_='seller_desc').text
                location = car.find('li', class_='loc_desc no-wrap-text-ellipsis').text
                documents = car.find('li', class_='doc_desc').text
                damage = car.find_all('li',class_='damage-info')[1].text
                sold_parameter = car.find_all('div', class_='price-box')
                sold_by = sold_parameter[1].text if len(sold_parameter) > 1 else 'Past Auction'
                additional_info = soup.find_all('span', {'data-original-title': True})
                key_status = additional_info[0]['data-original-title']
                transmission = additional_info[1]['data-original-title']
        
                # Store car details in dictionary
                car_data = {
                        'Name': name, 'Price': price, 
                        'Auction Name': auction_name, 
                        'Date of Sale': sale_date, 
                        'Condition': condition, 'VIN': vin, 
                        'Mileage': mileage, 'Seller': seller, 
                        'Documents': documents, 'Key': key_status,
                        'Location': location, 'Damage': damage, 
                        'Auction Type': sold_by, 
                        'Transmission': transmission
                }    

                # Append the car data to the DataFrame
                df = pd.concat([df, pd.DataFrame([car_data])], ignore_index=True)
                
                # Sleep for two seconds
                time.sleep(3)
            except Exception as e:
                # Handle any exceptions to ensure the code does not crash
                print(f'Error in the process: {e}')    
        
        # Save the scraped data to a CSV file after each page
        print(f'Saving data from page {page_count} to csv...') 
        df.to_csv('bidcars.csv', index=False)
        
        # Click on the "Load More" button to load more items
        try:
            load_more = driver.find_element('link text', 'Load More...')
            load_more.click()
            print(f'Reached the end of page {page_count}, loading more content...')
            time.sleep(3)
            
            # Wait for the next set of cars to load
            WebDriverWait(driver, 45).until(
                lambda driver: len(driver.find_elements(By.CLASS_NAME, 'item-horizontal')) > len(data)
            )
            
            # Scroll to the "Load More" button to make it visible
            driver.execute_script("arguments[0].scrollIntoView();", load_more)
            time.sleep(3)
            
            # Increment page count     
            page_count +=1
        except Exception as e:
            # Handle the case where the "Load More" button doesn't exist
            print(f'No more content to load. Stopping scrapping process. Error: {e}')
            break

    # Close the driver after all pages are processed
    driver.close()
    driver.quit()
        


# Main function
def main():
    start_time = time.time()
    extracting_data()
    print('*'*40)
    print(f'\n\nTime to complete the scraping: {time.time()- start_time}\n\n')
    print('*'*40)

# Entry point of the script
if __name__ == '__main__':
    main()