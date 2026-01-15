# to run macro: 
# >> %run -i /nsls2/data2/chx/shared/config/bluesky/profile_collection/usermacros/slee_macros.py

## After searching the hutchh:
# newsample(samplename)

# tweak diff.xh to have the yellow cross (beam position) at the center of the capillary
# tweak diff.yh to make sure the sample is in the beam

    
def SAXS_series(transmission=1):
    #saved as xf11id
    goto_beamline_pos(position_key='4m_in',interactive=False)
    att2.set_T(transmission)
    #newspot()
    series(det='eiger4m',expt=0.1,imnum=100, feedback_on=True,auto_compression=True,analysis='iso',comment='AUTO_COMMENT')
    #RE(sleep(10)) #hopefully not needed any longer...


def measure_transmission():
    goto_beamline_pos(position_key='4m_in',interactive=False)
    caput('XF:11IDB-ES{Det:Eig4M}cam1:AcquireTime',1)
    caput('XF:11IDB-ES{Det:Eig4M}cam1:AcquirePeriod',1)
    caput('XF:11IDB-ES{Det:Eig4M}cam1:NumImages',1)
    att2.set_T(4.8e-5)
    RE(mvr(saxs_bst.y1,10))
    RE(count([eiger4m_single]),Measurement='Transmission - sample in '+RE.md['sample'])
    sam_position=diff.xh.user_readback.value
    RE(mv(diff.xh,0)) #this should be off the sample
    RE(count([eiger4m_single]),Measurement='Transmission - sample out '+RE.md['sample'])
    RE(mv(diff.xh,sam_position))
    goto_beamline_pos(position_key='saxs_bst_in',interactive=False)
    att2.set_T(1)
    transmission=db[-2].table().eiger4m_single_stats1_total[1]/db[-1].table().eiger4m_single_stats1_total[1]
    RE.md['sample transmission']=float(transmission)
    message = " Transmission for sample "+RE.md['sample']+" =%s"%transmission
    olog_entry(message)
    print(message)


#def newspot(y_step=.1):
#    # x row start and end defined here
#    y_start=-4;y_end=-1
#    
#    if diff.yh.user_readback.value < y_end:
#        RE(mvr(diff.yh,y_step))
#    else:
#        RE(mv(diff.yh,y_start))
#
#        RE(mvr(diff.xh,.1))


def newspot(x_step=0.1,y_step=0.1):
    #covering a 'top of center' rectangular area on the flat cell holder
    y_center = -5.9
    x_center = 0.5
    if  diff.xh.user_readback.value > x_center-0.55 and diff.xh.user_readback.value < x_center+0.55:
        RE(mvr(diff.xh,x_step))
    else:
        RE(mvr(diff.yh,y_step))
        x_step=-x_step
        RE(mvr(diff.xh,x_step))
    if diff.yh.user_readback.value > y_center:
        RE(mv(diff.yh,y_center-0.5))

def pellet() :
    y_pos=-2
    RE(mv(diff.yh,y_pos))

def sup() :
    y_pos=-10
    RE(mv(diff.yh,y_pos))

def xpos(step):
    RE(mvr(diff.xh,step))

def ypos(step):
    RE(mvr(diff.yh,step))

def newsample(samplename):
    RE.md['sample']=samplename
    DBPM_feedback(verbose=True)
    print("Check the feedback, you should be ready to go!")


def SAXS_sequence(repeats,transmission):
    #RE.md['auto_pipeline']='SAXS_auto' #Do not need anymore since analysis becomes faster
    att2.set_T(transmission)
    
    #measure_transmission()   
    for i in range(repeats):
        series(expt=0.1,imnum=100,comment='',feedback_on=True,auto_compression=True)
        newspot()

    for i in range(repeats):
        series(expt=0.01,imnum=100,comment='',feedback_on=True,auto_compression=True)
        newspot()
    RE.md['auto_pipeline']='XPCS_SAXS_auto'


def runSAXS(repeats=8,transmission=1):
    foe_sh.open()  #just in case... :)
    #RE(mv(diff.yh,3.2))  # moving to Y-start
    print('Running SAXS protocol at 3.xx m for sample: '+RE.md['sample'])
    olog_entry(" New sample: "+RE.md['sample']+" repeats="+str(repeats))
    
    for i in range(repeats):
        only_SAXS(transmission=transmission)
    #caput('XF:11IDA-OP{Mir:HDM-Ax:P}Sts:FB-Sel',1)
    att2.set_T(1)

def XPCS_sequence():
    #1st run
    att2.set_T(1)
    series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.19)
    series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.036)
    #series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.0068)
    #series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()

    att2.set_T(1)
    series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()    
    att2.set_T(0.19)
    series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.036)
    series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    #att2.set_T(0.0068)
    #series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.0068/5)
    #series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()

    #att2.set_T(1)
    #series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    att2.set_T(0.19)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.036)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    #att2.set_T(0.0068/5)
    #series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()

    #att2.set_T(1)
    #series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.19)
    #series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    att2.set_T(0.036)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068/5)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()


def XPCS_temp():
    att2.set_T(1)
    series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068/5)
    series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()

    att2.set_T(1)
    series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()    
    att2.set_T(0.0068/5)
    series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()

    att2.set_T(1)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068/5)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()

    att2.set_T(1)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068/5)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()

def area_scan(T=0.19, E=.007, n_points = 500, x_step = 0.05, y_step = 0.05, width = 0.2):
    #covering a 'top of center' rectangular area on the flat cell holder
    start_time = time.perf_counter()
    
    print("Initial XPCS measurement at the center")
    att2.set_T(T)
    series(expt=E,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)

    print("Moving the beam to the top left corner of the exposed area")
    x_center = diff.xh.user_readback.value
    y_center = diff.yh.user_readback.value
    RE(mv(diff.xh,x_center-(width/2), diff.yh, y_center-(width/2)))
    buffer=y_step/10

    print("Scanning starts")
    for i in range (n_points-1):
        if  diff.xh.user_readback.value+x_step > x_center-((width/2)+buffer) and diff.xh.user_readback.value+x_step < x_center+((width/2)+buffer):
            fast_sh.open();RE(sleep(E*750));fast_sh.close()
            RE(mvr(diff.xh,x_step))
            print(f"{i+1} of {((width/y_step)+1)**2} - {((i+1)/((width/y_step)+1)**2)*100} % completed")
        else:
            fast_sh.open();RE(sleep(E*750));fast_sh.close()
            RE(mvr(diff.yh,y_step))
            x_step=-x_step
            print(f"{i+1} of {((width/y_step)+1)**2} - {((i+1)/((width/y_step)+1)**2)*100} % completed")
        if diff.yh.user_readback.value > y_center+((width/2)+buffer):
            print(f"All area covered. Total {i+1} exposure points")
            break

    print("Final XPCS measurement at the center")
    RE(mv(diff.xh,x_center, diff.yh, y_center)) 
    series(expt=E,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)

    end_time = time.perf_counter()
    elapsed_seconds = int(end_time - start_time)
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_seconds))
    print(f"Total exposure time is {formatted_time}")
    