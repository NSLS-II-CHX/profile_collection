from ophyd import (EpicsMotor, PVPositioner, Device, EpicsSignal,
                   EpicsSignalRO,PVPositionerPC)
from ophyd import (Component as Cpt, FormattedComponent,
                   DynamicDeviceComponent as DDC)


class hyrel_MK1(Device):
    """ class to support MK1 printheads from hyrel3D"""
    heat = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Cmd-Heat',put_complete=True)
    heat_RB = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:T-RB')
    fan = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Cmd-Fan',put_complete=True)
    deposition_volume = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Val-rVal:SP',put_complete=True)
    deposition_speed = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Cmd-Run',put_complete=True)
    prime_volume = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Val-pVal:SP',put_complete=True)
    prime_delay = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Val-pDly:SP',put_complete=True)
    prime_speed = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Cmd-Prime',put_complete=True)
    unprime_volume = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Val-uVal:SP',put_complete=True)
    unprime_delay = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Val-uDly:SP',put_complete=True)
    unprime_speed = EpicsSignal('XF:11ID-M3{Hyrel:1}T11:Cmd-uPrime',put_complete=True)


mk1 = hyrel_MK1(name='mk1')

class ultimus_V(Device):
    """" class to support Ultimus V dispenser from Nordson with EPICS timer """
    pressure = EpicsSignal('XF:11ID-M3{UltimusV}P',put_complete=True)
    pressure_RB = EpicsSignal('XF:11ID-M3{UltimusV}P-I:calc')
    pressure_unit = EpicsSignal('XF:11ID-M3{UltimusV}P:EU',put_complete=True)
    pressure_unit_RB = EpicsSignal('XF:11ID-M3{UltimusV}P:EU-RB')
    vacuum = EpicsSignal('XF:11ID-M3{UltimusV}Vac',put_complete=True)
    vacuum_RB = EpicsSignal('XF:11ID-M3{UltimusV}Vac-I:calc')
    vacuum_unit = EpicsSignal('XF:11ID-M3{UltimusV}Vac:EU',put_complete=True)
    vacuum_unit_RB = EpicsSignal('XF:11ID-M3{UltimusV}Vac:EU-RB')
    mode = EpicsSignal('XF:11ID-M3{UltimusV}Mode',put_complete=True)
    dispense_time = EpicsSignal('XF:11ID-M3{UltimusV}cdt5:setTimeSec',put_complete=True)
    dispense_start = EpicsSignal('XF:11ID-M3{UltimusV}cdt5:start',put_complete=True)
    dispense_status = EpicsSignal('XF:11ID-M3{UltimusV}Disp:Calc')

ultimus = ultimus_V(name='ultimus')

def ultimus_units(P='psi',V='kpa'):
    """
    set pressure and vacuum units on Ultimus V
    ultimus_set_units(P='psi',V='kpa')
    valid P: 'psi','bar','kpa'
    valid V: 'kpa',inches_h2o,inches_gh,mm_hg,torr
    """
    p_dict={'psi':0,'bar':1,'kpa':2}
    v_dict={'kpa':0,'inches_h2o':1,'inches_gh':2,'mm_hg':3,'torr':4}
    ultimus.pressure_unit.set(p_dict[P])
    ultimus.vacuum_unit.set(v_dict[V])
    pr=ultimus.pressure_unit_RB.get()
    vr=ultimus.vacuum_unit_RB.get()
    print('set units on ultimus V: P -> %s  V-> %s'%(p_dict[pr],v_dict[vr]))

def ultimus_mode(mode=1):
    """
    ultimus_mode(mode=1)
    expert mode! 0: internal timer, 1: steady [should be used!], 2: time/steady toggle
    """
    ultimus.mode.set(mode)

def ultimus_pressure(P='SP'):
    if P == 'SP': # just asking for current pressure
        p_dict={'psi':0,'bar':1,'kpa':2}
        #v_dict={'kpa':0,'inches_h2o':1,'inches_gh':2,'mm_hg':3,'torr':4}
        p=ultimus_pressure_RB.get()
        pu=ultimus_pressure_unit_RB.get()
        print('Ultimus-V current pressure: %s %s'%(p,p_dict[pu]))        
    else:
        caput('XF:11ID-M3{UltimusV}P',P,wait=True)
        #ultimus.pressure.set(P)

