####################################################################################################

#!#
#!# ==============================
#!#  Kicad Netlist Parser Example
#!# ==============================
#!#
#!# This example shows how to read a netlist generated from the |Kicad|_ Schematic Editor.
#!#
#!# This example is copied from Stafford Horne's Blog:
#!#  * http://stffrdhrn.github.io/electronics/2015/04/28/simulating_kicad_schematics_in_spice.html
#!#  * https://github.com/stffrdhrn/kicad-spice-demo
#!#
#!# .. note:: The netlist must be generated using numbered node. Subcircuit elements must have a
#!#           reference starting by *X* and a value corresponding to the subcircuit's name.
#!#

#lfig# kicad-pyspice-example/kicad-pyspice-example.sch.svg

#!# The netlist generated by Kicad is the following:

#itxt# kicad-pyspice-example/kicad-pyspice-example.cir

####################################################################################################

import os

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import SubCircuitFactory
from PySpice.Spice.Parser import SpiceParser
from PySpice.Unit.Units import *

####################################################################################################

libraries_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'libraries')
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

#!# We implement the *PowerIn*, *Opamp*, *JackIn* and *JackOut* elements as subcircuit.

class PowerIn(SubCircuitFactory):

    __name__ = 'PowerIn'
    __nodes__ = ('output_plus', 'ground', 'output_minus')

    ##############################################

    def __init__(self):

        super().__init__()

        self.V('positive', 'output_plus', 'ground', 3.3)
        self.V('negative', 'ground', 'output_minus', 3.3)

####################################################################################################

class Opamp(SubCircuitFactory):

    __name__ = 'Opamp'
    __nodes__ = ('output',
                 'input_negative', 'input_positive',
                 'power_positive', 'power_negative')

    ##############################################

    def __init__(self):

        super().__init__()

        self.X('opamp', 'LMV981',
               'input_positive', 'input_negative',
               'power_positive', 'power_negative',
               'output',
               'NSD')

####################################################################################################

class JackIn(SubCircuitFactory):

    __name__ = 'JackIn'
    __nodes__ = ('input', 'x', 'ground')

    ##############################################

    def __init__(self):

        super().__init__()

        self.V('micro', 'ground', 'input', 'AC SIN(0 0.02 440)')

####################################################################################################

class JackOut(SubCircuitFactory):

    __name__ = 'JackOut'
    __nodes__ = ('output', 'x', 'ground')

    ##############################################

    def __init__(self):

        super().__init__()

        self.R('load', 'output', 'x', 10)

####################################################################################################

#!# We read the generated netlist.
kicad_netlist_path = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                                  'kicad-pyspice-example',
                                  'kicad-pyspice-example.cir')
parser = SpiceParser(path=kicad_netlist_path)

#!# We build the circuit and translate the ground (5 to 0).
circuit = parser.build_circuit(ground=5)

#!# We include the operational amplifier module.
circuit.include(spice_library['LMV981'])

#!# We define the subcircuits.
for subcircuit in (PowerIn(), Opamp(), JackIn(), JackOut()):
    circuit.subcircuit(subcircuit)

# print(str(circuit))

#!# We perform a transient simulation.
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=milli(.1), end_time=milli(3))

figure = plt.figure(1, (20, 10))
plot(analysis['2']) # JackIn input
plot(analysis['7']) # Opamp output
plt.legend(('Vin [V]', 'Vout [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
#fig# save_figure(figure, 'kicad-example.png')
