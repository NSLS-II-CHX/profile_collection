from ophyd import (Device, Component as Cpt, EpicsSignalRO)

class CryostatTemperatureController(Device):
    sample = Cpt(EpicsSignalRO, 'Sample')
    control = Cpt(EpicsSignalRO, 'Control')
    heater = Cpt(EpicsSignalRO, 'Heater')
    setpoint = Cpt(EpicsSignalRO, 'SP1')
    ramp = Cpt(EpicsSignalRO, 'Ramp1')
    ramp_on = Cpt(EpicsSignalRO, 'Ramp1_on')
    heater_full_scale_wattage = Cpt(EpicsSignalRO, 'HeatRg')
    heater_percent_full_scale = Cpt(EpicsSignalRO, 'Heater')

ls340 = CryostatTemperatureController('XF:11IDB-ES{Env:02}LS340:TC1:',name = 'ls340')
