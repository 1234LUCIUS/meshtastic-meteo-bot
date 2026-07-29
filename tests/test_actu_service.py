
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.official_web_search import OfficialWebSearchService

def test_city_news():
    service = OfficialWebSearchService()
    cities = ["Caen", "Rouen", "Cherbourg"]
    
    print("--- TEST DE LA COMMANDE !ACTU ---")
    for city in cities:
        print(f"\nRecherche pour : {city}")
        result = service.get_city_news(city)
        print(result)
        print("-" * 30)

if __name__ == "__main__":
    test_city_news()
