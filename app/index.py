import panel as pn
pn.extension(notifications=True)
pn.extension(design='material')
pn.extension('plotly')

# plotting
import plotly
import plotly.express as px

# data science
import pandas as pd
import numpy as np

import pint
import pint_pandas
import pickle
ureg = pint.get_application_registry()

# MAIN APPLICATION CLASS ####################################################

class panel_app_class:
    def __init__(self):
        self.df_airports = None
        self.df_aircraft_database = None
        self.series_selected_aircraft = None
        self.selected_airport_origin = None
        self.selected_airport_destination = None
        self.selected_airport_alternate = None

app = panel_app_class()

# DATA INGESTION #############################################################

df_airports = pd.read_csv(
        filepath_or_buffer='/Users/michaelweinold/github/panel_ecopylot/airports_iata_only.csv',
        sep=',',
        header=0,
        index_col=None,
        usecols=['icao','iata','name','city','lat','lon'],
        dtype={
            'icao': str,
            'iata': str,
            'name': str,
            'city': str,
            'lat': float,
            'lon': float
        },
        engine='c',
    )
df_airports['combined_name'] = df_airports['name'] + ' (near ' + df_airports['city'] + ')' + '; IATA=' + df_airports['iata'] + '; ICAO=' + df_airports['icao']
app.df_airports = df_airports

df_aircraft_database = pd.read_excel(
    io='/Users/michaelweinold/Library/CloudStorage/OneDrive-TheWeinoldFamily/Documents/University/PhD/Data/Aircraft Performance/Test Table for EcoPyLot.xlsx',
    sheet_name='Data',
    header=[0, 1],
    engine='openpyxl'
)
df_aircraft_database = df_aircraft_database.pint.quantify(level=1)
df_aircraft_database['combined_name'] = df_aircraft_database['Manufacturer'] + ' ' + df_aircraft_database['Aircraft Designation'] + ' (' + df_aircraft_database['Engine Designation'] + ')'
app.df_aircraft_database = df_aircraft_database

with open('/Users/michaelweinold/github/panel_ecopylot/app/df.pkl', 'rb') as file:
    df = pickle.load(file)
df = df.pint.dequantify()
df.columns = df.columns.droplevel(level=1)

# FUNCTIONS ##################################################################


def generate_plotly_worldmap(
    lat: tuple[float, float],
    lon: tuple[float, float]
) -> plotly.graph_objs._figure.Figure:
    """_summary_

    _extended_summary_

    See Also
    --------
    - [plotly.express.line_geo](https://plotly.com/python-api-reference/generated/plotly.express.line_geo.html)

    Parameters
    ----------
    lat : tuple[float, float]
        _description_
    lon : tuple[float, float]
        _description_

    Returns
    -------
    plotly.graph_objs._figure.Figure
        _description_
    """
    
    # https://plotly.com/python-api-reference/generated/plotly.express.line_geo.html
    fig = px.line_geo(
        lat=lat,
        lon=lon,
        projection="natural earth",
        basemap_visible=True,
        fitbounds="locations",
        width=1000,
        height=300,
        #hover_name=airport_description,
        #text=airport_codes,
        #hover_data=[None, None],
    )
    # https://plotly.com/python/map-configuration/
    fig.update_geos(
        resolution=110,
        showcountries=True, countrycolor="Black",
        showland=True, landcolor="white",
        showocean=True, oceancolor="LightBlue",
    )
    # https://stackoverflow.com/a/69075593
    fig.update_traces(line_color='#0000ff', line_width=5)
    # https://community.plotly.com/t/excessive-margins-in-graphs-how-to-remove/
    fig.update_layout(
        margin=dict(l=0, r=0, t=3, b=3),
    )
    return fig


def generate_plotly_flight_profile(
    df: pd.DataFrame
) -> plotly.graph_objs._figure.Figure:
    """_summary_

    _extended_summary_

    See Also
    --------
    - [plotly.express.line](https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line)

    Parameters
    ----------
    df : pd.DataFrame
        _description_

    Returns
    -------
    plotly.graph_objs._figure.Figure
        _description_
    """
    
    fig = px.line(
        df,
        x="Distance",
        y="Altitude",
        width=1000,
        height=200,
        labels={"Distance": "Distance [NM]", "Altitude": "Altitude [ft]"}
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=3, b=3),
    )
    """
    fig.add_shape(
        type="rect",
        xref="paper", yref="paper",
        x0=-0.04, y0=-0.3, x1=1.04, y1=1.1, 
        line=dict(
            color="black",
            width=1,
            ),
    )
    """
    return fig


