import requests

from datetime import datetime


def get_meteo_data(
    latitude: float, longitude: float, tilt: float, azimuth: float, forecast_days
):

    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&forecast_days={forecast_days}&hourly=temperature_2m,global_tilted_irradiance,wind_speed_10m,weather_code&tilt={tilt}&azimuth={azimuth}"
    )
    response = response.json()

    # get now in same format as the response JSON, YYYY-MM-DDTHH:MM
    now = datetime.strftime(datetime.now(), "%Y-%m-%dT%H:%M")

    times = []
    temperature_2m = []
    wind_speed_10m = []
    gti = []
    weather_code = []

    # get only meteo data for the future
    for i, timestamp in enumerate(response["hourly"]["time"]):
        if timestamp > now:
            times.append(timestamp)
            temperature_2m.append(response["hourly"]["temperature_2m"][i])
            wind_speed_10m.append(response["hourly"]["wind_speed_10m"][i])
            gti.append(response["hourly"]["global_tilted_irradiance"][i])
            weather_code.append(int(response["hourly"]["weather_code"][i]))

    return (
        times,
        temperature_2m,
        wind_speed_10m,
        gti,
        weather_code
    )