# %%
import plotly
import plotly.express as px

fig = px.line_geo(
        lat=12.0,
        lon=lon,
        projection="robinson",
        #hover_name=airport_description,
        #text=airport_codes,
        #hover_data=[None, None],
    )
    return fig