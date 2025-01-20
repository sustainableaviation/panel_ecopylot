# %%
import plotly
import plotly.express as px

lat = [40.7127, 51.5072]
lon = [-74.0059, 0.1275]

# https://plotly.com/python-api-reference/generated/plotly.express.line_geo.html
fig = px.line_geo(
    lat=lat,
    lon=lon,
    projection="natural earth",
    basemap_visible=True,
    fitbounds="locations",
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
# https://stackoverflow.com/a/69075593
fig.update_traces(line_color='#0000ff', line_width=5)
# https://community.plotly.com/t/excessive-margins-in-graphs-how-to-remove/
fig.update_layout(
    margin=dict(l=0, r=0, t=3, b=3),
)

fig.show()
# %%

import pickle
with open('/Users/michaelweinold/github/panel_ecopylot/app/df.pkl', 'rb') as file:
    df = pickle.load(file)
df = df.pint.dequantify()
df.columns = df.columns.droplevel(level=1)

# https://plotly.com/python-api-reference/generated/plotly.express.line.html#plotly.express.line
fig = px.line(
    df,
    x="Distance",
    y="Altitude",
    width=500,
    height=200,
)
fig.update_layout(
    margin=dict(l=0, r=0, t=3, b=3),
)
fig.add_shape(type="rect",
    xref="paper", yref="paper",
    x0=-0.04, y0=-0.3, x1=1.04, y1=1.1, 
    line=dict(
        #color="RoyalBlue",
        color="black", #named colors from https://stackoverflow.com/a/72502441/8508004
        width=1,
    ),
    #fillcolor="LightSkyBlue",
)
fig.show()