def ultimus_vacuum(V='SP'):
    if V == 'SP': # just asking for current pressure
        v_dict={'kpa':0,'inches_h2o':1,'inches_gh':2,'mm_hg':3,'torr':4}
        v=ultimus_vacuum_RB.get()
        vu=ultimus_vacuum_unit_RB.get()
        print('Ultimus-V current vacuum: %s %s'%(v,v_dict[vu]))        
    else:
        ultimus.vacuum.set(V)

def ultimus_start():
    ultimus.dispense_start.set(1)

def ultimus_stop():
    ultimus.dispense_start.set(0)

def ultimus_status():
    s=ultimus.dispense_status.get()
    s_dict={0:'OFF',1:'ON'}
    print('Ultimus-V dispense status: %s'%s_dict[s])
    return s

def ultimus_dispense(t=10):
    """
    ultimus_dispense(t=10)
    start dispensing for t [s] with current dispenser settings
    """        
    ultimus.dispense_time.set(t)
    ultimus_start()

def ultimus_deposition(t=1,pressure=5):
    #ultimus_stop() # just to be sure it's stopped...
    #ultimus_pressure(P=pressure) # set the pressure in current device units
    caput('XF:11ID-M3{UltimusV}P',pressure,wait=True);RE(sleep(.5))
    ultimus_dispense(t=t)
    #ultimus_pressure(P=0)

#def mk1_250_printhead(nozzle_size=.5,filament_size=1.75):
#    """ function to operate hyrel3D MK1-250 FFF printhead """
def mk1_250_fan(speed=30,verbose=True):
    """
    set MK1-250 fan speed [Hz]: mk1_250_fan(speed=30)
    readback MK1-250 fan speed [Hz]: mk1_250_fan('RB')
    """
    if type(speed)==int or type(speed)==float:
        if speed>=0 and speed <=35:
            mk1.fan.set(speed)
            if verbose:
                print('set fan speed for MK1-250 to %sHz'%int(speed))
        else: raise Exception('fan speed for MK1-250 needs to be between 0 (=off) and 35 Hz')
    if speed == 'RB':
        current_speed=mk1.fan.get()
        if verbose:
            print('current fan speed for MK1-250 is %s Hz'%(current_speed))
        return current_speed

def mk1_250_heat(temperature=50,verbose=True):
    """
    set MK1-250 temperature [C]: mk1_250_heat(temperature=50)
    readback MK1-250 temperature setpoint [C]: mk1_250_fan('SP')
    readback MK1-250 current temperature [C]: mk1_250_fan('RB')

    """
    if type(temperature)==int or type(temperature)==float:
        if temperature>=0 and temperature <=450:
            mk1.heat.set(temperature)
            if verbose:
                print('set temperature for MK1-250 to %sC'%int(temperature))
        else: raise Exception('temperature for MK1-250 needs to be between 0 (=off) and 250C')
    if temperature == 'SP':
        current_temperature=mk1.heat.get()
        if verbose:
            print('current temperature setpoint for MK1-250 is %sC'%(current_temperature))
        return current_temperature
    elif temperature == 'RB':
        current_temperature=mk1.heat_RB.get()
        if verbose:
            print('current temperature for MK1-250 is %sC'%(current_temperature))
        return current_temperature

def mk1_250_prime(volume=200,delay=500,speed=500,temperature=40):
    """
    prime mk1 printhead. Volume [ct], delay [ms], speed [ct/s]
    """
    if np.abs(mk1_250_heat('RB')-temperature) >10:
        raise Exception('Temperature is off by more than 10C -> aborting prime. Set temperature first.')
    mk1.prime_volume.set(volume)
    mk1.prime_delay.set(delay)
    mk1.prime_speed.set(speed)

def mk1_250_unprime(volume=200,delay=500,speed=500,temperature=40):
    """
    unprime mk1 printhead. Volume [ct], delay [ms], speed [ct/s]
    """
    if np.abs(mk1_250_heat('RB')-temperature) >10:
        raise Exception('Temperature is off by more than 10C -> aborting unprime. Set temperature first.')
    mk1.unprime_volume.set(volume)
    mk1.unprime_delay.set(delay)
    mk1.unprime_speed.set(speed)


