from epics import caput,caget
#sys.path.insert(0, "/nsls2/data/chx/shared/CHX_Software/packages/standard_functions/")
#from standard_functions import save_pickle, load_pickle

try:
    trigger_signal_pv = 'XF:11ID-CT{M3}bi2' # trigger signal from printer setup
    caget(trigger_signal_pv)
    SAXS_done_pv='XF:11ID-CT{M3}bi3'
    caget(SAXS_done_pv)
    caput('XF:11ID-CT{M3}bi3.DESC','SAXS done')
    WAXS_done_pv='XF:11ID-CT{M3}bi4'
    caget(WAXS_done_pv)
    caput('XF:11ID-CT{M3}bi4.DESC','WAXS done')
    BL_busy_pv = 'XF:11ID-CT{M3}bi7'
    caget(BL_busy_pv)
    caput('XF:11ID-CT{M3}bi7.DESC','BL busy')
    print('Successfully defined and connected all PVs for status and trigger signals.')
except:
    print('Failed defining PVs for status and trigger signals.')

def wcount(detector_list=[pilatus800],imnum=[1],exposure_time=[1],acquire_period=['auto']):
    """
    wrapper for Pilatus800k count, add some detector specific metadata
    can set individual number of images, exposure time and acquire period for a list of detectors
    TODO: check of input arguments for consistency and format, option for just keeping current settings on detectors
    """
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
    if detector == pilatus800:
        RE.md.pop('pil800k_exposure_time')
        RE.md.pop('pil800k_acquire_period')
        RE.md.pop('pil800k_imnum')

def insitu_printing_individualized_waxs(detector_list,sample=None, multithreading=True, delay=0):
    # need to update collection_uid if not done already...how would we know?
    # most likely it has been updated: xpcs part will do this before telling the printer that it is ready for a trigger AND this macro doe not write anything BEFORE getting the trigger signal from the printer -> should work fine :-)
    param_dict = load_pickle('/nsls2/data/chx/shared/config/bluesky/profile_collection/usermacros/printing_database.pkl',verbose=True)
    # if multithreading, detector will be staged to NOT control the fast shutter; fast shutter will close after last post-series!
    if multithreading:
        pil800k_shutter_mode(0)
        caput(WAXS_done_pv,0)
    if param_dict[sample]['WAXS']['in-situ'][0] is not None: # share attenuators with WAXS data acquisition...only one of the two should control the attenutators
        att2.set_T(param_dict[sample]['WAXS']['in-situ'][0])
    RE.md['insitu_waxs']=True
    print('waiting for trigger signal....')
    while caget(trigger_signal_pv) <.5:
        RE(sleep(.5))
    RE(sleep(delay))
    spot_uid,=RE(wcount(detector_list=detector_list,imnum=[param_dict[sample]['WAXS']['in-situ'][2]],exposure_time=[param_dict[sample]['WAXS']['in-situ'][1]],acquire_period=['auto']),Measurement = '%s WAXS in-situ  %ss x %sfr'%(sample,param_dict[sample]['WAXS']['in-situ'][1],param_dict[sample]['WAXS']['in-situ'][2]))
    RE.md['transmission_dict'].update({spot_uid:{'pos':printer.x_bed.user_readback.get()}})
    caput(trigger_signal_pv,0)
    RE(sleep(0.5))
    RE.md['insitu_waxs']=False
    for kk,k in enumerate(list(param_dict[sample]['WAXS']['post'].keys())):
         if caget(SAXS_done_pv):
            RE(mvr(printer.x_bed,.1))
         spot_uid,=RE(wcount(detector_list=detector_list,imnum=[param_dict[sample]['WAXS']['post'][k][2]],exposure_time=[param_dict[sample]['WAXS']['post'][k][1]],acquire_period=['auto']),Measurement = '%s WAXS post #%s  %ss x %sfr'%(sample,kk+1,param_dict[sample]['WAXS']['post'][k][1],param_dict[sample]['WAXS']['post'][k][2]))
    RE.md['transmission_dict'].update({spot_uid:{'pos':printer.x_bed.user_readback.get()}})
    caput(WAXS_done_pv,1)
    caput('XF:11IDB-ES{Det:P800k}cam1:NumImages',1)
    if caget(SAXS_done_pv):
        fast_sh.close()
        caput(BL_busy_pv,0)
        collection_uid.reset_col_uid()
    RE(sleep(2))
    if caget(SAXS_done_pv):
        fast_sh.close()
        caput(BL_busy_pv,0)
        collection_uid.reset_col_uid()

# def triggered_WAXS(detector_list,imnum=[1],exposure_time=[1],acquire_period=['auto'],delay=0,comment=None,post_series=0):
#     # need to update collection_uid if not done already...how would we know?
#     pil800k_shutter_mode(0)
#     caput(WAXS_done_pv,0)
#     trigger_signal_pv = 'XF:11ID-CT{M3}bi2' # printer setup   
#     #trigger_signal_pv = 'XF:11ID-CT{ES:1}bi1'
#     print('waiting for trigger signal....')
#     while caget(trigger_signal_pv) <.5:
#         RE(sleep(.5))
#     RE(sleep(delay)) 
#     RE(wcount(detector_list=detector_list,imnum=imnum,exposure_time=exposure_time,acquire_period=acquire_period),Measurement = comment)
#     caput(trigger_signal_pv,0)
#     RE(sleep(0.5))
#     for p in range(post_series):
#          if caget(SAXS_done_pv):
#             RE(mvr(printer.x_bed,.1))
#          RE(mcount([pilatus800],imnum=[100],exposure_time=[.1],acquire_period=[.105]))
#     caput(WAXS_done_pv,1)
#     pil800k_shutter_mode(1)
#     caput('XF:11IDB-ES{Det:P800k}cam1:NumImages',1)
#     if caget(SAXS_done_pv):
#         fast_sh.close()

def WAXS_single_image():
    pil800k_shutter_mode(1)
    caput('XF:11IDB-ES{Det:P800k}cam1:NumImages',1)
    RE(wcount([pilatus800],exposure_time=[.1],acquire_period=[.15]))
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
    
