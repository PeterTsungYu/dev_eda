# Heating value version 1.7.3

from chemicals import MW, combustion_stoichiometry, Hfl, Hfg, HHV_stoichiometry, CAS_from_any, LHV_from_HHV, combustion_data
# ------------------------------------------------------------------------------------------------------------------------------------------------------
### H2O L 298 ~ 500 K, Liquid Phase
H2O_L = {
    'A': -203.6060,
    'B': 1523.290,
    'C': -3196.413,
    'D': 2474.455,
    'E': 3.855326,
    'F': -256.5478,
    'G': -488.7163,
    'H': -285.8304
}

### H2O G 500 ~ 1700 K, Gas Phase
H2O_G = {
    'A': 30.09200,
    'B': 6.832514,
    'C': 6.793435,
    'D': -2.534480,
    'E': 0.082139,
    'F': -250.8810,
    'G': 223.3967,
    'H': -241.8264
}
### CO2 298 ~ 1200 K
CO2 = {
    'A': 24.99735,
    'B': 55.18696,
    'C': -33.69137,
    'D': 7.948387,
    'E': -0.136638,
    'F': -403.6075,
    'G': 228.2431,
    'H': -393.5224
}
### CO 298 ~ 1300 K
CO = {
    'A': 6.096130,
    'B': 55.18696,
    'C': 4.054656,
    'D': -2.671301,
    'E': 0.131021,
    'F': -118.0089,
    'G': 227.3665,
    'H': -110.5271
}
### O2 100 ~ 700 K
O2_Lower = {
    'A': 31.32234,
    'B': -20.23531,
    'C': 57.86644,
    'D': -36.50624,
    'E': -0.007374,
    'F': -8.903471,
    'G': 246.7945,
    'H': 0.0
}
### O2 700 ~ 2000 K
O2_Higher = {
    'A': 30.03235,
    'B': 8.772972,
    'C': -3.988133,
    'D': 0.788313,
    'E': -0.741599,
    'F': -11.32468,
    'G': 236.1663,
    'H': 0.0
}
### N2 100 ~ 500 K
N2_Lower = {
    'A': 28.98641,
    'B': 1.853978,
    'C': -9.647459,
    'D': 16.63537,
    'E': 0.000117,
    'F': -8.671914,
    'G': 226.4168,
    'H': 0.0
}
### N2 500 ~ 2000 K
N2_Higher = {
    'A': 19.50583,
    'B': 19.88705,
    'C': -8.598535,
    'D': 1.369784,
    'E': 0.527601,
    'F': -4.935202,
    'G': 212.3900,
    'H': 0.0
}
### H2 298 ~ 1000 K
H2_Lower = {
    'A': 33.066178,
    'B': -11.363417,
    'C': 11.432816,
    'D': -2.772874,
    'E': -0.158558,
    'F': -9.980797,
    'G': 172.707974,
    'H': 0.0
}
### H2 1000 ~ 2500 K
H2_Higher = {
    'A': 18.563083,
    'B': 12.257357,
    'C': -2.859786,
    'D': 0.268238,
    'E': 1.977990,
    'F': -1.147438,
    'G': 156.288133,
    'H': 0.0
}
def ethalpy(t, A, B, C, D, E, F, G, H):
    '''
    The Shomate equation for ethalpy at different temperture compare with the temperture at 298.15 K.
    A to H is coefficients of the equation, data from NIST : https://webbook.nist.gov/chemistry/
    計算不同溫度下焓變的方程式，比較基準為 298.15 K 下的焓值
    '''
    t = (t + 273) / 1000
    dH = A * t + B * t ** 2 / 2 + C * t ** 3 / 3 + D * t ** 4 / 4 - E / t + F - H
    return dH
