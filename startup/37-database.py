import datetime
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
    reg_axes=['diff_xh','diff_yh','diff_zh','diff_gam','det_x','det_y','diff_Del','diff_gam']
    sm_axes=['foil_x','sample_x']
    
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
                if i in reg_axes:
                    new_val=eval(i.split('_')[0]+'.'+i.split('_')[1]+'.user_readback.value')
                    print('new value for '+i+':   '+str(new_val))
                    beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                elif i in sm_axes:
                    new_val=eval(i+'.user_readback.value')
                    print('new value for '+i+':   '+str(new_val))
                    beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                else: raise update_exception('ERROR: axis '+i+' not defined in function "update_beamline_pos"\nNOT all positions were updated@')
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
                if i in reg_axes:                    
                    #new_val=eval(i.split('_')[0]+'.'+i.split('_')[1]+'.user_readback.value')
                    print('moving '+i.split('_')[0]+'.'+i.split('_')[1]+':   '+str(new_val))
                    RE(mov(eval(i.split('_')[0]+'.'+i.split('_')[1]),new_val))
                    #beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                elif i in sm_axes:
                    #new_val=eval(i+'.user_readback.value')
                    print('moving '+i+':   '+str(new_val))
                    RE(mov(eval(i),new_val))
                    #beamline_pos.update_one({'_id':user_input_set},{'$set':{'positions.'+i : new_val}})
                else: raise update_exception('ERROR: axis '+i+' not defined in function "goto_beamline_pos"\nNOT all positions were reached!')
    else: 
        print('Sorry, requested set of beamline positions is not (yet) available!\n How to add a new set: ')
        print("new_set={'_id':'new-set_name',positions:{'diff_yh':.2,'diff_xh':-1.3,'diff_zh':4.5,'sample_x':.4}}")
        print("beamline_pos.insert_one(new_set)")



class update_exception(Exception):
    pass
