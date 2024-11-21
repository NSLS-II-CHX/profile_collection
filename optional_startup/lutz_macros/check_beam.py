import sys
sys.path.insert(0, "/nsls2/data/chx/shared/CHX_Software/packages/archiver_setup/")
import archiver_setup
import numpy as np
from archiver_setup import get_archived_pvs_from_uid

def check_past_data(uid,bpm_int_threshold=-1,fraction=.05,verbose=False):
    """
    Check whether beam had been lost during previous dataset
    uid: dataset to be checked
    bpm_int_threshold: if archived BPM intensity is LARGER (BPM intensity is negative!!) than this threshold for a number of datapoints > fraction of the total number of datapoitns in the dataset -> conclusion: beam has been lost during data acquisition for this uid
    Note: currently only checking BPM intensity, could also check for BPM positions, but losing the feedback is typically associated with the sydor ioc requiring a restart, which cannot be scripted at this time
    returns: False: beam has not been lost / True: beam has been lost
    """
    if verbose:
        print('checking for possible beam loss during data acquisition for uid: %s'%uid[:8])
    pv_list = ['XF:11IDB-BI{XBPM:02}Ampl:CurrTotal-I']
    pvd = get_archived_pvs_from_uid(pv_list,uid,verbose=verbose)
    ind = pvd[pv_list[0]]['data'] > bpm_int_threshold
    fr = np.nansum(ind)/len(ind)
    beam_lost = False
    if  fr > fraction:
        beam_lost = True
        if verbose:
            print('during data acquisition for uid %s BPM intensity was > %s for %0f percent of the time -> beam lost during data acquisition: %s'%(uid[:8],bpm_int_threshold,fr*100,beam_lost))
    else:
        if verbose:
            print('during data acquisition for uid %s BPM intensity was < %s for %0f percent of the time -> beam lost during data acquisition: %s'%(uid[:8],bpm_int_threshold,fr*100,beam_lost))
    return beam_lost

def check_current_beam(bpm_int_threshold=-1,wait_for_beam=True,olog_reporting=False,verbose=True):
    """
    Check current beam status: 
    beam on DBPM -> go and take data
    No beam on DBPM -> beam lost? -> wait for beam back and warm up the optics
    only check for beam, not position -> if sydor ioc is not running, there is nothing we can do anyways
    olog_reporting: if True, makes olog entry for 1) beam dumped, 2) beam back on BPM
    returns: True: if beam with sufficient intensity is on the BPM, False if BPM intensity is low, but 'wait_for_beam'=False
    """
    pv_bpm_int = 'XF:11IDB-BI{XBPM:02}Ampl:CurrTotal-I'
    pv_ring_current = 'SR:OPS-BI{DCCT:1}I:Real-I'
    pv_fe_shutter = 'XF:11ID-PPS{Sh:FE}Pos-Sts'
    pv_hdm_feedback = 'XF:11IDA-OP{Mir:HDM-Ax:P}Sts:FB-Sel'
    
    ## for testing only!
    # pv_bpm_int = 'XF:11ID-CT{ES:1}ai8'
    # pv_ring_current = 'XF:11ID-CT{ES:1}ai9'
    # pv_fe_shutter = 'XF:11ID-CT{ES:1}ai10'
    # pv_hdm_feedback = 'XF:11ID-CT{ES:1}ai7'
    test_timescale=1 # factor to devide wait times by for testing -> set to 1 when testing complete!
    ##################################################################################
    
    beam_status=False
    DBPM_feedback(check_PID_loop=False) # not checking PID loop
    RE(sleep(5))
    if caget(pv_bpm_int) < bpm_int_threshold: # Beam with sufficient intensity on the BPM -> good to go!
        beam_status=True
        if verbose:
            print(time.ctime(time.time())+' checked for beam: beam intensity on BPM is above the threshold of %s mA!'%bpm_int_threshold)
        
    elif caget(pv_ring_current)<300 or caget(pv_fe_shutter)>.5: # ring current below 300mA and/or FE shutter is closed (we assume FE shutter is on 'auto-open', so if it is closed it's done intentionally by the control room)
        beam_status=False;beam_dump=True
        if wait_for_beam:
            if verbose:
                print(time.ctime(time.time())+' Looks like ring current is low and/or FE shutter closed -> likely beam has dumped!')
            if olog_reporting:
                try: # we don't want to break this over e.g. a logbook timeout
                    olog_entry(time.ctime(time.time())+' Looks like ring current is low and/or FE shutter closed -> likely beam has dumped!')
                except: print('Olog entry had been requested, but failed...')
            while beam_dump:
                if verbose:
                    print(time.ctime(time.time())+' Likely beam has dumped -> checking again for beam in 5min')
                RE(sleep(300/test_timescale))
                if caget(pv_ring_current)>300 and caget(pv_fe_shutter)<.5: #beam in the ring and FE shutter open!
                    if verbose:
                        print(time.ctime(time.time())+' Looks like beam is available, going to wait 1/2h to warm up the optics')
                    caput(pv_hdm_feedback,1) # just making sure hdm encoder feedback is on (should be handled by EPICS ioc anyways)
                    RE(sleep(1800/test_timescale)) # wait 1/2h to warm up the optics again
                    if caget(pv_ring_current)>300 and caget(pv_fe_shutter)<.5:  #beam is still available, assume the optics is warm by now
                        DBPM_feedback(check_PID_loop=False) # not checking PID loop
                        RE(sleep(5))
                        if caget(pv_bpm_int) < bpm_int_threshold:
                            beam_dump=False;beam_status=True
                            if verbose: print(time.ctime(time.time())+' checked for beam: beam intensity on BPM is above the threshold of %s mA!'%bpm_int_threshold)
                            if olog_reporting:
                                try:
                                    olog_entry(time.ctime(time.time())+' checked for beam: beam intensity on BPM is above the threshold of %s mA!'%bpm_int_threshold)
                                except: print('Olog entry had been requested, but failed...')
        else:
            beam_status=False
            if verbose: print(time.ctime(time.time())+' beam has likely dumped, but waiting for beam has not been requested...continuing.')
            if olog_reporting:
                try:
                    olog_entry(time.ctime(time.time())+' beam has likely dumped, but waiting for beam has not been requested...continuing.')
                except: print('Olog entry had been requested, but failed...')
    else: #no beam on the BPM, but ring didn't dump...don't know what to do.
        beam_status=False
        if verbose: print(time.ctime(time.time())+' no beam on the BPM, but looks like beam has not dumped...something else is wrong!')
        if olog_reporting:
            try:
                olog_entry(time.ctime(time.time())+' no beam on the BPM, but looks like beam has not dumped...something else is wrong!')
            except: print('Olog entry had been requested, but failed...')
    return beam_status

def test_beam_checks():
    try:
        check_current_beam
    T=[300,270,260]
    for t in T:
        print('set_temperature(%s,cool_ramp=2)'%t)
        RE(sleep(5))
        print('att2_set_T(.00009)')
        waiting_for_data=True
        while waiting_for_data==True:
            print('newspot()')
            check_current_beam(bpm_int_threshold=-1,wait_for_beam=True)
            print('series(expt=.1,imnum=200,....)')
            waiting_for_data = check_past_data(db[-1].start['uid'],bpm_int_threshold=-1,fraction=.05,verbose=True)
        print('\n\n\n next temperature! \n\n')

print('successfully loaded check_beam.py ....')