# PV and Wind Power Generation Forecasting Tool
## Video Demo: <https://youtu.be/PgPR7JALq18>
### Description

This project is a command-line application that estimates photovoltaic and wind power generation using meteorological forecast data retrieved from the Open-Meteo API.
The user configures the forecast period, plant location, photovoltaic installation, and wind installation. The application then retrieves hourly weather data, estimates the expected renewable power generation, analyzes the resulting time series, creates a plot, and generates a PDF report.

The workflow is as follows:

1. The user is prompted for data regarding the forecast and parameters of the PV and wind power plants including:
    - Days to forecast
    - Location of the plant
    - Nominal power of the PV plant
    - Tilt and azimuth of the PV panels
    - Number of wind turbines
    - Rotor diameter of the wind turbines

This data is stored in an instantiated `PowerPlant` object named `power_plant`.
2. The meteorological data required for the forecast is requested from the Open-Meteo API. This information includes:
    - Air temperature 2 m above ground
    - Wind speed 10 m above ground
    - Global tilted irradiance
    - WMO weather code

3. This data is passed to methods of the `power_plant` object to calculate PV and wind power generation. A custom forecast-confidence value is also assigned according to each WMO weather code.

4. A plot representing these time series is generated and saved in the `outputs` folder.

5. A PDF report including a small analysis of the forecast (maximum and mean power generation over the forecasted days and energy generated) is generated and saved in the `outputs` folder.

### Files

#### project.py

The `project.py` file is the main entry point of the application and coordinates the complete forecasting workflow.

The `main` function first calls `ask_forecast_days`, which prompts the user to select a forecast period between 1 and 16 days. A `PowerPlant` object is then instantiated, causing the user to be prompted for the location and technical parameters of the photovoltaic and wind installations.

Once the plant has been configured, `project.py` calls the `get_meteo_data` function using the latitude, longitude, panel tilt, panel azimuth, and selected forecast duration. The function returns the forecast timestamps and the hourly meteorological series required by the generation models.
The program iterates through every forecast timestep and uses the methods of the `PowerPlant` object to calculate:

- Photovoltaic power generation from global tilted irradiance and ambient temperature.
- Wind power generation from wind speed and the configured wind turbine parameters.
- Forecast confidence from the corresponding WMO weather code.

The calculated values are stored in separate time-series lists. These lists are then passed to the `power_plots` function, which generates the forecast figure and returns the path of the saved image.

The `forecast_analyze` function calculates the maximum and mean values of temperature, global tilted irradiance, PV power, wind power, and forecast confidence. The results are returned as a dictionary so that each value can be accessed using a descriptive key instead of relying on tuple positions.

The `integral_calc` function estimates the energy generated during the forecast period by applying the trapezoidal integration rule to the power time series. The timestamps are converted into `datetime` objects to determine the timestep in hours. Since power is expressed in watts and time is expressed in hours, the resulting energy is returned in watt-hours.

Finally, the calculated statistics, energy values, plant configuration, and plot path are passed to the `gen_pdf` function. The path of the generated PDF report is displayed to the user when the process finishes.

#### test_project.py

The `test_project.py` file contains the automated tests for the main functions defined in `project.py`. The tests are written using `pytest` and verify the behavior of `ask_forecast_days`, `forecast_analyze`, and `integral_calc`.

The tests for `ask_forecast_days` use the `monkeypatch` fixture provided by `pytest`. This fixture temporarily replaces Python's built-in `input` function so that user input can be simulated automatically during testing. For example, replacing `input` with a lambda function that returns `"5"` allows the test to verify that `ask_forecast_days` correctly converts the input to an integer and returns the value `5`.

The boundary test checks that the function accepts values at the valid limits of the forecast range. The invalid-input test uses an iterator containing several values. Each time the function calls `input`, the next value from the iterator is returned. This makes it possible to simulate invalid text, out-of-range values, and finally a valid value. The test confirms that the function continues prompting until a valid number of forecast days is provided.

The `test_forecast_analyze` function verifies that the statistical analysis correctly calculates the maximum and mean values for temperature, photovoltaic power, wind power, global tilted irradiance, and forecast confidence. The returned dictionary is compared with the expected results.

The `test_integral_calc_constant_power` function verifies the numerical integration used to estimate generated energy. It uses a constant power series of 100 W over three one-hour intervals. The expected result is 300 Wh, confirming that the trapezoidal integration is being applied correctly.

#### src

##### power_plant.py

The file named `power_plant.py` contains the `PowerPlant` class, which represents the photovoltaic and wind generation system configured by the user.

When a `PowerPlant` object is instantiated, the class prompts the user for the plant location and the main technical parameters of both generation technologies. The input is validated before being stored as object attributes.

For the plant location, the user introduces a city and country. The class validates the text input, converts the country name into its corresponding two-letter country code using `pycountry`, and requests the coordinates from the Open-Meteo geocoding API. The resulting location name, country code, latitude, and longitude are stored in the object.

For the photovoltaic plant, the class requests:
- Nominal installed power, accepting values expressed in watts, kilowatts, or megawatts.
- Panel tilt, restricted to integer values between 0° and 90°.
- Panel azimuth, restricted to integer values between 0° and 180°.

The nominal PV power is converted and stored in watts.

For the wind plant, the class requests:
- Number of installed wind turbines.
- Rotor diameter of each turbine.

The class also contains the methods used to estimate power generation.

The `pv_power_calc` method calculates the photovoltaic AC power from the global tilted irradiance and ambient temperature. It first estimates the PV cell temperature, applies a temperature correction to the nominal power, and then includes a fixed conversion efficiency to estimate the final AC output.

