# Heating value version 1.5.0

from chemicals import MW, combustion_stoichiometry, Hfl, Hfg, HHV_stoichiometry, CAS_from_any, LHV_from_HHV, combustion_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Molecular weight
MW_H2O  = MW('water')
MW_CO2  = MW('carbon dioxide')
MW_CO   = MW('carbon monoxide')
MW_MeOH = MW('methanol')
MW_H2   = MW('hydrogen')
MW_O2   = MW('oxygen')
MW_N2   = MW('nitrogen')

# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Heating value of MeOH
CS_MeOH = combustion_stoichiometry({'C': 1, 'H': 4, 'O': 1}) # Elements number of MeOH in the combustion
Hf_MeOH = Hfl(CAS_from_any('methanol'), method = 'WEBBOOK')  # Formation ethalpy of MeOH, 298K, 1atm
HHV_Jm_MeOH = HHV_stoichiometry(CS_MeOH, Hf_MeOH)            # Higher heating value of MeOH J/mole, 298K, 1atm
HHV_Jg_MeOH = round(HHV_Jm_MeOH / MW_MeOH * (-1), 4)         # Higher heating value of MeOH J/g, 298K, 1atm
LHV_Jm_MeOH = LHV_from_HHV(HHV_Jm_MeOH, CS_MeOH['H2O'])      # Lower heating value of MeOH J/mole, 298K, 1atm
LHV_Jg_MeOH = round(LHV_Jm_MeOH / MW_MeOH * (-1), 4)         # Lower heating value of MeOH J/g, 298K, 1atm

# Heating value of H2
CS_H2 = combustion_stoichiometry({'C': 0, 'H': 2, 'O': 0})   # Elements number of H2 in the combustion
Hf_H2 = 0                                                    # Formation ethalpy of H2, 298K, 1atm
HHV_Jm_H2 = HHV_stoichiometry(CS_H2, Hf_H2)                  # Higher heating value of H2 J/mole, 298K, 1atm
HHV_Jg_H2 = round(HHV_Jm_H2 / MW_H2 * (-1), 4)               # Higher heating value of H2 J/g, 298K, 1atm
LHV_Jm_H2 = LHV_from_HHV(HHV_Jm_H2, CS_H2['H2O'])            # Lower heating value of H2 J/mole, 298K, 1atm
LHV_Jg_H2 = round(LHV_Jm_H2 / MW_H2 * (-1), 4)               # Lower heating value of H2 J/g, 298K, 1atm

# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Ideal Gas Constant
R = 0.082            # L*atm/K/mol
T = 298              # k
P = 1                # atm

# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Delta H calculation
## Shomate equation for ethalpy at different temperture
## H - H298.15 = A * t + B * t ** 2 / 2 + C * t ** 3 / 3 + D * t ** 4 / 4 - E / t + F - H
## t = temperture(K) / 1000
## A to H is coefficients data from NIST : https://webbook.nist.gov/chemistry/ 

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
def deltaH(t: float, A, B, C, D, E, F, G, H):
    t = (t + 273) / 1000
    dH = A * t + B * t ** 2 / 2 + C * t ** 3 / 3 + D * t ** 4 / 4 - E / t + F - H
    return dH
# ------------------------------------------------------------------------------------------------------------------------------------------------------

# Calculate delta H of the product after combustion (the exhaust)