def calculate_fuel_consumption(event):
    app.airport_origin = app.df_airports.loc[app.df_airports['combined_name'] == widget_autocomplete_airport_origin.value].iloc[0]
    app.airport_destination = app.df_airports.loc[app.df_airports['combined_name'] == widget_autocomplete_airport_destination.value].iloc[0]
    if widget_autocomplete_airport_alternate.value == '':
        app.airport_alternate = None
    else:
        app.airport_alternate = app.df_airports.loc[app.df_airports['combined_name'] == widget_autocomplete_airport_alternate.value].iloc[0]
    
    panel_plotly_worldmap.object = generate_plotly_worldmap(
        lat=(app.airport_origin['lat'], app.airport_destination['lat']),
        lon=(app.airport_origin['lon'], app.airport_destination['lon'])
    )
    panel_plotly_flight_profile.object = generate_plotly_flight_profile(df)


# COLUMN 1 ##################################################################


widget_autocomplete_airport_origin = pn.widgets.AutocompleteInput( 
    name='Departure Airport',
    options=df_airports['combined_name'].tolist(),
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Enter airport designation here. \'IATA=ABC\' or \'ICAO=ABCD\' is supported.',
    sizing_mode='stretch_width'
)
widget_autocomplete_airport_destination = pn.widgets.AutocompleteInput( 
    name='Destination Airport',
    options=df_airports['combined_name'].tolist(),
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Enter airport designation here. \'IATA=ABC\' or \'ICAO=ABCD\' is supported.',
    sizing_mode='stretch_width'
)
widget_autocomplete_airport_alternate = pn.widgets.AutocompleteInput( 
    name='Alternate Airport',
    options=df_airports['combined_name'].tolist(),
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Enter airport designation here. \'IATA=ABC\' or \'ICAO=ABCD\' is supported.',
    sizing_mode='stretch_width'
)
widget_autocomplete_selected_aircraft = pn.widgets.AutocompleteInput( 
    name='Aircraft',
    options=df_aircraft_database['combined_name'].tolist(),
    case_sensitive=False,
    search_strategy='includes',
    placeholder='Enter aircraft designation here.',
    sizing_mode='stretch_width'
)


widget_button_calculate = pn.widgets.Button( 
    name='Calculate',
    icon='database-plus',
    button_type='primary',
    sizing_mode='stretch_width'
)
widget_button_calculate.on_click(calculate_fuel_consumption)

# COLUMN 2 ##################################################################

panel_plotly_worldmap = pn.pane.Placeholder(sizing_mode='stretch_width')
panel_plotly_flight_profile = pn.pane.Placeholder(sizing_mode='stretch_width')
panel_plotly_piechart_fuel = pn.pane.Placeholder(sizing_mode='stretch_width')

# ALL COLUMNS ###############################################################

col1 = pn.Column(
    widget_autocomplete_airport_origin,
    widget_autocomplete_airport_destination,
    widget_autocomplete_airport_alternate,
    widget_autocomplete_selected_aircraft,
    widget_button_calculate
)
col2 = pn.Column(
    panel_plotly_worldmap,
    panel_plotly_flight_profile,
    panel_plotly_piechart_fuel
)

# SITE ######################################################################

code_open_window = """
window.open("https://github.com/sustainableaviation/EcoPyLot")
"""
button_about = pn.widgets.Button(name="Learn more about this prototype...", button_type="primary")
button_about.js_on_click(code=code_open_window)

header = pn.Row(
    button_about,
    pn.HSpacer(),
    pn.pane.SVG(
        'https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/logo_PSI-ETHZ-WISER_white.svg',
        #height=50,
        margin=0,
        align="center"
    ),
    sizing_mode="stretch_width",
)

template = pn.template.MaterialTemplate(
    header=header,
    title='EcoPyLot Demonstrator',
    header_background='#001485', # green
    logo='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/logo_brightway_white.svg',
    favicon='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/favicon.png',
)

gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0:1] = col1 # 1/3rd of the width
gspec[:,1:2] = col2 # 2/3rds of the width
gspec[:,2:3] = None# col3 # 3/3rds of the width

template.main.append(gspec)
template.servable()