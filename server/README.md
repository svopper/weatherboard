# Weatherboard Server

## Setup

To use Azure Application Insights, set env var APPINSIGHTS_INSTRUMENTATIONKEY to your instrumentation key.
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

- [ ] Figure out something for AQI replacement
- [ ] Create Python wrapper application for screen to enable use of buttons and generally more control
  - [ ] Program each button to change location
- [ ] Use Google Maps API to determine city based on lat and lon
  - [ ] Add city name to image
- [ ] Implement health endpoint
  - [ ] Google Maps API health
  - [ ] Open Weather API health