import requests
from bs4 import BeautifulSoup
from dashboard.models import Hotel

def fetch_booking_data(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    print(f"Booking Response Status: {response.status_code}")  # Debug
    return response.content if response.status_code == 200 else None

def extract_booking_hotels(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    hotels = []

    # Example selector for Booking.com hotel cards
    for el in soup.find_all("div", {"data-testid": "property-card"}):
        name = el.find("div", {"data-testid": "title"}).text.strip()
        link = el.find("a", {"data-testid": "title-link"})["href"]
        location = el.find("span", {"data-testid": "address"}).text.strip()
        pricing = el.find("span", {"data-testid": "price-and-discounted-price"}).text.strip().replace('$', '')
        rating = el.find("div", {"data-testid": "review-score"}).text.strip().split(" ")[0]
        image = el.find("img", {"data-testid": "image"})['src']

        hotels.append({'name': name, 'image_url': image, 'price': pricing, 'rating': rating, 'url': link})

    print(f"Extracted {len(hotels)} hotels from Booking.com")  # Debug
    return hotels

def save_booking_hotels(url):
    html_content = fetch_booking_data(url)
    if html_content:
        hotels = extract_booking_hotels(html_content)
        for hotel in hotels:
            obj, created = Hotel.objects.update_or_create(
                name=hotel['name'],
                defaults={
                    'image_url': hotel['image_url'],
                    'price_booking': float(hotel['price']) if hotel['price'] else None,
                    'star_rating': float(hotel['rating']) if hotel['rating'] else 0.0,
                    'booking_url': hotel['url'],
                }
            )
            print(f"Saved/Updated Hotel: {hotel['name']}")  # Debug
        return True
    return False