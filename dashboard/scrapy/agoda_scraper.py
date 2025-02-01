from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dashboard.models import Hotel
import time

def fetch_agoda_data(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)
    
    # Wait for the page to load completely
    time.sleep(10)
    
    # Extract the page source
    html_content = driver.page_source
    driver.quit()

    # Debug: Save HTML content to a file
    with open('agoda_page.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return html_content
def extract_agoda_hotels(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    hotels = []

    for hotel in soup.select('div.PropertyCardItem'):
        name = hotel.select_one('h3.PropertyCard__HotelName').text.strip() if hotel.select_one('h3.PropertyCard__HotelName') else ''
        price = hotel.select_one('span.Price__Value').text.strip().replace('$', '') if hotel.select_one('span.Price__Value') else None
        rating = hotel.select_one('span.ReviewScore__Score').text.strip() if hotel.select_one('span.ReviewScore__Score') else ''
        link = f"https://www.agoda.com{hotel.select_one('a.PropertyCard__Link')['href']}" if hotel.select_one('a.PropertyCard__Link') else ''
        image = hotel.select_one('img.PropertyCard__Image')['src'] if hotel.select_one('img.PropertyCard__Image') else ''

        hotels.append({'name': name, 'image_url': image, 'price': price, 'rating': rating, 'url': link})
    
    print(f"Extracted {len(hotels)} hotels from Agoda")  # Debug
    return hotels
def save_agoda_hotels(url):
    html_content = fetch_agoda_data(url)
    if html_content:
        hotels = extract_agoda_hotels(html_content)
        for hotel in hotels:
            obj, created = Hotel.objects.update_or_create(
                name=hotel['name'],
                defaults={
                    'image_url': hotel['image_url'],
                    'price_agoda': float(hotel['price']) if hotel['price'] else None,
                    'star_rating': float(hotel['rating']) if hotel['rating'] else 0.0,
                    'agoda_url': hotel['url'],
                }
            )
            print(f"Saved/Updated Hotel: {hotel['name']}")  # Debug
        return True
    return False