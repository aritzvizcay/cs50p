from fpdf import FPDF
from datetime import datetime

from src.power_plant import PowerPlant

class PDF(FPDF):
    def header(self):
        # logo 
        self.image('src/openmeteo_logo.png', x=self.l_margin, y=self.t_margin, w=10, h=10) 
        # font 
        self.set_font('helvetica', '', 10)
        self.set_text_color(169,169,169)
        # calculate width of date
        date=datetime.now().strftime('%Y/%m/%d') 
        # title 
        self.cell(0, 10, date, ln=1, align='R') 
        # line break 
        self.ln(10) 
        
    def footer(self):
        # set position of the footer 
        self.set_y(-self.b_margin) # negative is the distance to the bottom of the page, +15 would be 15 mm from the top of the page 
        # set font 
        self.set_font('helvetica', 'I', 8) 
        # set font color grey 
        self.set_text_color(169,169,169)
        
        author=self.author
        author_w=self.get_string_width(author)
        page_text=f"Page {self.page_no()}"
        page_text_w=self.get_string_width(page_text)
        
        # author
        self.cell(author_w,10, f"{self.author}", ln=0, align='L')
        
        # page number
        self.set_x(self.w-page_text_w-self.r_margin)
        self.cell(page_text_w,10, page_text, align='R')
    
    def add_report_title(self):
        self.set_y(self.t_margin+15)
        self.set_font("helvetica", style='BU', size=20)
        self.cell(0, 10, 'Power Generation Forecast Report', ln=1, align='C')
        self.set_font("helvetica", style='', size=14)
        self.cell(0, 10, datetime.now().strftime('%Y/%m/%d %H:%M'), align='C', ln=1)
    
    def add_forecast_info(self, forecast_days: int, power_plant: object): # para la version final pasar como arguumento la clase power_plant y sacar de ahi los atributos
        self.set_font("helvetica", style='BI', size=14)
        self.cell(0,10, "Input data", ln=1)
        
        self.set_font("helvetica", style='', size=11)
        self.multi_cell(0,7.5, "Forecast configuration\n"
                        f"  · Forecast days: {forecast_days}\n"
                        "Power Plant Configuration\n"
                        f"  · Location: {power_plant.location}, {power_plant.country}", border=1, align='C')
        top_col=self.get_y()
        self.set_x(self.l_margin)
        self.multi_cell((self.w-2*self.l_margin)/2, 7.5,"   · PV Power Plant Parameter Configuration\n"
                        f"      - Nominal power: {power_plant.pv_p_nom} W\n"
                        f"      - Tilt: {power_plant.tilt}°\n"
                        f"      - Azimuth: {power_plant.azimuth}°\n", border=1)
        self.set_xy(self.w/2,top_col)
        self.multi_cell((self.w-2*self.l_margin)/2, 7.5,"   · Wind Power Plant Parameter Configuration\n"
                        f"      - Number of wind turbines: {power_plant.n_wind_turbines}\n"
                        f"      - Rotor diameter: {power_plant.rotor_diam} m\n\n", border=1
                        )
        
    
    def add_plot(self, plot_path):
        plot_y=self.get_y()
        self.image(plot_path, x=self.l_margin, y=plot_y, w=self.w-self.l_margin-self.r_margin, h=85) # modificar para dejar hueco para la info de forecast y los datos de power plant
        self.set_y(plot_y+85)
        self.set_font("helvetica", style='', size=10)
        self.set_text_color(100,100,100)
        self.cell(0, 10, 'Figure 1. Generation forecast plot', align='C', ln=1)
        
    
    def add_summary(self, maxes_means_data: dict, energies:dict):
        self.set_font("helvetica", style='BI', size=14)
        self.set_text_color(0,0,0)
        self.set_x(self.l_margin)
        self.multi_cell(0,10, "Forecast Analysis", ln=1)
        
        self.set_font("helvetica", style='', size=11)
        self.multi_cell(0,8, f'The maximum and mean temperature is {maxes_means_data['max_temp']} and {maxes_means_data['mean_temp']} °C.\n'
                        f'The maximum and mean global tilted irradiance is {maxes_means_data['max_gti']} and {maxes_means_data['mean_gti']} W/m².\n'
                        f'The maximum and mean PV power generated is {maxes_means_data['max_pv_power']} and {maxes_means_data['mean_pv_power']} W.\n'
                        f'The maximum and mean wind power generation is {maxes_means_data['max_wind_power']} and {maxes_means_data['mean_wind_power']} W.\n'
                        f'The mean forecast confidence is {maxes_means_data['mean_forecast_confidence']}.\n'
                        f'The PV energy generated over the forecasted period is {energies['pv_energy']} Wh.\n'
                        f'The wind energy generated over the forecasted period is {energies['wind_energy']} Wh.\n'
                        f'The total energy generated over the forecasted period is {energies['total_energy']} Wh.',
                        ln=1
                        )
        
        self.set_font("helvetica", style='BI', size=12)
        self.multi_cell(0,10, "Summary Tables", ln=1)
        
        # table 1 3 columns
        col_w_3=(self.w-self.l_margin-self.r_margin)/3
        self.set_font("helvetica", style='BU', size=11)
        self.cell(col_w_3,8, '', border=1)
        self.cell(col_w_3,8,'Mean', border=1, align='C')
        self.cell(col_w_3,8,'Max', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_3,8, 'Temperaure [°C]', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_3,8,f'{maxes_means_data['mean_temp']}', border=1, align='C')
        self.cell(col_w_3,8,f'{maxes_means_data['max_temp']}', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_3,8, 'Global Tilted Irradiance [W/m²]', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_3,8,f'{maxes_means_data['mean_gti']}', border=1, align='C')
        self.cell(col_w_3,8,f'{maxes_means_data['max_gti']}', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_3,8, 'PV Power [W]', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_3,8,f'{maxes_means_data['mean_pv_power']}', border=1, align='C')
        self.cell(col_w_3,8,f'{maxes_means_data['max_pv_power']}', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_3,8, 'Wind Power [W]', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_3,8,f'{maxes_means_data['mean_wind_power']}', border=1, align='C')
        self.cell(col_w_3,8,f'{maxes_means_data['max_wind_power']}', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_3,8, 'Forecast Confidence', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_3,8,f'{maxes_means_data['mean_forecast_confidence']}', border=1, align='C')
        self.cell(col_w_3,8,f'{maxes_means_data['max_forecast_confidence']}', border=1, align='C', ln=1)
        
        self.cell(col_w_3,8,'', align='C', ln=1)
        
        # table 2 2 columns
        col_w_2=(self.w-self.l_margin-self.r_margin)/2
        
        self.cell(col_w_2,8,'', border=1, align='C')
        self.set_font("helvetica", style='BU', size=11)
        self.cell(col_w_2,8,'Energy [Wh]', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_2,8, 'PV', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_2,8,f'{energies['pv_energy']}', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='B', size=11)
        self.cell(col_w_2,8, 'Wind', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_2,8,f'{energies['wind_energy']}', border=1, align='C', ln=1)
        
        self.set_font("helvetica", style='BI', size=11)
        self.cell(col_w_2,8, 'Total', border=1)
        self.set_font("helvetica", style='', size=11)
        self.cell(col_w_2,8,f'{energies['total_energy']}', border=1, align='C', ln=1)
        
        

def gen_pdf(forecast_days: int, power_plant: object, plot_path: str, max_mean_data:dict, energies:dict):
    pdf=PDF(orientation='P', unit='mm', format='A4')
    
    # metadata
    pdf.set_title(f"Power Generation Forecast Report for {datetime.now().strftime('%Y/%m/%d %H:%M')}") # se debe modificar con la fecha en la que se hace el request, no en la que se genera el pdf
    pdf.set_author('Aritz Vizcay')
    pdf.set_lang('EN')
    pdf.set_creation_date(datetime.now())
    
    # margins
    pdf.set_margins(left=15, top=20, right=15)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    pdf.add_page()
    
    pdf.add_report_title()
    pdf.add_forecast_info(forecast_days, power_plant)
    pdf.add_plot(plot_path)
    
    pdf.add_summary(max_mean_data, energies)
    
    pdf.output(f'outputs/power_generation_forecast_report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf')
    
    return f"outputs/power_generation_forecast_report_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.pdf"
    
if __name__=='__main__':
    power_plant=PowerPlant()
    gen_pdf(10, power_plant, plot_path="outputs\pv_wind_generation_forecast_2026-07-22_11-09.jpg")