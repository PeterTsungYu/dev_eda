# library
import numpy as np
import pandas as pd
import requests
import random
import pandas as pd
import mariadb
from flask import send_file, request
from dash import Dash, dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# customized library
from utility import db_conn, db_get_table_lst, eda, db_table_to_df, compared_eda
import utility
import config 


app = Dash(__name__, 
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            routes_pathname_prefix="/Dash/",
            requests_pathname_prefix="/Dash/"
            )

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

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
            html.H6(id='db_table_preview_title'),
            html.Div(id='db_table_preview_container'),
            html.A(
                'Download Data',
                id='download_link',
                target="_blank"
            ),
            html.Br(),
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
                    id="eda_display_mode",
                    className="btn-group",
                    inputClassName="btn-check",
                    labelClassName="btn btn-outline-primary",
                    labelCheckedClassName="active",
                    options=[
                        {"label": "Table", "value": 'Table'},
                        {"label": "Visualization", "value": 'Visualization'},
                    ],
                    value='Table',
                ),
                dcc.Checklist(
                    id="eda_steady_state_check",
                    options=[{'label': 'Steady-State Only', 'value': 'SS'},],
                    value=['SS'],
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
                    persistence=True,
                ),
                dcc.Dropdown(
                    options=[],
                    placeholder='Analyze A Source Table...',
                    id='eda_db_table_dropdown',
                    style={"width": "50%"},
                ),
                html.Br(),
                dbc.Card(
                    dbc.CardBody([
                            html.H6("Time Range Slider [min]"),
                            html.P(id='row_count', children='Duration: None'),
                            dcc.RangeSlider(
                            step=10,
                            id='eda_time_range_slider',
                            updatemode='mouseup',
                            tooltip={"placement": "bottom", "always_visible": True},
                            marks=None,
                            pushable=1,
                            allowCross=False,
                            ),
                        ]
                    )
                ),
                dbc.Card(
                    dbc.CardBody([
                            html.H6("Summary Table"),
                            html.Div(id='eda_table_sum_debug'),
                            dash_table.DataTable(
                                                id='eda_table_sum', 
                                                editable=False,
                                                filter_action="native",
                                                sort_action="native",
                                                #sort_mode="multi",
                                                column_selectable="multi",
                                                row_selectable="multi",
                                                #row_deletable=True,
                                                selected_columns=[],
                                                selected_rows=[],
                                                style_table={'overflowX': 'auto',
                                                            'minWidth': '100%',
                                                            },
                                                fixed_columns={ 'headers': True, 'data': 1 },
                                                #css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                                                style_cell={ 
                                                            'textAlign': 'center',               # ensure adequate header width when text is shorter than cell's text
                                                            'minWidth': '180px', 'maxWidth': '180px', 'width': '180px',
                                                            'whiteSpace': 'normal',
                                                            'height': '35px',
                                                            },
                                                style_header={
                                                            'backgroundColor': '#0074D9',
                                                            'color': 'white'
                                                            },
                                                export_format='xlsx',
                                                export_headers='display',
                                        )
                        ]
                    )
                ),
            ],
            #style=dict(display='flex'),
            ),
            dbc.Card(
                    dbc.CardBody([
                        html.H6("Comparison Graph"),
                        html.Div(id='eda_comparison_graph_debug'),
                        dbc.Button('Generate Comparison Graph', id='comparison_graph_button', n_clicks=0),
                        html.Div(id='eda_comparison_graph_container'),
                        ])
            ),
            dbc.Card(
                    dbc.CardBody([
                        html.H6("Selection Graph"),
                        html.Div(id='eda_selection_graph_debug'),
                        html.Div(id='eda_selection_table_container'),
                        dbc.Button('Generate Selection Graph', id='selection_graph_button', n_clicks=0),
                        html.Div(id='eda_selection_graph_container'),
                        ])
            ),
            html.Br(),
            dbc.Card(
                    dbc.CardBody([
                        html.H6("Summary Graph"),
                        html.Div(id='eda_graph_container'),
                        ])
            ),
            html.Div(id="debug_output_1"),
        ]),
    ],
    body=True,
    ),
])


@app.callback(
    Output('debug_output_1', 'children'),
    Input('eda_display_mode', 'value'),
    Input('eda_steady_state_check', 'value'),
    Input('eda_time_range_slider', 'value'), 
)
def debug(a, b, c):
    print(a, b, c)
    return a, c[0], c[1] 


@app.callback(
    Output('download_link', 'href'),
    Output('db_table_preview_title', 'children'),
    Output('db_table_preview_container', 'children'),
    Input('db_table_dropdown', 'value'),
)
def update_table_preview_and_download_link(Table_name):
    if Table_name == None:
        return None, f'title: {Table_name}', None
    df = db_table_to_df(db_name='reformer', Table_name=Table_name).reset_index()
    df = df.head(5)
    print(df)
    table = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], style_table={'overflowX': 'auto','minWidth': '100%',})
    link = '/Dash/urlToDownload?value={}'.format(Table_name)
    return link, f'title: {Table_name}', table


