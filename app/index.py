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

import sys
import os
module_path = os.path.abspath("/Users/michaelweinold/github/EcoPyLot")
if module_path not in sys.path:
    sys.path.append(module_path)

from ecopylot.route import compute_flight_profile
from ecopylot.geospatial import haversine_distance
from ecopylot.utilities import remove_pint_units_from_df


# MAIN APPLICATION CLASS ####################################################

class panel_app_class:
    def __init__(self):
        self.df_airports = None
        self.df_aircraft_database = None
        self.series_selected_aircraft = None
        self.selected_airport_origin = None
        self.selected_airport_destination = None
        self.selected_airport_alternate = None
        self.route_distance = None
        self.df_flight_profile = None

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

dict_fuel_consumption = {
    'taxi': 3,
    'takeoff': 7,
    'climb': 10,
    'cruise': 65,
    'descent': 7,
    'approach': 2,
}

# FUNCTIONS ##################################################################


def generate_plotly_map_origin_destination(
    coordinates_origin: tuple[float, float],
    coordinates_destination: tuple[float, float],
    coordinates_alternate: tuple[float, float],
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

    dict_map_settings = {
        "resolution": 110,
        "projection": "natural earth",
        "fitbounds": "locations",
        "width":1000,
        "height":300,
    }
    
    # https://plotly.com/python-api-reference/generated/plotly.express.line_geo.html
    fig = px.line_geo(
        lat=[coordinates_origin[0], coordinates_destination[0]],
        lon=[coordinates_origin[1], coordinates_destination[1]],
        projection=dict_map_settings["projection"],
        fitbounds=dict_map_settings["fitbounds"],
        width=dict_map_settings["width"],
        height=dict_map_settings["height"],
        basemap_visible=True,
        #hover_name=airport_description,
        #text=airport_codes,
        #hover_data=[None, None],
    )
    # https://plotly.com/python/map-configuration/
    fig.update_geos(
        resolution=50,
        showcountries=True, countrycolor="Black",
        showland=True, landcolor="white",
        showocean=True, oceancolor="LightBlue",
    )
    # https://stackoverflow.com/a/69075593
    fig.update_traces(line_color='red', line_width=5)
    # https://community.plotly.com/t/excessive-margins-in-graphs-how-to-remove/
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=3),
    )

    if coordinates_alternate is not None:
        alternate_figure = px.line_geo(
            lat=[coordinates_destination[0], coordinates_alternate[0]],
            lon=[coordinates_destination[1], coordinates_alternate[1]],
            width=dict_map_settings["width"],
            height=dict_map_settings["height"],
        )
        alternate_figure.data[0].name='alternate'
        fig.add_trace(
            alternate_figure.data[0]
        )
        fig.update_traces(
            patch={
                "line": {
                    "color": "#fc9403",
                    "width": 5,
                    "dash": 'dot',
                }
            },
            selector = ({'name':'alternate'})
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


def generate_plotly_piechart_fuel(
    dict_fuel_consumption: dict[str, float]
) -> plotly.graph_objs._figure.Figure:
    """_summary_

    _extended_summary_

    See Also
    --------
    - [plotly.express.pie](https://plotly.com/python-api-reference/generated/plotly.express.pie)

    Parameters
    ----------
    dict_fuel_consumption : dict[str, float]
        _description_

    Returns
    -------
    plotly.graph_objs._figure.Figure
        _description_
    """
    
    fig = px.pie(
        values=list(dict_fuel_consumption.values()),
        names=list(dict_fuel_consumption.keys()),
        width=1000,
        height=400,
    )
    fig.update_layout(
        margin=dict(l=0, r=0, t=3, b=3),
        font=dict(size=14),
    )
    return fig


def calculate_fuel_consumption(event):
    if widget_autocomplete_airport_origin.value == '' or widget_autocomplete_airport_destination.value == '':
        pn.state.notifications.error('Please select a departure and destination airport first!', duration=5000)
        return
    app.airport_origin = app.df_airports.loc[app.df_airports['combined_name'] == widget_autocomplete_airport_origin.value].iloc[0]
    app.airport_destination = app.df_airports.loc[app.df_airports['combined_name'] == widget_autocomplete_airport_destination.value].iloc[0]
    if widget_autocomplete_airport_alternate.value == '':
        app.airport_alternate = None
    else:
        app.airport_alternate = app.df_airports.loc[app.df_airports['combined_name'] == widget_autocomplete_airport_alternate.value].iloc[0]
    
    panel_plotly_worldmap.object = generate_plotly_map_origin_destination(
        coordinates_origin=(app.airport_origin['lat'], app.airport_origin['lon']),
        coordinates_destination=(app.airport_destination['lat'], app.airport_destination['lon']),
        coordinates_alternate=(app.airport_alternate['lat'], app.airport_alternate['lon']) if app.airport_alternate is not None else None
    )
    app.route_distance = haversine_distance(
        A_lat=app.airport_origin['lat'],
        A_lon=app.airport_origin['lon'],
        B_lat=app.airport_destination['lat'],
        B_lon=app.airport_destination['lon']
    ).to('km')
    panel_indicator_route_distance.value = app.route_distance.magnitude
    _, _, _, app.df_flight_profile = compute_flight_profile(
        df_aircraft=app.df_aircraft_database,
        aircraft_designation='A220-300',
        altitude_cruise=32000*ureg.ft,
        distance_route=app.route_distance,
    )
    app.df_flight_profile = remove_pint_units_from_df(app.df_flight_profile)
    panel_plotly_flight_profile.object = generate_plotly_flight_profile(app.df_flight_profile)
    panel_plotly_piechart_fuel.object = generate_plotly_piechart_fuel(dict_fuel_consumption)


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
panel_plotly_piechart_fuel = pn.pane.Placeholder(sizing_mode='stretch_both')

panel_indicator_route_distance = pn.indicators.Number(
    name='Distance [km]',
    value=0,
    format='{value:,.0f}',
)
panel_indicator_fuel_amount = pn.indicators.Number(
    name='Fuel Consumption [t]',
    value=0,
)

row_indicator_route_and_fuel = pn.Row(
    panel_indicator_route_distance,
    panel_indicator_fuel_amount,
    sizing_mode='stretch_width'
)

# ALL COLUMNS ###############################################################

col1 = pn.Column(
    '# Flight Settings',
    widget_autocomplete_airport_origin,
    widget_autocomplete_airport_destination,
    widget_autocomplete_airport_alternate,
    widget_autocomplete_selected_aircraft,
    widget_button_calculate
)
col2 = pn.Column(
    '# Flight Parameters',
    panel_plotly_worldmap,
    row_indicator_route_and_fuel,
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
    logo='/Users/michaelweinold/github/panel_ecopylot/media/icon.svg',
    favicon='https://raw.githubusercontent.com/brightway-lca/brightway-webapp/main/app/_media/favicon.png',
)

gspec = pn.GridSpec(ncols=3, sizing_mode='stretch_both')
gspec[:,0:1] = col1 # 1/3rd of the width
gspec[:,1:2] = col2 # 2/3rds of the width
gspec[:,2:3] = None# col3 # 3/3rds of the width

template.main.append(gspec)
template.servable()