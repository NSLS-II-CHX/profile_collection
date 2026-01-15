99-userpv_mag='XF:11IDM-M3{IO}DO:1-Cmd'
pv_mag_act='XF:11IDM-M3{IO:2}DO:1-Cmd'
pv_valve_act='XF:11IDM-M3{IO:2}DO:4-Cmd'
pv_cart_act='XF:11IDM-M3{IO:2}DO:3-Cmd'



z_bed=71. # 126 (printing)
y_head_print=17.0
y_head_assembly=26.1
x_head_assembly=573.58


x_head_start=452.
x_bed_start=120.

prime_x_bed=120.
prime_x_head=573.
prime_z_bed=122.
prime_y_head=60.

def prime_Loc(prime_time=5):
    RE(mv(printer.y_head,80))
    RE(mv(printer.z_bed,prime_z_bed))
    RE(mv(printer.x_bed,prime_x_bed))
    RE(mv(printer.x_head,prime_x_head))
    RE(mv(printer.y_head,prime_y_head))
    deposition_Loc(timer=prime_time)
    RE(sleep(prime_time+2))

def goto_deposition_start():
    RE(mv(printer.y_head,80))
    RE(mv(printer.z_bed,z_bed))
    RE(mv(printer.x_bed,x_bed_start))
    RE(mv(printer.x_head,x_head_start))

y_head_printing_p1=66.45 ### set nozzle height for printing here!!
x_head_beam=412.

def new_platform_spot(offset=35):   ### for RAMA
   RE(mv(printer.y_head,80))
   RE(mv(printer.x_head,x_head_beam))
   RE(mvr(printer.x_bed,offset))
   #RE(mv(printer.y_head,y_head_printing_p1))
   


position_dict={'z_pos':{'p1':128.,'p2':58.},'y_head_pos':{'p1':58.35,'p2':58.35},'x_head_beam_pos':447.5,'y_pos':{'p1':-21.9,'p2':-21.4}}

def goto_platform(platform='p1'):
    printer.y_head.velocity.set(7);printer.z_bed.velocity.set(5)
    RE(mv(printer.y_head,80)) # move head up, so there is no change to have a collision
    RE(mv(printer.z_bed,position_dict['z_pos'][platform]))
    RE(mv(printer.y_head,position_dict['y_head_pos'][platform]))
    #RE(mv(diff.yh,position_dict['y_pos'][platform]))

def setup_magnet():
    caput(pv_mag_act+'.DESC','magnet acutator')
    caput(pv_mag+'.DESC','electro magnet')

def setup_deposition_trigger():
    caput('XF:11ID-CT{M3}DB:1userCalcEnable.VAL',1)
    caput('XF:11ID-CT{M3}DB:1userCalc1.INAN','XF:11ID-CT{M3}cdt1:start')
    caput('XF:11ID-CT{M3}DB:1userCalc1.SCAN',2)
    caput('XF:11ID-CT{M3}DB:1userCalc1.OUTN',pv_valve_act)
    caput('XF:11ID-CT{M3}DB:1userCalc1.CALC','A')
    caput(pv_valve_act+'.DESC','LOCTITE valve')

def setup_cartridge_trigger():
    caput('XF:11ID-CT{M3}DB:1userCalcEnable.VAL',1)
    caput('XF:11ID-CT{M3}DB:1userCalc3.INAN','XF:11ID-CT{M3}cdt3:start')
    caput('XF:11ID-CT{M3}DB:1userCalc3.SCAN',2)
    caput('XF:11ID-CT{M3}DB:1userCalc3.OUTN','XF:11IDM-M3{IO:2}DO:3-Cmd')
    caput('XF:11ID-CT{M3}DB:1userCalc3.CALC','A')
    caput('XF:11IDM-M3{IO:2}DO:3-Cmd.DESC','LOCTITE cartridge')


def deposition_Loc(timer=5):
    caput('XF:11ID-CT{M3}cdt1:start',0);caput('XF:11ID-CT{M3}cdt3:start',0);
    caput('XF:11ID-CT{M3}cdt1:setTimeSec',timer);caput('XF:11ID-CT{M3}cdt3:setTimeSec',timer)
    caput('XF:11ID-CT{M3}cdt1:start',1);caput('XF:11ID-CT{M3}cdt3:start',1)

