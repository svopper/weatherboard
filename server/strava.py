import os
import requests

class StravaService:    
    def get_ride_ytd(self):
        url = f'https://www.strava.com/api/v3/athletes/{os.environ.get("STRAVA_RIDER_ID")}/stats'
        response = requests.get(url, headers = { "Authorization": f'Bearer {self.acquire_access_token()}'})
        
        if response.status_code != 200:
            print("something went wrong with strava api")
            return -1
        return response.json()['ytd_ride_totals']['distance']

    def acquire_access_token(self):
        auth_url = "https://www.strava.com/oauth/token"

        payload = {
            "client_id": os.environ.get("STRAVA_CLIENT_ID"),
            "client_secret": os.environ.get("STRAVA_CLIENT_SECRET"),
            "grant_type": "refresh_token",
            "refresh_token": os.environ.get("STRAVA_REFRESH_TOKEN"),
        }

        response = requests.post(auth_url, data=payload)
        if response.status_code != 200:
            print("something went wrong with strava api")
            return -1
            
        return response.json()['access_token']
