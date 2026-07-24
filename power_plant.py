import re
import pycountry
import requests
import math


class PowerPlant:
    def __init__(self):
        self._ask_place()
        self._ask_pv()
        self._ask_wind()

    # Ask user for location of the power plant w erro handling
    def _ask_place(self):
        print(f"\n{'-'*80}\nPower Plant Configuration\n{'-'*80}")
        print(f"· Location")
        while True:
            location = input(
                "Introduce the location of the PV and wind power plants: "
            ).strip()
            country = input(
                "Introduce the name of the country where they are located: "
            ).strip()
            location_match = re.search(r"^([a-zA-Z\s]+)$", location)
            if not location_match:
                print("Invalid location")
                continue
            country_match = re.search(r"^([a-zA-Z\s]+)$", country)
            if not country_match:
                print("Invalid country")
                continue
            try:
                lat, lon, name, country_code = self.coordinates_from_name(
                    location_match.group(1), country_match.group(1)
                )

                self.location = name
                self.country = country_code
                self.lat = lat
                self.lon = lon
                break
            except:
                print("Invalid combination of location and country")

    def coordinates_from_name(self, name: str, country_name: str, n_results=1):
        country_code = self.country_code_from_name(country_name)
        response = requests.get(
            f"https://geocoding-api.open-meteo.com/v1/search?name={name}&count={n_results}&language=en&format=json&countryCode={country_code}"
        )
        response = response.json()
        return (
            response["results"][0]["latitude"],
            response["results"][0]["longitude"],
            response["results"][0]["name"],
            response["results"][0]["country_code"],
        )

    def country_code_from_name(self, name: str):
        country_info = pycountry.countries.search_fuzzy(name)
        return country_info[0].alpha_2

    # Ask user for PV plant data w error handling
    def _ask_pv(self):
        print(f"\n· PV Power Plant Parameter Configuration")
        while True:
            pv_power_input = input(
                "Introduce the nominal power of the PV plant: "
            ).strip()
            matches = re.search(
                r"^([0-9]+(?:[,\.][0-9]+)?)\s?([MmkK]?)\s?[wW]?$", pv_power_input
            )
            if not matches:
                print("Invalid input for PV plant nominal power")
                continue
            elif matches.group(2) == "M" or matches.group(2) == "m":
                self.pv_p_nom = float(matches.group(1)) * 1e6
                break
            elif matches.group(2) == "k" or matches.group(2) == "K":
                self.pv_p_nom = float(matches.group(1)) * 1e3
                break
            else:
                self.pv_p_nom = float(matches.group(1))
                break

        while True:
            tilt_input = input("Introduce the PV panels' tilt [0-90]: ").strip()
            match = re.search(r"^([0-9]{1,2})$", tilt_input)
            if not match:
                print("Invalid input for Pv panels' tilt")
            elif 0 <= int(match.group(1)) <= 90:
                self.tilt = int(match.group(1))
                break
            else:
                print("Input for Pv panels' tilt must be [0-90]")

        while True:
            azimuth_input = input("Introduce the PV panels' azimuth [0-180]: ").strip()
            match = re.search(r"^([0-9]{1,3})$", azimuth_input)
            if not match:
                print("Invalid input for PV panels' azimuth")
            elif 0 <= int(match.group(1)) <= 180:
                self.azimuth = int(match.group(1))
                break
            else:
                print("Input for PV panels' azimuth must be [0-180]")

    # Ask user for wind plant data w error handling
    def _ask_wind(self):
        print(f"\n· Wind Power Plant Parameter Configuration")

        while True:
            n_gen_input = input(
                "Introduce the number of wind turbines installed: "
            ).strip()
            match = re.search(r"^([0-9]*)$", n_gen_input)
            if not match:
                print("Invalid input for number wind turbines")
                continue
            else:
                self.n_wind_turbines = int(match.group(1))
                break
        while True:
            rotor_diameter = input(
                "Introduce the rotor's diameter of the wind turbine: "
            ).strip()
            match = re.search(r"^([0-9]+(?:[,\.][0-9]+)?)$", rotor_diameter)
            if not match:
                print("Invalid input for turbine's diameter")
                continue
            else:
                self.rotor_diam = float(match.group(1))
                break
            
    def pv_power_calc(self, gti: float, t_amb: float):
        t_cell = t_amb + (45 - 20) / 800 * gti
        pv_power_dc = self.pv_p_nom * gti / 1000 * (1 - 0.004 * (t_cell - 25))
        pv_power_ac = pv_power_dc * 0.9
        return pv_power_ac

    def wind_power_calc(self, speed: float):
        if 3 < speed < 25:
            area_rotor = math.pi * (self.rotor_diam / 2) ** 2 * self.n_wind_turbines
            avail_wind_power = 1 / 2 * 1.2 * area_rotor * speed**3
            wind_power = avail_wind_power * 0.9
            return wind_power
        else:
            return 0

    def forecast_confidence_calc(self, code: int):
        confidence = {
            0: 0.95,
            1: 0.90,
            2: 0.80,
            3: 0.85,
            45: 0.65,
            48: 0.65,
            51: 0.70,
            53: 0.68,
            55: 0.65,
            56: 0.55,
            57: 0.50,
            61: 0.70,
            63: 0.65,
            65: 0.55,
            66: 0.52,
            67: 0.48,
            71: 0.65,
            73: 0.60,
            75: 0.50,
            77: 0.55,
            80: 0.60,
            81: 0.50,
            82: 0.35,
            85: 0.55,
            86: 0.40,
            95: 0.30,
            96: 0.20,
            99: 0.15,
        }

        return confidence[code]


if __name__ == "__main__":
    a = PowerPlant()