def deltaH(T):
    '''
    To calculate the delta H of each species.
    計算焓變
    Temperture range:
    H2O_L 298 ~ 500 K, Liquid Phase
    H2O_G 500 ~ 1700 K, Gas Phase
    CO2 298 ~ 1200 K
    CO 298 ~ 1300 K
    O2_Lower 100 ~ 700 K
    O2_Higher 700 ~ 2000 K
    N2_Lower 100 ~ 500 K
    N2_Higher 500 ~ 2000 K
    H2_Lower 298 ~ 1000 K
    H2_Higher 1000 ~ 2500 K
    '''
    # for H2O, N2
    if T <= 500 - 273:
        H_H2O = ethalpy(T,**H2O_L)
        H_N2 = ethalpy(T,**N2_Lower)
    else:
        H_H2O = ethalpy(T,**H2O_G)
        H_N2 = ethalpy(T,**N2_Higher)
    # for of O2
    if T <= 700 - 273:
        H_O2 = ethalpy(T,**O2_Lower)
    else:
        H_O2 = ethalpy(T,**O2_Higher)
    # for of CO2, CO
    H_CO2 = ethalpy(T,**CO2)
    H_CO = ethalpy(T,**CO)
    H_H2 = ethalpy(T,**H2_Lower)

    return H_O2, H_N2, H_CO2, H_H2O, H_CO, H_H2,

