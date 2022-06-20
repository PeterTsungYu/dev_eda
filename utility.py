import sys
import re
import mariadb
import pandas as pd
import matplotlib.pyplot as plt
import config

def db_conn(username: str, password: str, db_name:str):
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
        #display(f"Connected to {config.db_name}@localhost ")
        return cur
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
        
def plot(Table_name: str, Time: tuple, SS: bool, Calc: bool, Ploting: bool):
    if Calc or Ploting:
        #print(Table_name, Time)
        config.cur.execute(f"SELECT * FROM {Table_name}")
        df = pd.DataFrame(config.cur.fetchall(), columns=[entry[0] for entry in config.cur.description]).set_index('Id')
#         pd.set_option('display.max_columns', df.shape[0]+1)
#         pd.set_option('display.max_rows', df.shape[0]+1)

        pd.set_option('display.max_columns',None)
        pd.set_option('display.expand_frame_repr', False)
        pd.set_option('display.html.border',1)
#         pd.set_option('display.large_repr', 'truncate')
#         pd.set_option('display.large_repr', 'info')

        
        _leng = len(df)
        #plt.figure('123') 
        #ax = plt.axes(frame_on=False)# 不要額外框線
        #ax.xaxis.set_visible(False)  # 隱藏X軸刻度線
        #ax.yaxis.set_visible(False)  # 隱藏Y軸刻度線
        #pd.plotting.table(ax, df, loc='center') #將mytable投射到ax上，且放置於ax的中間
        #plt.savefig('table.png')     # 存檔     
        _bls=[]
        _effls = 0
        _heff = 0
        _get = 0
        _wasted = 0
        
        if config.db_name == 'Reformer_SE':
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
        elif config.db_name == 'Reformer_BW':
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
            i.avg_calc(df=df, d=avg)
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
        for i in Set_Point_lst:
            i.gen_dataframe()
            if i.ss_time:
#                 print(i.sum_rows)
                df_sum = pd.concat([df_sum, i.sum_rows])
        if not df_sum.empty:
            df_sum = df_sum.sort_values(by=['Init[s]']).reset_index(drop=True)
            display(df_sum)
        else:
            print('No Steady-State is found!')
        
        if SS:        
            _bmask = pd.Series([True if i in _bls else False for i in range(0, _leng)])
            df = df.where(_bmask, 0)
        else:
            pass
        
        # set to global var
        get_values = lambda df, col : df.get(col) if not df_sum.empty else None
        config.Steady_State_lst = get_values(df_sum, 'Steady State')
        config.avg_H2_flow_lst = get_values(df_sum, 'avg_H2_flow')
        config.ideal_H2_flow_lst = get_values(df_sum, 'ideal_H2_flow')
        config.avg_Air_MFC_SET_SV_lst = get_values(df_sum, 'avg_Air_MFC_SET_SV')
        config.avg_H2_MFC_SET_SV_lst = get_values(df_sum, 'avg_H2_MFC_SET_SV')
        config.avg_GA_H2_lst = get_values(df_sum, 'avg_GA_H2')
        config.avg_GA_CO2_lst = get_values(df_sum, 'avg_GA_CO2')
        config.avg_GA_CO_lst = get_values(df_sum, 'avg_GA_CO')
#         config.avg_TC6_lst = df_sum['avg_TC6'].values
#         config.avg_TC7_lst = df_sum['avg_TC7'].values
        config.avg_TC8_lst = get_values(df_sum, 'avg_TC8')
        config.avg_TC9_lst = get_values(df_sum, 'avg_TC9')
        config.avg_TC10_lst = get_values(df_sum, 'avg_TC10')
#         config.avg_TC11_lst = df_sum['avg_TC11'].values
        config.avg_EVA_Out_lst = get_values(df_sum, 'avg_EVA_Out')