def mk1_250_deposition(nozzle_size=.74,filament_size=1.68,speed=5,road_length=30,temperature=40,verbose=True):
    """
        

    filament size 1.68 -> nominal 1.75mm ABS
    nozzle size .74: measured from extruded filament
    """
    if np.abs(mk1_250_heat('RB')-temperature) >10:
        raise Exception('Temperature is off by more than 10C -> aborting deposition. Set temperature first.')
    cts_mm=228 #counts/mm feed -> this should be independent of nozzle and filament diameter
    Vext=road_length*np.pi*(nozzle_size/2)**2
    feed_length=Vext/np.pi/((filament_size/2)**2)
    Vct=feed_length*cts_mm
    speed_cts_s=Vct/(road_length/speed)
    if verbose:
        print('printing %s mm road at %s mm/s\nnozzle diameter: %smm,  filament diameter: %smm\nVolume [ct]: %s  Run [ct/s]: %s'%(road_length,speed,np.round(nozzle_size,2),np.round(filament_size,2),np.round(Vct,1),np.round(speed_cts_s,1)))
    mk1.deposition_volume.set(int(Vct))
    mk1.deposition_speed.set(int(speed_cts_s))


class loctite_UV(Device):
    """ class to support Loctite UV curing system """
    ch1_select = EpicsSignal('XF:11ID{LOCTITE:Chan1}:SW-Out',put_complete=True)
    ch2_select = EpicsSignal('XF:11ID{LOCTITE:Chan2}:SW-Out',put_complete=True)
    ch3_select = EpicsSignal('XF:11ID{LOCTITE:Chan3}:SW-Out',put_complete=True)
    ch4_select = EpicsSignal('XF:11ID{LOCTITE:Chan4}:SW-Out',put_complete=True)
    ch1_time = EpicsSignal('XF:11ID{LOCTITE:Chan1}:TIME-NEW-RAW',put_complete=True)
    ch2_time = EpicsSignal('XF:11ID{LOCTITE:Chan2}:TIME-NEW-RAW',put_complete=True)
    ch3_time = EpicsSignal('XF:11ID{LOCTITE:Chan3}:TIME-NEW-RAW',put_complete=True)
    ch4_time = EpicsSignal('XF:11ID{LOCTITE:Chan4}:TIME-NEW-RAW',put_complete=True)
    ch1_intensity = EpicsSignal('XF:11ID{LOCTITE:Chan1}:INT-Inp',put_complete=True)
    ch2_intensity = EpicsSignal('XF:11ID{LOCTITE:Chan2}:INT-Inp',put_complete=True)
    ch3_intensity = EpicsSignal('XF:11ID{LOCTITE:Chan3}:INT-Inp',put_complete=True)
    ch4_intensity = EpicsSignal('XF:11ID{LOCTITE:Chan4}:INT-Inp',put_complete=True)
    uv_off = EpicsSignal('XF:11ID{LOCTITE}:OFF',put_complete=True)
    uv_on = EpicsSignal('XF:11ID{LOCTITE}:ON',put_complete=True)

UV = loctite_UV(name='UV')

def UV_channel_select(channel_list=[1]):
    """
    selecting channels on Loctite UV source
    UV_channel_select([1]) -> LIST of channels
    """
    # everything off:
    UV.ch1_select.set(0); UV.ch2_select.set(0); UV.ch3_select.set(0); UV.ch4_select.set(0);
    # selected on:
    if 1 in channel_list:
        UV.ch1_select.set(1)
    if 2 in channel_list:
        UV.ch2_select.set(1)
    if 3 in channel_list:
        UV.ch3_select.set(1)
    if 4 in channel_list:
        UV.ch4_select.set(1)

def UV_channel_setup(setup_dict={1:[10,25],}):
    """
    function to set intensity and time for channels of Loctite UV curing system
    UV_channel_setup(setup_dict={1:[10,25],}) -> channel 1, 10s, 25% intensity
    """
    channel_list=list(setup_dict.keys())
    UV_channel_select(channel_list)
    if 1 in channel_list:
        UV.ch1_time.set(setup_dict[1][0]*10)
        UV.ch1_intensity.set(setup_dict[1][1])
    if 2 in channel_list:
        UV.ch2_time.set(setup_dict[2][0]*10)
        UV.ch2_intensity.set(setup_dict[2][1])
    if 3 in channel_list:
        UV.ch3_time.set(setup_dict[3][0]*10)
        UV.ch3_intensity.set(setup_dict[3][1])
    if 4 in channel_list:
        UV.ch4_time.set(setup_dict[4][0]*10)
        UV.ch4_intensity.set(setup_dict[4][1])

def UV_on():
    UV.uv_on.set(1)

def UV_off():
    UV.uv_off.set(1)

