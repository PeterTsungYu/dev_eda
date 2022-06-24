import os
from dotenv import load_dotenv
import sys
import re
import mariadb
import pandas as pd
import matplotlib.pyplot as plt
import config
from dash import dcc
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go


load_dotenv()
username = os.environ.get("db_user")
password = os.environ.get("db_pwd")
State_eda_df_sum = pd.DataFrame()
State_eda_df = pd.DataFrame()

def db_conn(db_name:str):
    global username, password
    try:
        # Connect to MariaDB Platform
        conn = mariadb.connect(
            user=username,
            password=password,
            host="localhost",
            port=3306,
            database=db_name,
            autocommit=True
        )
        # Get Cursor for tx
        cur = conn.cursor(named_tuple=False)
        #print(conn)
        return cur
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)


def db_get_table_lst(db_name:str):
    try:
        cur = db_conn(db_name=db_name)
        cur.execute('SHOW tables')
        source_table_lst = [u for i in cur.fetchall()[:] for u in i][::-1]
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        return None
    finally:
        cur.close()
    return source_table_lst


def db_table_to_df(db_name:str, Table_name: str):
    df = pd.DataFrame()
    try:
        cur = db_conn(db_name=db_name)
        cur.execute(f"SELECT * FROM {Table_name}")
        df = pd.DataFrame(cur.fetchall(), columns=[entry[0] for entry in cur.description]).set_index('Id')
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
    finally:
        cur.close()
        return df


def eda(db_name:str, Table_name: str, Time: tuple, SS: str, mode: str):
    df = db_table_to_df(db_name=db_name, Table_name=Table_name)
    if df.empty:
        return None, [], [], 'db is not loaded'
    
    global State_eda_df
    State_eda_df = df
    _leng = len(df)
    _bls=[]
    _effls = 0
    _heff = 0
    _get = 0
    _wasted = 0
    
    if db_name == 'Reformer_SE':
        Set_Point_lst = config.SE_Set_Point_lst
        TC_ss = 'TC10'
        avg = {
                'avg_Air_MFC_SET_SV':'Air_MFC_SET_SV',
                'avg_H2_MFC_SET_SV':'H2_MFC_SET_SV',
                'avg_TC6':'TC6',
#                    'avg_TC7':'TC7',
#                    'avg_TC8':'TC8',
                'avg_TC12':'TC12',
                'avg_Exhaust_gas':'Exhaust_gas',
                'avg_TC9':'TC9',
                'avg_TC10':'TC10', 
                'avg_TC11':'TC11', 
                'avg_EVA_Out':'EVA_Out',
                'avg_RAD_Out':'RAD_Out',
                'avg_Scale':'Scale', 
#                    'avg_DFM_RichGas':'DFM_RichGas',
                'avg_DFM_RichGas_1min':'DFM_RichGas_1min',
#                    'avg_DFM_AOG':'DFM_AOG',
                'avg_DFM_AOG_1min':'DFM_AOG_1min',
                'avg_current':'current',
                'avg_GA_H2':'GA_H2',
                'avg_GA_CO2':'GA_CO2',
                'avg_GA_CO':'GA_CO',
                'avg_GA_N2':'GA_N2',
                'avg_GA_CH4':'GA_CH4',
                'avg_ADAM_P_Out':'ADAM_P_Out',
                'avg_ADAM_P_MeMix':'ADAM_P_MeMix',
                'avg_Header_BR_PV':'Header_BR_PV',
                'avg_Header_EVA_PV':'Header_EVA_PV',
                'avg_PCB_SET_PV':'PCB_SET_PV'
        }
    elif db_name == 'Reformer_BW':
        Set_Point_lst = config.BW_Set_Point_lst
        TC_ss = 'TC8'
        avg = {'avg_TC7':'TC7',
                'avg_TC8':'TC8',
                'avg_TC9':'TC9',
                'avg_TC10':'TC10',
                'avg_Steam_Out':'TC11',
                'avg_EVA_Out':'EVA_out',
                'avg_Header_BR_PV':'Header_BR_PV',
                'avg_RAD_out':'RAD_out',
                'avg_Scale':'Scale', 
                'avg_DFM_RichGas':'DFM_RichGas', 
                'avg_DFM_AOG':'DFM_AOG',
                'avg_GA_H2':'GA_H2',
                'avg_GA_CO2':'GA_CO2',
                'avg_GA_CO':'GA_CO',
                'avg_Air_MFC_SET_SV':'Air_MFC_SET_SV',
                'avg_H2_MFC_SET_SV':'H2_MFC_SET_SV',
                'avg_Pump_SET_SV':'Pump_SET_SV',
                'avg_Lambda':'Lambda'
                }
    else:
        pass
    
    for i in Set_Point_lst:
        i.cond(df, TC=TC_ss, current='current')
        i.avg_calc(df=df, d=avg, db_name=db_name)
        if i.ss_time:
            for u in i.ss_time:
                #print(u)
                for v in range(u[0], u[-1]):
                    _bls.append(v)
            for q in i.ss_avg['con_rate']:
                q.gen_series(leng=_leng)
