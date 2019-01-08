#import datetime
import pymongo 
from tqdm import tqdm
from bson import ObjectId
import matplotlib.patches as mpatches
from IPython.display import clear_output
cli = pymongo.MongoClient('xf11id-ca')    
samples_2 = cli.get_database('samples').get_collection('samples_2')
data_acquisition_collection = cli.get_database('samples').get_collection('data_acquisition_collection')
beamline_pos = cli.get_database('samples').get_collection('beamline_pos')
from databroker import Broker                                                   
#db = Broker.named('temp')  # for real applications, 'temp' would be 'chx' 
print('available databases:')
print(cli.database_names())
print('\n available collection in database samples:')
print(cli.samples.collection_names())


def update_beamline_pos(position_key='none',interactive=True):
    #### NEEDS UPDATE FOR REAL IMPLEMENTATION!!!
    # complication: some motors are defined as e.g. diff.yh (usually stepper motors)
    # while SmarActs are EPICS signals and typically named: axis_x...

    
    print('defined sets of beamline positions available: ')
    all_pos=beamline_pos.find().distinct('_id')
    print(all_pos)
       
    if interactive:
        user_input_set = input('Pick set to update: ')
    else: 
        user_input_set = position_key
    if user_input_set in all_pos:
        print('Current positions defined in ',user_input_set+':')
        print(beamline_pos.find_one({'_id':user_input_set}))
        if interactive:
              input_update = input('Update set of motor positions? yes/no: ')
        else: input_update = 'yes'
        if input_update == 'yes':
            for i in list(beamline_pos.find_one({'_id':user_input_set})['positions'].keys()):
                #if i in reg_axes:
                try:
                    try:
                        new_val=eval(i.rsplit('_',1)[0]+'.'+i.rsplit('_',1)[1]+'.user_readback.value')
                    except:
                        new_val=eval(i.rsplit('_',1)[0]+'.'+i.rsplit('_',1)[1]+'.user.value')   
                    print('new value for '+i+':   '+str(new_val))
                    beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                #elif i in sm_axes:
                except:
                    try:
                        try:
                            new_val=eval(i+'.user_readback.value')
                        except:
                            new_val=eval(i+'.readback.value')
                        print('new value for '+i+':   '+str(new_val))
                        beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                    except:
                        raise update_exception('ERROR: axis '+i+' not defined in function "update_beamline_pos"\nNOT all positions were updated@')
    else: 
        print('Sorry, requested set of beamline positions is not (yet) available!\n How to add a new set: ')
        print("new_set={'_id':'new-set_name','positions':{'diff_yh':.2,'diff_xh':-1.3,'diff_zh':4.5,'sample_x':.4}}")
        print("beamline_pos.insert_one(new_set)")



def update_beamline_pos_original(position_key='none',interactive=True):
    #### NEEDS UPDATE FOR REAL IMPLEMENTATION!!!
    # complication: some motors are defined as e.g. diff.yh (usually stepper motors)
    # while SmarActs are EPICS signals and typically named: axis_x...

    
    print('defined sets of beamline positions available: ')
    all_pos=beamline_pos.find().distinct('_id')
    print(all_pos)
       
    if interactive:
        user_input_set = input('Pick set to update: ')
    else: 
        user_input_set = position_key
    if user_input_set in all_pos:
        print('Current positions defined in ',user_input_set+':')
        print(beamline_pos.find_one({'_id':user_input_set}))
        if interactive:
              input_update = input('Update set of motor positions? yes/no: ')
        else: input_update = 'yes'
        if input_update == 'yes':
            for i in list(beamline_pos.find_one({'_id':user_input_set})['positions'].keys()):
                #if i in reg_axes:
                try:
                    new_val=eval(i.rsplit('_',1)[0]+'.'+i.rsplit('_',1)[1]+'.user_readback.value')
                    print('new value for '+i+':   '+str(new_val))
                    beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                #elif i in sm_axes:
                except:
                    try:
                        new_val=eval(i+'.user_readback.value')
                        print('new value for '+i+':   '+str(new_val))
                        beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                    except:
                        raise update_exception('ERROR: axis '+i+' not defined in function "update_beamline_pos"\nNOT all positions were updated@')
    else: 
        print('Sorry, requested set of beamline positions is not (yet) available!\n How to add a new set: ')
        print("new_set={'_id':'new-set_name',positions:{'diff_yh':.2,'diff_xh':-1.3,'diff_zh':4.5,'sample_x':.4}}")
        print("beamline_pos.insert_one(new_set)")
        