The `wind_power_calc` method estimates the wind power generated from the forecasted wind speed. The method estimates the available wind power from air density, total rotor swept area, and the cube of wind speed. A fixed conversion factor is then applied to obtain an approximate generated power. Generation is only calculated when the wind speed is between the assumed cut-in and cut-out speeds of 3 m/s and 25 m/s. Outside this range, the method returns zero power.

Finally, the `forecast_confidence_calc` method applies a custom heuristic that maps each WMO weather code to a predefined confidence value between 0 and 1. Clear-weather conditions receive higher values, while fog, heavy precipitation, snowfall, and thunderstorms receive lower values. These values are defined by the application and are not provided directly by Open-Meteo.

##### meteo_data.py

The `meteo_data.py` file contains the `get_meteo_data` function. It receives the plant latitude, longitude, PV panel tilt, PV panel azimuth, and number of forecast days.

The function builds a request to the Open-Meteo Forecast API and retrieves hourly air temperature at 2 m, wind speed at 10 m, global tilted irradiance, and WMO weather codes.

Because the API response may include timestamps prior to the execution time, the function filters the returned data and preserves only forecast values whose timestamps are later than the execution time. The timestamps and meteorological variables are returned as lists for use by the power calculation functions.

##### timeseries_plot.py

The `timeseries_plot.py` file contains the `power_plots` function. It receives the forecast timestamps, PV power series, wind power series, forecast confidence series, forecast duration, plant location, country code, and output directory.

The function creates a `Matplotlib` figure with PV and wind generation on the primary vertical axis and forecast confidence on a secondary vertical axis. It formats the date labels, combines the legends from both axes, and adds a title containing the location and forecast period.

The resulting figure is saved as an SVG file in the `outputs` directory. The function returns the generated file path so that the plot can later be embedded in the PDF report.

##### pdf_gen.py

The `pdf_gen.py` file is responsible for generating the final PDF forecast report. It contains a custom `PDF` class that inherits from `FPDF` and defines the layout and content of the document.

The `header` method is executed automatically whenever a new page is created. It adds the Open-Meteo logo, the current date, and the visual formatting used at the top of every page.

The `footer` method adds the report author on the left side and the current page number on the right side. The footer is positioned relative to the configured bottom margin and is generated automatically on every page.

The `add_report_title` method creates the main title of the report and includes the date and time at which the document is generated.

The `add_forecast_info` method displays the user-defined input data. It includes the forecast duration, plant location, PV nominal power, panel tilt and azimuth, number of wind turbines, and rotor diameter. The PV and wind plant parameters are displayed in two separate columns.

The `add_plot` method inserts the forecast plot generated by `timeseries_plot.py`. The image is scaled to the usable width of the page and is followed by a centered figure caption.

The `add_summary` method creates the analytical section of the report. It presents the maximum and mean values of temperature, global tilted irradiance, PV power, wind power, and forecast confidence. It also reports the estimated PV, wind, and total energy generated during the forecast period.

The analytical results are also presented in two summary tables. The first table compares maximum and mean forecast values, while the second table summarizes PV, wind, and total energy generation.

The `gen_pdf` function initializes the PDF document, defines its metadata, margins, language, author, and automatic page-break behavior. It then adds the title, input configuration, forecast plot, and analytical summary before saving the completed report in the `outputs` directory. The function returns the path of the generated PDF so that it can be displayed by the main application.

### Design Choices

The project was divided into separate modules for plant configuration, meteorological data retrieval, plotting, PDF generation, testing, and application control. This modular structure keeps each file focused on a single responsibility and makes the code easier to understand, test, and maintain.

A `PowerPlant` class was used because the plant parameters and the methods that calculate PV and wind generation belong to the same conceptual entity. Once the object has been configured, its stored parameters can be reused for every forecast timestep.

All power values are converted to watts before performing calculations. Although the user may enter PV nominal power in watts, kilowatts, or megawatts, using a single internal unit prevents inconsistencies during the calculations and report generation.

The forecast analysis is returned as a dictionary instead of a tuple. Descriptive keys such as `max_pv_power`, `mean_temp`, and `mean_forecast_confidence` make the results easier to access and reduce the risk of confusing tuple positions.

The trapezoidal rule was selected to estimate energy from the hourly power series because it accounts for changes between consecutive power values. Since the timestep is expressed in hours and power is expressed in watts, the resulting energy is obtained in watt-hours.

Forecast confidence is implemented as a custom heuristic based on WMO weather codes. It provides a qualitative indication of forecast conditions but should not be interpreted as a formal uncertainty metric supplied by Open-Meteo.

Generated plots and PDF reports are stored in the `outputs` directory so that source code remains separated from generated artifacts.


### Author

Developed by Aritz Vizcay Espronceda as the final project for Harvard University's CS50P course.

Linkedin [Aritz Vizcay Espronceda](https://www.linkedin.com/in/aritzvies/)

GitHub: [aritzvizcay](https://github.com/aritzvizcay)

edX: [aritzvizcay](https://profile.edx.org/u/aritzvizcay?_gl=1*whtxol*_gcl_au*NTUxNjEyNTU1LjE3ODQ5MDk0Njc.*_ga*MTUxNDY3MDU5Ny4xNzg0OTA5NDY3*_ga_D3KS4KMDT0*czE3ODQ5MDk0NjYkbzEkZzEkdDE3ODQ5MDk0ODAkajQ3JGwwJGgw)