# ------------------------------------------------------------------------------------------------------------------------------------------------------
class CombustionCalc:
    '''
    This class is for the calculation of combustion prosses. To use this, you need some parameters:
    計算燃燒過程，以下為需要參數
    1. burner: a dict, including:
    'fuel type': str, 'H2', 'MeOH', or 'AOG'
    'fuel flow': float, [g/min] for 'MeOH', [LPM] for 'H2' & 'AOG'
    'air flow': float, [LPM]
    'air T': float, [oC]
    'burner out T': float, [oC]
    'gas composition': dict, composition of AOG the unit of values use [%]

    2. Idealgasconstant: a dict, including:
    'R': float, the ideal gas constant usually use 0.082
    'T': float, [K]
    'P': float, [atm]
    '''
    def __init__(self, burner, Idealgasconstant):
        self.burner = burner
        self.Idealgasconstant = Idealgasconstant

    # The combustion data of fuel
    def data(self):
        '''
        To calculate the combustion data, will get HHV at [298 K], [1 atm].
        計算常溫常壓下的高熱值
        return EX: CombustionData(stoichiometry={'CO2': 0, 'O2': -0.5, 'H2O': 1.0}, HHV=-285825.0, Hf=0, MW=2.01588)
        '''
        fuel_type = self.burner['fuel type']
        if fuel_type == 'MeOH':
            CS = {'C': 1, 'H': 4, 'O': 1}
            Hf = Hfl(CAS_from_any('methanol'), method = 'WEBBOOK')
        elif fuel_type == 'H2' or 'AOG':
            CS = {'C': 0, 'H': 2, 'O': 0}
            Hf = 0
        else:
            pass
        com_data = combustion_data(CS, Hf = Hf)
        return com_data

    # Calculate unit of all reactants to mole/min
    def fuelunit(self):
        '''
        To turn the unit of air and fuel into [mole/min].
        將空氣及燃料的單位轉換為 莫耳每分鐘
        return EX: (0.687785344944984, 2.58607289699314, 4.817784907513504)
                   (O2_before, N2_before, fuel_before)
        '''
        BR = self.burner
        IGC = self.Idealgasconstant
        O2_before = BR['air flow'] / IGC['R'] / IGC['T'] * IGC['P'] / 4.76
        N2_before = O2_before * 3.76
        if BR['fuel type'] == 'MeOH':
            fuel_before = BR['fuel flow'] / MW('methanol')
        elif BR['fuel type'] == 'H2':
            fuel_before = MW('hydrogen') * BR['fuel flow'] / IGC['R'] / IGC['T'] * IGC['P']
        elif BR['fuel type'] == 'AOG':
            fuel_before = MW('hydrogen') * BR['fuel flow'] * BR['gas composition']['H2'] / 100 / IGC['R'] / IGC['T'] * IGC['P']
        else:
            raise KeyError('Fuel shoud be H2, MeOH, or AOG.')
        return O2_before, N2_before, fuel_before
    
    # Calculate unit of all products to mole/min
    def exhaustgasunit(self):
        '''
        To turn the unit of products after combustion into [mole/min].
        將燃燒後產物的單位轉換為 莫耳每分鐘
        return EX: (-1.721107108811768, 2.58607289699314, 0.06138484203633983, 4.817784907513504)
                   (O2_after, N2_after, CO2_after, H2O_after)
        '''
        BR = self.burner
        IGC = self.Idealgasconstant
        O2_after = self.reactantsunit()[0] - (self.data().stoichiometry['O2'] * (-1)) * self.reactantsunit()[2]
        N2_after = self.reactantsunit()[1]
        CO_after = 0
        H2O_after = self.reactantsunit()[2] * self.data().stoichiometry['H2O']
        if BR['fuel type'] == 'MeOH':
            CO2_after = self.reactantsunit()[2] * self.data().stoichiometry['CO2']
        elif BR['fuel type'] == 'H2' or 'AOG':
            CO2_after = BR['gas composition']['CO2'] / 100 * BR['fuel flow'] / IGC['R'] / IGC['T'] * IGC['P']
        else:
            raise KeyError('Fuel shoud be H2, MeOH, or AOG.')
        
        return O2_after, N2_after, CO2_after, H2O_after
    # Heating value of fuel, and turn into kW
    def heatgive(self):
        '''
        According to the fuel type, calculate the heating value and total heat-gived of combustion.
        根據不同的燃料種類，計算熱值以及燒提供的熱
        return EX: (85.38723604517922, 141786.71349485088, 141786.71349485088)
                   (Give_Heat, HHV_Jg, LHV_Jg)
                   (kJ, J/g, J/g)
        '''
        fuel_type = self.burner['fuel type']
        if fuel_type == 'MeOH':
            CS_fuel = combustion_stoichiometry({'C': 1, 'H': 4, 'O': 1})
            Hf_fuel = Hfl(CAS_from_any('methanol'), method = 'WEBBOOK')
            HHV_Jm = HHV_stoichiometry(CS_fuel, Hf_fuel)
            HHV_Jg = HHV_Jm / MW('methanol') * (-1)
            LHV_Jm = LHV_from_HHV(HHV_Jm, CS_fuel['H2O'])
            LHV_Jg = HHV_Jm / MW('methanol') * (-1)
        elif fuel_type == 'H2' or 'AOG':
            CS_fuel = combustion_stoichiometry({'C': 0, 'H': 2, 'O': 0})
            Hf_fuel = 0
            HHV_Jm = HHV_stoichiometry(CS_fuel, Hf_fuel)
            HHV_Jg = HHV_Jm / MW('hydrogen') * (-1)
            LHV_Jm = LHV_from_HHV(HHV_Jm, CS_fuel['H2O'])
            LHV_Jg = HHV_Jm / MW('hydrogen') * (-1)
        else:
            raise KeyError('Fuel shoud be H2, MeOH, or AOG.')
        Give_Heat = HHV_Jg * self.reactantsunit()[2] / 1000 
        return Give_Heat, HHV_Jg, LHV_Jg
    # wasted heat go into environment
    def wasted(self):
        '''
        To calculate the heat wasted to environment.
        計算排放到環境中的廢熱
        return EX: (29.144561197012237,)
                   (W_total,)
                   (kJ,)
        '''
        products_mole = self.productsunit()
        products_H = deltaH(self.burner['burner out T'])
        # MeOH, Cp regression line, 279 ~ 585 K
        H_MeOH = (0.0808 * (self.burner['burner out T'] - 25) + 19.265) * self.fuelunit()[2] / MW('methanol') * (self.burner['burner out T'] - 25) / 1000
        W_O2 = products_mole[0] * products_H[0]
        W_N2 = products_mole[1] * products_H[1]
        W_CO2 = products_mole[2] * products_H[2]
        W_H2O = products_mole[3] * products_H[3]
        if self.burner['burner out T'] <= 298 - 273:
            W_total = 0
        else:
            W_total = (W_O2 + W_N2 + W_CO2 + W_H2O) 
        return W_total,
    # no function yet
    def _incompletecombustion(self, efficiency = 1):
        burner = self.burner
        return burner, efficiency

