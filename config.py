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

    
class SerEnergy_Set_Point:
    density_H2 = 0.08988 # kg/m3 @ STP
    enthalpy_H2 = 120.21 # MJ/kg-LHV
    enthalpy_MeOH = 20.09 # MJ/kg-LHV
    MeOH_weight = 0.543 # 54.3wt%
    cont_step = 60 #continue for 1 min
    TC_range = 5 #5oC
    Scale_range = 5 #5g/min
    continuity = 10 #10min
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
        
    def eff_calc(self, df: pd.core.frame.DataFrame, TC10: str, TC11: str, EVA_Out: str, Scale: str, DFM_RichGas: str, GA_H2: str):
        if self.ss_time:
            self.ss_TC10 = []
            self.ss_TC11 = []
            self.ss_EVA_Out = []
            self.ss_weight_rate = []
            self.ss_DFM_RichGas = []
            self.ss_GA_H2 = []
            self.heff = []
            for u in self.ss_time:
                #print(u)
                ls = [v for v in range(u[0],u[-1])]
                df_mean = df[df.index.isin(ls)]
                _avg_TC10 = df_mean[TC10].mean()
                _avg_TC11 = df_mean[TC11].mean()
                _avg_EVA_Out = df_mean[EVA_Out].mean()
                _avg_Scale = df_mean[Scale].mean()
                _avg_DFM_RichGas = df_mean[DFM_RichGas].mean()
                _avg_GA_H2 = df_mean[GA_H2].mean()
                self.ss_TC10.append(_ss_dict(span=u, avg_value=_avg_TC10))
                self.ss_TC11.append(_ss_dict(span=u, avg_value=_avg_TC11))
                self.ss_EVA_Out.append(_ss_dict(span=u, avg_value=_avg_EVA_Out))
                self.ss_weight_rate.append(_ss_dict(span=u, avg_value=_avg_Scale))
                self.ss_DFM_RichGas.append(_ss_dict(span=u, avg_value=_avg_DFM_RichGas))
                self.ss_GA_H2.append(_ss_dict(span=u, avg_value=_avg_GA_H2))
                _avg_H2_flow = self.density_H2 * ((_avg_DFM_RichGas * _avg_GA_H2) / 100 - self.dummy) / 1000 # kg/min @ STP
                _heff = ((_avg_H2_flow * self.enthalpy_H2) / (_avg_Scale / 1000 * self.MeOH_weight * self.enthalpy_MeOH)) * 100 # enthalpy eff [%]
                self.heff.append(_ss_dict(span=u, avg_value=_heff))
            self.ss_TC10 = tuple(self.ss_TC10)
            self.ss_TC11 = tuple(self.ss_TC11)
            self.ss_EVA_Out = tuple(self.ss_EVA_Out)
            self.ss_weight_rate = tuple(self.ss_weight_rate)
            self.ss_DFM_RichGas = tuple(self.ss_DFM_RichGas)
            self.ss_GA_H2 = tuple(self.ss_GA_H2)
            self.heff = tuple(self.heff)
            #print(self.name, self.ss_weight_rate, self.ss_DFM_RichGas, self.ss_GA_H2)
            #print(self.name, self.heff)
        else:
            pass
        
    def gen_dataframe(self): # dataframe of summaries
        if self.ss_time:
            _sum_rows = []
            for i in range(len(self.ss_time)):
                _sum_rows.append(pd.DataFrame([[self.name, self.ss_time[i][0], 
                                                self.ss_time[i][-1], 
                                                round(self.ss_TC10[i].avg_value, 2), 
                                                round(self.ss_TC11[i].avg_value, 2), 
                                                round(self.ss_EVA_Out[i].avg_value, 2), 
                                                round(self.ss_weight_rate[i].avg_value, 2), 
                                                round(self.ss_DFM_RichGas[i].avg_value, 2), 
                                                round(self.ss_GA_H2[i].avg_value, 2), 
                                                round(self.heff[i].avg_value, 2)]], 
                                              columns=['Steady State', 
                                                       'Init[s]', 
                                                       'End[s]', 
                                                       'TC10[oC]', 
                                                       'TC11[oC]', 
                                                       'EVA_Out[oC]', 
                                                       'Avg_WeightRate[g/min]', 
                                                       'Avg_RichGas[LPM]', 
                                                       'Avg_H2_Conc[%]', 
                                                       'Enthalpy_Eff[%]']
                                             )
                                )
            self.sum_rows = pd.concat(_sum_rows)
        else:
            pass

        
cur = None
db_name=''
Set_Point_lst = [SerEnergy_Set_Point(name= '18A', temp=300, weight_rate=18.91, dummy=0), 
                 SerEnergy_Set_Point(name= '34A', temp=305, weight_rate=31.85, dummy=0), 
                 SerEnergy_Set_Point(name= '51A', temp=315, weight_rate=49.02, dummy=9.5), 
                 SerEnergy_Set_Point(name= '68A', temp=325, weight_rate=63.1, dummy=0), 
                 SerEnergy_Set_Point(name= '85A', temp=332, weight_rate=81.45, dummy=12.5)]