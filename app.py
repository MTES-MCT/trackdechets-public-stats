# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
from dash import dcc
from dash import html
import plotly.express as px
import pandas as pd
from sqlalchemy import create_engine
from os import getenv

app = dash.Dash(__name__)

# postgresql://admin:admin@localhost:5432/ibnse
engine = create_engine(getenv('PGSQL_CONNECT'))

df = pd.read_sql_query('SELECT id, status, "Form"."isDeleted" FROM "default$default"."Form"', con=engine)
# df = pd.read_csv('./td-prod.csv', delimiter='|')

# breakpoint()
bsdd = df[df['isDeleted'] == False].count()[0]
status_order = ['bla', 'DRAFT']
fig = px.bar(df.groupby(by='status').count().sort_values(['id'], ascending=True), x='id', title="Répartition des BSDD "
                                                                                                "par statut")

app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Dash: A web application framework for your data.
    '''),

    dcc.Graph(
        id='example-graph',
        figure=fig
    ),

    html.P("Nombre total de BSDD " + str(bsdd))
])

if __name__ == '__main__':
    app.run_server(debug=True)