class ReformerReactionCalc:
    '''
    This class is for the calculation of reaction prosses. To use this, you need some parameters:
    計算反應過程，以下為需要參數
    1. reaction: a dict, including:
    'reactants T': float, [oC]
    'products T': float, [oC]
    'reactants flow': float, [g/min]
    'products flow': float, [LPM]
    'burner out T': float, [oC]
    'gas composition': dict, composition of AOG the unit of values use [%]
    'convertion': float, [%]
    'pressure': float, [bar]
    'RAD T': float, [oC]

    2. Idealgasconstant: a dict, including:
    'R': float, the ideal gas constant usually use 0.082
    'T': float, [K]
    'P': float, [atm]
    '''
    def __init__(self, reaction, Idealgasconstant):
        self.reaction = reaction
        self.Idealgasconstant = Idealgasconstant
    # Convertion adjustment
    def conver(self):
        '''
        Adjust the convertion, if over 100 % let it no more than one hundred, if no convertion given assume 100 %, 
        if convertion below 0 raise error.
        調整轉化率，轉化率的值應介於 0 ~ 100 之間
        '''
        RC = self.reaction
        if RC.get('convertion') == None:
            conver = 1
#             print('Assume convertion = 100 %')
        elif RC.get('convertion') > 100:
            conver = 1
#             print('Convertion over 100 %, automaticly change to 100 %')
        elif RC.get('convertion') < 0:
            raise ValueError('Convertion can not less than 0')
        else:
            conver = RC.get('convertion') / 100
        return conver
    # According to the convertion, calculate unit of all reactants to mole/min
    def reactantsunit(self):
        '''
        According to the convertion, turn the unit of reactants into [mole/min].
        根據轉化率將甲醇水的單位轉換為 莫耳每分鐘
        return EX: (1.308953974582, 1.308953974582, 1.308953974582, 1.9593744865469753)
                   (MeOH_react, H2O_react, MeOH_before, H2O_before)
        '''
        RC = self.reaction
        weight_percentage = 0.543

        MeOH_before = RC['reactants flow'] / MW('methanol') * weight_percentage
        H2O_before = RC['reactants flow'] / MW('water') * (1 - weight_percentage)
        MeOH_react = H2O_react = MeOH_before * self.conver()
        return MeOH_react, H2O_react, MeOH_before, H2O_before
    # According to the convertion, calculate unit of all products to mole/min
    def productsunit(self):
        '''
        According to the convertion, turn the unit of products into [mole/min].
        根據轉化率將產物的單位轉換為 莫耳每分鐘
        return EX: (0.0, 0.6504205119649753, 1.33695043902439, 0.4774558829268293, 0.009245853658536585)
                   (MeOH_after, H2O_after, H2_after, CO2_after, CO_after)
        '''
        RC = self.reaction
        IGC = self.Idealgasconstant
        MeOH_after = self.reactantsunit()[2] - self.reactantsunit()[0]
        H2O_after = self.reactantsunit()[3] - self.reactantsunit()[1]
        H2_after = RC['products flow'] * RC['gas composition']['H2'] / 100 / IGC['R'] / (RC['RAD T'] + 273) * (RC['pressure'] / 1.01325 + 1)
        CO2_after = RC['products flow'] * RC['gas composition']['CO2'] / 100 / IGC['R'] / (RC['RAD T'] + 273) * (RC['pressure'] / 1.01325 + 1)
        CO_after = RC['products flow'] * RC['gas composition']['CO'] / 100 / IGC['R'] / (RC['RAD T'] + 273) * (RC['pressure'] / 1.01325 + 1)
        return MeOH_after, H2O_after, H2_after, CO2_after, CO_after,
    # Calculate energy of all species, [kJ/min]
    def heatcalculate(self):
        '''
        To calculate the energy of all species, the unit of each is [kJ/min]
        計算產物和反應物的能量，單位為 千焦每分鐘
        return EX: (0.27208653346614053, 0.0, 29.000339425637602, 0.0, 8.848885994891035, 8.848885994891035, 0.02982309933657279)
                   (kJ_b_MeOH, kJ_a_MeOH, kJ_b_H2O, kJ_a_H2O, kJ_H2, kJ_CO2, kJ_CO)
        '''
        RC = self.reaction
        RU = self.reactantsunit()
        PU = self.productsunit()
        dH_b = deltaH(RC['reactants T'])
        dH_a = deltaH(RC['products T'])
        # MeOH, Cp regression line, 279 ~ 585 K 
        H_MeOH = (0.0808 * (RC['reactants T'] - 25) + 19.265) * self.reactantsunit()[2] / MW('methanol') * (RC['reactants T'] - 25) / 1000
        kJ_b_MeOH = H_MeOH
        kJ_a_MeOH = H_MeOH / RU[2] * PU[0]
        kJ_b_H2O = dH_b[3] * RU[3]
        kJ_a_H2O = H_MeOH * PU[1]
        kJ_H2 = dH_a[5] * PU[2]
        kJ_CO2 = dH_a[5] * PU[3]
        kJ_CO = dH_a[4] * PU[4]
        return kJ_b_MeOH, kJ_a_MeOH, kJ_b_H2O, kJ_a_H2O, kJ_H2, kJ_CO2, kJ_CO
    #  Calculate the heat that reaction need
    def need(self):
        '''
        To calculate the energy that reaction need, [kJ/min]
        計算反應所需能量，單位為 千焦每分鐘
        return EX: (29.272425959103742, 17.72759508911864, 52.8557046794493)
                   (kJ_before, kJ_after, need_heat)
        '''
        RU = self.reactantsunit()
        HC = self.heatcalculate()
        kJ_before = HC[0] + HC[2]
        kJ_after = HC[1] + HC[3] + HC[4] + HC[5] + HC[6]
        reaction_H0 = 49.2
        need_heat = kJ_after - kJ_before + 49.2 * RU[0]
        return kJ_before, kJ_after, need_heat
    
    def percentage(self):
        '''
        To calculate the percentage of products.
        計算各產物的占比
        return EX: {'MeOH': 0.0, 'H2O': 11.933828038475774, 'H2': 42.557277505272765, 'CO2': 26.99360568785995, 'CO': 18.51528876839152}
        '''
        products = self.productsunit()
        VolumeP_list = []
        for i in range(0, len(products)):
            VolumeP_list.append(products[i] / sum(products) * 100)
        VolumeP = {
            'MeOH%': round(VolumeP_list[0], 2),
            'H2O%': round(VolumeP_list[1], 2),
            'H2%': round(VolumeP_list[2], 2),
            'CO2%': round(VolumeP_list[3], 2),
            'CO%':round(VolumeP_list[4], 2),
        }
        return VolumeP, VolumeP_list


