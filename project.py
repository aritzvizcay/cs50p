"""
PV and Wind Power Generation Forecasting Tool

Author: Aritz Vizcay
CS50P Final Project
"""

from datetime import datetime

from src.meteo_data import get_meteo_data
from src.timeseries_plot import power_plots
from src.power_plant import PowerPlant
from src.pdf_gen import gen_pdf


def main():
    forecast_days=ask_forecast_days()
    power_plant=PowerPlant()
    times, temperature_2m, wind_speed_10m, global_tilted_irradiance, weather_code = (
        get_meteo_data(power_plant.lat, power_plant.lon, power_plant.tilt, power_plant.azimuth, forecast_days)
    )

    # get the power generation from the meteo data
    pv_power = []
    wind_power = []
    forecast_confidence = []

    for i in range(len(times)):
        pv_power.append(
            round(
                power_plant.pv_power_calc(
                    global_tilted_irradiance[i],
                    temperature_2m[i],
                ),
                3,
            )
        )
        wind_power.append(
            round(power_plant.wind_power_calc(wind_speed_10m[i]), 3)
        )
        forecast_confidence.append(power_plant.forecast_confidence_calc(weather_code[i]))

    # plot the power generation timeseries
    print('\nGenerating plot...')
    plot_path=power_plots(times, pv_power, wind_power, forecast_confidence, forecast_days, power_plant.location, power_plant.country)
    
    maxes_means=forecast_analyze(pv_power, wind_power, temperature_2m, global_tilted_irradiance, forecast_confidence)
    
    pv_energy_forecast=integral_calc(times, pv_power)
    wind_energy_forecast=integral_calc(times, wind_power)
    total_energy=pv_energy_forecast+wind_energy_forecast
    energies={
        'pv_energy': pv_energy_forecast,
        'wind_energy': wind_energy_forecast,
        'total_energy': total_energy
    }
    
    print('\nGenerating PDF report...')
    pdf_path=gen_pdf(forecast_days, power_plant, plot_path, maxes_means, energies)
    
    print(f'\nPDF generated in {pdf_path}')
    


def ask_forecast_days():
    print(f"{'='*80}\nPV and Wind Power Generation Forecast App\n{'='*80}")
    
    print(f"\n{'-'*80}\nForecast configuration\n{'-'*80}")
    while True:
        try:
            forecast_days = int(
                input("Introduce the number of days to forecast [1-16]: ").strip()
            )
            if 1<=forecast_days<=16:
                return forecast_days
            else:
                raise ValueError
        except ValueError:
            print('Invalid input for forecast days')
            

def forecast_analyze(pv: list, wind:list, temp:list, gti:list, forecast_confidence:list):
    
    max_temp=round(max(temp),2)
    max_pv_power=round(max(pv),2)
    max_wind_power=round(max(wind),2)
    max_gti=round(max(gti),2)
    max_forecast_confidence=round(max(forecast_confidence),2)
    
    mean_temp=round(sum(temp)/len(temp),2)
    mean_pv_power=round(sum(pv)/len(pv),2)
    mean_wind_power=round(sum(wind)/len(wind),2)
    mean_gti=round(sum(gti)/len(gti),2)
    mean_forecast_confidence=round(sum(forecast_confidence)/len(forecast_confidence),2)

    return {
        'max_temp': max_temp, 
        'mean_temp': mean_temp,
        'max_pv_power': max_pv_power,
        'mean_pv_power': mean_pv_power,
        'max_wind_power': max_wind_power,
        'mean_wind_power': mean_wind_power,
        'max_gti': max_gti,
        'mean_gti': mean_gti,
        'max_forecast_confidence': max_forecast_confidence,
        'mean_forecast_confidence': mean_forecast_confidence
    }

def integral_calc(x:list, y:list):
    timedelta=datetime.strptime(x[1], "%Y-%m-%dT%H:%M")-datetime.strptime(x[0], "%Y-%m-%dT%H:%M")
    timedelta_h=timedelta.total_seconds()/3600
    integral=0
    for i in range(len(y)-1):
        integral+=timedelta_h/2*(y[i]+y[i+1]) # trapezoidal rule
        
    return round(integral,2)

if __name__ == "__main__":
    main()
