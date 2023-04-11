import requests

API_KEY = "YOUR_API_KEY"

lat = '56.075008' # Example latitude
lng = '12.545572' # Example longitude

url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={API_KEY}'

response = requests.get(url).json()

city = ''
for result in response['results']:
    for component in result['address_components']:
        if 'locality' in component['types']:
            city = component['long_name']
            break
    if city:
        break

print(city)