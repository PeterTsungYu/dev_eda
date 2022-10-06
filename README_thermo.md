# Thermodynamics of reformer reaction
## Content
thermo_ver_2.py is for the calculation of thermodynamic of reformer reaction writing by Python.
Inculding:
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

## Install package
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

CombustionCalc(combustion_heat, Ideal_gas_constant)
ReformerReactionCalc(reformer_heat, Ideal_gas_constant)
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
