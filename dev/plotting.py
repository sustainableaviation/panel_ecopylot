# %%
import plotly
import plotly.express as px

# https://plotly.com/python-api-reference/generated/plotly.express.line_geo.html
fig = px.line_geo(
    lat = [40.7127, 51.5072],
    lon = [-74.0059, 0.1275],
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
# https://stackoverflow.com/a/69075593
fig.update_traces(line_color='#0000ff', line_width=5)
# https://community.plotly.com/t/excessive-margins-in-graphs-how-to-remove/
fig.update_layout(
    margin=dict(l=0, r=0, t=3, b=3),
)

fig.show()