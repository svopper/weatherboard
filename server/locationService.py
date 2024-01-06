import requests
import logging

class LocationService:
    def __init__(self, api_key):
        self.api_key = api_key

    
    def get_city(self, lat, lon):
        url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={self.api_key}'
        logging.error(url)
        response = requests.get(url).json()
        if response['status'] != 'OK':
            logging.error("Something went wrong with Google Maps API. Error: %s" % response['error_message'])
            return response['error_message']
        
        city = ''
        for result in response['results']:
            for component in result['address_components']:
                if 'locality' in component['types']:
                    city = component['long_name']
                    break
            if city:
                break

        return city