def goto_beamline_pos(position_key='none',interactive=True):
    #### NEEDS UPDATE FOR REAL IMPLEMENTATION!!!
    # complication: some motors are defined as e.g. diff.yh (usually stepper motors)
    # while SmarActs are EPICS signals and typically named: axis_x...
    reg_axes=reg_axes=['diff_xh','diff_yh','diff_zh','diff_gam','det_x','det_y','diff_Del','diff_gam']
    sm_axes=['foil_x','sample_x']
    
    print('defined sets of beamline positions available: ')
    all_pos=beamline_pos.find().distinct('_id')
    print(all_pos)
       
    if interactive:
        user_input_set = input('Pick set to move to positions: ')
    else: 
        user_input_set = position_key
    if user_input_set in all_pos:
        print('Current positions defined in ',user_input_set+':')
        print(beamline_pos.find_one({'_id':user_input_set}))
        if interactive:
              input_update = input('Move to this set of motor positions? yes/no: ')
        else: input_update = 'yes'
        if input_update == 'yes':
            for i in list(beamline_pos.find_one({'_id':user_input_set})['positions'].keys()):
                new_val = beamline_pos.find_one({'_id':user_input_set})['positions'][i]
                #if i in reg_axes:
                try:
                    #new_val=eval(i.split('_')[0]+'.'+i.split('_')[1]+'.user_readback.value')
                    print('moving '+i.rsplit('_',1)[0]+'.'+i.rsplit('_',1)[1]+':   '+str(new_val))
                    RE(mov(eval(i.rsplit('_',1)[0]+'.'+i.rsplit('_',1)[1]),new_val))
                    #beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                #elif i in sm_axes:
                except:
                    try:
                        #new_val=eval(i+'.user_readback.value')
                        print('moving '+i+':   '+str(new_val))
                        RE(mov(eval(i),new_val))
                        #beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                    except:
                        raise update_exception('ERROR: axis '+i+' not defined in function "goto_beamline_pos"\nNOT all positions were reached!')
    else: 
        print('Sorry, requested set of beamline positions is not (yet) available!\n How to add a new set: ')
        print("new_set={'_id':'new-set_name','positions':{'diff_yh':.2,'diff_xh':-1.3,'diff_zh':4.5,'sample_x':.4}}")
        print("beamline_pos.insert_one(new_set)")

def get_focus(mount,holder):
    """
    currently only implemented for sample mount 'multi'
    assumes that reference position for focus in beamline_pos is on the mounting frame
    returns z-position of sample upstream surface
    """
    if mount != 'multi':
        print('sorry, automatic focus adjustment is currently only implemented for mount "multi"')
    else: 
        z_off = beamline_pos.find_one({'_id':mount+'_sample_center'})['positions']['diff_zh']
        z_positions = beamline_pos.find_one({'_id':'mount_dict'})[holder[0]+'_zpos']
        if holder[0] == 'capillary':
            thickness=holder[1]
        elif holder[0] == 'flat_cell':
            thickness=holder[2]
        z_pos=np.array(z_positions[1])[np.array(z_positions[0])==thickness][0]
        print('diff_zh position (on frame) from database: '+str(z_off))
        print(z_positions)
        print('z_pos: '+str(z_pos))
        return z_off+z_pos