#         config.avg_DFM_RichGas_lst = get_values(df_sum, 'avg_DFM_RichGas')
        config.avg_DFM_RichGas_1min_lst = get_values(df_sum, 'avg_DFM_RichGas_1min')
        config.avg_DFM_AOG_lst = get_values(df_sum, 'avg_DFM_AOG')
        config.avg_DFM_AOG_1min_lst = get_values(df_sum, 'avg_DFM_AOG_1min')
        config.avg_current_lst = get_values(df_sum, 'avg_current')
        config.con_rate_lst = get_values(df_sum, 'con_rate')
        config.avg_Scale_lst = get_values(df_sum, 'avg_Scale')
        config.initial_time_lst = get_values(df_sum, 'Init[s]')
        config.end_time_lst = get_values(df_sum, 'End[s]')
        config.avg_Pump_SET_SV_lst = get_values(df_sum, 'avg_Pump_SET_SV')
        config.avg_Header_EVA_PV_lst = get_values(df_sum, 'avg_Header_EVA_PV')
        config.avg_Exhaust_gas_lst = get_values(df_sum, 'avg_Exhaust_gas')
        config.avg_PCB_SET_PV_lst = get_values(df_sum, 'avg_PCB_SET_PV')
    if Ploting:
        #plt.clf()
        fig, (ax_TC, ax_DFM, ax_GA, ax_con, ax_heff) = plt.subplots(5, constrained_layout=True, figsize=(10, 10), sharex=False)
        fig.canvas.toolbar_position = 'left'
        
        #ax_TC_2 = ax_TC.twinx()
        if config.db_name == 'Reformer_SE':
            pd.DataFrame({'BR':df['TC10']}, index=df.index).plot(legend=True, ax=ax_TC, kind='area', color='lightblue',
                                                                ylim=(0,400), yticks=range(0,400,50), ylabel='Temp[oC]',
                                                                title=f'TC_{Table_name}', xlim=Time, xticks=range(Time[0],Time[1],1200)
                                                               )
            df_TC_2 = pd.DataFrame({
                'TC6':df['TC6'],
                'TC12':df['TC12'],
                'Exhaust_gas':df['Exhaust_gas'],
                'TC9':df['TC9'],
                'TC11':df['TC11'],
                'EVA_out':df['EVA_Out'],
            }, index=df.index).plot(legend=True, ax=ax_TC, secondary_y=True, xlabel='Time[s]')
            df_TC_2.set(ylabel='Temp [oC]', ylim=(0,800), yticks=range(0,800,100))

        elif config.db_name == 'Reformer_BW':
            pd.DataFrame({'BR':df['TC7']}, index=df.index).plot(legend=True, ax=ax_TC, kind='area', color='lightblue',
                                                                ylim=(0,1000), yticks=range(0,1000,100), ylabel='Temp[oC]',
                                                                title=f'TC_{Table_name}', xlim=Time, xticks=range(Time[0],Time[1],1200)
                                                               )
            df_TC_2 = pd.DataFrame({
                'Steam_Out':df['TC11'],
                'SR_Front':df['TC8'],
                'SR_Mid':df['TC9'],
                'SR_End':df['TC10'],
                'BR_outlet':df['Header_BR_PV'],
            }, index=df.index).plot(legend=True, ax=ax_TC, secondary_y=True, xlabel='Time[s]')
            #df_TC_2.set(ylabel='Temp [oC]', ylim=(0,400), yticks=range(0,50,400))
        
        df_DFM = pd.DataFrame({
            'DFM_AOG_1min':df['DFM_AOG_1min'],
            'DFM_RichGas_1min':df['DFM_RichGas_1min'],
        }, index=df.index)
        
        df_DFM.plot(legend=True, ax=ax_DFM, kind='area', stacked=True, 
                title=f'DFM_{Table_name}',
                ylabel='Gas Production [LPM] & Current [A]',
                grid=True,
                xlim=Time, 
                xticks=range(Time[0],Time[1],1200),
                ylim=(0,160), 
                yticks=range(0,160,20)
               )
#         ax_DFM_2 = df['Scale'].plot(legend=True, ax=ax_DFM, secondary_y=True, xlabel='Time[s]',)
        ax_DFM_3 = df['current'].plot(legend=True, ax=ax_DFM, xlabel='Time[s]',)
#         ax_DFM_2.set(ylabel='Scale [g/min]', ylim=(0,150), yticks=range(0,150,10))
#         ax_DFM_3.set(ylabel='current [A]', ylim=(0,100), yticks=range(0,100,10))
        
        df_GA = pd.DataFrame({
            'GA_H2':df['GA_H2'],
            'GA_CO':df['GA_CO'],
            'GA_CO2':df['GA_CO2'],
            'GA_CH4':df['GA_CH4'],
            'GA_N2':df['GA_N2'],
        }, index=df.index)
        
        df_GA.plot(legend=True, ax=ax_GA, kind='area', stacked=True, 
                title=f'GA_{Table_name}', 
                ylabel='Gas Composition [%]', 
                #grid=True,  
                xlim=Time, 
                xticks=range(Time[0],Time[1],1200),
                ylim=(0,100), 
                yticks=range(0,105,10)
               )
        df['CO_line'] = df['GA_CO']
        ax_GA_2 = df['CO_line'].plot(legend=True, ax=ax_GA, secondary_y=True, xlabel='Time[s]',)
        ax_GA_2.set_ylabel('CO [%]')
        ax_GA_2.set_ylim(0,5)
        
        if not df_sum.empty:
            _effls.plot(legend=False, ax=ax_con, kind='area', stacked=True, 
                    title=f'con_{Table_name}', 
                    ylabel='con_rate [%]',
                    xlabel='Time[s]',
                    #grid=True,  
                    xlim=Time, 
                    xticks=range(Time[0],Time[1],1200),
                    ylim=(0,105), 
                    yticks=range(0,105,10)
                   )
            
            df_heat = pd.DataFrame({
            'heat get':_get,
            'heff':_heff,
            'heat wasted':_wasted,
            }, index=df.index)

            df_heat.plot(legend=True, ax=ax_heff, stacked=False, 
                    title=f'heff_{Table_name}', 
                    ylabel='[%]',
                    xlabel='Time[s]',
                    #grid=True,  
                    xlim=Time, 
                    xticks=range(Time[0],Time[1],1200),
                    ylim=(0,105), 
                    yticks=range(0,105,10)
                   )
        plt.show()
    
    else:
        pass

def plot_cols(col_string:str, table_name:str, ax):
    config.cur.execute(f"SELECT {col_string} FROM {table_name}")
    df = pd.DataFrame(config.cur.fetchall(), columns=[entry[0] for entry in config.cur.description])
    df.plot(ax=ax)
    