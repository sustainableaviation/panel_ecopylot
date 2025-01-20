# %%
import plotly
import plotly.express as px

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

# https://plotly.com/python-api-reference/generated/plotly.express.line_geo.html
fig = px.line_geo(
    lat=(12.0,20),
    lon=(12.0,20),
    projection="natural earth",
    basemap_visible=True,
    width=500,
    height=200,
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
# https://community.plotly.com/t/excessive-margins-in-graphs-how-to-remove/
fig.update_layout(
    margin=dict(l=0, r=0, t=3, b=3),
)

fig.show()