#                     print(q.series.sum())
                _effls = _effls + q.series
            for h in i.ss_avg['heff']:
                h.gen_series(leng=_leng)
                _heff = _heff + h.series
#                     print(_heff)
            for g in i.ss_avg['get']:
                g.gen_series(leng=_leng)
                _get = _get + g.series
#                     print(_get)
            for w in i.ss_avg['wasted']:
                w.gen_series(leng=_leng)
                _wasted = _wasted + w.series
#                     print(_wasted)
    
    df_sum = pd.DataFrame()
    _Steady_state = False
    for i in Set_Point_lst:
        i.gen_dataframe()
        if i.ss_time:
            df_sum = pd.concat([df_sum, i.sum_rows])
    if not df_sum.empty:
        _Steady_state = True
        df_sum = df_sum.sort_values(by=['Init[s]']).reset_index(drop=True)
        global State_eda_df_sum
        State_eda_df_sum = df_sum
        table_data = df_sum.to_dict('records')
        table_columns = [{"name": i, "id": i, "selectable": True} for i in df_sum.columns]
        
        get_values = lambda df, col : df.get(col) if _Steady_state else None
        Steady_State_lst = get_values(df_sum, 'Steady State')
        markdown = [
                    dcc.Markdown(
                        '''
                        * Item 1
                        * Item 2
                        * Item 2a
                        * Item 2b
                        '''
                    ),
                    dcc.Markdown(
                        f'''
                        * state_{Steady_State_lst[0]}
                        * state_{Steady_State_lst[1]}
                        '''
                    ),
        ]

        if mode == 'Table':
            return table_data, table_columns, [], f'table: {Table_name}@{db_name}, time_range: {Time}, mode: {mode}, Steady_State_box: {SS}, any_Steady_State: {_Steady_state}', markdown
    else:
        print('No Steady-State is found!')
        if mode == 'Table':
            table_columns = [{"name": i, "id": i, "selectable": True} for i in df.columns]
            return None, table_columns, [], f'table: {Table_name}@{db_name}, time_range: {Time}, mode: {mode}, Steady_State_box: {SS}, any_Steady_State: {_Steady_state}', []


    if mode == 'Visualization':
        graph_lst = []
        x_axis = df.index/60
        if SS == 'SS':        
            _bmask = pd.Series([True if i in _bls else False for i in range(0, _leng)])
            df = df.where(_bmask, 0)
        
        ## create a secondary y-axis
        fig_TC_Curve = make_subplots(specs=[[{"secondary_y": True}]])
        graph_lst.append(
            dcc.Graph(id='fig_TC_Curve', figure=fig_TC_Curve)
        )
        if db_name == 'Reformer_SE':
            ## add your data using traces
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC10'], name='TC10: CatBed_Front (Right)', fill='tozeroy', mode='lines'),
                secondary_y=True
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC6'], name='TC6', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC12'], name='Out', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['Exhaust_gas'], name='Exhaust_gas', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC9'], name='TC9', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC11'], name='TC11', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['EVA_Out'], name='EVA_Out', mode='lines'),
            )

        elif db_name == 'Reformer_BW':
            ## add your data using traces
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC7'], name='TC7: CatBed_Front (Right)', fill='tozeroy', mode='lines'),
                secondary_y=True
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC11'], name='Steam_Out', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC8'], name='SR_Front', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC9'], name='SR_Mid', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['TC10'], name='SR_End', mode='lines'),
            )
            fig_TC_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['Header_BR_PV'], name='BR_outlet', mode='lines'),
            )
        fig_TC_Curve.update_layout(
            title='TC Curve',
            xaxis = dict(title= 'Time [min]', tickmode = 'linear', tick0 = 0, dtick = 10),
            xaxis_range=Time,
            yaxis = dict(title='Temp [oC]', tickmode = 'linear', rangemode='tozero', dtick = 50),
            yaxis2 = dict(title='Temp [oC]', tickmode = 'linear', rangemode='tozero', dtick = 50),
        )    
        fig_TC_Curve.for_each_xaxis(lambda x: x.update(showgrid=False))
        fig_TC_Curve.for_each_yaxis(lambda x: x.update(showgrid=False))


        fig_H2_Curve = make_subplots(specs=[[{"secondary_y": True}]])
        graph_lst.append(
            dcc.Graph(id='fig_H2_Curve', figure=fig_H2_Curve)
        )
        fig_H2_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['current'], name='Expected Current (Right)', mode='lines'),
                secondary_y=True
            )
        fig_H2_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['DFM_AOG_1min'], name='DFM_AOG_1min', mode='lines', stackgroup='one'),
        )
        fig_H2_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['DFM_RichGas_1min'], name='DFM_RichGas_1min', mode='lines', stackgroup='one'),
        )
        fig_H2_Curve.update_layout(
            title='H2 Curve',
            xaxis = dict(title='Time [min]', tickmode = 'linear', tick0 = 0, dtick = 10),
            xaxis_range=Time,
            yaxis = dict(title='H2 Production [LPM]', tickmode = 'linear', rangemode='tozero', dtick = 20),
            yaxis2 = dict(title='Expected Current [A]', tickmode = 'linear', rangemode='tozero', dtick = 20),
        )
        fig_H2_Curve.for_each_xaxis(lambda x: x.update(showgrid=False))
        fig_H2_Curve.for_each_yaxis(lambda x: x.update(showgrid=False))


        fig_Gas_Curve = make_subplots(specs=[[{"secondary_y": True}]])
        graph_lst.append(
            dcc.Graph(id='fig_Gas_Curve', figure=fig_Gas_Curve)
        )
        fig_Gas_Curve.add_trace(
                go.Scatter(x=x_axis, y=df['GA_CO'], name='GA_CO_line (Right)', mode='lines'),
                secondary_y=True
            )
        fig_Gas_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['GA_H2'], name='GA_H2', mode='lines', stackgroup='one'),
        )
        fig_Gas_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['GA_CO'], name='GA_CO', mode='lines', stackgroup='one'),
        )
        fig_Gas_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['GA_CO2'], name='GA_CO2', mode='lines', stackgroup='one'),
        )
        fig_Gas_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['GA_CH4'], name='GA_CH4', mode='lines', stackgroup='one'),
        )
        fig_Gas_Curve.add_trace(
            go.Scatter(x=x_axis, y=df['GA_N2'], name='GA_N2', mode='lines', stackgroup='one'),
        )
        fig_Gas_Curve.update_layout(
            title='Gas Curve',
            xaxis = dict(title='Time [min]', tickmode = 'linear', tick0 = 0, dtick = 10),
            xaxis_range=Time,
            yaxis = dict(title='Gas Composition [%]', tickmode = 'linear', rangemode='tozero', dtick = 20),
            yaxis2 = dict(title='CO [%]', tickmode = 'linear', rangemode='tozero', dtick = .5),
        )
        fig_Gas_Curve.for_each_xaxis(lambda x: x.update(showgrid=False))
        fig_Gas_Curve.for_each_yaxis(lambda x: x.update(showgrid=False))

        if _Steady_state:
            #print(table_data, table_columns, graph_lst)
            df_con_rate = df_sum[['Steady State', 'con_rate']].reset_index()
            df_con_rate.columns = ['order', 'Steady State', 'value']
            df_con_rate['order'] = [f'Order_{i+1}' for i in df_con_rate['order']]
            df_con_rate['type'] = 'con_rate'
            df_heff = df_sum[['Steady State', 'heff']].reset_index()
            df_heff.columns = ['order', 'Steady State', 'value']
            df_heff['order'] = [f'Order_{i+1}' for i in df_heff['order']]
            df_heff['type'] = 'heff'
            df_cluster = pd.concat([df_con_rate, df_heff], sort=False)
            #print(df_cluster)
            fig_Rate_Bar = px.bar(df_cluster, title='Different Rate Cluster Bar', x="type", y="value",
                        color='order', barmode='group', text='Steady State', labels={"value": "Percentage [%]", "type": "Rate Category"})
            graph_lst.append(
                dcc.Graph(id='fig_Rate_Bar', figure=fig_Rate_Bar) 
            )
            
            df_thermo = df_sum[['Steady State', 'get', 'wasted']].reset_index()
            df_thermo.columns = ['order', 'Steady State', 'get', 'wasted']
            fig_Thermo_Bar = px.bar(df_thermo, x='order', y=["wasted", "get"], labels={"value": "heat [kW]"}, title="Thermodynamics Calc Bar", text='value')
            graph_lst.append(
                dcc.Graph(id='fig_Thermo_Bar', figure=fig_Thermo_Bar) 
            )

            return table_data, table_columns, graph_lst, f'table: {Table_name}@{db_name}, time_range: {Time}, mode: {mode}, Steady_State_box: {SS}, any_Steady_State: {_Steady_state}', markdown
        else:
            table_columns = [{"name": i, "id": i, "selectable": True} for i in df.columns]
            return None, table_columns, graph_lst, f'table: {Table_name}@{db_name}, time_range: {Time}, mode: {mode}, Steady_State_box: {SS}, any_Steady_State: {_Steady_state}', markdown
    
        # set to global var
    get_values = lambda df, col : df.get(col) if _Steady_state else None
    Steady_State_lst = get_values(df_sum, 'Steady State')
    avg_H2_flow_lst = get_values(df_sum, 'avg_H2_flow')
    ideal_H2_flow_lst = get_values(df_sum, 'ideal_H2_flow')
    avg_Air_MFC_SET_SV_lst = get_values(df_sum, 'avg_Air_MFC_SET_SV')
    avg_H2_MFC_SET_SV_lst = get_values(df_sum, 'avg_H2_MFC_SET_SV')
    avg_GA_H2_lst = get_values(df_sum, 'avg_GA_H2')
    avg_GA_CO2_lst = get_values(df_sum, 'avg_GA_CO2')
    avg_GA_CO_lst = get_values(df_sum, 'avg_GA_CO')
