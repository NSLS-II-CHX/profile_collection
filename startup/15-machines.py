from ophyd import PVPositionerPC, EpicsSignal, EpicsSignalRO
from ophyd import Component as Cpt

# Undulator
class InsertionDevice(Device):
    gap = Cpt(EpicsMotor, '-Ax:Gap}-Mtr',
              kind='hinted', name='')
    brake = Cpt(EpicsSignal, '}BrakesDisengaged-Sts',
                write_pv='}BrakesDisengaged-SP',
                kind='omitted', add_prefix=('read_pv', 'write_pv', 'suffix'))

    def set(self, *args, **kwargs):
        set_and_wait(self.brake, 1)
        return self.gap.set(*args, **kwargs)

    def stop(self, *, success=False):
        return self.gap.stop(success=success)


ivu_gap = InsertionDevice('SR:C11-ID:G1{IVU20:1', name='ivu')
# ivu_gap.readback = 'ivu_gap'   ####what the ^*(*()**)(* !!!!
#To solve the "KeyError Problem" when doing dscan and trying to save to a spec file, Y.G., 20170110
ivu_gap.gap.name = 'ivu_gap'

# This class is defined in 10-optics.py
fe = VirtualMotorCenterAndGap('FE:C11A-OP{Slt:12', name='fe') # Front End Slits (Primary Slits)
