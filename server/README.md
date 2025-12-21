# Weatherboard Server

## Setup

Set the following environment variables:
- `MAPS_API_KEY` - Google Maps API key

### Prepare

```bash
python -m venv venv
pip install -r requirements.txt
cp fonts/* /usr/share/fonts/
fc-cache
```

Or use Docker: `docker build -t 'weatherboard-api' .`. Remember to set environment variables.

### Run dev

```bash
FLASK_APP=server:app flask run --reload
```

## TODO

- [x] Figure out something for AQI replacement
- [x] Create Python wrapper application for screen to enable use of buttons and generally more control
  - [x] Program each button to change location
- [x] Use Google Maps API to determine city based on lat and lon
  - [x] Add city name to image
- [x] Implement health endpoint
  - [ ] Google Maps API health
  - [ ] Open Weather API health


## Deployment
Server is deployed automatically to Hetzner VPS using Dokploy on push to main branch.