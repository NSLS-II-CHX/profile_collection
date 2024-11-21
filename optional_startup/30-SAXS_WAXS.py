from epics import caput,caget

scan_id_pv = 'XF:11ID-CT{ES:1}ai3'
scan_ID = EpicsSignal(scan_id_pv, name='scan_ID')

SAXS_done_pv='XF:11ID-CT{M3}bi3'
caget(SAXS_done_pv)
caput('XF:11ID-CT{M3}bi3.DESC','SAXS done')
WAXS_done_pv='XF:11ID-CT{M3}bi4'
caget(WAXS_done_pv)
caput('XF:11ID-CT{M3}bi4.DESC','WAXS done')

class Printer_3D(Device):
    "4 axes for the 3D printer"
    x_bed = Cpt(EpicsMotor,'Bed:X}Mtr')
    z_bed = Cpt(EpicsMotor,'Bed:Z}Mtr')
    x_head = Cpt(EpicsMotor,'Head:X}Mtr')
    y_head = Cpt(EpicsMotor,'Head:Y}Mtr')

printer = Printer_3D('XF:11IDM3-3D{',name='printer')

def mcount(detector_list,imnum=[1],exposure_time=[1],acquire_period=['auto']):
    """
    wrapper for multi-BlueSky session count: keep track of current scan_id as an EPICS PV that can be shared between BlueSky sessions
    can set individual number of images, exposure time and acquire period for a list of detectors
    TODO: check of input arguments for consistency and format, option for just keeping current settings on detectors
    """
    last_scan_id = int(max(scan_ID.get(),RE.md['scan_id']))
    yield from mv(scan_ID,last_scan_id+1)
    new_scan_id = int(last_scan_id+1)
    print('synchronizing BlueSky sessions: last scan ID: %s -> next scan ID: %s'%(last_scan_id,new_scan_id))
    RE.md['scan_id'] = last_scan_id
    
    # setting up the detectors:
    for ii,i in enumerate(detector_list):
        detector=i
        if acquire_period[ii] == 'auto':
            acquire_period[ii] = exposure_time[ii]+.01
        i.cam.acquire_time.value=exposure_time[ii]       # setting up exposure for eiger500k/1m/4m_single
        i.cam.acquire_period.value=acquire_period[ii]
        i.cam.num_images.value=imnum[ii]
        if detector == pilatus800: # Pilatus doesn't seem to capture acquisition parameters in start document...
            RE.md['pil800k_exposure_time']=exposure_time[ii]
            RE.md['pil800k_acquire_period']=acquire_period[ii]
            RE.md['pil800k_imnum']=imnum[ii]

    yield from count(detector_list)
    
def mdscan(detectors, *args, num=None, per_step=None, md=None):
    """
    wrapper for multi-BlueSky session dscan: keep track of current scan_id as an EPICS PV that can be shared between BlueSky sessions
    """
    last_scan_id = int(max(scan_ID.get(),RE.md['scan_id']))
    yield from mv(scan_ID,last_scan_id+1)
    new_scan_id = int(last_scan_id+1)
    print('synchronizing BlueSky sessions: last scan ID: %s -> next scan ID: %s'%(last_scan_id,new_scan_id))
    RE.md['scan_id'] = last_scan_id
    yield from dscan(detectors, *args, num=None, per_step=None, md=None)
    
def mseries(det='eiger4m',shutter_mode='single',expt=.1,acqp='auto',imnum=5,comment='', feedback_on=False, PV_trigger=False, position_trigger=False ,analysis='', use_xbpm=False, OAV_mode='none',auto_compression=False,md_import={},auto_beam_position=True):
    """
    wrapper for multi-BlueSky session series: keep track of current scan_id as an EPICS PV that can be shared between BlueSky sessions
    """
    last_scan_id = int(max(scan_ID.get(),RE.md['scan_id']))
    RE(mv(scan_ID,last_scan_id+1))
    new_scan_id = int(last_scan_id+1)
    print('synchronizing BlueSky sessions: last scan ID: %s -> next scan ID: %s'%(last_scan_id,new_scan_id))
    RE.md['scan_id'] = last_scan_id
    series(det=det,shutter_mode=shutter_mode,expt=expt,acqp=acqp,imnum=imnum,comment=comment,feedback_on=feedback_on,PV_trigger=PV_trigger,position_trigger=position_trigger,analysis=analysis,use_xbpm=use_xbpm,OAV_mode=OAV_mode,auto_compression=auto_compression,md_import=md_import,auto_beam_position=auto_beam_position)
    