@app.server.route('/Dash/urlToDownload') 
def download_csv():
    Table_name = request.args.get('value')
    df = db_table_to_df(db_name='reformer', Table_name=Table_name)
    df.to_csv(f'./csv/{Table_name}.csv')
    return send_file(f'csv/{Table_name}.csv',
                     mimetype='text/csv',
                     download_name=f'{Table_name}.csv',
                     as_attachment=True)


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
        succeed = False
        try:
            cur = db_conn(db_name=destination_db)
            #print(f"create table {new_table_name} as select * from {source_db}.{db_table};")
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
    Output('row_count', 'children'),
    Output('eda_time_range_slider', 'max'),
    Output('eda_time_range_slider', 'value'),
    Input('eda_source_db', 'value'),
    Input('eda_db_table_dropdown', 'value'),
)
def update_eda_time_slider(eda_source_db, eda_db_table):
    _lst = [eda_source_db, eda_db_table]
    #print(_lst)
    if any(_arg == None for _arg in _lst):
        return ['Duration: None', None, [None,None]]
    else:
        succeed = False
        try:
            cur = db_conn(db_name=eda_source_db)
            cur.execute(f"SELECT * FROM {eda_db_table}")
            cur.fetchall()
            max = cur.rowcount
            #print(max)
            succeed = True
        except mariadb.Error as e:
            print(f"Error connecting to MariaDB Platform: {e}")
            return ['Duration: None', None, [None,None]]
        finally:
            if succeed:
                cur.close()
                return [f'Duration: {round(max/60,2)} [min]', max/60, [0, max/60]]


@app.callback(
    Output('eda_table_sum', 'data'),
    Output('eda_table_sum', 'columns'),
    Output('eda_graph_container', 'children'),
    Output('eda_table_sum_debug', 'children'),
    Output('eda_selection_table_container', 'children'),
    Input('eda_time_range_slider', 'value'),
    Input('eda_display_mode', 'value'),
    Input('eda_steady_state_check', 'value'),
    Input('eda_source_db', 'value'),
    Input('eda_db_table_dropdown', 'value'),

)
def update_eda_report(eda_time_range, _mode:str, _ss:str, eda_source_db, eda_db_table):
    _ss = _ss[0] if len(_ss) == 1 else '!SS'
    _lst = [eda_time_range, _mode, _ss, eda_source_db, eda_db_table]
    #print(_lst)
    if any(_arg == None for _arg in _lst):
        return None, None, None, 'Something is missing', 'Something is missing'
    else:
        succeed = False
        try:
            table_data, table_columns, fig, msg = eda(db_name=eda_source_db, Table_name=eda_db_table, Time=eda_time_range, SS=_ss, mode=_mode)    
            succeed = True
        except Exception as e:
            return None, None, None, e, None
        finally:
            if succeed:
                cols = dash_table.DataTable(data=None, columns=[{"name": i, "id": i, "selectable": True} for i in utility.State_eda_df.columns], 
                                            style_table={'overflowX': 'auto','minWidth': '100%',}, column_selectable="multi", selected_columns=[],)    
                return table_data, table_columns, fig, msg, cols


@app.callback(
    Output('eda_table_sum', 'style_data_conditional'),
    Input('eda_table_sum', 'selected_columns'),
    Input('eda_table_sum', 'selected_rows')
)
def update_eda_table_styles(selected_columns, selected_rows):
    print(selected_columns, selected_rows)
    selected_cols_conditions = [{
                                    'if': { 'column_id': i },
                                    'background_color': '#D2F3FF'
                                } for i in selected_columns]
    selected_rows_conditions = [{
                                    'if': { 'row_index': i },
                                    'background_color': '#11FFBB'
                                } for i in selected_rows]
    return selected_cols_conditions + selected_rows_conditions


@app.callback(
    Output('eda_comparison_graph_container', 'children'),
    Output('eda_comparison_graph_debug', 'children'),
    Input('comparison_graph_button', 'n_clicks_timestamp'),
    State('eda_table_sum', 'selected_columns'),
    State('eda_table_sum', 'selected_rows'),
)
def generate_compare_graph(n_clicks_timestamp, selected_columns, selected_rows):
    fig = compared_eda(selected_rows=selected_rows, selected_columns=selected_columns)
    return fig, f'selected_rows: {selected_rows}, selected_columns: {selected_columns}'

'''
@app.callback(
    Output('eda_comparison_graph_container', 'children'),
    Output('eda_comparison_graph_debug', 'children'),
    Input('comparison_graph_button', 'n_clicks_timestamp'),
    State('eda_table_sum', 'selected_columns'),
    State('eda_table_sum', 'selected_rows'),
)
def generate_select_graph(n_clicks_timestamp, selected_columns, selected_rows):
    fig = compared_eda(selected_rows=selected_rows, selected_columns=selected_columns)
    return fig, f'selected_rows: {selected_rows}, selected_columns: {selected_columns}' 
'''

if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
