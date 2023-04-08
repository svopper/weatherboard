# Weatherboard

[![Trigger auto deployment for API](https://github.com/svopper/weatherboard/actions/workflows/weatherboard-api-ca-AutoDeployTrigger.yml/badge.svg)](https://github.com/svopper/weatherboard/actions/workflows/weatherboard-api-ca-AutoDeployTrigger.yml)

- `display` contains a basic Python script that renders an image onto the e-paper from a URL or local file. This is only for the 3-colour Waveshare display - for the 7-colour Pimoroni display I just use their prebuilt example with wget: https://github.com/pimoroni/inky/blob/master/examples/7color/image.py

- `server` contains the server that this script is scheduled to fetch an image from periodically, and which renders the actual weather display. It takes an OpenWeatherMap API key as a GET parameter, and a "style" parameter to choose what kind of image to return.

If you want to use this yourself, you need to run the server somewhere, and then script your board to fetch and show that image on a regular schedule. I find this easier than running the code on the device itself, since deploying changes can all be done via GitHub Actions.

## Setup

To use Azure Application Insights, set env var APPINSIGHTS_INSTRUMENTATIONKEY to your instrumentation key.