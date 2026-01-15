from ophyd import (EpicsMotor, PVPositioner, Device, EpicsSignal,
                   EpicsSignalRO,PVPositionerPC)
from ophyd import (Component as Cpt, FormattedComponent,
                   DynamicDeviceComponent as DDC)

class heated_platform(Device):
    """
    setup notes:
    control cable coming FROM power supply:
    voltage-control: AO:1
    current-control: AO:2
    power supply OFF: DO:1

    Cable FROM platform:
    Power +/- (thick cable, red/black connectors): front of Power supply
    Logic power +/- (thin cable, red/black connectors): build in power supply (from PLC)
    temperature 1/2 (platform RTDs): RTD:1/2
    enable heater platform 1 (DO:1) -> DO2
    enable heater platform 2 (DO:2) -> DO3
    Note: DO:3 and second set of power from this cable is NOT used for this setup
    !!! IMPORTANT !!!
    even though calc, pid and ioLogik seem to be up and running, MUST restart IOCs to work properly
    also: EPID output might be 'off' (pid01)
    """
    power_inhibit_pv = 'XF:11IDM-M3{IO:1}DO:1-Cmd'
    power_input_V_pv = 'XF:11IDM-M3{IO}AO:1-SP'
    p1_enable_pv = 'XF:11IDM-M3{IO:1}DO:2-Cmd'
    p2_enable_pv = 'XF:11IDM-M3{IO:1}DO:3-Cmd'
    power_inhibit = EpicsSignal(power_inhibit_pv,put_complete=True)  # 1: short to GND on remote PowerSupply (=OFF)
    power_input_V = EpicsSignal(power_input_V_pv,put_complete=True)  # Voltage setting for remote PS: 2.95V -> 24V out
    power_input_V_RB = EpicsSignal('XF:11IDM-M3{IO}AO:1-RB')
    power_input_I_max = EpicsSignal('XF:11ID-CT{FbPid:01}PID.DRVH',put_complete=True)  #current limit in feedback loop: max is 2
    p1_enable = EpicsSignal(p1_enable_pv,put_complete=True) # relay for platform 1
    p2_enable = EpicsSignal('XF:11IDM-M3{IO:1}DO:3-Cmd',put_complete=True) # relay for platform 2
    PID_on = EpicsSignal(p1_enable_pv,put_complete=True) # PID loop on/off (off sets drive signal for current to 0)
    PID_input = EpicsSignal('XF:11ID-CT{FbPid:01}PID:in.CALC',put_complete=True) #temperature input for PID: B=P1, C=P2
    temperature_SP = EpicsSignal('XF:11ID-CT{FbPid:01}PID.VAL',put_complete=True) #temperature setpoint
    temperature_FE = EpicsSignal('XF:11ID-CT{FbPid:01}PID.ERR') # temperature following error

hp = heated_platform(name='hp')

def set_hp(platform=1,temperature=20,I_max_V=1.,verbose=True):
    """
    function to set temperature on heated platform(s)
    only allows heating one platform at the time (current limit): if a new platform is heated, previous one will be disabled.
    """
    # check status:
    #p1_status = hp.p1_enable.get();p2_status = hp.p2_enable.get()
    if hp.p1_enable.get() !=0 and hp.p2_enable.get() != 0: # this shouldn't happen...
        hp.p1_enable.set(0);hp.p2_enable.set(0);hp.PID_on.set(0) # disable both and stop PID loop
    elif (hp.p1_enable.get() !=0 and platform==2): 
        hp.p1_enable.set(0);hp.p2_enable.set(0);hp.PID_on.set(0) #
    elif (hp.p2_enable.get() !=0 and platform==1): 
        hp.p1_enable.set(0);hp.p2_enable.set(0);hp.PID_on.set(0)
    # make sure the power supply is set up:
    if np.abs(hp.power_input_V_RB.get()-2.95)>.1:
        hp.power_input_V.set(2.95)
    if I_max_V >=0 and I_max_V <=2:
        hp.power_input_I_max.set(I_max_V)
    else: raise Exception('drive voltage for current output must be 0<I_max_V<2')
   
 
    if hp.power_inhibit.get()==1:
        hp.power_inhibit.set(1)
   
    if temperature >150:
            raise Exception('max temperature is 150')

    p1_status = hp.p1_enable.get();p2_status = hp.p2_enable.get()
    if p1_status==0 and platform ==1:
        hp.p1_enable.set(1)
        if verbose:
          print('switched temperature control to platform 1')
    elif p2_status==0 and platform == 2:
        hp.p2_enable.set(1)
        if verbose:
          print('switched temperature control to platform 2')
    #p1_status = hp.p1_enable.get();p2_status = hp.p2_enable.get()
    if hp.p1_enable.get() == 1 and  platform==1: # just changing temperature on p1
        if hp.PID_input.get()!='B':
            hp.PID_input.set('B')
        hp.temperature_SP.set(temperature)
        if hp.PID_on.get()==0:
            hp.PID_on.set(1)    
        if verbose:
            print('set temperature for platform 1 to %sC'%temperature)
    elif hp.p2_enable.get() == 1 and  platform==2: # just changing temperature on p2
        if hp.PID_input.get()!='C':
            hp.PID_input.set('C')
        hp.temperature_SP.set(temperature)
        if hp.PID_on.get()==0:
            hp.PID_on.set(1)     
        if verbose:
            print('set temperature for platform 2 to %sC'%temperature)
    if platform == 1:
        hp.p2_enable.set(0)
    elif platform == 2:
        hp.p1_enable.set(0)



def set_hp_labels(action='set'):
    label_dict = {hp.power_inhibit_pv:['DO Channel 1','Heater power OFF'],
        hp.power_input_V_pv:['AO Chan1 (0-10V)','Voltage Heater PS'],
        hp.p1_enable_pv:['DO Channel 2','Heater Platform 1'],
        hp.p2_enable_pv:['DO Channel 3','Heater Platform 2'],
        'XF:11IDM-M3{IO}AO:2-SP':['AO Chan2 (0-10V)','Current Heater PS'],
        'XF:11IDM-M3{IO:RTD}T:1-I':['RTD Channel 1','Temp. Platform 1'],
        'XF:11IDM-M3{IO:RTD}T:2-I':['RTD Channel 2','Temp. Platform 2'],
        }
    if action == 'set': n=1
    elif action == 'reset': n=0
    for i in list(label_dict.keys()):
        caput(i+'.DESC',label_dict[i][n])





    