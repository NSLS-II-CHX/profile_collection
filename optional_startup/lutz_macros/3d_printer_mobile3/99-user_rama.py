## to reload macro:  

z_bed=127. # 126 (printing)
#y_head_print=64.0
#x_head_start=452.
x_bed_start=-80.
def goto_printbed_start():      ### starting position on x-bed e.g. after changing Kapton tape
    RE(mv(printer.y_head,80))
    RE(mv(printer.x_bed,x_bed_start,printer.z_bed,z_bed))
    

def change_tape():            ### convenient position to change the Kapton tape
    RE(mv(printer.y_head,149))
    RE(mv(printer.x_bed,x_bed_start+500,printer.z_bed,160))


#def goto_deposition_start():
#    RE(mv(printer.y_head,80))
#    RE(mv(printer.z_bed,z_bed))
#    RE(mv(printer.x_bed,x_bed_start))
#    RE(mv(printer.x_head,x_head_start))

y_head_printing_p1=56.2### set nozzle height for printing here!! IMPORTANT  !!!!!!!
print('macro 99-user_rama has been reloaded, printhead height for printing will be ',y_head_printing_p1)
x_head_beam=416.5

def new_platform_spot(offset='auto'):   ### go to a fresh spot on the platform, e.g. after a deposition
   if offset=='auto':
       offset=RE.md['length of last deposition']+10
   RE(mv(printer.y_head,80))
   RE(mv(printer.x_head,x_head_beam))
   RE(mvr(printer.x_bed,offset))
   RE(mv(printer.z_bed,z_bed))
   #RE(mv(printer.y_head,y_head_printing_p1))
   


position_dict={'z_pos':{'p1':125.,'p2':58.},'y_head_pos':{'p1':58.35,'p2':58.35},'x_head_beam_pos':447.5,'y_pos':{'p1':-21.9,'p2':-21.4}}

def goto_platform(platform='p1'):
    printer.y_head.velocity.set(7);printer.z_bed.velocity.set(5)
    RE(mv(printer.y_head,80)) # move head up, so there is no change to have a collision
    RE(mv(printer.z_bed,position_dict['z_pos'][platform]))
    RE(mv(printer.y_head,position_dict['y_head_pos'][platform]))
    #RE(mv(diff.yh,position_dict['y_pos'][platform]))

def platform_zero():
    RE.md['platform 0 position']=diff.yh.user_readback.value

def set_platform_height(height):
    zero_position=RE.md['platform 0 position']
    RE(mv(diff.yh,zero_position-height))
    RE.md['beam position relative to platform']=height

def get_platform_height():
    ph=-1*(diff.yh.user_readback.value-RE.md['platform 0 position'])
    print('current height of the X-ray beam with respect to printbed: %s mm'%np.round(ph,4))


def goto_pool():   ## to 
    RE.md['last x_bed position'] = printer.x_bed.user_readback.value
    printer.y_head.velocity.set(9)
    printer.x_head.velocity.set(20)
    printer.x_bed.velocity.set(20)
    RE(mv(printer.y_head,80))
    RE(mv(printer.x_head,x_head_beam,printer.z_bed,90,printer.x_bed,-40))
    RE(mv(printer.y_head,62))
    

def return_from_pool(x_position):  ## for RAMA!
   if x_position == 'last':
       x_position=RE.md['last x_bed position']
   printer.y_head.velocity.set(9)
   RE(mv(printer.y_head,80))
   RE(mv(printer.z_bed,z_bed))
   RE(mv(printer.x_bed,x_position))

def super_macro(key='print_param_dict'):
    param_dict=RE.md[key]
    ## pre-macro actions go here ###
    print_ct=0
    print('Doing actions before starting automated printing macro')

    #####################################
    for k in range(len(param_dict['completed'])):
        param_dict=RE.md[key]
        if param_dict['completed'][k]==False:
            ## pre-deposition actions go here ###
            print('Doing actions before printing run # %s!'%(k+1))

            #####################################
            speed=param_dict['speed_list'][k]
            dist1=param_dict['dist1_list'][k]
            dist2=param_dict['dist2_list'][k]
            pre_depos=param_dict['pre_depos_list'][k]
            post_depos=param_dict['post_depos_list'][k]
            pressure=param_dict['pressure_list'][k]
            nozzle_height=param_dict['nozzle_height_list'][k]
            sleep_time=param_dict['sleep_list'][k]
            if print_ct >0:
                new_spot=True
            else: new_spot=False
            print_ct+=1
            print('Executing: deposition_ultimus_printer(speed=%s,dist1=%s,dist2=%s,pre_depos=%s,post_depos=%s,pressure=%s,nozzle_height=%s)'%(speed,dist1,dist2,pre_depos,post_depos,pressure,nozzle_height))
            deposition_ultimus_printer(speed=speed,dist1=dist1,dist2=dist2,pre_depos=pre_depos,post_depos=post_depos,pressure=pressure,nozzle_height=nozzle_height,new_spot=new_spot)
            print('%s  Going to sleep for %s s to allow for data acquisition.'%(time.strftime('%Y-%m-%d %H:%M:%S'),sleep_time))
            param_dict['completed'][k]=True
            RE.md['print_param_dict']=param_dict
            RE(sleep(sleep_time))
            print('Doing actions after printing run # %s!'%(k+1))
            
            #####################################
    print('Doing actions after completing automated printing macro')

    #####################################
    