class ThermodynamicsCalculation(CombustionCalc, ReformerReactionCalc):
    def __init__(self, burner, reaction, Idealgasconstant):
        self.burner = burner
        self.reaction = reaction
        self.Idealgasconstant = Idealgasconstant

    def heff(self):
        ideal_reformer_get = round((self.heatgive()[0] - self.wasted()[0]) / 60, 2)
        combustion_give = round(self.heatgive()[0] / 60, 2)
        conbustion_wasted = round(self.wasted()[0] / 60, 2)
        reaction_need = round(self.need()[2] / 60, 2)
        heat_efficiency = round(self.need()[2] / self.heatgive()[0] * 100, 2)
        return ideal_reformer_get, combustion_give, conbustion_wasted, reaction_need, heat_efficiency

# ----------------------------------------------------------------------- 
if __name__ == '__main__':
    GA = {'H2': 70.55, 'CO2': 24.51, 'CO': 0.76}
    Ideal_gas_constant = {'R': 0.082, 'P': 1, 'T': 298}
    combustion_heat = {
        'fuel type': 'AOG',
        'fuel flow': 17.66,
        'air flow': 130,
        'air T': 25,
        'burner out T': 206.96,
        'gas composition': GA,
    }
    reformer_heat = {
        'reactants T': 174.77,
        'products T': 262.14,
        'reactants flow': 19.87,
        'products flow': 32.8,
        'gas composition': GA,
        'convertion': 96.32,
        'pressure': 0.03,
        'RAD T': 32.11,
    }

    Cb = CombustionCalc(combustion_heat, Ideal_gas_constant)
    Re = ReformerReactionCalc(reformer_heat, Ideal_gas_constant)
    T = ThermodynamicsCalculation(combustion_heat, reformer_heat, Ideal_gas_constant)
    print(T.percentage())
    print(T.productsunit())