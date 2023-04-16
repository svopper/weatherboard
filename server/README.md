# Weatherboard Server

## Setup

To use Azure Application Insights, set env var APPINSIGHTS_INSTRUMENTATIONKEY and MAPS_API_KEY to your instrumentation key.
Update container app env vars: `az containerapp update -n <app-name> -g <resource-group> --set-env-vars KEY=value`

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