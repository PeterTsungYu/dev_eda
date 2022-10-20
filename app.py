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
from utility import db_conn, db_get_table_lst, eda, db_table_to_df, compared_eda, selected_eda, animation_eda
import utility
import config 


app = Dash(__name__, 
            external_stylesheets=[dbc.themes.BOOTSTRAP],
            routes_pathname_prefix="/Dash/",
            requests_pathname_prefix="/Dash/",
            suppress_callback_exceptions=True,
            )

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

url = dcc.Location(id='url', refresh=True)
app.layout = html.Div(children=[
    # represents the browser address bar and doesn't render anything
    url,
    # content will be rendered in this element
    html.Div(id='page_content', children=[])
    ])

data_analysis_layout = [html.Div([
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
            dcc.Dropdown(
                    ['reformer', 'Reformer_BW', 'Reformer_BW_Alert', 'Reformer_SE', 'Reformer_SE_Alert', 'Prototype_15kW', 'Prototype_15kW_Alert'],
                    'reformer',
                    placeholder='Select A Database...',
                    id='source_db',
                    style={"width": "50%"},
                    persistence=True,
                ),
            dcc.Dropdown(
                options=[],
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
                            html.H6("Report Table and Graph"),
                            html.Br(),
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
                            html.Br(),
                            html.Div(id='eda_table_sum_debug'),
                            dbc.Button('Generate Report', id='report_button', n_clicks=0),
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
                            ),
                            html.Div(id='eda_graph_container'),
                            dcc.Store(id='eda_report_store'),
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
                        dcc.Store(id='eda_comparison_table_store'),
                        ])
            ),
            dbc.Card(
                    dbc.CardBody([
                        html.H6("Selection Graph"),
                        html.Div(id='eda_selection_graph_debug'),
                        dash_table.DataTable(id='selection_table', data=None, 
                                            style_table={'overflowX': 'auto','minWidth': '100%',}, style_header={'backgroundColor': '#0074D9', 'color': 'white'},
                                            style_cell={'textAlign': 'center', 'minWidth': '180px', 'maxWidth': '180px', 'width': '180px', 'whiteSpace': 'normal', 'height': '35px',},
                                            column_selectable="multi", selected_columns=[],),    
                        dbc.Button('Generate Selection Graph', id='selection_graph_button', n_clicks=0),
                        html.Div(id='eda_selection_graph_container'),
                        dcc.Store(id='eda_selection_table_store'),
                        ]),
            ),
            dbc.Card(
                    dbc.CardBody([
                        html.H6("Animation Graph"),
                        html.Div(id='eda_animation_graph_debug'),
                        dash_table.DataTable(id='animation_table', data=None, 
                                            style_table={'overflowX': 'auto','minWidth': '100%',}, style_header={'backgroundColor': '#0074D9', 'color': 'white'},
                                            style_cell={'textAlign': 'center', 'minWidth': '180px', 'maxWidth': '180px', 'width': '180px', 'whiteSpace': 'normal', 'height': '35px',},
                                            column_selectable="multi", selected_columns=[],),    
                        dbc.Button('Generate Animation Graph', id='animation_graph_button', n_clicks=0),
                        html.Div(id='eda_animation_graph_container'),
                        dcc.Store(id='eda_animation_table_store'),
                        ]),
            ),
            html.Div(id="debug_output_1"),
            dbc.Card(
                    dbc.CardBody([
                        html.H6("Summary"),
                        html.Div(id='eda_summary_debug'),
                        html.Div(id='eda_summary_container'),
                        #dcc.Store(id='eda_comparison_table_store'),
                        ])
            ),
        ]),
    ],
    body=True,
    ),
])]


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
    Output('new_table_name_input', 'value'),
    Output('destination_db', 'value'),
    Input('db_table_dropdown', 'value'),
)
def update_table_preview_and_download_link(Table_name):
    if Table_name == None:
        return None, f'title: {Table_name}', None, None, None
    df = db_table_to_df(db_name='reformer', Table_name=Table_name).reset_index()
    df = df.head(5)
    #print(df)
    table = dash_table.DataTable(df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], style_table={'overflowX': 'auto','minWidth': '100%',})
    link = '/Dash/urlToDownload?value={}'.format(Table_name)
    if 'BW' in Table_name:
        destination_db = 'Reformer_BW'
    elif 'SE' in Table_name:
        destination_db = 'Reformer_SE'
    elif '15kW' in Table_name:
        destination_db = 'Prototype_15kW'
    return link, f'title: {Table_name}', table, Table_name, destination_db


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
    Output('db_table_dropdown', 'options'),
    Input('source_db', 'value')
)
def update_table_dropdown(source_db):
    return db_get_table_lst(source_db)


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
    Input('eda_db_table_dropdown', 'value'),
    State('eda_source_db', 'value'),
)
def update_eda_time_slider(eda_db_table, eda_source_db):
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
    Output('eda_report_store', 'data'),
    Output('eda_table_sum', 'data'),
    Output('eda_table_sum', 'columns'),
    Output('eda_graph_container', 'children'),
    Output('eda_table_sum_debug', 'children'),
    Output('selection_table', 'columns'),
    Output('animation_table', 'columns'),
    Output('eda_summary_container', 'children'),
    Input('report_button', 'n_clicks_timestamp'),
    Input('eda_db_table_dropdown', 'value'),
    State('eda_report_store', 'data'),
    State('eda_time_range_slider', 'value'),
    State('eda_display_mode', 'value'),
    State('eda_steady_state_check', 'value'),
    State('eda_source_db', 'value'),

)
def update_eda_report(n_clicks_timestamp, db_table, pre_db_table, time_range, _mode:str, _ss:str, source_db,):
    _ss = _ss[0] if len(_ss) == 1 else '!SS'
    _lst = [time_range, _mode, _ss, source_db, db_table]
    #print(_lst)
    debug_msg = f'table: {db_table}@{source_db}, time_range: {time_range}, mode: {_mode}, Steady_State_box: {_ss}, any_Steady_State: False'
    if any(_arg == None for _arg in _lst):
        return None, None, [], [], debug_msg, [], [], []
    
    if db_table != pre_db_table:
        return db_table, None, [], [], debug_msg, [], [], [] 
    else:
        table_data, table_columns, fig, debug_msg, markdown = eda(db_name=source_db, Table_name=db_table, Time=time_range, SS=_ss, mode=_mode)    
        cols = [{"name": i, "id": i, "selectable": True} for i in utility.State_eda_df.columns]
        return db_table, table_data, table_columns, fig, debug_msg, cols, cols, markdown


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
    Output('eda_comparison_table_store', 'data'),
    Output('eda_comparison_graph_container', 'children'),
    Output('eda_comparison_graph_debug', 'children'),
    Input('comparison_graph_button', 'n_clicks_timestamp'),
    Input('eda_db_table_dropdown', 'value'),
    State('eda_comparison_table_store', 'data'),
    State('eda_source_db', 'value'),
    State('eda_table_sum', 'selected_columns'),
    State('eda_table_sum', 'selected_rows'),
)
def generate_compare_graph(n_clicks_timestamp, db_table, pre_db_table, source_db, selected_columns, selected_rows):
    print('generate_compare_graph')
    print(pre_db_table)
    print(db_table)
    if db_table != pre_db_table:
        return db_table, [], f'table: {db_table}@{source_db}, selected_columns: {selected_columns}'
    else:    
        fig = compared_eda(selected_rows=selected_rows, selected_columns=selected_columns)
        return db_table, fig, f'table: {db_table}@{source_db}, selected_rows: {selected_rows}, selected_columns: {selected_columns}'