def parameters_for_multiprint():
    param_dict={'speed_list':[40,30,20,10,40,30,20,10],'dist1_list':0,'dist2_list':[60,60,50,50,60,60,50,50],'pre_depos_list':1,'post_depos_list':1,'pressure_list':[33,25,17,10,33,25,17,10],'nozzle_height_list':y_head_printing_p1,'sleep_list':120}
    l_list=[]
    for i in list(param_dict.keys()):
        try:
            l_list.append(len(param_dict[i]))
        except:
            l_list.append(1)
    if len(list(set(l_list)))>2:
        raise Exception('input parameters need to be list of equal length and/or floats where parameters are not varied!')
    else:
        for i in list(param_dict.keys()):
            tmp=param_dict[i]
            try:
                len(tmp)
                param_dict[i]=np.array(tmp)
            except:
                param_dict[i]=np.ones(max(l_list))*tmp
    param_dict['completed']=np.zeros(max(l_list))
    RE.md['print_param_dict']=param_dict
    
            



# deposition using Ultimus-V as printhead -> for Rama!
def deposition_ultimus_printer(speed=10,dist1=0,dist2=90,pre_depos=1,post_depos=-1,pressure=9.5,nozzle_height=y_head_printing_p1,new_spot=False):
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
    RE.md['length of last deposition']=dist1+dist2
    minimum_trigger_delay = 2 # minimum time needed for triggering the detecor, engaging feedback, etc.
    # If new_platform_spot() was used to move to a new spot, the printhead should be raised, but check just in case...
    caput('XF:11ID-CT{M3}ai1',pressure)
    #if printer.y_head.user_readback.value < nozzle_height+10: #looks like the printhead is not raised, at least not far enought to safely move in x-direction
    #    RE(mv(printer.y_head,nozzle_height+10))
    #RE(mv(printer.x_head,x_head_beam-(dist1+dist2)*.66)) #that's the start position for the deposition
    #RE(mv(printer.y_head,nozzle_height))
    
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
    if new_spot:
        new_platform_spot(offset='auto')
    if printer.y_head.user_readback.value < nozzle_height+10: #looks like the printhead is not raised, at least not far enought to safely move in x-direction
        RE(mv(printer.y_head,nozzle_height+10))
    RE(mv(printer.x_head,x_head_beam-(dist1+dist2)*.66)) #that's the start position for the deposition
    RE(mv(printer.y_head,nozzle_height))
    total_deposition_time=((dist1+dist2)/speed+pre_depos+post_depos)
    if (dist1+dist2)*.66/speed <= minimum_trigger_delay: # need to trigger detector FIRST, before doing anyting else...
        print('triggering detector first')
        caput('XF:11ID-CT{M3}bi2',1,wait=True)
        #RE(sleep(minimum_trigger_delay-pre_depos))
    #mk1_250_deposition(nozzle_size=nozzle_size,filament_size=1.68,speed=speed,road_length=dist1+dist2,temperature=temperature,verbose=True)
    ultimus_deposition(t=total_deposition_time,pressure=pressure)
    RE(sleep(pre_depos))
    
    if (dist1+dist2)*.66/speed > minimum_trigger_delay:   
        print('using timer to trigger beamline')
        BL_trigger_timer(timer=(dist1+dist2)*.66/speed-minimum_trigger_delay)
    #else:
        #RE(sleep(dist1/speed))
    #    caput('XF:11ID-CT{M3}bi2',1)
    printer.x_head.set(printer.x_head.user_readback.get()+dist1+dist2)
    RE(sleep((dist1+dist2)/speed))
    #ultimus_pressure(P=0)
    #RE(mvr(printer.y_head,30)) # raise printhead at the end of deposition
    printer.x_head.velocity.value=20 # set speed to something sensible
    caput('XF:11ID-CT{M3}bi2',0)  # reset beamline trigger


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