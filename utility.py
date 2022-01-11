import sys
import re
import mariadb
import pandas as pd
import matplotlib.pyplot as plt
import config

def db_conn(username: str, password: str,):
    try:
        # Connect to MariaDB Platform
        conn = mariadb.connect(
            user=username,
            password=password,
            host="localhost",
            port=3306,
            database=config.db_name,
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
    print(type(config.cur))
    if Calc or Ploting:
        #print(Table_name, Time)
        config.cur.execute(f"SELECT * FROM {Table_name}")
        df = pd.DataFrame(config.cur.fetchall(), columns=[entry[0] for entry in config.cur.description]).set_index('Id')
        _leng = len(df)
            
        _bls=[]
        _heffls = 0
        for i in config.Set_Point_lst:
            i.cond(df, TC='TC10', Scale='Scale')
            i.eff_calc(df, 
                       TC10='TC10', 
                       TC11='TC11', 
                       EVA_Out='EVA_Out', 
                       Scale='Scale', 
                       DFM_RichGas='DFM_RichGas', 
                       GA_H2='GA_H2'
                      )
            if i.ss_time:
                for u in i.ss_time:
                    #print(u)
                    for v in range(u[0], u[-1]):
                        _bls.append(v)
                for q in i.heff:
                    q.gen_series(leng=_leng)
                    #print(q.series.sum())
                    _heffls = _heffls + q.series
        #print(_effls.sum())
        
        df_sum = pd.DataFrame()
        for i in config.Set_Point_lst:
            i.gen_dataframe()
            if i.ss_time:
                #print(i.sum_rows)
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
    
    if Ploting:
        #plt.clf()
        fig, (ax_TC, ax_DFM, ax_GA, ax_heff) = plt.subplots(4, constrained_layout=True, figsize=(10, 10), sharex=False)
        fig.canvas.toolbar_position = 'left'
        
        if config.db_name == 'Reformer_SE':
            df['TC10'].plot(legend=True, ax=ax_TC, kind='area', color='lightblue')
            df['TC6'].plot(legend=True, ax=ax_TC)
            df['TC7'].plot(legend=True, ax=ax_TC)
            df['TC8'].plot(legend=True, ax=ax_TC)
            df['TC9'].plot(legend=True, ax=ax_TC)
            df['TC11'].plot(legend=True, ax=ax_TC)
            df['EVA_Out'].plot(legend=True, ax=ax_TC)
            ylim = (0,600)
            yticks = range(0,600,100)
        elif config.db_name == 'Reformer_BW':
            df['TC7'].plot(legend=True, ax=ax_TC, kind='area', color='lightblue')
            df['TC8'].plot(legend=True, ax=ax_TC)
            df['TC9'].plot(legend=True, ax=ax_TC)
            df['TC10'].plot(legend=True, ax=ax_TC)
            df['EVA_out'].plot(legend=True, ax=ax_TC)
            ylim = (0,1000)
            yticks = range(0,1000,100)
        
        ax_TC.set(title=f'TC_{Table_name}',
                  xlim=Time, 
                  xticks=range(Time[0],Time[1],1200),
                  ylabel='Temp[oC]',
                  xlabel='Time[s]',
                  ylim=ylim, 
                  yticks=yticks,
                 )
        ax_TC_2 = ax_TC.twinx()
        ax_TC_2.set(ylim=ylim, yticks=yticks,)
        
        df_DFM = pd.DataFrame({
            'DFM_AOG':df['DFM_AOG'],
            'DFM_RichGas':df['DFM_RichGas'],
        }, index=df.index)
        
        df_DFM.plot(legend=True, ax=ax_DFM, kind='area', stacked=True, 
                title=f'DFM_{Table_name}',
                ylabel='Gas Production [LPM]',
                grid=True,
                xlim=Time, 
                xticks=range(Time[0],Time[1],1200),
                ylim=(0,150), 
                yticks=range(0,150,10)
               )
        ax_DFM_2 = df['Scale'].plot(legend=True, ax=ax_DFM, secondary_y=True, xlabel='Time[s]',)
        ax_DFM_2.set_ylabel('Scale [g/min]')
        ax_DFM_2.set_ylim(0,100)
        
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
                yticks=range(0,100,10)
               )
        df['CO_line'] = df['GA_CO']
        ax_GA_2 = df['CO_line'].plot(legend=True, ax=ax_GA, secondary_y=True, xlabel='Time[s]',)
        ax_GA_2.set_ylabel('CO [%]')
        ax_GA_2.set_ylim(0,5)
        
        if not df_sum.empty:
            _heffls.plot(legend=False, ax=ax_heff, kind='area', stacked=False, 
                    title=f'heff_{Table_name}', 
                    ylabel='Enthalpy Eff. [%]',
                     xlabel='Time[s]',
                    #grid=True,  
                    xlim=Time, 
                    xticks=range(Time[0],Time[1],1200),
                    ylim=(0,100), 
                    yticks=range(0,100,10)
                   )
        
        plt.show()
    
    else:
        pass