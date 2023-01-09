import plotly.graph_objects as go
import plotly.io as pio

from src.data.data_extract import get_bs_data, get_company_data, get_user_data

# Override the 'none' template
pio.templates["gouv"] = go.layout.Template(
    layout=dict(
        font=dict(family="Marianne"),
        title=dict(font=dict(color="black", size=22, family="Marianne-Bold"), x=0.01),
        paper_bgcolor="rgb(238, 238, 238)",
        colorway=[
            "#000091",
            "#5E2A2B",
            "#66673D",
            "#E4794A",
            "#60E0EB",
        ],  # Taken from DSFR illustrative colors : https://gouvfr.atlassian.net/wiki/spaces/DB/pages/911081484/Palette+de+couleurs+version+1+DSFR+1.1.0#Les-couleurs-illustratives%5BhardBreak%5D
        yaxis=dict(
            tickformat=",0f",
            separatethousands=True,
        ),
    ),
)


pio.templates.default = "gouv"

# Load all needed data
BSDD_DATA = get_bs_data(
    "get_bsdd_data.sql",
)
BSDA_DATA = get_bs_data(
    "get_bsda_data.sql",
)
BSFF_DATA = get_bs_data(
    "get_bsff_data.sql",
)
BSDASRI_DATA = get_bs_data(
    "get_bsdasri_data.sql",
)

COMPANY_DATA = get_company_data()
USER_DATA = get_user_data()