def setup_BL_trigger():
    caput('XF:11ID-CT{M3}DB:1userCalcEnable.VAL',1)
    caput('XF:11ID-CT{M3}DB:1userCalc2.INAN','XF:11ID-CT{M3}cdt2:start')
    caput('XF:11ID-CT{M3}DB:1userCalc2.SCAN',2)
    caput('XF:11ID-CT{M3}DB:1userCalc2.OUTN','XF:11ID-CT{M3}bi2')
    caput('XF:11ID-CT{M3}DB:1userCalc2.CALC','!A')
    caput('XF:11ID-CT{M3}bi2.DESC','BL trigger')

def setup_BL_PVs():
    caput('XF:11ID-CT{M3}bi5.DESC','BL monitoring')
    caput('XF:11ID-CT{M3}bi6.DESC','BL ready for trigger signal')

def BL_trigger_timer(timer=5):
    caput('XF:11ID-CT{M3}cdt2:start',0)
    caput('XF:11ID-CT{M3}cdt2:setTimeSec',timer)
    caput('XF:11ID-CT{M3}cdt2:start',1)

def platform_zero():
    RE.md['platform 0 position']=diff.yh.user_readback.value

def set_platform_height(height):
    zero_position=RE.md['platform 0 position']
    RE(mv(diff.yh,zero_position-height))
    RE.md['beam position relative to platform']=height

# prep for deposition:
def prep_for_deposition():
    #caput(pv_mag,0)
    printer.y_head.velocity.value=9
    RE(mv(printer.y_head,70))
    caput(pv_mag_act,0)
    caput(pv_valve_act,0)
    caput(pv_cart_act,0)
    printer.x_head.velocity.value=100;RE(mv(printer.x_head,x_head_start))
    printer.z_bed.velocity.value=5;RE(mv(printer.z_bed,z_bed))
    printer.x_bed.velocity.value=20;RE(mv(printer.x_bed,x_bed_start))

def goto_pool():   ## for RAMA
    RE(mv(printer.y_head,80))
    RE(mv(printer.z_bed,90))
    #printer.y_head.velocity.set(9)
    RE(mv(printer.x_bed,-40))
    RE(mv(printer.y_head,62))

def return_from_pool(x_position):  ## for RAMA!
   printer.y_head.velocity.set(100)
   RE(mv(printer.y_head,80))
   RE(mv(printer.z_bed,z_bed))
   RE(mv(printer.x_bed,x_position))

# deposition
def deposition(speed=7.,dist1=4,dist2=31,pre_depos=0,post_depos=-1,y_head_print=y_head_print,x_head_start=x_head_start):
    # reset trigger signals    
    caput('XF:11ID-CT{M3}bi2',0);caput('XF:11ID-CT{M3}bi1',0)
    # goto starting position for deposition
    printer.x_head.velocity.value=20
    printer.y_head.velocity.value=5
    RE(mv(printer.y_head,y_head_print))
    RE(mv(printer.x_head,x_head_start))
    printer.x_head.velocity.value=speed
    curr_pos=caget('XF:11IDM3-3D{Head:X}Mtr.RBV')
    #check if BL is ready
    pc=0
    while caget('XF:11ID-CT{M3}bi5')!=1:
        if pc ==0:
            print('waiting for BL to monitor')
        RE(sleep(.5));pc=1
    # tell BL to grab metadata
    caput('XF:11ID-CT{M3}bi1.DESC','write MD');caput('XF:11ID-CT{M3}bi1',1)
    # wait for BL to be ready for trigger signal
    pc=0
    while caget('XF:11ID-CT{M3}bi6')!=1:
        if pc ==0:
            print('waiting for BL to get ready for trigger signal')
        RE(sleep(.5));pc=1
    # start deposition
    depos_time=(dist1+dist2)/speed+pre_depos-np.abs(post_depos) # total time for deposition
    if pre_depos>0: # need to start deposition first and than start moving
        deposition_Loc(timer=depos_time)
        RE(sleep(pre_depos))
        caput('XF:11IDM3-3D{Head:X}Mtr.VAL',(curr_pos+dist1+dist2))
        BL_trigger_timer(timer=dist1/speed)
    else:
        caput('XF:11IDM3-3D{Head:X}Mtr.VAL',(curr_pos+dist1+dist2))
        BL_trigger_timer(timer=dist1/speed)
        RE(sleep(pre_depos))
        deposition_Loc(timer=depos_time)
    printer.x_head.velocity.value=50
    

