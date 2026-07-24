import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def power_plots(times_series: list, pv_series: list, wind_series: list, forecast_confidence_series: list, forecast_days: int, place: str, country_code: str, out_dir: str = 'outputs'):
    start_date = datetime.now()
    end_date = start_date + timedelta(days=forecast_days)
    clean_dates=[datetime.strptime(date,'%Y-%m-%dT%H:%M').strftime('%m/%d %H:%M') for date in times_series]
    
    plt.style.use('ggplot')
    plt.figure(figsize=(14, 6))

    ax1 = plt.gca()
    ax2 = ax1.twinx()

    ax1.plot(clean_dates, pv_series, color='orange', label='PV power')
    ax1.plot(clean_dates, wind_series, color='green', label='Wind power')
    ax2.plot(clean_dates, forecast_confidence_series, color='r', linestyle='--', label='Forecast confidence')

    ax1.set_xlabel('Date')
    ax1.set_xticks(clean_dates[::max(1, len(times_series) // 10)])
    ax1.tick_params("x", labelrotation=30)
    ax1.set_ylabel('Power generation [W]')
    ax1.set_ylim(-max((max(pv_series), max(wind_series)))*0.05, max((max(pv_series), max(wind_series)))*1.1)
    ax2.set_ylabel('Forecast confidence')
    ax2.set_ylim(-0.05, 1.05)
    
    ax1.grid(True, alpha=0.3)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, frameon=True, fancybox=True, loc='upper right', facecolor='white', edgecolor='black', framealpha=1)

    ax1.set_title(
        f"PV and wind power generation forecast\n {forecast_days} day forecast in {place}, {country_code}\n"
        f"{start_date.strftime('%Y/%m/%d')} - {end_date.strftime('%Y/%m/%d')}",
        fontweight='bold'
    )
    
    plt.savefig(f"{out_dir}/power_generation_forecast_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.svg")
    
    return f"{out_dir}/power_generation_forecast_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.svg"