from ast import Interactive
import bluesky.plan_stubs as bps
import time

def goto_transmission_hole():
    xhole = 9.0
    yhole = -7.0 
    RE(mv(diff.xh,xhole))
    RE(mv(diff.yh,yhole))

def measure_transmission():
    roi_no = 1
    eiger4m.cam.acquire_time.set(.1)
    eiger4m.cam.acquire_period.set(.1)
    eiger4m.cam.num_images.set(1)
    
    att.set_T(0.05)
    #if att2.get_T()>1E-4:
    #    raise Exception('something went wrong with setting attenuators...NOT save to remove beamstop!')

    RE(mvr(saxs_bst.y1,10))

    last_xh = diff.xh.user_setpoint.value
    last_yh = diff.yh.user_setpoint.value

    # measure I0
    #eiger4m.cam.num_images.set(1)
    goto_transmission_hole()
    RE.md['ring current I0']=caget('SR:OPS-BI{DCCT:1}I:Real-I')
    RE(count([eiger4m_single]))
    h=db[-1]
    I0 = np.average(h.table()[f'eiger4m_single_stats{roi_no}_total'])

    # measure I_transmitted
    RE(mv(diff.xh,last_xh,diff.yh,last_yh))
    RE.md['ring current sample']=caget('SR:OPS-BI{DCCT:1}I:Real-I')
    RE(count([eiger4m_single]))
    h=db[-1]

    transmission = np.average(h.table()[f'eiger4m_single_stats{roi_no}_total'])/I0

    RE.md['sample_transmission']=transmission

    print(f'Sample transmission = {transmission}')

    RE(mvr(saxs_bst.y1,-10))

    att.set_T(1)
    att2.set_T(1)


def new_sample(name):
    RE.md['sample']=name
    print(f'Measuring transmission for sample {name}')
    measure_transmission()



def newspot(step=0.2):
    xlim= 2.8
    xstart= 1.5
    ystart=-7.5
    ylim=-6.5


    if np.abs(diff.xh.user_readback.value-xlim) <= step-0.1:
        RE(mv(diff.xh,xstart));
        if(ylim-diff.yh.user_readback.value) <= step-0.1:
            RE(mv(diff.yh,ystart));
        else:
            RE(mvr(diff.yh,step))
    else:
        RE(mvr(diff.xh,step))

def old_measure_transmission():
    eiger4m.cam.acquire_time.set(.1)
    eiger4m.cam.acquire_period.set(.1)
    eiger4m.cam.num_images.set(1)
    att2.set_T(1E-5)
    if att2.get_T()>1E-4:
        raise Exception('something went wrong with setting attenuators...NOT save to remove beamstop!')
    RE(mvr(saxs_bst.y1,10))
    RE(dscan([eiger4m_single],diff.xh,-.1,.1,5))
    goto_beamline_pos('saxs_bst_in',interactive=False)
    h=db[-1]
    roi_no=1
    RE.md['sample_transmission']=np.average(h.table()['eiger4m_single_stats%s_total'%roi_no][1:])/RE.md['I_0']
    RE.md['ring current']=caget('SR:OPS-BI{DCCT:1}I:Real-I')
    RE.md['BPM_Total I']=caget('XF:11IDB-BI{XBPM:02}Ampl:CurrTotal-I')
    att2.set_T(1)

def set_temperature_safe2(temp, heat_ramp = 10, cool_ramp = 10, wt =0):
    temp = float(temp)

    if temp > 80:
        print("Error: Cannot set temperature above 80 degrees!")

    else:
        set_temperature(temp, heat_ramp, cool_ramp, check_vac=False)
        time.sleep(wt)


def set_temperature_safe(temp, heat_ramp = 3, cool_ramp = 0):
    temp = float(temp)

    if temp > 80:
        print("Error: Cannot set temperature above 80 degrees!")

    else:
        set_temperature(temp, heat_ramp, cool_ramp, check_vac=False)