def assembly():
    printer.y_head.velocity.value=5;RE(mv(printer.y_head,y_head_assembly+2.))
    xoff= printer.x_bed.position-x_bed_start   # offset because of moving to new spot inbetween datasets
    printer.x_head.velocity.value=20;RE(mv(printer.x_head,x_head_assembly+xoff))
    caput(pv_mag_act,1);RE(sleep(1))
    printer.y_head.velocity.value=1
    RE(mv(printer.y_head,y_head_assembly))
    caput(pv_mag,0)
    RE(sleep(2))
    caput(pv_mag_act,0)
    printer.y_head.velocity.value=5

# deposition using Ultimus-V as printhead -> for Rama!
def deposition_ultimus_printer(speed=10,dist1=0,dist2=90,pre_depos=1,post_depos=1,pressure=14,nozzle_height=y_head_printing_p1):
    """
    Macro to deposit single filaments using the Ultimus-V as printhead

    deposition_ultimus_printer((speed=5.,dist1=1,dist2=26,pre_depos=1,post_depos=-.5,nozzle_height=y_head_printing_p1)

    speed: speed at which the printhead moves
    dist1: distance to move before sending trigger signal to beamline
    dist2: distance to move after sending trigger singal to beamline -> total length of filament is dist1=dist2
    pre_depos: extrusion time prior to start moving the printhead (priming), pre_depos is >0 or it is ignored
    post_depos: extrusion time after the printhead has completed it's move (post_depos <0: stop prior to move complete, e.g. to avoid puddle at the end of filament
    pressure: extrusion pressure from the DISPENSER (in current units set on the device), NOT the boosted pressure when using a high pressure adapter

    Note: use new_platform_spot(offset) to go to a fresh spot on the printing platform
    """
    minimum_trigger_delay = 3 # minimum time needed for triggering the detecor, engaging feedback, etc.
    # If new_platform_spot() was used to move to a new spot, the printhead should be raised, but check just in case...
    caput('XF:11ID-CT{M3}ai1',pressure)
    if printer.y_head.user_readback.value < nozzle_height+10: #looks like the printhead is not raised, at least not far enought to safely move in x-direction
        RE(mv(printer.y_head,nozzle_height+10))
    RE(mv(printer.x_head,x_head_beam-(dist1+dist2)*.66)) #that's the start position for the deposition
    RE(mv(printer.y_head,nozzle_height))
    
    # reset trigger signals    
    caput('XF:11ID-CT{M3}bi2',0);caput('XF:11ID-CT{M3}bi1',0)
    printer.x_head.velocity.value=speed # set printhead speed
 
    #check if BL is ready
    pc=0
    while caget('XF:11ID-CT{M3}bi5')!=1:
        if pc ==0:
            print('waiting for BL to monitor')
        RE(sleep(.5));pc=1
    # tell BL to grab metadata
    caput('XF:11ID-CT{M3}bi1.DESC','write MD');caput('XF:11ID-CT{M3}bi1',1)
    # wait for BL to be ready for trigger signal
    pc=0
    while caget('XF:11ID-CT{M3}bi6')!=1:
        if pc ==0:
            print('waiting for BL to get ready for trigger signal')
        RE(sleep(.5));pc=1
    # start deposition
    total_deposition_time=((dist1+dist2)/speed+pre_depos+post_depos)
    if dist1/speed <= minimum_trigger_delay: # need to trigger detector FIRST, before doing anyting else...
        caput('XF:11ID-CT{M3}bi2',1)
        RE(sleep(minimum_trigger_delay-pre_depos))
    #mk1_250_deposition(nozzle_size=nozzle_size,filament_size=1.68,speed=speed,road_length=dist1+dist2,temperature=temperature,verbose=True)
    ultimus_deposition(t=total_deposition_time,pressure=pressure)
    RE(sleep(pre_depos))
    
    if np.floor(dist1/speed) > minimum_trigger_delay:    
        BL_trigger_timer(timer=np.floor(dist1/speed))
    #else:
        RE(sleep(dist1/speed))
    #    caput('XF:11ID-CT{M3}bi2',1)
    printer.x_head.set(printer.x_head.user_readback.get()+dist1+dist2)
    RE(sleep((dist1+dist2)/speed))
    #ultimus_pressure(P=0)
    RE(mvr(printer.y_head,30)) # raise printhead at the end of deposition
    printer.x_head.velocity.value=20 # set speed to something sensible 


