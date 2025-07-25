# Import required modules
from seleniumbase import Driver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Function to extract the data
def extracting_data(MAX_PAGES = 4):
    url = 'https://bid.cars/en/search/archived/results?search-type=filters&type=Automobile&make=BMW&model=3%20Series&year-from=2013&year-to=2019&order-by=dateDesc'
    df = pd.DataFrame(columns=[
                'Name', 'Price', 'Auction Type', 'Date of Sale', 'Sold by', 
                'Condition', 'Mileage', 'Seller', 'Location', 'Damage', 
                'Transmission', 'VIN'
            ])
    page_count = 1
    processed_cars = set()
    driver = Driver(uc=True)
    driver.uc_open_with_reconnect(url, 10)
    
    while page_count < MAX_PAGES:
        
        soup = BeautifulSoup(driver.page_source, 'lxml')
        data = soup.find_all('div', class_ = 'item-horizontal lots-search')
        print(f'Number of cars found on page {page_count}: {len(data)}')

        # Run for loop in reversed order(explanation in the documentation)
        for car in reversed(data): # Alt solution to scrap only 50 in reversed order from data and then load more, that way we won't need to check for lot number.
            
            try:
                # Find lot number 
                lot_number = car.find('ul').find('li').find('span').next_sibling.strip()
                
                # Check for lot number if it was already processed
                if lot_number in processed_cars:
                    print(lot_number)
                    try:
                        # Press button to load more cars, and break the loop
                        load_more = driver.find_element('link text', 'Load More...')
                        load_more.click()
                        time.sleep(2)
                        print(f'Reached the end of page {page_count}, loading more content...')
                        
                        # Wait for new items to be loaded
                        WebDriverWait(driver, 20).until(
                            lambda driver: len(driver.find_elements(By.CLASS_NAME, 'item-horizontal')) > len(data)
                        )
                        # Increment page count     
                        page_count +=1
                        break
                    except Exception as e:
                        print(f'Error when pressing Load More... button: {e}')
                        return
                            
                
                # Extract car details 
                name = car.find('a', class_='damage-info').text
                price = car.find('div', class_='price-box').text.split(':')[1].strip()
                auction_name = car.find('span', class_='item-seller').text
                sale_date = car.find('div', class_='date no-wrap-text-ellipsis').text
                condition =car.find('strong').text
                info = car.find_all('li', class_='no-wrap-text-ellipsis')
                mileage = info[1].text.split(':')[1].strip()
                vin = info[0].text.split(':')[1].strip()
                seller = info[3].text.split(':')[1].strip()
                location = info[2].text.split(':')[1].strip()
                info2 = car.find_all('li', class_='damage-info')
                documents = info2[0].text.split(':')[1].strip()
                damage = info2[1].text.split(':')[1].strip()
                sold_by = car.find('div', class_='bid-status status-orange').text
                
                # Dictionary to store our vehicle info
                car_data = {
                        'Name': name, 'Price': price, 
                        'Auction Name': auction_name, 
                        'Date of Sale': sale_date, 
                        'Condition': condition, 'VIN': vin, 
                        'Mileage': mileage, 'Seller': seller, 
                        'Documents': documents, 'Location': location, 
                        'Damage': damage, 'Auction Type': sold_by
                }    

                # Add lot number into processed cars
                processed_cars.add(lot_number)

                # Concatenate our data into dataframe
                df = pd.concat([df, pd.DataFrame([car_data])], ignore_index=True)
                
                # Sleep for two seconds
                time.sleep(2)
            except Exception as e:
                print(f'Error in the process: {e}')    
        
        # Save to csv
        print(f'Saving data from page {page_count} to csv...') 
        df.to_csv('bidcars.csv', index=False)

    # Close drivers
    driver.close()
    driver.quit()
        


# Main function
def main():
    start_time = time.time()
    extracting_data()
    print('*'*40)
    print(f'\n\nTime to complete the scraping: {time.time()- start_time}\n\n')
    print('*'*40)


if __name__ == '__main__':
    main()