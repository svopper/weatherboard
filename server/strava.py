import requests

class StravaService:
    def __init__(self, api_key, rider_id):
        self.api_key = api_key
        self.rider_id = rider_id

    
    def get_ride_ytd(self):
        url = f'https://www.strava.com/api/v3/athletes/{self.rider_id}/stats'
        response = requests.get(url, headers = { "Authorization": f'Bearer {self.api_key}'}).json()
        return response['ytd_ride_totals']['distance']