# deposition with mk1 printhead
def deposition_mk1_printer(speed=5.,dist1=1,dist2=26,pre_depos=1,post_depos=-.5,temperature=40,nozzle_height=y_head_printing_p1,nozzle_size=1.2):
    caput('XF:11ID-CT{M3}ai1',nozzle_size)
    RE(mvr(printer.x_head,-1*(dist1+dist2)*.66))
    RE(mv(printer.y_head,nozzle_height))
# reset trigger signals    
    caput('XF:11ID-CT{M3}bi2',0);caput('XF:11ID-CT{M3}bi1',0)
   
    printer.x_head.velocity.value=speed
    #curr_pos=caget('XF:11IDM3-3D{Head:X}Mtr.RBV')
    #check if BL is ready
    pc=0
    while caget('XF:11ID-CT{M3}bi5')!=1:
        if pc ==0:
            print('waiting for BL to monitor')
        RE(sleep(.5));pc=1
    # tell BL to grab metadata
    caput('XF:11ID-CT{M3}bi1.DESC','write MD');caput('XF:11ID-CT{M3}bi1',1)
    # wait for BL to be ready for trigger signal
    pc=0
    while caget('XF:11ID-CT{M3}bi6')!=1:
        if pc ==0:
            print('waiting for BL to get ready for trigger signal')
        RE(sleep(.5));pc=1
    # start deposition (looks like it takes ~1s for the printhead to start printing...)
    mk1_250_deposition(nozzle_size=nozzle_size,filament_size=1.68,speed=speed,road_length=dist1+dist2,temperature=temperature,verbose=True)
    RE(sleep(pre_depos))
    #mk1_250_prime(volume=1000,delay=0,speed=1000,temperature=temperature)
    if np.floor(dist1/speed) >1:    
        BL_trigger_timer(timer=np.floor(dist1/speed))
    else:
        RE(sleep(dist1/speed))
        caput('XF:11ID-CT{M3}bi2',1)
    printer.x_head.set(printer.x_head.user_readback.get()+dist1+dist2+speed) # add an extra 1s move
    printer.x_head.velocity.value=20
    RE(sleep((dist1+dist2)/speed))
    RE(mvr(printer.y_head,30))

def brushing(reps=2):
    printer.y_head.velocity.set(9)
    printer.z_bed.velocity.set(5)
    printer.x_bed.velocity.set(50)
    printer.x_head.velocity.set(50)
    # capture current position -> return to here
    y_head_cur = printer.y_head.user_readback.get()
    z_bed_cur = printer.z_bed.user_readback.get()
    x_bed_cur = printer.x_bed.user_readback.get()
    x_head_cur = printer.x_head.user_readback.get()
    # go to brush
    
    RE(mv(printer.z_bed,156.5))
    RE(mv(printer.y_head,70)) #70
    RE(mv(printer.x_bed,-100))
    RE(mv(printer.x_head,447.5))
    RE(mv(printer.y_head,66))
    # brushing:
    for i in range(reps):
        RE(mvr(printer.x_head,35))
        RE(mvr(printer.x_head,-35))
    # go back to where we came from
    RE(mv(printer.y_head,100))
    RE(mv(printer.z_bed,z_bed_cur))
    RE(mv(printer.x_bed,x_bed_cur))
    RE(mv(printer.x_head,x_head_cur))
    RE(mv(printer.y_head,y_head_cur))
    
    
    