@app.callback(
    Output('eda_selection_table_store', 'data'),
    Output('eda_selection_graph_container', 'children'),
    Output('eda_selection_graph_debug', 'children'),
    Input('selection_graph_button', 'n_clicks_timestamp'),
    Input('eda_db_table_dropdown', 'value'),
    State('eda_selection_table_store', 'data'),
    State('eda_source_db', 'value'),
    State('selection_table', 'selected_columns'),
)
def generate_select_graph(n_clicks_timestamp, db_table, pre_db_table, source_db, selected_columns):
    print('generate_select_graph')
    print(pre_db_table)
    print(db_table)

    if db_table != pre_db_table:
        return db_table, [], f'table: {db_table}@{source_db}, selected_columns: {selected_columns}' 
    else:
        fig = selected_eda(selected_columns=selected_columns)
        return db_table, fig, f'table: {db_table}@{source_db}, selected_columns: {selected_columns}' 

@app.callback(
    Output('eda_animation_table_store', 'data'),
    Output('eda_animation_graph_container', 'children'),
    Output('eda_animation_graph_debug', 'children'),
    Input('animation_graph_button', 'n_clicks_timestamp'),
    Input('eda_db_table_dropdown', 'value'),
    State('eda_animation_table_store', 'data'),
    State('eda_source_db', 'value'),
    State('animation_table', 'selected_columns'),
)
def generate_animation_graph(n_clicks_timestamp, db_table, pre_db_table, source_db, selected_columns):
    print('generate_animation_graph')
    print(pre_db_table)
    print(db_table)

    if db_table != pre_db_table:
        return db_table, [], f'table: {db_table}@{source_db}, selected_columns: {selected_columns}' 
    else:
        fig = animation_eda(selected_columns=selected_columns)
        return db_table, fig, f'table: {db_table}@{source_db}, selected_columns: {selected_columns}'

# route to check_layout / index_page / leave_form
@app.callback(
    [
        Output('page_content', 'children'),
        ],
    [
        Input('url', 'pathname'), 
        Input('url', 'search'),
        ]
    )
def display_page(pathname, search):
    print([pathname, search])

    if pathname == '/Dash/':
        return data_analysis_layout
    elif pathname == '/Dash/SE_Reformer/':
        pass


if __name__ == '__main__':
    app.run_server(debug=True, threaded=True)