#         avg_TC6_lst = df_sum['avg_TC6'].values
#         avg_TC7_lst = df_sum['avg_TC7'].values
    avg_TC8_lst = get_values(df_sum, 'avg_TC8')
    avg_TC9_lst = get_values(df_sum, 'avg_TC9')
    avg_TC10_lst = get_values(df_sum, 'avg_TC10')
#         avg_TC11_lst = df_sum['avg_TC11'].values
    avg_EVA_Out_lst = get_values(df_sum, 'avg_EVA_Out')
#         avg_DFM_RichGas_lst = get_values(df_sum, 'avg_DFM_RichGas')
    avg_DFM_RichGas_1min_lst = get_values(df_sum, 'avg_DFM_RichGas_1min')
    avg_DFM_AOG_lst = get_values(df_sum, 'avg_DFM_AOG')
    avg_DFM_AOG_1min_lst = get_values(df_sum, 'avg_DFM_AOG_1min')
    avg_current_lst = get_values(df_sum, 'avg_current')
    con_rate_lst = get_values(df_sum, 'con_rate')
    avg_Scale_lst = get_values(df_sum, 'avg_Scale')
    initial_time_lst = get_values(df_sum, 'Init[s]')
    end_time_lst = get_values(df_sum, 'End[s]')
    avg_Pump_SET_SV_lst = get_values(df_sum, 'avg_Pump_SET_SV')
    avg_Header_EVA_PV_lst = get_values(df_sum, 'avg_Header_EVA_PV')
    avg_Exhaust_gas_lst = get_values(df_sum, 'avg_Exhaust_gas')
    avg_PCB_SET_PV_lst = get_values(df_sum, 'avg_PCB_SET_PV')


def compared_eda(selected_rows=[], selected_columns=[]):
    global State_eda_df_sum
    _df = State_eda_df_sum.loc[selected_rows, selected_columns]
    #print(_df)
    if _df.empty:
        return []
    else:
        compared_fig = px.bar(_df, x=_df.index, y=selected_columns, text='value', barmode='group')
        return dcc.Graph(id='compared_fig', figure=compared_fig) 
    
    
def selected_eda(selected_columns=[]):
    global State_eda_df
    _df = State_eda_df[selected_columns]
    #State_eda_df.loc[:, selected_columns]
    print(_df)
    if _df.empty:
        return []
    else:
        compared_fig = px.line(_df)
        return dcc.Graph(id='compared_fig', figure=compared_fig)
    
    
    