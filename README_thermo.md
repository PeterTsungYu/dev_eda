# Thermodynamics of Reformer Reaction
## Content
thermo_ver_2.py is for the calculation of thermodynamic of reformer reaction writing by Python. In thermo_ver_2.py, all of the theory calculation refer to [NIST](https://webbook.nist.gov/chemistry/), include formulas and constants.
Function:
- Calculation of heating value
- Combustion efficency:
  - Giving heat
  - Ideal reformer get heat
  - Waste heat
  - Heat efficency
- Reaction process:
  - Reaction ethalpy
  - Reaction needed heat
- Composition of products in percentage

## Install Package
Before starting, there is a package required:

[chemicals 1.1.2](https://pypi.org/project/chemicals/)

``` shell
pip3 install chemicals
```

## Quick Start
To use, some experimental data required, there is the example data below. The detail of each parameter illustrate by comment message.

``` shell
import thermo_ver_2

# experimental data
GA = {'H2': 70.55, 'CO2': 24.51, 'CO': 0.76} # product compostion (%)
Ideal_gas_constant = {'R': 0.082, 'P': 1, 'T': 298}
combustion_heat = {
    'fuel type': 'AOG', # 'MeOH', 'H2', or 'AOG'
    'fuel flow': 17.66, # for 'MeOH' use g/min, 'H2' & 'AOG' use LPM
    'air flow': 130, # LPM
    'air T': 25, # oC
    'burner out T': 206.96, # exhaust gas tempertrue (oC)
    'gas composition': GA,
}
reformer_heat = {
    'reactants T': 174.77, # tempertrue of reactants (oC)
    'products T': 262.14, # tempertrue of products before cooling down (oC)
    'reactants flow': 19.87, # MeOH/H2O flow rate (g/min)
    'products flow': 32.8, # total products flow rate (LPM)
    'gas composition': GA,
    'convertion': 96.32, # ideal convertion (%)
    'pressure': 0.03, # pressure of products (bar)
    'RAD T': 32.11, # tempertrue of products after cooling down (oC)
}
# ------------------------------------------------------------------------
Ther = ThermodynamicsCalculation(combustion_heat, reformer_heat, Ideal_gas_constant)

# Combustion efficency
# ideal_reformer_get, combustion_give, conbustion_wasted, reaction_need, heat_efficiency (kW)
heff = Ther.heff()
for i in heff:
    print(i)

# Reaction process
# reaction needed heat (kJ/min)
react_ethalpy = Ther.need()
print(round(react_ethalpy[2], 2))

# Composition of products in percentage
percentage_ratio = T.percentage()[0]
print(percentage_ratio)
```
## Class and Function
### Basic Function
`ethalpy(t, A, B, C, D, E, F, G, H)`  
The Shomate equation for ethalpy at different temperture compare with the temperture at 298.15 K. A to H is coefficients of the equation, data from [NIST](https://webbook.nist.gov/chemistry/).
t is tempertrue giving by °C.

`deltaH(T)`  
To calculate the delta H of each species.
T is tempertrue giving by K.

### `CombustionCalc(burner, Idealgasconstant)`
This class is for the calculation of combustion prosses. To use this, you need some parameters:
1. burner: a dict, including:
   - fuel type: str, 'H2', 'MeOH', or 'AOG'
   - fuel flow: float, [g/min] for 'MeOH', [LPM] for 'H2' & 'AOG'
   - air flow: float, [LPM]
   - air T: float, [°C]
   - burner out T: float, [°C]
   - gas composition: a dict, composition of AOG the unit of values use [%]
2. Idealgasconstant: a dict, including:
   - R: float, the ideal gas constant usually use 0.082
   - T: float, [K]
   - P: float, [atm]
#### `CombustionCalc.data()`
To calculate the combustion data, will get HHV at [298 K], [1 atm].  

**Return**
  - *com_data*: class
  - Combustion data of fuel, inculding the mole ratio of CO2, H2O, and O2. Also the higher heating value(HHV), standard enthalpy of formation, and molecular weight     of fuel.  

**Example**
```shell
Cb = CombustionCalc(burner, Idealgasconstant) # The argument please refer to the example in Quick Start
Cb.data()
# return
CombustionData(stoichiometry={'CO2': 0, 'O2': -0.5, 'H2O': 1.0}, HHV=-285825.0, Hf=0, MW=2.01588)
```
#### `CombustionCalc.fuelunit()`
To turn the unit of air and fuel into [mole/min].  

**Return**
  - *(O2_before, N2_before, fuel_before)*: tuple
  - The flow rate of fuel and air before combustion, [mole/min].  

**Example**
```shell
Cb = CombustionCalc(burner, Idealgasconstant) # The argument please refer to the example in Quick Start
Cb.fuelunit()
# return
(1.117651185535599, 4.2023684576138525, 1.0278323368963824)
```

#### `CombustionCalc.exhaustgasunit()`
To turn the unit of products after combustion into [mole/min].  

**Return**
  - *(O2_after, N2_after, CO2_after, H2O_after)*: tuple
  - The flow rate of fuel and air after fully combustion, [mole/min].  

**Example**
```shell
Cb = CombustionCalc(burner, Idealgasconstant) # The argument please refer to the example in Quick Start
Cb.exhaustgasunit()
# return
(0.8606931013115035, 4.2023684576138525, 0.17713480111311183, 1.0278323368963824)
```

#### `CombustionCalc.heatgive()`
According to the fuel type, calculate the heating value and total heat-gived of combustion.  

**Return**
  - *(Give_Heat, HHV_Jg, LHV_Jg)*: tuple
  - Giving heat by combustion and heating value accorrding to different fuel type, [kJ, J/g, J/g].  

**Example**
```shell
Cb = CombustionCalc(burner, Idealgasconstant) # The argument please refer to the example in Quick Start
Cb.heatgive()
# return
(145.7329690722704, 141786.71349485088, 119954.3147409568)
```

#### `CombustionCalc.wasted()`
To calculate the heat wasted to environment.  

**Return**
  - *W_total*: tuple
  - The heat of exhaustgas, [kJ].  

**Example**
```shell
Cb = CombustionCalc(burner, Idealgasconstant) # The argument please refer to the example in Quick Start
Cb.wasted()
# return
(42.76296365954362,)
```

### `ReformerReactionCalc(reaction, Idealgasconstant)`
This class is for the calculation of reaction prosses. To use this, you need some parameters:
1. reaction: a dict, including:
   - 'reactants T': float, [°C]
   - 'products T': float, [°C]
   - 'reactants flow': float, [g/min]
   - 'products flow': float, [LPM]
   - 'burner out T': float, [°C]
   - 'gas composition': a dict, composition of AOG the unit of values use [%]
   - 'convertion': float, [%]
   - 'pressure': float, [bar]
   - 'RAD T': float, [°C]
2. Idealgasconstant: a dict, including:
   - 'R': float, the ideal gas constant usually use 0.082
   - 'T': float, [K]
   - 'P': float, [atm]

#### `conver(self)`
Adjust the convertion, if over 100 % let it no more than one hundred, if no convertion given assume 100 %, if convertion below 0 raise error.

#### `reactantsunit(self)`
According to the convertion, turn the unit of reactants into [mole/min].

#### `productsunit(self)`
According to the convertion, turn the unit of products into [mole/min].

#### `heatcalculate(self)`
To calculate the energy of all species, the unit of each is [kJ/min].

#### `need(self)`
To calculate the energy that reaction need, [kJ/min].

#### `percentage(self)`
To calculate the percentage of products.

### `ThermodynamicsCalculation(burner, reaction, Idealgasconstant)`
This class is inherit `CombustionCalc` and `ReformerReactionCalc`, and has function to give quick results.

#### `heff(self)`
To show the heat efficeny results according to the parameters given.
