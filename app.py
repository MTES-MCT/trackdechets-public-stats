# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from os import getenv
import dash_bootstrap_components as dbc
from datetime import date

app = dash.Dash("trackdechets-public-stats", title='Trackdéchets : statistiques et impact',
                external_stylesheets=[dbc.themes.BOOTSTRAP])
theme = 'plotly_white'

# postgresql://admin:admin@localhost:5432/ibnse
engine = create_engine(getenv('DATABASE_URL'))

df = pd.read_sql_query('SELECT id, status, "Form"."createdAt", "Form"."isDeleted" FROM "Form"',
                       con=engine)
df = df.loc[(df['isDeleted'] == False) & (df['status'] != 'DRAFT')]

#  2020-10-26 14:52:54.995 ===> 2020-10-26
df['createdAt'] = df['createdAt'].dt.date

bsdd = df.count()[0]
fig = px.bar(df.groupby(by='status').count().sort_values(['id'], ascending=True), x='id', title="Répartition des BSDD "
                                                                                                "par statut")
fig.layout.template = theme
line = px.line(df[['createdAt', 'id']].groupby(by='createdAt').count(), y='id')

app.layout = html.Div(children=[
    html.H1(children='Quantité de déchets traités'),

    dbc.Container(fluid=True, children=[
        dbc.Row(
            [
                dcc.DatePickerRange(
                    id='my-date-picker-range',
                    min_date_allowed=date(1995, 8, 5),
                    max_date_allowed=date(2017, 9, 19),
                    initial_visible_month=date(2017, 8, 5),
                    end_date=date(2017, 8, 25)
                ),
                html.Div(id='output-container-date-picker-range')
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id='example-graph',
                        figure=fig
                    )
                ),
                dbc.Col(
                    dcc.Graph(
                        id='example-graph2',
                        figure=fig
                    )
                )
            ]
        ),
        dbc.Row(
            [
                dcc.Graph(
                    id='example-graph3',
                    figure=line
                ),
                html.P("Nombre total de BSDD " + str(bsdd))
            ]
        )
    ]
                  )

])

if __name__ == '__main__':
    app.run_server(debug=True, port=int(getenv('PORT')))