def acquisition_from_database(acquisition_database_obid,error_mode='try',focus_correction=False,stop_key='none',OAV_mode='single'):
    """
    #####TODOLIST:  move OAV_mode to obid   ---> commented by Y.G. 10.15.2018
    
    #error_mode='try' # 'try' / 'skip': select what do do with slots where the data acquisition has errors: try to collect whatever possible, skip: skip slot alltogether
    """
    
    org_md_keys=list(RE.md.keys())
    obid=acquisition_database_obid
    mount_dict=beamline_pos.find_one({'_id':'mount_dict'})
    #org_md_keys=list(RE.md.keys())
    det_in='unknown'
    data_acq_dict=data_acquisition_collection.find_one({'_id':obid})
    det_list={'500k':'eiger500k','4m':'eiger4m','1m':'eiger1m'}
    for i in data_acq_dict['slots used']:
        acq_count = 0
        if error_mode == 'skip' and data_acq_dict[i]['errors']:
            print (bcolors.FAIL + "Error in data acquisition definition for "+i+" -> no data will be collected for this sample"+ bcolors.ENDC)
        elif error_mode == 'try':
            #try:   ######################################### comment for debugging!!!
                if data_acq_dict[i]['stats'][4] > 0:
                    print(bcolors.WARNING+'\nTAKING DATA FOR '+i+ bcolors.ENDC)
                    acq_count = 1
                    sample_info=samples_2.find_one({'_id':data_acq_dict[i]['sample_id']})
                    # prep data acquisition: move to slot center, taking offsets from beamlin_data
                    offsets=beamline_pos.find_one({'_id':data_acq_dict['sample_mount']+'_sample_center'})['positions']
                    y_off = offsets['diff_yh'];z_off=offsets['diff_zh'];
                    # get correct z-offset for sample holder, depends e.g. on capillary diameter (only capillary and flat cell are implemented)
                    if focus_correction == True:
                        zfocus=get_focus(mount=data_acq_dict['sample_mount'],holder=sample_info['sample']['holder'])
                        print(bcolors.WARNING+'adjusting z-position to keep OAV focused:'+ bcolors.ENDC)
                        print(bcolors.WARNING+'RE(mov(diff.zh,'+str(zfocus)+')) '+ bcolors.ENDC)
                        RE(mov(diff.zh,zfocus))
                    print('center position of '+i+' in sample holder mount '+data_acq_dict['sample_mount']+': '+str(mount_dict[data_acq_dict['sample_mount']][i[4:]]))
                    x_cen=mount_dict[data_acq_dict['sample_mount']][i[4:]][0];y_cen=mount_dict[data_acq_dict['sample_mount']][i[4:]][1]
                    if not data_acq_dict['sample_mount'] == 'multi':
                        x_off=offsets['diff_xh']
                        print(bcolors.WARNING+'RE(mov(diff.xh,'+str(-x_cen+x_off)+',diff.yh,'+str(-y_cen+y_off)+')) '+ bcolors.ENDC)
                        RE(mov(diff.xh,-x_cen+x_off,diff.yh,-y_cen+y_off))
                    else:
                        x_off = offsets['sample_x']                          
                        print(bcolors.WARNING+'RE(mov(sample_x,'+str(-x_cen+x_off)+',diff.yh,'+str(-y_cen+y_off)+',diff.xh,'+str(offsets['diff_xh'])+')) '+ bcolors.ENDC)
                        RE(mov(sample_x,-x_cen+x_off,diff.yh,-y_cen+y_off,diff.xh,offsets['diff_xh']))
                    # prep data acquisition: update md
                    RE.md['automatic data collection for ObjectID']=str(obid)
                    RE.md['sample_mount']=data_acq_dict['sample_mount']
                    RE.md['sample database id']=str(data_acq_dict[i]['sample_id'])
                    RE.md['owner']=sample_info['info']['owner']
                    RE.md['new_spot_method']=sample_info['info']['new_spot_method']
                    md_list=list(sample_info['sample'].keys())
                    for g in md_list:
                        RE.md[g]=sample_info['sample'][g]
                    RE.md['sample']=RE.md['sample name']
                    #print(RE.md)
                    # check what's requested: temp change, wait or data acquisition -> move to next sampling grid point
                    for m in range(len(data_acq_dict[i]['acq_list'])):
                        if not data_acq_dict[i]['acq_completed'][m]: # task in database has not been previously completed
                            if data_acq_dict[i]['acq_list'][m][0] in list(det_list.keys()):   # this is a data series!
                                print(bcolors.WARNING+'next data acquisition: '+str(data_acq_dict[i]['acq_list'][m])+ bcolors.ENDC)
                                if det_in != data_acq_dict[i]['acq_list'][m][0]:   # move to the requested detector
                                    print(bcolors.WARNING+'changing detector to: '+data_acq_dict[i]['acq_list'][m][0]+ bcolors.ENDC)
                                    x_det_pos=beamline_pos.find_one({'_id':data_acq_dict[i]['acq_list'][m][0]+'_in'})['positions']['saxs_detector_x']
                                    y_det_pos=beamline_pos.find_one({'_id':data_acq_dict[i]['acq_list'][m][0]+'_in'})['positions']['saxs_detector_y']
                                    print(bcolors.WARNING+'RE(mov(saxs_detector.x,'+str(x_det_pos)+',saxs_detector.y,'+str(y_det_pos)+')) '+ bcolors.ENDC)
                                    RE(mov(saxs_detector.x,x_det_pos,saxs_detector.y,y_det_pos)) 
                                    det_in=data_acq_dict[i]['acq_list'][m][0]
                                nspm = samples_2.find_one({'_id':data_acq_dict[i]['sample_id']})['info']['new_spot_method']
                                if nspm != 'static': # request to change the sample position for each new data point
                                    print('new_spot_method is '+nspm)
                                    if float(get_n_fresh_spots(data_acq_dict[i]['sample_id'])) >= 1: #sufficient number of fresh spots available
                                        print('sufficient number of fresh spots available!')
                                        x_point=np.array(samples_2.find_one({'_id':data_acq_dict[i]['sample_id']})['info']['points'][0])
                                        y_point=np.array(samples_2.find_one({'_id':data_acq_dict[i]['sample_id']})['info']['points'][1])
                                        dose=np.array(samples_2.find_one({'_id':data_acq_dict[i]['sample_id']})['info']['points'][2])
                                        # where is the next sample grid point?
                                        [dose_ind,next_x_point,next_y_point]=next_grid_point(x_point,y_point,dose,mode=nspm)
                                        print('new spot: [x,y]: '+str([next_x_point,next_y_point]))
                    # move to next sample grid point:
                                        x_cen=mount_dict[data_acq_dict['sample_mount']][i[4:]][0]+next_x_point;y_cen=mount_dict[data_acq_dict['sample_mount']][i[4:]][1]+next_y_point
                                        if not data_acq_dict['sample_mount'] == 'multi':
                                            print(bcolors.WARNING+'RE(mov(diff.xh,'+str(-x_cen+x_off)+',diff.yh,'+str(-y_cen+y_off)+')) '+ bcolors.ENDC)
                                            RE(mov(diff.xh,-x_cen+x_off,diff.yh,-y_cen+y_off))
                                        else:
                                            x_off = offsets['sample_x']
                                            print(bcolors.WARNING+'RE(mov(sample_x,'+str(-x_cen+x_off)+',diff.yh,'+str(-y_cen+y_off)+')) '+ bcolors.ENDC)
                                            RE(mov(sample_x,-x_cen+x_off,diff.yh,-y_cen+y_off))
 
                                     
                                ################################################################################
                                ####################YG's change START                                           
                                            
                                        # update dose for sampling grid point and update database:
                                        dose[dose_ind] = data_acq_dict[i]['acq_list'][m][1]*data_acq_dict[i]['acq_list'][m][2]*data_acq_dict[i]['acq_list'][m][3]
                                        fresh_spots = int(sum(dose==0))
                                        update_sample_database_with_new_sampling_grid(data_acq_dict[i]['sample_id'],x_point,y_point,dose,fresh_spots)
                                    else:
                                        print(bcolors.FAIL+'number of fresh spots available is 0! NOT moving to fresh spot.'+bcolors.ENDC)
                                else:
                                    print('new_spot_method is "static": will not change sample spot between data series')
                                
                                                                    
                                # take actual data!!!
                                print(bcolors.WARNING+'att2.set_T('+str(data_acq_dict[i]['acq_list'][m][3])+')'+ bcolors.ENDC)                                
                                att2.set_T(data_acq_dict[i]['acq_list'][m][3])
                                acql=data_acq_dict[i]['acq_list'][m]                                

                                
                                series_options =  acql[4]['series_options']
                                if 'feedback_on' in list(   series_options.keys() ):
                                	feedback_on = series_options[ 'feedback_on' ]
                                else:
                                	feedback_on = False
                                if 'analysis' in list(   series_options.keys() ):
                                	analysis = series_options[ 'analysis' ]
                                else:
                                	analysis = 'iso'                           
                                
                                
                                
                                print(bcolors.WARNING+'series(det='+det_list[acql[0]]+',expt='+str(acql[1])+',acqp="auto",imnum='+str(acql[2])+',OAV_mode='+OAV_mode+',feedback_on='+ str(feedback_on )+',comment='+str(acql[1])+'s x'+str(str(acql[2]))+'  '+RE.md['sample']+')' +bcolors.ENDC)
                                
                                
                                series(det=det_list[acql[0]],expt=acql[1],acqp='auto',imnum=acql[2],OAV_mode=OAV_mode,feedback_on=feedback_on,comment=str(acql[1])+'s x'+str(str(acql[2]))+'  '+RE.md['sample'])
                                

                                
                                
                                # fake some data acquisition to get a uid:
                                #RE(count([eiger1m_single]))   # this will become series!!
                                uid=db[-1]['start']['uid']
                                #for ics in tqdm(range(100)):
                                #    time.sleep(.1)
                                # add uid to database for compression:
                                uid_list=data_acquisition_collection.find_one({'_id':'general_list'})['uid_list']
                                sample_uidlist=samples_2.find_one({'_id':data_acq_dict[i]['sample_id']})['info']['uids']
                                uid_list.append(uid);
                                
                                
                                ustr = str(acquisition_database_obid)
                                if ustr not in list( sample_uidlist.keys() ):
                                    sample_uidlist[ ustr ] = []    
                                sample_uidlist[ ustr ].append(  uid ) 
                                
                                data_acquisition_collection.update_one({'_id': 'general_list'},{'$set':{'uid_list' : uid_list}})
                                # add uid to sample database:
                                samples_2.update_one({'_id': data_acq_dict[i]['sample_id']},{'$set':{'info.uids' : sample_uidlist}})

 

                                ####################YG's change END
                                #################################################################################
                                                                

                            elif data_acq_dict[i]['acq_list'][m][0] == 'T_ramp':
                                print(bcolors.WARNING+'set_temperature('+str(data_acq_dict[i]['acq_list'][m][1])+',cool_ramp='+str(data_acq_dict[i]['acq_list'][m][2])+',heat_ramp='+str(data_acq_dict[i]['acq_list'][m][2])+')' +bcolors.ENDC)
                                set_temperature(data_acq_dict[i]['acq_list'][m][1],cool_ramp=data_acq_dict[i]['acq_list'][m][2],heat_ramp=data_acq_dict[i]['acq_list'][m][2])
                                print(bcolors.WARNING+'wait_temperature('+str(data_acq_dict[i]['acq_list'][m][3])+')' +bcolors.ENDC)
                                wait_temperature(data_acq_dict[i]['acq_list'][m][3])
                            elif data_acq_dict[i]['acq_list'][m][0] == 'wait':
                                 print(bcolors.WARNING+'RE(sleep('+str(data_acq_dict[i]['acq_list'][m][1])+'))' +bcolors.ENDC)
                                 RE(sleep(data_acq_dict[i]['acq_list'][m][1]))
                            # mark task as complete:
                            acq_completed_list = data_acquisition_collection.find_one({'_id':obid})[i]['acq_completed']
                            acq_completed_list[m] = True
                            data_acquisition_collection.update_one({'_id':obid},{'$set':{i+'.acq_completed' : acq_completed_list}})

                        else:
                            print(bcolors.FAIL+'Task '+str(data_acq_dict[i]['acq_list'][m])+' has been previously completed: skip!'+bcolors.ENDC)

                # clean up: remove metadata
                for q in list(RE.md.keys()):
                    if q not in org_md_keys:
                        waste=RE.md.pop(q)
                else:
                    if acq_count == 0:
                        print(bcolors.WARNING+'SKIP SLOT '+i+': No data points requested'+ bcolors.ENDC)
                    else:
                        print(bcolors.OKGREEN+'\nDATA ACQUISITION FOR SLOT '+i+' COMPLETED.'+ bcolors.ENDC)

            #except:
            #    print (bcolors.FAIL + "Error in data acquisition definition for "+i+" -> no or} not all data collected for this sample"+ bcolors.ENDC) 
    if stop_key != 'none': # key to automatically stop compression and analysis
        uid_list=data_acquisition_collection.find_one({'_id':'general_list'})['uid_list']
        uid_list.append(stop_key)
        data_acquisition_collection.update_one({'_id': 'general_list'},{'$set':{'uid_list' : uid_list}})

