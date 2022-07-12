import plotly.graph_objects as go
import plotly.io as pio

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne"),
        title=dict(font=dict(color="black", size=22, family="Marianne-Bold"), x=0.01),
        paper_bgcolor="rgb(238, 238, 238)",
        colorway=["#2F4077", "#a94645", "#8D533E", "#417DC4"],
        yaxis=dict(
            tickformat=",0f",
            separatethousands=True,
        ),
    ),
)


pio.templates.default = "none+gouv"
