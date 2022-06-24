import pandas as pd
import thermo_ver_2

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
    Ideal_gas_constant = {'R': 0.082, 'P': 1, 'T': 298}
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
        
    def cond(self, df: pd.core.frame.DataFrame, TC: str, current: str):
        self.ss_time = []
        count_60 = 0 #counter for steady mins
        ss_temp = []
        ss_lst = []
        ss = ((df[TC] >= (self.temp - self.TC_range)) & (df[TC] <= (self.temp + self.TC_range))) \
        & ((df['current'] >= (self.weight_rate - self.Scale_range)) & (df['current'] <= (self.weight_rate + self.Scale_range)))
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
        
    def avg_calc(self, df:pd.core.frame.DataFrame, d:dict, db_name: str):
        _ss_time = self.ss_time
        self.ss_avg = {'avg_H2_flow':[], 'ideal_H2_flow':[], 'AOG/Rich':[], 'H2/MeOHWater_L/g':[], 'con_rate':[], 'heff':[], 'get':[], 'wasted':[], 'H2%':[], 'CO2%':[], 'CO%':[], 'H2O%':[], 'MeOH%':[], 'Products mole':[],}
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
                A = self.ss_avg.get('avg_DFM_RichGas_1min')[i].avg_value * self.ss_avg.get('avg_GA_H2')[i].avg_value / 100 * 1000 / (6.959 / 22.386 * 24.47) / 120
                if db_name == 'Reformer_BW':
                    BR_get_heat = thermo.combustion('MeOH', self.ss_avg.get('avg_Pump_SET_SV')[i].avg_value, self.ss_avg.get('avg_Air_MFC_SET_SV')[i].avg_value, self.ss_avg.get('avg_Header_BR_PV')[i].avg_value)
                    gas_comp = {
                        'H2': self.ss_avg.get('avg_GA_H2')[i].avg_value,
                        'CO2': self.ss_avg.get('avg_GA_CO2')[i].avg_value,
                        'CO': self.ss_avg.get('avg_GA_CO')[i].avg_value
                    }
                    Reaction_need_heat = thermo.reformer_heat(self.ss_avg.get('avg_Steam_Out')[i].avg_value, self.ss_avg.get('avg_TC10')[i].avg_value, self.ss_avg.get('avg_Scale')[i].avg_value, self.ss_avg.get('avg_DFM_RichGas_1min')[i].avg_value, gas_comp)
                   
                elif db_name == 'Reformer_SE':
                    DFM_total = self.ss_avg.get('avg_DFM_RichGas_1min')[i].avg_value + self.ss_avg.get('avg_DFM_AOG_1min')[i].avg_value
                    flow_ratio = self.ss_avg.get('avg_DFM_AOG_1min')[i].avg_value / self.ss_avg.get('avg_DFM_RichGas_1min')[i].avg_value
                    flow_ratio2 = DFM_total / self.ss_avg.get('avg_Scale')[i].avg_value
                    avg_H2_flow = DFM_total * self.ss_avg.get('avg_GA_H2')[i].avg_value / 100 - self.dummy # LPM
                    ideal_H2_flow = self.ss_avg.get('avg_Scale')[i].avg_value / self.MeOH_mw * self.MeOH_weight* self.decomp * (2 + self.WGS_conver) * self.Ideal_gas_constant['R'] * (self.ss_avg.get('avg_RAD_Out')[i].avg_value + 273) / (self.ss_avg.get('avg_ADAM_P_Out')[i].avg_value / 1.01325 + 1)
                    con_rate = avg_H2_flow / ideal_H2_flow * 100
                    gas_comp = {
                            'H2': self.ss_avg.get('avg_GA_H2')[i].avg_value,
                            'CO2': self.ss_avg.get('avg_GA_CO2')[i].avg_value,
                            'CO': self.ss_avg.get('avg_GA_CO')[i].avg_value
                        }
                    combustion_heat = {
                        'fuel type': 'AOG',
                        'fuel flow': self.ss_avg.get('avg_DFM_AOG_1min')[i].avg_value,
                        'air flow': self.ss_avg.get('avg_Air_MFC_SET_SV')[i].avg_value,
                        'air T': 25,
                        'burner out T': self.ss_avg.get('avg_Exhaust_gas')[i].avg_value,
                        'gas composition': gas_comp,
                    }
                    reformer_heat = {
                        'reactants T': self.ss_avg.get('avg_EVA_Out')[i].avg_value,
                        'products T': self.ss_avg.get('avg_TC12')[i].avg_value,
                        'reactants flow': self.ss_avg.get('avg_Scale')[i].avg_value,
                        'products flow': DFM_total,
                        'gas composition': gas_comp,
                        'convertion': con_rate,
                        'pressure': self.ss_avg.get('avg_ADAM_P_Out')[i].avg_value,
                        'RAD T': self.ss_avg.get('avg_RAD_Out')[i].avg_value,
                    }
                    Cb = thermo_ver_2.CombustionCalc(combustion_heat, self.Ideal_gas_constant)
                    Re = thermo_ver_2.ReformerReactionCalc(reformer_heat, self.Ideal_gas_constant)
                    Thermo = thermo_ver_2.ThermodynamicsCalculation(combustion_heat, reformer_heat, self.Ideal_gas_constant).heff
                    Volume_P = thermo_ver_2.ThermodynamicsCalculation(combustion_heat, reformer_heat, self.Ideal_gas_constant).percentage()[0]
                    Total = sum(thermo_ver_2.ThermodynamicsCalculation(combustion_heat, reformer_heat, self.Ideal_gas_constant).productsunit())
                heff = Thermo()[4]
                get = Thermo()[0] / Thermo()[1] * 100
                wasted = Thermo()[2] / Thermo()[1] * 100
                
                self.ss_avg['avg_H2_flow'].append(_ss_dict(span=_ss_time[i], avg_value=avg_H2_flow))
                self.ss_avg['ideal_H2_flow'].append(_ss_dict(span=_ss_time[i], avg_value=ideal_H2_flow))
                self.ss_avg['AOG/Rich'].append(_ss_dict(span=_ss_time[i], avg_value=flow_ratio))
                self.ss_avg['H2/MeOHWater_L/g'].append(_ss_dict(span=_ss_time[i], avg_value=flow_ratio2))
                self.ss_avg['con_rate'].append(_ss_dict(span=_ss_time[i], avg_value=con_rate))
                self.ss_avg['heff'].append(_ss_dict(span=_ss_time[i], avg_value=heff))
                self.ss_avg['get'].append(_ss_dict(span=_ss_time[i], avg_value=get))
                self.ss_avg['wasted'].append(_ss_dict(span=_ss_time[i], avg_value=wasted))
                self.ss_avg['H2%'].append(_ss_dict(span=_ss_time[i], avg_value=Volume_P['H2%']))
                self.ss_avg['CO2%'].append(_ss_dict(span=_ss_time[i], avg_value=Volume_P['CO2%']))
                self.ss_avg['CO%'].append(_ss_dict(span=_ss_time[i], avg_value=Volume_P['CO%']))
                self.ss_avg['H2O%'].append(_ss_dict(span=_ss_time[i], avg_value=Volume_P['H2O%']))
                self.ss_avg['MeOH%'].append(_ss_dict(span=_ss_time[i], avg_value=Volume_P['MeOH%']))
                self.ss_avg['Products mole'].append(_ss_dict(span=_ss_time[i], avg_value=Total))
                
            for k in self.ss_avg.keys():
                self.ss_avg[k] = tuple(self.ss_avg[k])
        
        else:
            pass
        

#         print(self.ss_avg)
#         print(self.ss_time)

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


SE_Set_Point_lst = [Set_Point(name= '18A', temp=300,weight_rate=18, dummy=0), 
                 Set_Point(name= '34A', temp=305, weight_rate=34, dummy=0), 
                 Set_Point(name= '51A', temp=315, weight_rate=51, dummy=0), 
                 Set_Point(name= '68A', temp=325, weight_rate=68, dummy=0), 
                 Set_Point(name= '85A', temp=332, weight_rate=85, dummy=0)]

BW_Set_Point_lst = [Set_Point(name= '20%', temp=270, weight_rate=24.08, dummy=0), 
                 Set_Point(name= '40%', temp=280, weight_rate=48.16, dummy=0), 
                 Set_Point(name= '60%', temp=260, weight_rate=72.23, dummy=0), 
                 Set_Point(name= '80%', temp=260, weight_rate=96.31, dummy=0), 
                 Set_Point(name= '100%', temp=260, weight_rate=120.39, dummy=0)]