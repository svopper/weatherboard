# Setting up Raspberry Pi

The display driver code is automatically copied to the `~/apps/weatherboard` directory from GitHub Actions.

The disaply should update every hour, pulling the latest forecast from the API. This is configured though `cron`. Use command `crontab -e` to configure. The below configuration tells to run the show script on every reboot and then update it every hour at minute 0.

```cron
@reboot python ~/apps/weatherboard/show.py <URL_TO_FORECAST_ENDPOINT>

0 * * * * python ~/apps/weatherboard/show.py <URL_TO_FORECAST_ENDPOINT>
```

