# library
import os
import numpy as np
import pandas as pd
import requests
import random
from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
from dotenv import load_dotenv
import mariadb

# customized library
from utility import db_conn, plot
import config 

load_dotenv()
username = os.environ.get("db_user")
password = os.environ.get("db_pwd")

def db_get_table_lst(db_name:str):
    global username, password
    try:
        cur = db_conn(username=username, password=password, db_name=db_name)
        cur.execute('SHOW tables')
        source_table_lst = [u for i in cur.fetchall()[:] for u in i][::-1]
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None
    finally:
        cur.close()
    return source_table_lst


app = Dash(__name__, 
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            routes_pathname_prefix="/Dash/",
            requests_pathname_prefix="/Dash/"
            )

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

df = pd.read_csv('https://plotly.github.io/datasets/country_indicators.csv')

app.layout = html.Div([
    html.H1(children='Hi Platformer', 
            style={
                'textAlign': 'center',
                'color': colors['text'],
            }),

    dbc.Card([
        html.Div([
            html.H3(children='Archive', 
                    style={'color': colors['text'],}
                    ),
            html.I(children='Archive From Database:',
                    style={
                        'textAlign': 'left',
                        'color': colors['text'],
                    }),
            dcc.RadioItems(
                ['reformer',],
                'reformer',
                id='source_db',
                inline=True
            ),
            html.Br(),
            dcc.Dropdown(
                options=db_get_table_lst('reformer'),
                placeholder='Select A Source Table...',
                id='db_table_dropdown',
                style={"width": "50%"},
            ),
            html.Br(),
            html.I(children='To Destination Database:', 
                    style={
                        'textAlign': 'left',
                        'color': colors['text'],
                    }),
            dcc.Dropdown(
                ['Reformer_BW', 'Reformer_BW_Alert', 'Reformer_SE', 'Reformer_SE_Alert', 'Prototype_15kW', 'Prototype_15kW_Alert'],
                placeholder='Select A Destination Database...',
                id='destination_db',
                style={"width": "50%"},
            ),
            html.Br(),
            html.Div([
                dbc.Input(placeholder="Input Goes Here...", type="text", size="md", 
                        id='new_table_name_input', debounce=True, style={"width": "30%"},
                        ),
                dbc.FormText("Please Assign A New Table Name"),
                ]),
            html.Hr(),
            dbc.Button('Archive', id='archive_button', n_clicks=0),
            html.Span(id="archive_output", style={"margin-left":'10px', "verticalAlign": "middle"}),
        ],),
    ],
    body=True,
    ),
    html.Br(),

    dbc.Card([
        html.Div([
            html.H3(children='Data Analysis', 
                    style={'color': colors['text'],}
            ),
            html.Div(
                [
                dbc.RadioItems(
                    id="display_mode",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "Only Calc", "value": 'Calc'},
                        {"label": "Plot It!", "value": 'Ploting'},
                    ],
                    value='Calc',
                ),
                dcc.Checklist(
                    id="steady_state_check",
                    options=['Steady-State Only'],
                    #inline=True,
                    style={
                        "margin-left":'2em',
                        "verticalAlign":"middle"
                    },
                )
                ],
                style=dict(display='flex'),
            ),
            html.Br(),
            html.I(children='From Database:',
                    style={
                        'textAlign': 'left',
                        'color': colors['text'],
                    }
            ),
            html.Div([
            dcc.Dropdown(
                ['reformer', 'Reformer_BW', 'Reformer_BW_Alert', 'Reformer_SE', 'Reformer_SE_Alert', 'Prototype_15kW', 'Prototype_15kW_Alert'],
                'reformer',
                placeholder='Select A Database...',
                id='eda_source_db',
                style={"width": "50%"},
            ),
            dcc.Dropdown(
                options=[],
                placeholder='Analyze A Source Table...',
                id='eda_db_table_dropdown',
                style={"width": "50%"},
            ),
            ],
            #style=dict(display='flex'),
            ),
            html.Br(),
        ]),
    ],
    body=True,
    ),
    
    html.Div(id="debug_output"),

    html.Div([
            dcc.Dropdown(
                df['Indicator Name'].unique(),
                'Fertility rate, total (births per woman)',
                id='xaxis-column'
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='xaxis-type',
                inline=True
            ),
            dcc.Dropdown(
                df['Indicator Name'].unique(),
                'Life expectancy at birth, total (years)',
                id='yaxis-column'
            ),
            dcc.RadioItems(
                ['Linear', 'Log'],
                'Linear',
                id='yaxis-type',
                inline=True
            )
        ],
        ),

    dcc.Graph(id='indicator-graphic'),

    dcc.Slider(
        df['Year'].min(),
        df['Year'].max(),
        step=None,
        id='year--slider',
        value=df['Year'].max(),
        marks={str(year): str(year) for year in df['Year'].unique()},

    )
])

@app.callback(
    Output("archive_output", "children"), 
    [
        Input("archive_button", "n_clicks_timestamp"),
        Input("source_db", "value"),
        Input("db_table_dropdown", "value"),
        Input("destination_db", "value"),
        Input("new_table_name_input", "value"),
    ]
)
def on_archive_button_click(n_clicks_timestamp, source_db, db_table, destination_db, new_table_name):
    _lst = [n_clicks_timestamp, source_db, db_table, destination_db, new_table_name]
    #print(_lst)
    if any(_arg == None for _arg in _lst):
        return "Something Is Missing..."
    else:
        #print(n_clicks_timestamp)
        global username, password
        succeed = False
        try:
            cur = db_conn(username=username, password=password, db_name=destination_db)
            print(f"create table {new_table_name} as select * from {source_db}.{db_table};")
            cur.execute(f"create table {new_table_name} as select * from {source_db}.{db_table};")
            succeed = True
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return "Not Archived" 
        finally:
            if succeed:
                cur.close()
                return f"Archived As {destination_db}.{new_table_name}"


@app.callback(
    Output('eda_db_table_dropdown', 'options'),
    Input('eda_source_db', 'value')
    )
def update_eda_table_dropdown(eda_source_db):
    return db_get_table_lst(eda_source_db)

@app.callback(
    Output('debug_output', 'children'),
    Input('display_mode', 'value'),
    Input('steady_state_check', 'value'), 
)
def debug(a, b):
    print(a,b)
    return a, b[0] 

@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value'),
    Input('xaxis-type', 'value'),
    Input('yaxis-type', 'value'),
    Input('year--slider', 'value'))
def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df[df['Year'] == year_value]
    print(dff.head())
    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['Value'],
                     y=dff[dff['Indicator Name'] == yaxis_column_name]['Value'],
                     hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['Country Name'])

    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    fig.update_xaxes(title=xaxis_column_name,
                     type='linear' if xaxis_type == 'Linear' else 'log')

    fig.update_yaxes(title=yaxis_column_name,
                     type='linear' if yaxis_type == 'Linear' else 'log')

    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