def combustion(fuel: str, f_amount: float, air_amount: float, outlet_T: float, com_eff = 1): # exhaust product: H20, CO2, O2, N2, CO
    '''
    air_amount: float [LPM]
    fuel: str, fuel type [MeOH, H2]
    f_amount: float. MeOH [g/min], H2 [LPM]
    H2O -> liq, use HHV to calc
    H2O -> vapor, use LHV to calc
    return a delta_enthalpy of exhaust at certain outlet_T, Ideal_Reformer_Get_Heat [kW], and waste heat ratio
    '''
    # reactant
    RR_O2    = air_amount / R / T * P / 4.76 #[mole/min]
    RR_N2    = RR_O2 * 3.76                  #[mole/min]
    
    # To calculate parameters of incomplete combustion
    if com_eff == 1: # complete
        if fuel == 'MeOH':
            CS = {'C': 1, 'H': 4, 'O': 1}
            Hf = Hfl(CAS_from_any('methanol'), method = 'WEBBOOK')
        elif fuel == 'H2':
            CS = {'C': 0, 'H': 2, 'O': 0}
            Hf = 0
        else:
            pass
        com_data = combustion_data(CS, Hf = Hf)
    elif com_eff > 1 or com_eff < 0 :
        return ValueError('"com_eff" must between 0 ~ 1!')
    else: # incmoplete
        if fuel == 'MeOH':
            class InComData(object):
                def __init__(self, stoichiometry, HHV, Hf):
                    self.stoichiometry = stoichiometry
                    self.HHV = HHV
                    self.Hf = Hf
                @property
                def LHV(self):
                    """Lower heating value [LHV; in J/mol]"""
                    return LHV_from_HHV(self.HHV, self.stoichiometry.get('H2O'))
                def __repr__(self):
                    return 'IncompleteCombustionData(stoichiometry=%s, HHV=%s, Hf=%s)' % (
                    self.stoichiometry, self.HHV, self.Hf)
            CS = {'C': 1, 'H': 4, 'O': 1}
            Hf = Hfl(CAS_from_any('methanol'), method = 'WEBBOOK')
            stoichiometry = {
            'CO2': com_eff,
            'CO': round(1 - com_eff, 2),
            'H2O': 2.0,
            }
            stoichiometry['O2'] = round((stoichiometry['CO2'] * 2 + stoichiometry['H2O'] + stoichiometry['CO'] - 1) / 2 * (-1), 2)
            HHV = round(Hfg(CAS_from_any('CO2'), method = 'WEBBOOK') * com_eff + Hfg(CAS_from_any('CO'), method = 'WEBBOOK') * (1 - com_eff) + Hfl(CAS_from_any('H2O'), method = 'WEBBOOK') * stoichiometry['H2O'] - Hf, 2)
            com_data = InComData(stoichiometry, HHV, Hf)
        elif fuel == 'H2':
            CS = {'C': 0, 'H': 2, 'O': 0}
            Hf = 0
            com_data = combustion_data(CS, Hf = Hf)
            print('Assume the combustion is completely for H2 always.')
        else:
            pass

    # Heating value of fuel 
    # Using MeOH or H2 to be fuel, complete combustion
    if fuel == 'MeOH':
        PR_CO2   = f_amount / MW_MeOH * com_data.stoichiometry['CO2']
        PR_H2O   = f_amount / MW_MeOH * com_data.stoichiometry['H2O']
        if com_eff != 1:
            PR_CO = f_amount / MW_MeOH * com_data.stoichiometry['CO']
        else:
            PR_CO = 0
        MeOH_out = f_amount / MW_MeOH * (1 - com_data.stoichiometry['CO2'])
        PR_O2    = RR_O2 - (com_data.stoichiometry['O2'] * (-1)) * (f_amount / MW_MeOH) #[mole/min]
        AFR = ((com_data.stoichiometry['O2'] * MW_O2 * (-1)) * (f_amount / MW_MeOH)) / f_amount # Air-fuel ratio
        AFR_Real = round((RR_O2 * MW_O2) / f_amount, 4)
        Lambda   = round(AFR_Real / AFR, 4)
        Give_Heat = (com_data.HHV * (-1) / MW_MeOH) * f_amount / 1000 / 60 # kW
    elif fuel == 'H2':
        H2_gpm   = MW_H2 * f_amount / R / T * P #[g/min]
        PR_CO2   = 0
        PR_CO    = 0
        PR_H2O   = H2_gpm / MW_H2 * com_data.stoichiometry['H2O']
        H2_out   = H2_gpm / MW_H2 * (1 - com_data.stoichiometry['CO2'])
        PR_O2    = RR_O2 - (com_data.stoichiometry['O2'] * (-1)) * (H2_gpm / MW_H2) #[mole/min]
        AFR = ((com_data.stoichiometry['O2'] * MW_O2 * (-1)) * (H2_gpm / MW_H2)) / H2_gpm # Air-fuel ratio
        AFR_Real = round((RR_O2 * MW_O2) / H2_gpm, 4)
        Lambda   = round(AFR_Real / AFR, 4)
        Give_Heat = HHV_Jg_H2 * H2_gpm / 1000 / 60 # kW
    else:
        pass

    # product
    PR_N2    = RR_N2 #[mole/min]

    outlet_T = outlet_T + 273
    t = outlet_T / 1000
    # delta_H of H2O, N2 
    if outlet_T <= 500:
        delta_H_H2O = deltaH(outlet_T,**H2O_L)
        delta_H_N2 = deltaH(outlet_T,**N2_Lower)
    else:
        delta_H_H2O = deltaH(outlet_T,**H2O_G)
        delta_H_N2 = deltaH(outlet_T,**N2_Higher)
    
    # delta_H of O2
    if outlet_T <= 700:
        delta_H_O2 = delta_H_N2 = deltaH(outlet_T,**O2_Lower)
    else:
        delta_H_O2 = deltaH(outlet_T,**O2_Higher)

    # delta_H of CO2, CO
    delta_H_CO2 = deltaH(outlet_T,**CO2)
    delta_H_CO = deltaH(outlet_T,**CO)
    delta_H_H2 = deltaH(outlet_T,**H2_Lower)

    # MeOH, Cp regression line, 279 ~ 585 K
    delta_H_MeOH = (0.0808 * outlet_T + 19.265) * f_amount / MW_MeOH * outlet_T / 1000 # [kJ/min]

    # Waste heat
    # Out tempertuer can not equal or lower than 298 K
    W_H2O = delta_H_H2O * PR_H2O
    W_N2 = delta_H_N2 * PR_N2
    W_O2 = delta_H_O2 * PR_O2
    W_CO2 = delta_H_CO2 * PR_CO2
    W_CO = delta_H_CO * PR_CO

    if outlet_T <= 298:
        Waset_Heat,WP_H2O,WP_CO2,WP_O2,WP_N2,WP_CO = (0,0,0,0,0,0)
    else:
        Waset_Heat = (W_H2O + W_CO2 + W_O2 + W_N2 + W_CO) / 60 # kW
        WP_H2O = round(W_H2O / 60 / Waset_Heat * 100, 4) # %
        WP_CO2 = round(W_CO2 / 60 / Waset_Heat * 100, 4)
        WP_O2 = round(W_O2 / 60 / Waset_Heat * 100, 4)
        WP_N2 = round(W_N2 / 60 / Waset_Heat * 100, 4)
        WP_CO = round(W_CO / 60 / Waset_Heat * 100, 4)
    Waset_Heat = round(Waset_Heat, 4)
    Ideal_Reformer_Get_Heat = round((Give_Heat - Waset_Heat), 4) # kW

    return Ideal_Reformer_Get_Heat, Waset_Heat, Give_Heat, WP_H2O, WP_CO2, WP_O2, WP_N2, WP_CO


