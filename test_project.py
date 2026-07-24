from project import integral_calc, ask_forecast_days, forecast_analyze
import pytest

def test_ask_forecast_days_valid(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '5')
    assert ask_forecast_days()==5
    
def test_ask_forecast_days_limits(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: '1')
    assert ask_forecast_days()==1
    
    monkeypatch.setattr('builtins.input', lambda _: '16')
    assert ask_forecast_days()==16
    
def test_ask_forecast_days_invalid_then_valid(monkeypatch):
    answers = iter(["abc", "20", "-1", "7"])

    monkeypatch.setattr(
        "builtins.input",
        lambda _: next(answers)
    )

    assert ask_forecast_days() == 7

def test_forecast_analyze():
    pv = [0, 100, 200, 300]
    wind = [50, 100, 150, 200]
    temp = [10, 20, 30, 40]
    gti = [0, 200, 400, 600]
    confidence = [0.5, 0.6, 0.7, 0.8]

    result = forecast_analyze(
        pv,
        wind,
        temp,
        gti,
        confidence
    )

    assert result == {
        "max_temp": 40,
        "mean_temp": 25,
        "max_pv_power": 300,
        "mean_pv_power": 150,
        "max_wind_power": 200,
        "mean_wind_power": 125,
        "max_gti": 600,
        "mean_gti": 300,
        "max_forecast_confidence": 0.8,
        "mean_forecast_confidence": 0.65
    }
    
def test_integral_calc_constant_power():
    times = [
        "2026-07-24T00:00",
        "2026-07-24T01:00",
        "2026-07-24T02:00",
        "2026-07-24T03:00"
    ]

    power = [100, 100, 100, 100]

    assert integral_calc(times, power) == 300
    
