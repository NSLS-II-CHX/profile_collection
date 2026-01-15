from ophyd import (EpicsMotor, PVPositioner, Device, EpicsSignal,
                   EpicsSignalRO,PVPositionerPC)
from ophyd import (Component as Cpt, FormattedComponent,
                   DynamicDeviceComponent as DDC)

class Printer_3D(Device):
    "4 axes for the 3D printer"
    x_bed = Cpt(EpicsMotor,'Bed:X}Mtr')
    z_bed = Cpt(EpicsMotor,'Bed:Z}Mtr')
    x_head = Cpt(EpicsMotor,'Head:X}Mtr')
    y_head = Cpt(EpicsMotor,'Head:Y}Mtr')
    
class Diffractometer(Device):
    yh = Cpt(EpicsMotor, '-Ax:YH2}Mtr')

diff = Diffractometer('XF:11IDB-ES{Dif', name='diff')

printer = Printer_3D('XF:11IDM3-3D{',name='printer')