def reformer_heat(inlet_T: float, outlet_T: float, f_amount: float, p_amount: float, gas_comp: dict, residual_MeOH = 0.0):
    '''
    inlet_T: float, reformer inlet T [oC]
    outlet_T: float, reformer outlet T [oC]
    f_amount: float, fuel(MeOH + Water) input [g/min]
    p_amount: reformate [LPM]
    gas_comp: composition dict {'H2': float, 'CO': float, 'CO2': float} [%]
    residual_MeOH: float [g/min]

    '''
    outlet_T = outlet_T + 273 #[K]
    inlet_T = inlet_T + 273 # [K]
    mole_MeOH = f_amount / MW_MeOH * 0.543
    mole_H2O = f_amount / MW_H2O * (1 - 0.543)
    mole_residual_MeOH = residual_MeOH / MW_MeOH
    mole_residual_H2O = mole_H2O - (mole_MeOH - mole_residual_MeOH)

    # inlet
    t = inlet_T / 1000 # The temperture of MeOH/H2O before reaction 
    if inlet_T <= 500:
        delta_H_H2O = deltaH(inlet_T,**H2O_L)
    else:
        delta_H_H2O = deltaH(inlet_T,**H2O_G)
    
    # MeOH, Cp regression line, 279 ~ 585 K
    delta_H_MeOH = (0.0808 * inlet_T + 19.265) * mole_MeOH * inlet_T / 1000 # [kJ/min]

    # outlet
    t = outlet_T / 1000 # The end of temperture of reformate after reaction
    delta_H_CO2 = deltaH(outlet_T,**CO2)
    delta_H_CO = deltaH(outlet_T,**CO)
    delta_H_H2 = deltaH(outlet_T,**H2_Lower)
    delta_H_residual_MeOH = (0.0808 * outlet_T + 19.265) * (residual_MeOH / MW_MeOH) * outlet_T / 1000 - ((0.0808 * inlet_T + 19.265) * (residual_MeOH / MW_MeOH) * inlet_T / 1000) # [kJ/min]
    if outlet_T <= 500:
        delta_H_residual_H2O = deltaH(outlet_T,**H2O_L) - delta_H_H2O       # kJ/mole
    else:
        delta_H_residual_H2O = deltaH(outlet_T,**H2O_G) - delta_H_H2O       # kJ/mole

    # gas comp
    H2_p_amount = p_amount * gas_comp['H2'] / 100 / R / T * P   # [mole/min]
    CO2_p_amount = p_amount * gas_comp['CO2'] / 100 / R / T * P # [mole/min]
    CO_p_amount = p_amount * gas_comp['CO'] / 100 / R / T * P   # [mole/min]
    reaction_H = 49.2                                           # [kJ/mole]

    Reaction_Heat_Need = round(((delta_H_CO2 * CO2_p_amount + delta_H_H2 * H2_p_amount + delta_H_CO * CO_p_amount + mole_residual_MeOH * delta_H_residual_MeOH + mole_residual_H2O * delta_H_residual_H2O) - (delta_H_MeOH + delta_H_H2O * mole_H2O) + reaction_H * (mole_MeOH - mole_residual_MeOH)) / 60, 4)
    Reaction_H0 = round(reaction_H * (mole_MeOH - mole_residual_MeOH) / 60, 4)
    H_ratio = round(Reaction_H0 / Reaction_Heat_Need * 100, 4) # %
    return Reaction_Heat_Need, Reaction_H0, H_ratio

# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

# To calculate volume percentage of all products and unreacted species

def VolumePercentage(f_amount: float, DFM_total: float, convertion: float, P: float, RAD_Out: float, gas_comp: dict):
    '''
    f_amount: float, scale in [g/min]
    DFM_total: float, DFM_RichGas + DFM_AOG [LPM]
    convertion: float, convertion rate [%]
    P: float, pressure of gas products [bar]
    RAD_Out: float, temperture of gas products after cooling [oC]
    gas_comp: dict, gas composition [%]
    return:
    1. Precentage of products inculding H2, CO2, CO, MeOH, H2O
    2. Total volume [LPM]
    all units will turn into mole to calculate the ratio of volume
    '''
    P = P / 1.01325 + 1 # bar to atm
    R = 0.082 # ideal gas constant
    T = RAD_Out + 273 # oC to K
    convertion = convertion / 100
    # gas porducts mole
    H2_flow = gas_comp['H2'] / 100 * DFM_total * P / R / T
    CO2_flow = gas_comp['CO2'] / 100 * DFM_total * P / R / T
    CO_flow = gas_comp['CO'] / 100 * DFM_total * P / R / T
    
    # remaining MeOH & H2O mole
    MeOH_after = f_amount * 0.543 / MW('methanol') * (1 - convertion)
    H2O_after = f_amount * (1 - 0.543) / MW('H2O') - f_amount * 0.543 / MW('methanol') * convertion

    all_mole = H2_flow + CO2_flow + CO_flow + MeOH_after + H2O_after
    H2_P = round(H2_flow / all_mole * 100, 2)
    CO2_P = round(CO2_flow / all_mole * 100, 2)
    CO_P = round(CO_flow / all_mole * 100, 2)
    MeOH_P = round(MeOH_after / all_mole * 100, 2)
    H2O_P = round(H2O_after / all_mole * 100, 2)
    all_V = round(all_mole * R * T / P, 2)
    Volume_Percentage = {
        'H2': H2_P,
        'CO2': CO2_P,
        'CO': CO_P,
        'MeOH': MeOH_P,
        'H2O': H2O_P,
        'Total': all_V,
    }
    return Volume_Percentage
# ----------------------------------------------------------------------------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    BR_get_heat = combustion('MeOH', 2.44, 14.3, 105)
    GA = {'H2': 73.78, 'CO2':25.94, 'CO':0.4}
    Reaction_need_heat = reformer_heat(134.23, 259.39, 23.63, 38.49, GA)

    Heat_efficiency = round(Reaction_need_heat[0] / BR_get_heat[0] * 100, 4) # %
    Waste_efficiency = round((BR_get_heat[0] - Reaction_need_heat[0]) / BR_get_heat[0] * 100, 4)

    print(BR_get_heat)
    print(Reaction_need_heat)
    print(Heat_efficiency)
    print(Waste_efficiency)