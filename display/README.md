# Setting up Raspberry Pi

The display driver code is automatically copied to the `~/apps/weatherboard` directory from GitHub Actions.

The disaply should update every hour, pulling the latest forecast from the API and updates the display. This is configured though `cron`. Use command `crontab -e` to configure. The below configuration tells to run the show script on every reboot and then update it every hour at minute 0. The URL should return an image.

## Setup

Make sure to update the Raspberry by running `sudo apt upgrade`. Remember to reboot, otherwise there could be issues with I2C and SPI, which are requirements for the screen.

### Crontab
Use the following crontab script to configure updating the screen.

```cron
@reboot python ~/apps/weatherboard/show.py <URL_TO_FORECAST_ENDPOINT>

0 * * * * python ~/apps/weatherboard/show.py <URL_TO_FORECAST_ENDPOINT>
```

NB: This is about to change to just run a single script on reboot.