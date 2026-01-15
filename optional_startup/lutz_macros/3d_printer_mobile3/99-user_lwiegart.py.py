def cross_OAV():
    cross_x=477
    cross_y=1601
    cross_dict = {'XF:11ID-M3{Det-Cam:3}Over1:1:PositionX':cross_x,
    'XF:11ID-M3{Det-Cam:3}Over1:1:SizeX':100,
    'XF:11ID-M3{Det-Cam:3}Over1:1:PositionY':cross_y,
    'XF:11ID-M3{Det-Cam:3}Over1:1:SizeY':100}
    for c in list(cross_dict.keys()):
        caput(c,cross_dict[c])
    RE.md['oav_cross']=[cross_x,cross_y]



z_bed=118 #(printing)
y_head_print=50.6



x_head_start=452.
x_bed_start=120.

prime_x_bed=125.
prime_x_head=573.
prime_z_bed=125.
prime_y_head=65.



def goto_deposition_start():
    RE(mv(printer.y_head,80))
    RE(mv(printer.z_bed,z_bed))
    RE(mv(printer.x_bed,x_bed_start))
    RE(mv(printer.x_head,x_head_start))

y_head_printing_p1=50.6 ### set nozzle height for printing here!!
x_head_beam=362

def new_platform_spot(offset=45):   ### for RAMA
   RE(mv(printer.y_head,80))
   RE(mv(printer.x_head,x_head_beam))
   RE(mvr(printer.x_bed,offset))
   #RE(mv(printer.y_head,y_head_printing_p1))
   


position_dict={'z_pos':{'p1':128.,'p2':58.},'y_head_pos':{'p1':58.35,'p2':58.35},'x_head_beam_pos':362.,'y_pos':{'p1':-21.9,'p2':-21.4}}

def goto_platform(platform='p1'):
    printer.y_head.velocity.set(7);printer.z_bed.velocity.set(5)
    RE(mv(printer.y_head,80)) # move head up, so there is no change to have a collision
    RE(mv(printer.z_bed,position_dict['z_pos'][platform]))
    RE(mv(printer.y_head,position_dict['y_head_pos'][platform]))
    #RE(mv(diff.yh,position_dict['y_pos'][platform]))


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

def BL_trigger_timer(timer=5):
    caput('XF:11ID-CT{M3}cdt2:start',0)
    caput('XF:11ID-CT{M3}cdt2:setTimeSec',timer)
    caput('XF:11ID-CT{M3}cdt2:start',1)


#def platform_zero():
#    RE.md['platform 0 position']=diff.yh.user_readback.value

#def set_platform_height(height):
#    zero_position=RE.md['platform 0 position']
#    RE(mv(diff.yh,zero_position-height))
#    RE.md['beam position relative to platform']=height


y_head_printing_p2 = 53.35
# deposition with mk1 printhead
def deposition_mk1_printer(speed=10.,dist1=1,dist2=40,pre_depos=.5,post_depos=0,liftoff=False,unprime=True,temperature=225,nozzle_height=y_head_printing_p2,nozzle_size=.5,filament_size=.4,motion_only=False):
    #caput('XF:11ID-CT{M3}ai1',nozzle_size)
    # publish printing parameters:
    caput('XF:11ID-CT{M3}ai3',caget('XF:11ID-M3{Hyrel:1}T11:T-RB'))

    Vext=(dist1+dist2)*np.pi*(nozzle_size/2)**2 # this calculation is redundant, i.e. it is part of mk1_250_deposition(), but need to dublicate it here to publish speed in ct/s
    feed_length=Vext/np.pi/((filament_size/2)**2)
    cts_mm=228 #counts/mm feed -> this should be independent of nozzle and filament diameter
    Vct=feed_length*cts_mm
    speed_cts_s=Vct/((dist1+dist2)/speed)
    caput('XF:11ID-CT{M3}ai4', speed_cts_s)
    caput('XF:11ID-CT{M3}ai5', filament_size)

    road_fraction = .5 # where along the road the beam will be intersected
    RE(mvr(printer.x_head,-1*(dist1+dist2)*road_fraction))
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

    # timing between printing and trigger
    data_offset = 2 # time actual data acquisition starts before the filament is being printed across the beam 
    bl_rt = 6 # 'beamline reaction time': this might vary? time [s] between trigger PV->1 and fast shutter open
    travel_time = road_fraction*(dist1+dist2)/speed # time for the filament to reach the beam position after deposition is started
    
    if data_offset+bl_rt > travel_time+pre_depos: # need to set the trigger PV BEFORE actually starting the deposition
        caput('XF:11ID-CT{M3}bi2',1)        
        RE(sleep((data_offset+bl_rt)-(travel_time+pre_depos)))
        if not motion_only:
            mk1_250_deposition(nozzle_size=nozzle_size,filament_size=filament_size,speed=speed,road_length=dist1+dist2,temperature=temperature,verbose=True)
    else: # need to start the deposition, then have the trigger signal set -> NEED TO RUN setup_BL_trigger() first to set up the EPICS timer!!
        BL_trigger_timer((travel_time+pre_depos)-(data_offset+bl_rt))
        if not motion_only:
            mk1_250_deposition(nozzle_size=nozzle_size,filament_size=filament_size,speed=speed,road_length=dist1+dist2,temperature=temperature,verbose=True)
    RE(sleep(pre_depos))
    printer.x_head.set(printer.x_head.user_readback.get()+dist1+dist2)    
    if liftoff or unprime:    
        RE(sleep((dist1+dist2+speed)/speed))
    if liftoff: RE(mvr(printer.y_head,5))
    if unprime and (not motion_only): mk1_250_unprime(volume=1000,delay=-300,speed=1000,temperature=temperature)
    RE.md['length of last deposition']=dist1+dist2
    printer.x_head.velocity.value=5

def print_wall(layers=2,layer_thickness=.5, first_layer_height=y_head_printing_p2):
    for i in range(layers):
        try: # if wall_height exists from previous deposition
            current_height=RE.md['wall_height'];new_height=current_height+layer_thickness
        except: # this is printing the first layer
            new_height = first_layer_height 
        deposition_mk1_printer(temperature=220,pre_depos=.5,filament_size=1.2,nozzle_height=new_height,liftoff=True)
        RE.md['wall_height']=new_height;RE(sleep(10));RE(mv(printer.x_head,x_head_beam))

def reset_printer():
    RE(mv(printer.y_head,55))
    RE(mv(printer.x_head,368))
    RE(mvr(printer.x_bed,40))
    
    
    