# to run macro: 
# >> %run -i /XF11ID/analysis/2024_2/slee/slee_macros.py

## To define a new sample
#RE.md['sample']='sample name'

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


def newspot(y_step=.1):
    # x row start and end defined here
    y_start=-1.8;y_end=-0.2
    
    if diff.yh.user_readback.value < y_end:
        RE(mvr(diff.yh,y_step))
    else:
        RE(mv(diff.yh,y_start))
        RE(mvr(diff.xh,.1))

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
    DBPM_feedback()
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
    #att2.set_T(0.19)
    #series(expt=.00134,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
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
    #att2.set_T(0.036)
    #series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.0068)
    #series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.0068/5)
    #series(expt=.007,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()

    att2.set_T(1)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.19)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.036)
    series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    #att2.set_T(0.0068)
    #series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    #att2.set_T(0.0068/5)
    #series(expt=.035,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()

    #att2.set_T(1)
    #series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()
    att2.set_T(0.19)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.036)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    att2.set_T(0.0068)
    series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    newspot()
    #att2.set_T(0.0068/5)
    #series(expt=.175,acqp='auto',imnum=750,comment='', feedback_on=True,auto_compression=True)
    #newspot()


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