def triggered_WAXS(detector_list,imnum=[1],exposure_time=[1],acquire_period=['auto'],delay=0,comment='AUTO',post_series=0, post_acquire_period=['auto'],post_imnum=[100],post_exposure_time=[.1],post_att=None,long_series=False):
    RE.md['col_uid'] = collection_uid.get_col_uid()
    pil800k_shutter_mode(0)
    caput(WAXS_done_pv,0)
    trigger_signal_pv = 'XF:11ID-CT{M3}bi2' # printer setup   
    #trigger_signal_pv = 'XF:11ID-CT{ES:1}bi1'
    if comment == 'AUTO':
        com='WAXS expt: %s  acquire period: %s frames: %s'%(exposure_time[0],acquire_period[0],imnum[0])
    else:
        com=comment
    print('waiting for trigger signal....')
    while caget(trigger_signal_pv) <.5:
        RE(sleep(.5))
    RE(sleep(delay)) 
    RE(mcount(detector_list=detector_list,imnum=imnum,exposure_time=exposure_time,acquire_period=acquire_period), Measurement = com)
    caput(trigger_signal_pv,0)
    RE(sleep(0.5))
    if comment == 'AUTO':
        com='WAXS expt: %s  acquire period: %s frames: %s'%(post_exposure_time[0],post_acquire_period[0],post_imnum[0])
    else:
        com=comment
    if post_att != None:
        att2.set_T(post_att)
    for p in range(post_series):
         #pil800k_shutter_mode(1)
         #att2.set_T(.19)
         if caget(SAXS_done_pv):
            RE(mvr(printer.x_bed,.1))
         RE(mcount(detector_list,post_imnum,post_exposure_time,post_acquire_period), Measurement = com)
    if long_series:
        com = 'WAXS long post series expt=2.5 imnum=240 transmission=.036'
        if caget(SAXS_done_pv):
            RE(mvr(printer.x_bed,.1))
            att2.set_T(.02)
            RE(mcount(detector_list,[240],[2.5],['auto']), Measurement = com)
    
    caput(WAXS_done_pv,1)
    caput('XF:11IDB-ES{Det:P800k}cam1:NumImages',1)
    if caget(SAXS_done_pv):
        fast_sh.close()
        pil800k_shutter_mode(1)
    else: 
        print('waiting for SAXS data to finish to re-set WAXS shutter mode')
        while caget(SAXS_done_pv) <1:
            RE(sleep(1))
        pil800k_shutter_mode(1)

def WAXS_single_image():
    pil800k_shutter_mode(1)
    caput('XF:11IDB-ES{Det:P800k}cam1:NumImages',1)
    RE(mcount([pilatus800],exposure_time=[.1],acquire_period=[.15]))
    pil800k_shutter_mode(0)



def triggered_WAXS_continuous(detector_list,imnum=[1],exposure_time=[1],acquire_period=['auto'],delay=0,comment=None):
    while(True):
        triggered_WAXS(detector_list,imnum,exposure_time,acquire_period,delay,comment)
    

def pil800k_shutter_mode(mode):
    assert mode in [0,1] ,'mode must be 0 (no shutter) or 1 (EPICS signal)'
    caput('XF:11IDB-ES{Det:P800k}cam1:ShutterMode',mode)

    
# WAXS_acquisitions:
# homopolymer MI35 'slow'
# triggered_WAXS(detector_list=[pilatus800],imnum=[400],exposure_time=[.1],acquire_period=['auto'],delay=0,post_series=3, post_acquire_period=[
#    ...: 'auto'],post_imnum=[200],post_exposure_time=[.1])
# homopolymer MI35 'fast'
# triggered_WAXS(detector_list=[pilatus800],imnum=[400],exposure_time=[.035],acquire_period=['auto'],delay=0,post_series=2, post_acquire_period=[
#    ...: 'auto'],post_imnum=[200],post_exposure_time=[.1])
# Homo+PPMA+0.5 vol% SI
#triggered_WAXS(detector_list=[pilatus800],imnum=[800],exposure_time=[.045],acquire_period=['auto'],delay=0,post_series=2, post_acquire_perio
#     ...: d=['auto'],post_imnum=[200],post_exposure_time=[.3])

sample_string_PV='XF:11IDM-M3{IO:1}DI:5-Sts.DESC'
def collect_waxs(expt=.1,imnum=1,comment=''):
    RE.md['sample']=caget(sample_string_PV)
    RE(mcount([pilatus800],exposure_time=[expt],imnum=[imnum]),Measurement='comment')
    