def next_grid_point(x_point,y_point,dose,mode='consecutive'):
    """
    
    by LW 08/28/2018
    """
    # points with zero dose available:
    x_available=x_point[dose==0]
    y_available=y_point[dose==0]

    # center of grid:
    x_cen=np.mean(x_point)
    y_cen=np.mean(y_point)
    
    # next point to be used:
    if mode == 'from_center':
        distance=(x_available-x_cen)**2+(y_available-y_cen)**2
        next_ind=np.argmin(distance)
    elif mode == 'consecutive':
        next_ind = 0
    elif mode == 'random':
        next_ind=np.random.randint(0,len(x_available)-1)

    next_x_point=x_available[next_ind]
    next_y_point=y_available[next_ind]
    # need to find index of that point in the whole grid (to update dose)
    a=x_point == x_available[next_ind]
    b=y_point == y_available[next_ind]
    dose_ind= [i for i, x in enumerate(a*b) if x]
    return [dose_ind[0],next_x_point,next_y_point]

def get_n_fresh_spots(obid):
    t_dict=samples_2.find_one({'_id':obid})
    try: 
        n_points=t_dict['info']['points'][3]
        return n_points
    except:
        return False
      
# update 'points' in sample database:
def update_sample_database_with_new_sampling_grid(obid,x_point,y_point,dose,fresh_spots,verbose=False):
    points=[x_point.tolist(),y_point.tolist(),dose.tolist(),fresh_spots]
    samples_2.update_one({'_id':  obid},{'$set':{'info.points' : points}})
    if verbose:
        print('sample information has been updated with new points for data acquisition:\n')
        print(samples_2.find_one({'_id':obid}))


class update_exception(Exception):
    pass
  
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
