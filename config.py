import pandas as pd

class _ss_dict:
    def __init__(self, span: tuple, avg_value: float):
        self.span=span
        self.avg_value=avg_value
    def gen_series(self, leng: int,): # series of avg_value @ certain time span
        _series = pd.Series(0, index=range(leng))
        for i in range(self.span[0], self.span[-1]):
            _series[i] = self.avg_value
        self.series = _series
    def __repr__(self):
        rep = f'Steady State@{self.span}, avg: {self.avg_value}'
        return rep

    
class Set_Point:
    density_H2 = 0.08988 # kg/m3 @ STP
    enthalpy_H2 = 120.21 # MJ/kg-LHV
    enthalpy_MeOH = 20.09 # MJ/kg-LHV
    MeOH_weight = 0.543 # 54.3wt%
    MeOH_mw = 32 # methanol molecular weight
    decomp = 0.99 # Percentage of methanol decomposition
    WGS_conver = 0.97 # WGS convertion
    R = 0.082 # Ideal gas constnat
    pres = 1 # pressure of product(atm)
    cont_step = 60 #continue for 1 min
    TC_range = 5 #5+-oC
    Scale_range = 5 #5+-g/min
    continuity = 5 #5min
    def __init__(self, name: str, temp: float, weight_rate: float, dummy: float):
        self.name = name
        # set points
        self.temp = temp 
        self.weight_rate = weight_rate
        self.dummy = dummy
        
    def cond(self, df: pd.core.frame.DataFrame, TC: str, Scale: str):
        self.ss_time = []
        count_60 = 0 #counter for steady mins
        ss_temp = []
        ss_lst = []
        ss = ((df[TC] >= (self.temp - self.TC_range)) & (df[TC] <= (self.temp + self.TC_range))) \
            & ((df[Scale] >= (self.weight_rate - self.Scale_range)) & (df[Scale] <= (self.weight_rate + self.Scale_range)))
        #print(ss.sum())
        for i in range(0, len(ss), self.cont_step):
            if i + self.cont_step <= len(ss):
                if ss.iloc[i:i + self.cont_step].sum() == 60:
                    count_60 += 1
                    ss_temp.append(i)
                else:
                    count_60 = 0
                    if ss_temp != []:
                        ss_lst.append(ss_temp)
                        ss_temp = []
                    continue
        #print(ss_lst)
        for u in ss_lst:
            if len(u) >= self.continuity:
                self.ss_time.append((u[0], u[-1]))
        self.ss_time = tuple(self.ss_time)
        
    def avg_calc(self, df:pd.core.frame.DataFrame, d:dict):
        _ss_time = self.ss_time
        self.ss_avg = {'avg_H2_flow':[], 'ideal_H2_flow':[], 'con_rate':[], 'heff':[], }
        if _ss_time:
            _df_mean_ls = []
            for u in _ss_time:
                _ls = [v for v in range(u[0],u[-1])]
                _df_mean_ls.append(df[df.index.isin(_ls)])
                
            for k, v in d.items():
                self.ss_avg[k] = []
                for i in range(len(_ss_time)):
                    _avg = _df_mean_ls[i][v].mean()
                    self.ss_avg[k].append(_ss_dict(span=_ss_time[i], avg_value=_avg))
            
            for i in range(len(_ss_time)):
                avg_H2_flow = self.ss_avg.get('avg_DFM_RichGas')[i].avg_value * self.ss_avg.get('avg_GA_H2')[i].avg_value / 100 - self.dummy # LPM
                heff = (avg_H2_flow / 1000 * self.density_H2 * self.enthalpy_H2 / (self.ss_avg.get('avg_Scale')[i].avg_value / 1000 * self.MeOH_weight * self.enthalpy_MeOH)) * 100 # enthalpy eff [%]
                ideal_H2_flow = self.ss_avg.get('avg_Scale')[i].avg_value / self.MeOH_mw * self.MeOH_weight* self.decomp * (2 + self.WGS_conver) * self.R * (self.ss_avg.get('avg_RAD_out')[i].avg_value + 273) / self.pres
                con_rate = avg_H2_flow / ideal_H2_flow * 100 
                self.ss_avg['avg_H2_flow'].append(_ss_dict(span=_ss_time[i], avg_value=avg_H2_flow))
                self.ss_avg['ideal_H2_flow'].append(_ss_dict(span=_ss_time[i], avg_value=ideal_H2_flow))
                self.ss_avg['con_rate'].append(_ss_dict(span=_ss_time[i], avg_value=con_rate))
                self.ss_avg['heff'].append(_ss_dict(span=_ss_time[i], avg_value=heff))
            print(ideal_H2_flow)
            for k in self.ss_avg.keys():
                self.ss_avg[k] = tuple(self.ss_avg[k])
        
        else:
            pass
        
        #print(self.ss_avg)
        #print(self.ss_time)
        
    def gen_dataframe(self): # dataframe of summaries
        if self.ss_time and self.ss_avg:
            _sum_rows = []
            for i in range(len(self.ss_time)):
                _sum_rows.append(pd.DataFrame({**{'Steady State':self.name, 'Init[s]':self.ss_time[i][0], 'End[s]':self.ss_time[i][-1]},\
                                               **{k:round(v[i].avg_value, 2) for k,v in self.ss_avg.items()}},
                                             index=[i])
                                )
            self.sum_rows = pd.concat(_sum_rows)
        else:
            pass

        
cur = None
db_name=''
SE_Set_Point_lst = [Set_Point(name= '18A', temp=300, weight_rate=18.91, dummy=0), 
                 Set_Point(name= '34A', temp=305, weight_rate=31.85, dummy=0), 
                 Set_Point(name= '51A', temp=315, weight_rate=49.02, dummy=9.5), 
                 Set_Point(name= '68A', temp=325, weight_rate=63.1, dummy=0), 
                 Set_Point(name= '85A', temp=332, weight_rate=81.45, dummy=12.5)]

BW_Set_Point_lst = [Set_Point(name= '20%', temp=270, weight_rate=24.08, dummy=0), 
                 Set_Point(name= '40%', temp=280, weight_rate=48.16, dummy=0), 
                 Set_Point(name= '60%', temp=260, weight_rate=72.23, dummy=0), 
                 Set_Point(name= '80%', temp=260, weight_rate=96.31, dummy=0), 
                 Set_Point(name= '100%', temp=260, weight_rate=120.39, dummy=0)]