def measure_SAXS(expt=.01,imnum=10):
    newspot() 
    att2.set_T(1)
    RE.md['sample_x']=diff.xh.user_readback.value
    RE.md['sample_y']=diff.yh.user_readback.value
    comment = f'SAXS xh={diff.xh.user_readback.value:.2f} yh={diff.yh.user_readback.value:.2f} '+'AUTO_COMMENT'
    series(det='eiger4m',expt=expt,imnum=imnum, feedback_on=False,auto_compression=True,OAV_mode='none',comment=comment)
    RE.md.pop('sample_x')
    RE.md.pop('sample_y')

def measure_XPCS():

    #1. Fast series - total of 1s 750 frames
    att2.set_T(1)
    newspot()
    RE.md['sample_x']=diff.xh.user_readback.value
    RE.md['sample_y']=diff.yh.user_readback.value
    comment = f'Fast XPCS xh={diff.xh.user_readback.value:.2f} yh={diff.yh.user_readback.value:.2f} '+'AUTO_COMMENT'

    series(det='eiger4m',expt=0.00134,imnum=750, feedback_on=False,auto_compression=True,OAV_mode='none',comment=comment)

    #2 Medium (fast) series total of 12 seconds, 750 frames but ther same integrated dose
    att2.set_T(0.083) 
    newspot()
    RE.md['sample_x']=diff.xh.user_readback.value
    RE.md['sample_y']=diff.yh.user_readback.value
    comment = f'Medium XPCS xh={diff.xh.user_readback.value:.2f} yh={diff.yh.user_readback.value:.2f} '+'AUTO_COMMENT'
    series(det='eiger4m',expt=0.016,imnum=750, feedback_on=False,auto_compression=True,OAV_mode='none',comment=comment)
    
    #3 Slow series - total of 63 s, 750 frames
    att2.set_T(0.016)
    newspot()
    RE.md['sample_x']=diff.xh.user_readback.value
    RE.md['sample_y']=diff.yh.user_readback.value
    comment = f'Slow XPCS xh={diff.xh.user_readback.value:.2f} yh={diff.yh.user_readback.value:.2f} '+'AUTO_COMMENT' 
    series(det='eiger4m',expt=0.084,imnum=750, feedback_on=False,auto_compression=True,OAV_mode='none',comment=comment)

    att2.set_T(1)

    RE.md.pop('sample_x')
    RE.md.pop('sample_y')

    #temperatures=[300,290,280,270,260,250,240,230,220,210]
#temperatures=[47.4,47.2,47,46.8,46.6,46.4,46.2,46]
temperatures = np.linspace(65, 57,14)
def temperature_series(temperatures, wt=60, reps=30 ):
    # modified by you (keep original concepts)
    olog_entry('NEW TEMPERATURE SERIES: %s' % RE.md['sample'])

    # First, reach the starting temperature 
    #set_temperature_safe(temperatures[0])

    for idx, t in enumerate(temperatures):
        # Reach the current temperature and wait for it to stabilize.
        set_temperature_safe(t, heat_ramp=3, cool_ramp=3)
        time.sleep(20)

        # The measurement was repeated several times at this temperature: because `measure_SAXS()` calls `newspot()`, the measurements are naturally taken at different locations.
        for i in range(reps):
            measure_SAXS()
            #measure_XPCS()
        #set_temperature_safe(50, heat_ramp=5, cool_ramp=0.1)
        #time.sleep(60)

        # # If there's another temperature step: heat to 40 degrees and hold for 10 minutes, then the next cycle will decrease to the next temperature.
        # if idx < len(temperatures) - 1:
        #     set_temperature_safe(high_temp, heat_ramp=5, cool_ramp=.5)
        #     wait_temperature(wait_time=wt)

    set_temperature_safe(65,heat_ramp=7)
    wait_temperature(wait_time=wt)

    olog_entry('END OF TEMPERATURE SERIES: %s' % RE.md['sample'])
