# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 14:02:59 2015
by LW March 2015
set of utility functions for beamline alingment and commissioning
v 0.0.1 (this version): might have created a typo in E-calibration!!!
                        added dcm_roll for calculating DCM Roll correction
"""
import datetime as dtt
import time
import numpy as np
from PIL import Image
# from databroker import db, get_fields, get_images, get_table
get_fields = db.get_fields
get_images = db.get_images
get_table = db.get_table
from matplotlib import pyplot as pltfrom
from lmfit import  Model
from lmfit import minimize, Parameters, Parameter, report_fit
from scipy.special import erf

from zoneinfo import ZoneInfo
import json, re, os
from termcolor import colored

from IPython.display import clear_output

def check_roi_masknames(path='/nsls2/data/chx/shared/CHX_Setup/Detector_masks/ROI_masks',verbose=False):
    files_ = [f for f in os.listdir(path) if re.match('general_', f) and f.split('.')[1]=='json']
    files=[]
    for f in files_:
        files.append(f.split('general_roi_mask_')[1].split('.')[0])
    if verbose:
        print('available Q-Phi ROI masks: %s'%files)
    return files



################ set of functions to manage metadata #####################
def compare_dicts(dict1,dict2,key_list):
    """
    support function for manage_metadata()
    creates a new dictionary comp_dict that for each k in key_list has the key, value of dict1, value of dict2 IF k in dict1.keys().
    LW 02/26/2024
    """
    comp_dict={}
    for k in key_list:
        try: 
            comp_dict[k]={'original':dict1[k],'backup':dict2[k]}
        except:
            pass
    return comp_dict

def backup_md(md_dict,backup_dict_path,md_filename,verbose=False):
    """
    support function for manage_metadata()
    dumps dictionary as json file
    creates directory specified as backup_dict_path IF it does not exist
    backup_md(md_dict,backup_dict_path,md_filename,verbose=False)
    LW 02/26/2024
    """
    #create filename
    t=str(datetime.now(ZoneInfo("America/New_York"))) # remove one datetime for beamline...
    json_filename = backup_dict_path+md_filename+t.split()[0]+'_%s_%s_%s.json'%(t.split()[1].split(':')[0],t.split()[1].split(':')[1],t.split()[1].split(':')[2].split('.')[0])

    if not os.path.exists(backup_dict_path):
        os.makedirs(backup_dict_path)
    md_dict['backup_epoch']=time.time()
    with open(json_filename, "w") as outfile:
        json.dump(json.dumps(md_dict), outfile)
    if verbose:
        print('saved metadata backup file as ',json_filename)

def list_md_backups(backup_dict_path,md_filename,newest_first=True,max_number=None):
    """
    support function for manage_metadata()
    list_md_backups(backup_dict_path,md_filename,newest_first=True)
    lists available metadata backups in specified directory, ordered by time
    md_filename is the template name, currently 'CHX_md_backup_'
    newest_first=True: latest backup is top of the list (False: oldest backup is top of the list)
    LW 02/26/2024
    """
    files_ = [f for f in os.listdir(path=backup_dict_path) if re.match(md_filename, f) and f.split('.')[1]=='json']
    md_epoch_dict={};md_timestr_dict={}
    for f in files_:
        fn = open(backup_dict_path+f)
        tmp_ = json.load(fn);fn.close()
        tmp = json.loads(tmp_);del tmp_
        tstring=str(datetime.fromtimestamp(tmp['backup_epoch'])).split('.')[0]
        md_epoch_dict[tmp['backup_epoch']]={'time_str':tstring,'filename':f}
        md_timestr_dict[tstring]=f
    del tmp;select_dict = {}
    print('#     backup time     ->       backup filename')
    for tt,t in enumerate(sorted(list(md_epoch_dict.keys()),reverse=newest_first)[:max_number]):
        select_dict[tt+1]={'time_str':md_epoch_dict[t]['time_str'],'filename':md_epoch_dict[t]['filename'].split('.')[0]}
        print('%s   %s -> %s'%(tt+1,select_dict[tt+1]['time_str'],select_dict[tt+1]['filename']))
    return select_dict
95
def manage_metadata(action=None,verbose=True,**kwargs):
    """
    function to manage beamline metadata dictionary
    manage_metadata(action=None,verbose=True,**kwargs)
    action
    None:   - list standard keys
            - default dict
            - WARNING: missing standard keys in current metadata dict
            - list of user metadata keys that could be removed 
    'remove_user_keys': - list user md that can be removed, asks for confirmation to remvove it
                        - creates a backup prior to removing md
    'md_backup':  save current metadata dictionary as json file
    'set_default_values':   - save current metadata dictionary as json file
                            - set keys in default dict to standard values
    'restore_md':   - show available backup files, ordered by date
                    - interactively select backup to be restored 
                    - interactively check which metadata to restore for standard and user metadata, show values that would be restored
                    - IF any modifications are made to the current metadata dictionary, save a backup first as json file
    optional keywords with action='restore_md':
    - newest_first = True/False -> if True: list newest backup files first
    - max_number = integer or None -> maximum number of available backup files shown; if None: show all
    LW 02/26/2024
    """    
    backup_dict_path = '/home/xf11id/CHX_metadata_backups/'
    md_filename = 'CHX_md_backup_'
    # what to do with data session? what's the default?
    keep_list = ['scan_id','cycle','sample','auto_pipeline','beam_position_dict','OAV_resolution [um_pixel]','data_session','beamline_id','owner','username','user_group','start_datetime', 'proposal']
    default_dict = {'sample':'none','auto_pipeline':'none','OAV_resolution [um_pixel]':'N.A.','user':'CHX_staff','user_group':[]}
    
    md_dict=dict(RE.md)
    current_list = list(md_dict.keys())
    
    if action is None or action == 'remove_user_keys': 
        warn_list = []
        for k in keep_list:
            if k not in current_list:
                warn_list.append(k)
        user_list = []
        for k in current_list:
            if k not in keep_list:
                user_list.append(k)
    if action is None:
        print(colored('standard metadata keys that cannot be removed: ','green'),'\n%s\n'%keep_list)
        print(colored('user metadata keys that could be removed: ','green'),'\n%s\n'%user_list)
        if len(warn_list)>0:
            print(colored('WARNING: mandatory standard metadata keys that are currently missing: \n%s\n'%warn_list,'yellow'))
        print(colored('defaults that can be assigned to a subset of metadata keys: ','green'),'\n%s\n'%default_dict)
    
    if action == 'remove_user_keys':
        print(colored('WARNING: user metadata keys that will be removed: \n%s\n'%user_list,'yellow'))
        confirm=False
        print(colored('ATTENTION: remove user metadata keys listed above? yes/no: ','red'));confirm = input()
        if confirm == 'yes':
            backup_md(md_dict,backup_dict_path,md_filename,verbose=True)
            for u in user_list:
                del RE.md[u]    
        else:
            print(colored('abort: no user keys have been removed','yellow'))
        if len(warn_list)>0: #courtesy warning, nothing to do with removing user keys
            print(colored('WARNING: mandatory standard metadata keys that are currently missing: \n%s\n'%warn_list,'yellow'))
               
    if action == 'md_backup':
        backup_md(md_dict,backup_dict_path,md_filename,verbose=verbose)
    
    if action == 'set_default_values':
        print('will set standard keys from current value to default values:\n',colored('    key:        current value     ->      default value','green'))
        for k in list(default_dict.keys()):
            try:
                is_value = md_dict[k]
            except:
                is_value = None
            print('%s:   %s      ->      %s'%(k,is_value,default_dict[k]))
        confirm=False
        print(colored('ATTENTION: reset standard metadata keys with defaults listed above? yes/no: ','red'));confirm = input()
        if confirm == 'yes':
            backup_md(md_dict,backup_dict_path,md_filename,verbose=True)
            for k in list(default_dict.keys()):
                RE.md[k] = default_dict[k]
        else:
            print(colored('abort: no standard metadata keys have been reset to dafaults','yellow'))
        warn_list = []
        for k in keep_list:
            if k not in list(md_dict.keys()):
                warn_list.append(k)
        if len(warn_list)>0: #courtesy warning, nothing to do with removing user keys
            print(colored('WARNING: mandatory standard metadata keys that are currently missing: \n%s\n'%warn_list,'yellow'))
    
    if action == 'restore_md':
        newest_first=True;max_number=None
        print('Available metadata backups that could be restored: ')
        if 'newest_first' in kwargs:
            if kwargs['newest_first'] in [True,False]:
                newest_first=kwargs['newest_first']
        if 'max_number' in kwargs:
            if type(kwargs['max_number'])==int or kwargs['max_number'] == None:
                max_number = kwargs['max_number']
        select_dict = list_md_backups(backup_dict_path,md_filename,newest_first=newest_first,max_number=max_number)
        print(colored('Selection: either use backup # (int) or backup filename','green'));fn_=input()
        try: # if fn_ is integer...but it's coming back anyways as str from input()
            fn=backup_dict_path+select_dict[int(fn_)]['filename']+'.json'
        except: fn=backup_dict_path+fn_+'.json'
        try:
            f = open(fn)  ### load json file
            tmp = json.load(f);f.close()
            backup_dict=json.loads(tmp);del tmp
        except:
            print(colored('ERROR: selected backup file %s could not be loaded....'%fn,'red'))
        print('content of selected backup: ',backup_dict)
        backed_up = False # IF any modifications will be made to the current metadata, do a backup first!
        standard_dict = compare_dicts(dict1=md_dict,dict2=backup_dict,key_list=keep_list)
        user_list_backup = [i for i in list(backup_dict.keys()) if i not in keep_list]
        user_list_dict = {}
        for k in user_list_backup:
            if  k not in ['backup_epoch']:
                try: org=md_dict[k]
                except: org=None
                user_list_dict[k]={'original':org,'backup':backup_dict[k]}

        # restore user metadata
        print(colored('User metadata that can be restored:\n  key:      current    ->      backup','green'))
        for u in list(user_list_dict.keys()):
            print('%s    %s   ->   %s'%(u,user_list_dict[u]['original'],user_list_dict[u]['backup']))
        print(colored('Restore user metadata from backup? yes/no:','red'));confirm=False;confirm=input()
        if confirm == 'yes':
            if not backed_up:
                backup_md(md_dict,backup_dict_path,md_filename,verbose=verbose);backed_up=True
            for k in list(user_list_dict.keys()):
                RE.md[k]=user_list_dict[k]['backup']
        else:
            print(colored('user metadata has NOT been restored','yellow'))
        clear_output()
        print(colored('standard metadata that can be restored:\n  key:      current    ->      backup','green'))
        for u in list(standard_dict.keys()):
            print('%s    %s   ->   %s'%(u,standard_dict[u]['original'],standard_dict[u]['backup']))
        print(colored("Restore standard metadata from backup? Be sure you know what you're doing... yes/no:",'red'));confirm=False;confirm=input()    
        if confirm == 'yes':
            if not backed_up:
                backup_md(md_dict,backup_dict_path,md_filename,verbose=verbose);backed_up=True
            for k in list(standard_dict.keys()):
                RE.md[k]=standard_dict[k]['backup']
        else:
            print(colored('Standard metadata has NOT been restored','yellow'))
        
        warn_list = []
        for k in keep_list:
            if k not in list(md_dict.keys()):
                warn_list.append(k)
        if len(warn_list)>0: #courtesy warning, nothing to do with removing user keys
            print(colored('WARNING: mandatory standard metadata keys that are currently missing: \n%s\n'%warn_list,'yellow'))
    elif action not in [None, 'remove_user_keys', 'md_backup', 'set_default_values', 'restore_md']: print(colored("ERROR: 'action' argument must be one of [None, 'remove_user_keys', 'md_backup', 'set_default_values', 'restore_md']",'red'))


##########################################################################





import itertools 
markers =  ['o',   'H', 'D', 'v',  '^', '<',  '>', 'p',
                's',  'h',   '*', 'd', 
            '$I$','$L$', '$O$','$V$','$E$', 
            '$c$', '$h$','$x$','$b$','$e$','$a$','$m$','$l$','$i$','$n$', '$e$',
            '8', '1', '3', '2', '4',     '+',   'x',  '_',   '|', ',',  '1',]

markers = np.array(   markers *100 )
colors = np.array( ['darkorange', 'mediumturquoise', 'seashell', 'mediumaquamarine', 'darkblue', 
           'yellowgreen',  'mintcream', 'royalblue', 'springgreen', 'slategray',
           'yellow', 'slateblue', 'darkslateblue', 'papayawhip', 'bisque', 'firebrick', 
           'burlywood',  'dodgerblue', 'dimgrey', 'chartreuse', 'deepskyblue', 'honeydew', 
           'orchid',  'teal', 'steelblue', 'limegreen', 'antiquewhite', 
           'linen', 'saddlebrown', 'grey', 'khaki',  'hotpink', 'darkslategray', 
           'forestgreen',  'lightsalmon', 'turquoise', 'navajowhite', 
            'darkgrey', 'darkkhaki', 'slategrey', 'indigo',
           'darkolivegreen', 'aquamarine', 'moccasin', 'beige', 'ivory', 'olivedrab',
           'whitesmoke', 'paleturquoise', 'blueviolet', 'tomato', 'aqua', 'palegoldenrod', 
           'cornsilk', 'navy', 'mediumvioletred', 'palevioletred', 'aliceblue', 'azure', 
             'orangered', 'lightgrey', 'lightpink', 'orange',  'wheat', 
           'darkorchid', 'mediumslateblue', 'lightslategray', 'green', 'lawngreen', 
           'mediumseagreen', 'darksalmon', 'pink', 'oldlace', 'sienna', 'dimgray', 'fuchsia',
           'lemonchiffon', 'maroon', 'salmon', 'gainsboro', 'indianred', 'crimson',
            'mistyrose', 'lightblue', 'darkgreen', 'lightgreen', 'deeppink', 
           'palegreen', 'thistle', 'lightcoral', 'lightgray', 'lightskyblue', 'mediumspringgreen', 
           'mediumblue', 'peru', 'lightgoldenrodyellow', 'darkseagreen', 'mediumorchid', 
           'coral', 'lightyellow', 'chocolate', 'lavenderblush', 'darkred', 'lightseagreen', 
           'darkviolet', 'lightcyan', 'cadetblue', 'blanchedalmond', 'midnightblue', 
           'darksage', 'lightsteelblue', 'darkcyan', 'floralwhite', 'darkgray', 
           'lavender', 'sandybrown', 'cornflowerblue',  'gray', 
           'mediumpurple', 'lightslategrey',   'seagreen', 
           'silver', 'darkmagenta', 'darkslategrey', 'darkgoldenrod', 'rosybrown', 
           'goldenrod',   'darkturquoise', 'plum',
                 'purple',   'olive', 'gold','powderblue',  'peachpuff','violet', 'lime',  'greenyellow', 'tan',    'skyblue',
                    'magenta',   'black', 'brown',   'green', 'cyan', 'red','blue'] *100 )

colors = colors[::-1]
colors_ = itertools.cycle(   colors  )
#colors_ = itertools.cycle(sorted_colors_ )
markers_ = itertools.cycle( markers )


def plot1D( y,x=None, yerr=None, ax=None,return_fig=False, ls='-', 
           legend_size=None, lw=None, *argv,**kwargs):    
    """a simple function to plot two-column data by using matplotlib.plot
    pass *argv,**kwargs to plot
    
    Parameters
    ----------
    y: column-y
    x: column-x, by default x=None, the plot will use index of y as x-axis
    Returns
    -------
    None
    """
    RUN_GUI = False
    if ax is None:
        if RUN_GUI:
            fig = Figure()
            ax = fig.add_subplot(111)
        else:
            fig, ax = plt.subplots()
        
    if 'legend' in kwargs.keys():
        legend =  kwargs['legend']  
    else:
        legend = ' '

    try:
         logx = kwargs['logx']
    except:
        logx=False
    try:
         logy = kwargs['logy']
    except:
        logy=False
        
    try:
         logxy = kwargs['logxy']
    except:
        logxy= False        

    if logx==True and logy==True:
        logxy = True
        
    try:
        marker = kwargs['marker']         
    except:
        try:
            marker = kwargs['m'] 
        except:            
            marker= next(  markers_    )
    try:
        color =  kwargs['color']
    except:    
        try:
            color =  kwargs['c']
        except: 
            color = next(  colors_    ) 
            
    if x is None:
        x=range(len(y))
    if yerr is None:    
        ax.plot(x,y, marker=marker,color=color,ls=ls,label= legend, lw=lw)#,*argv,**kwargs)
    else:
        ax.errorbar(x,y,yerr, marker=marker,color=color,ls=ls,label= legend, lw=lw)#,*argv,**kwargs)
    if logx:
        ax.set_xscale('log')
    if logy:
        ax.set_yscale('log')
    if logxy:
        ax.set_xscale('log')
        ax.set_yscale('log')
         
 
    
    if 'xlim' in kwargs.keys():
         ax.set_xlim(    kwargs['xlim']  )    
    if 'ylim' in kwargs.keys():
         ax.set_ylim(    kwargs['ylim']  )
    if 'xlabel' in kwargs.keys():            
        ax.set_xlabel(kwargs['xlabel'])
    if 'ylabel' in kwargs.keys():            
        ax.set_ylabel(kwargs['ylabel'])
        
    if 'title' in kwargs.keys():
        title =  kwargs['title']
    else:
        title =  'plot'
    ax.set_title( title ) 
    #ax.set_xlabel("$Log(q)$"r'($\AA^{-1}$)')    
    ax.legend(loc = 'best', fontsize=legend_size )
    if 'save' in kwargs.keys():
        if  kwargs['save']: 
            #dt =datetime.now()
            #CurTime = '%s%02d%02d-%02d%02d-' % (dt.year, dt.month, dt.day,dt.hour,dt.minute)         
            #fp = kwargs['path'] + '%s'%( title ) + CurTime + '.png'  
            fp = kwargs['path'] + '%s'%( title )   + '.png' 
            plt.savefig( fp, dpi=fig.dpi)         
    if return_fig:
        return fig

def get_data(scan_id, field='ivu_gap', intensity_field='elm_sum_all', det=None, debug=False):
    """Get data from the scan stored in the table.
from Maksim
    :param scan_id: scan id from bluesky.
    :param field: visualize the intensity vs. this field.
    :param intensity_field: the name of the intensity field.
    :param det: the name of the detector.
    :param debug: a debug flag.
    :return: a tuple of X, Y and timestamp values.
    """
    scan, t = get_scan(scan_id)
    if det:
        imgs = get_images(scan, det)
        im = imgs[-1]
        if debug:
            print(im)

    table = get_table(scan)
    fields = get_fields(scan)

    if debug:
        print(table)
        print(fields)
    x = table[field]
    y = table[intensity_field]

    return x, y, t


def get_scan(scan_id, debug=False):
    """Get scan from databroker using provided scan id.
from Maksim
    :param scan_id: scan id from bluesky.
    :param debug: a debug flag.
    :return: a tuple of scan and timestamp values.
    """
    scan = db[scan_id]
    #t = datetime.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')
    #t = dtt.datetime.fromtimestamp(scan['start']['time']).strftime('%Y-%m-%d %H:%M:%S')
    t='N.A. conflicting with other macro'
    if debug:
        print(scan)
    print('Scan ID: {}  Timestamp: {}'.format(scan_id, t))
    return scan, t

def ps(uid='-1',det='default',suffix='default',shift=.5,logplot='off',figure_number=999):
    '''
    function to determine statistic on line profile (assumes either peak or erf-profile)\n
    calling sequence: uid='-1',det='default',suffix='default',shift=.5)\n
    det='default' -> get detector from metadata, otherwise: specify, e.g. det='eiger4m_single'\n
    suffix='default' -> _stats1_total / _sum_all, otherwise: specify, e.g. suffix='_stats2_total'\n
    shift: scale for peak presence (0.5 -> peak has to be taller factor 2 above background)\n
    figure_number: default=999 -> specify figure number for plot
    '''
    #import datetime
    #import time
    #import numpy as np
    #from PIL import Image
    #from databroker import db, get_fields, get_images, get_table
    #from matplotlib import pyplot as pltfrom
    #from lmfit import  Model
    #from lmfit import minimize, Parameters, Parameter, report_fit
    #from scipy.special import erf
    
    # get the scan information:
    if uid == '-1':
        uid=-1
    h=db[uid]
    if det == 'default':
        if h.start['detectors'][0] == 'elm' and suffix=='default':
            intensity_field='elm_sum_all'
        elif h.start['detectors'][0] == 'elm':
            intensity_field='elm'+suffix
        elif suffix == 'default':
            intensity_field= h.start['detectors'][0]+'_stats1_total'
        else:
            intensity_field= h.start['detectors'][0]+suffix
    else:
        if det=='elm' and suffix == 'default':
            intensity_field='elm_sum_all'
        elif det=='elm':
            intensity_field = 'elm'+suffix
        elif suffix == 'default':
            intensity_field=det+'_stats1_total'
        else:
            intensity_field=det+suffix 
            
    field = h.start['motors'][0]    
    
    #field='dcm_b';intensity_field='elm_sum_all'
    [x,y,t]=get_data(uid,field=field, intensity_field=intensity_field, det=None, debug=False)  #need to re-write way to get data
    x=np.array(x)
    y=np.array(y)

    x = np.nan_to_num(x)
    y = np.nan_to_num(y)
    
    PEAK=x[np.argmax(y)]
    PEAK_y=np.max(y)
    COM=np.sum(x * y) / np.sum(y)
    
    ### from Maksim: assume this is a peak profile:
    def is_positive(num):
        return True if num > 0 else False

    # Normalize values first:
    ym = (y - np.min(y)) / (np.max(y) - np.min(y)) - shift  # roots are at Y=0

    positive = is_positive(ym[0])
    list_of_roots = []
    for i in range(len(y)):
        current_positive = is_positive(ym[i])
        if current_positive != positive:
            list_of_roots.append(x[i - 1] + (x[i] - x[i - 1]) / (abs(ym[i]) + abs(ym[i - 1])) * abs(ym[i - 1]))
            positive = not positive
    if len(list_of_roots) >= 2:
        FWHM=abs(list_of_roots[-1] - list_of_roots[0])
        CEN=list_of_roots[0]+0.5*(list_of_roots[1]-list_of_roots[0])
        ps.fwhm=FWHM
        ps.cen=CEN
        #return {
        #    'fwhm': abs(list_of_roots[-1] - list_of_roots[0]),
        #    'x_range': list_of_roots,
        #}
    else:    # ok, maybe it's a step function..
        print('no peak...trying step function...')  
        ym = ym + shift
        def err_func(x, x0, k=2, A=1,  base=0 ):     #### erf fit from Yugang
            return base - A * erf(k*(x-x0))
        mod = Model(  err_func )
        ### estimate starting values:
        x0=np.mean(x)
        #k=0.1*(np.max(x)-np.min(x))
        pars  = mod.make_params( x0=x0, k=2,  A = 1., base = 0. ) 
        result = mod.fit(ym, pars, x = x )
        CEN=result.best_values['x0']
        FWHM = result.best_values['k']
        ps.cen = CEN
        ps.fwhm = FWHM

    ### re-plot results:   
    if logplot=='on':
        plt.close(figure_number)
        plt.figure(figure_number)
        plt.semilogy([PEAK,PEAK],[np.min(y),np.max(y)],'k--',label='PEAK')
        #plt.hold(True)
        plt.semilogy([CEN,CEN],[np.min(y),np.max(y)],'r-.',label='CEN')
        plt.semilogy([COM,COM],[np.min(y),np.max(y)],'g.-.',label='COM')
        plt.semilogy(x,y,'bo-')
        plt.xlabel(field);plt.ylabel(intensity_field)
        plt.legend()
        plt.title('uid: '+str(uid)+' @ '+str(t)+'\nPEAK: '+str(PEAK_y)[:8]+' @ '+str(PEAK)[:8]+'   COM @ '+str(COM)[:8]+ '\n FWHM: '+str(FWHM)[:8]+' @ CEN: '+str(CEN)[:8],size=9)
        plt.show()    
    else:
        plt.close(figure_number)
        plt.figure(figure_number)
        plt.plot([PEAK,PEAK],[np.min(y),np.max(y)],'k--',label='PEAK')
        #plt.hold(True)
        plt.plot([CEN,CEN],[np.min(y),np.max(y)],'r-.',label='CEN')
        plt.plot([COM,COM],[np.min(y),np.max(y)],'g.-.',label='COM')
        plt.plot(x,y,'bo-')
        plt.xlabel(field);plt.ylabel(intensity_field)
        plt.legend()
        plt.title('uid: '+str(uid)+' @ '+str(t)+'\nPEAK: '+str(PEAK_y)[:8]+' @ '+str(PEAK)[:8]+'   COM @ '+str(COM)[:8]+ '\n FWHM: '+str(FWHM)[:8]+' @ CEN: '+str(CEN)[:8],size=9)
        plt.show()
    
    ### assign values of interest as function attributes:
    ps.peak=PEAK
    ps.com=COM

 
	




def fit_gisaxs_height_scan_profile( uid='-1', x0=0, k=2, A=1, base=0, 
                             motor = 'diff_yh', det =  'eiger4m_single_stats1_total' ):

    '''Fit a GiSAXS scan (diff.yh scan) by a error function
    
       The scan data is first normlized by a simple normalization function:
            (y - y.min()) / (y.max() - y.min())        
       Then fit by error function is defined as  base - A * erf(k*(x-x0))
           erf is Error function is defined by 2/sqrt(pi)*integral(exp(-t**2), t=0..z)
           erf function is import: from scipy.special import erf
       
       Parameters:
           x0: the fit center, by default, 0
           k: the strech factor, by default 2
           A: amplitude of the scan, default 1
           base: baseline of the scan, default 0
       
           uid: the uid of the scan, by default is -1, i.e., the last scan
           motor: the scan motor, by default 'diff.yh'
           det: detector, by default is 'eiger4m_single_stats1_total'
      return:
           the plot of scan and fitted curve
           the fitted x0      
    '''
    
    from lmfit import  Model
    from lmfit import minimize, Parameters, Parameter, report_fit
    from scipy.special import erf
    def norm_y(y ):
        return (y - y.min()) / (y.max() - y.min())
    def err_func(x, x0, k=2, A=1,  base=0 ):        
        return base - A * erf(k*(x-x0))
    
    mod = Model(  err_func )
    pars  = mod.make_params( x0=x0, k=k,  A = A, base = base )    
    if uid == '-1':
        uid = -1
    x = np.array( get_table( db[uid],  fields = [motor],  )[motor] ) 
    y = np.array( get_table( db[uid],  fields = [det],  )[det] )
    ym = norm_y(y)    
    result = mod.fit(ym, pars, x = x )
    
    fig, ax = plt.subplots()
    plot1D( x=x, y = ym, m='o', c='k', ls ='', legend='scan',ax=ax,)
    plot1D( x=x, y = result.best_fit,m='', c='r', ls='-',  legend='fit-x0=%s'%result.best_values['x0'],ax=ax,)
    
    return result.best_values['x0']


def trans_data_to_pd(data, label=None,dtype='array'):
    '''
    convert data into pandas.DataFrame
    Input:
        data: list or np.array
        label: the coloum label of the data
        dtype: list or array
    Output:
        a pandas.DataFrame
    '''
    #lists a [ list1, list2...] all the list have the same length
    from numpy import arange,array
    import pandas as pd,sys    
    if dtype == 'list':
        data=array(data).T        
    elif dtype == 'array':
        data=array(data)        
    else:
        print("Wrong data type! Now only support 'list' and 'array' tpye")        
    N,M=data.shape    
    #print( N, M)
    index =  arange( N )
    if label is None:label=['data%s'%i for i in range(M)]
    #print label
    df = pd.DataFrame( data, index=index, columns= label  )
    return df


def export_scan_scalar( uid, x='dcm_b', y= ['xray_eye1_stats1_total'],
                       path='/XF11ID/analysis/2016_3/commissioning/Results/exported/' ):
    '''export uid data to a txt file
    uid: unique scan id
    x: the x-col 
    y: the y-cols
    path: save path
    Example:
        data = export_scan_scalar( uid, x='dcm_b', y= ['xray_eye1_stats1_total'],
                       path='/XF11ID/analysis/2016_3/commissioning/Results/exported/' )
    A plot for the data:
        d.plot(x='dcm_b', y = 'xray_eye1_stats1_total', marker='o', ls='-', color='r')
        
    '''
    from databroker import DataBroker as db, get_images, get_table, get_events, get_fields 
    #from chxanalys.chx_generic_functions import  trans_data_to_pd
    import numpy as np
    hdr = db[uid]
    print( get_fields( hdr ) )
    data = get_table( db[uid] )
    xp = data[x]
    datap = np.zeros(  [len(xp), len(y)+1])
    datap[:,0] = xp
    for i, yi in enumerate(y):
        datap[:,i+1] = data[yi]
        
    datap = trans_data_to_pd( datap, label=[x] + [yi for yi in y])   
    fp = path + 'uid=%s.csv'%uid
    datap.to_csv( fp )
    print( 'The data was saved in %s'%fp)
    return datap




import bluesky.plans as bp

############
##################
####
def plot_reflectivity(db_si,db_rh, default_path='/home/xf11id/.ipython/profile_collection/data_files/'):
	"""
	by LW 10/04/2016
	plot measured reflectivity R_Si / R_Rh against theoretical curve for 0.18deg incident angle
	calling sequence: plot_reflectivity(db_si,db_rh)
	db_si: data brooker object for reflectivity scan (E_scan) from Si layer; db_rh: same for Rh layer
	Notes: 1) assumes E_scan was used to obtain the data
	2) same scan range and number of data points for both scans (does not interpolate to common x-grid)
	3) use Ti foil in BPM for scan on elm detector
	"""
	si_dat=get_table(db_si)
	rh_dat=get_table(db_rh)
	en_r=xf.get_EBragg('Si111cryo',-si_dat.dcm_b)
	plt.figure(19)
	plt.semilogy(en_r,si_dat.elm_sum_all/rh_dat.elm_sum_all,label='measured')
	#plt.hold(True)
	r_eng=np.array(np.loadtxt(default_path+"R_Rh_0p180.txt"))[:,0]/1e3
	rsi_0p18=np.array(np.loadtxt(default_path+"R_Si_0p180.txt"))[:,1]
	rrh_0p18=np.array(np.loadtxt(default_path+"R_Rh_0p180.txt"))[:,1]
	plt.semilogy(r_eng,rsi_0p18/rrh_0p18,'r--',label="calc 0.18 deg")
	plt.xlabel('E [keV]')
	plt.ylabel('R_Si / R_Rh')
	plt.grid()
	plt.legend()


def E_calibration(file,Edge='Cu',xtal='Si111cryo',B_off=0):
    """
    by LW 3/25/2015
    function to read energy scan file and determine offset correction
    calling sequence: E_calibration(file,Edge='Cu',xtal='Si111cryo',B_off=0)
    file: path/filename of experimental data; 'ia' opens interactive dialog; file can be databrooker object, e.g. file=db[-1] t process data from last scan
    Edge: elment used for calibration
    xtal: monochromator crystal under calibration
    B_off (optional): apply offset to Bragg angle data
    currently there is no check on input parameters!
    """
    # read the data file 
    import csv
    import numpy as np
    import matplotlib.pyplot as plt
    #import xfuncs as xf
    #import Tkinter, tkFileDialog
        
    if file=='ia':          # open file dialog
        print('this would open a file input dialog IF Tkinter was available in the $%^& python environment as it used to')
        #root = Tkinter.Tk()
        #root.withdraw()
        #file_path = tkFileDialog.askopenfilename()
        description=file_path
    elif isinstance(file, str) and file!='ia':
        file_path=file
        descritpion=file_path
    #elif isinstance(file,dict) and 'start' in file.keys():	# some genius decided that db[-1] is no longer a dictionary....
    elif 'start' in file.keys():
       databroker_object=1
       description='scan # ',file.start['scan_id'],' uid: ', file.start['uid'][:10]
    plt.close("all")
    Edge_data={'Cu': 8.979, 'Ti': 4.966}
    if databroker_object !=1:
       Bragg=[]
       Gap=[]
       Intensity=[]
       with open(file_path, 'rb') as csvfile:
           filereader = csv.reader(csvfile, delimiter=' ')
           filereader.next()   # skip header lines
           filereader.next()
           filereader.next()
           for row in filereader:              # read data
               try: Bragg.append(float(row[2]))
               except: print('could not convert: ',row[2])
               try: Gap.append(float(row[5]))
               except: print('could not convert: ',row[5])
               try: Intensity.append(float(row[7]))
               except: print('could not convert: ',row[8])
    elif databroker_object==1:
       data = get_table(file)
       Bragg = data.dcm_b[1:]     #retrive the data (first data point is often "wrong", so don't use
       #Gap = data.SR:C11-ID:G1{IVU20:1_readback[1:] name is messed up in databroker -> currently don't use gap
       Intensity = data.elm_sum_all [1:] 			#need to find signal from electrometer...elm is commented out in detectors at the moment...???														


    B=np.array(Bragg)*-1.0+B_off
    #G=np.array(Gap[0:len(B)])   # not currently used, but converted for future use
    Int=np.array(Intensity[0:len(B)])
        
    # normalize and remove background:
    Int=Int-min(Int)
    Int=Int/max(Int)

    plt.figure(1)
    plt.plot(B,Int,'ko-',label='experimental data')
    plt.plot([get_Bragg(xtal,Edge_data[Edge])[0],get_Bragg(xtal,Edge_data[Edge])[0]],[0,1],'r--',label='Edge for: '+Edge) # NOTE: using local get_Bragg for now
    plt.legend(loc='best')
    plt.xlabel(r'$\theta_B$ [deg.]')
    plt.ylabel('intensity')
    plt.title(['Energy Calibration using: ',description])
    plt.grid()
        
    plt.figure(2)
    Eexp=xf.get_EBragg(xtal,B)
    plt.plot(Eexp,Int,'ko-',label='experimental data')
    plt.plot([Edge_data[Edge],Edge_data[Edge]],[0,1],'r--',label='Edge for: '+Edge)
    plt.legend(loc='best')
    plt.xlabel('E [keV.]')
    plt.ylabel('intensity')
    plt.title(['Energy Calibration using: ',description])
    plt.grid()
        
    # calculate derivative and analyze:
    Bragg_Edge=get_Bragg(xtal,Edge_data[Edge])[0]
    plt.figure(3)
    diffdat=np.diff(Int)
    plt.plot(B[0:len(diffdat)],diffdat,'ko-',label='diff experimental data')
    plt.plot([Bragg_Edge,Bragg_Edge],[min(diffdat),max(diffdat)],'r--',label='Edge for: '+Edge)
    plt.legend(loc='best')
    plt.xlabel(r'$\theta_B$ [deg.]')
    plt.ylabel('diff(int)')
    plt.title(['Energy Calibration using: ',description])
    plt.grid()
        
    plt.figure(4)
    plt.plot(xf.get_EBragg(xtal,B[0:len(diffdat)]),diffdat,'ko-',label='diff experimental data')
    plt.plot([Edge_data[Edge],Edge_data[Edge]],[min(diffdat),max(diffdat)],'r--',label='Edge for: '+Edge)
    plt.legend(loc='best')
    plt.xlabel('E [keV.]')
    plt.ylabel('diff(int)')
    plt.title(['Energy Calibration using: ',description])
    plt.grid()
        
    edge_index=np.argmax(diffdat)
    B_edge=get_Bragg(xtal,Edge_data[Edge])[0]
        
    print('') 
    print('Energy calibration for: ',description)
    print('Edge used for calibration: ',Edge)
    print('Crystal used for calibration: ',xtal)
    print('Bragg angle offset: ', B_edge-B[edge_index],'deg. (CHX coordinate system: ',-(B_edge-B[edge_index]),'deg.)')
    print('=> move Bragg to ',-B[edge_index],'deg. and set value to ',-Bragg_Edge,'deg.')
    print( 'Energy offset: ',Eexp[edge_index]-Edge_data[Edge],' keV')

def dcm_roll(Bragg,offset,distance,offmode='mm',pixsize=5.0):
    """
    by LW 03/27/2015
    function to calculate Roll correction on the DCM
    calling sequence: dcm_roll(Bragg,offset,distance,offmode='mm',pixsize=5.0)
    Bragg: set of Bragg angles [use negative values, as in beamline coordinate system!!!]
    offset: set of corresponding offsets
    offmode: units of offsets = mm or pixel (default:'mm')
    pixsize: pixel size for offset conversion to mm, if offsets are given in pixels
    default is 5um (pixsize is ignored, if offmode is 'mm')
    distance: DCM center of 1st xtal to diagnostic/slit [mm]
    preset distances available: 'dcm_bpm',dcm_mbs', 'dcm_bds', 'dcm_sample', 'dcm_s1' (pre-kinoform slit)
    """
    import numpy as np
    from scipy import optimize
    from matplotlib import pyplot as plt
    Bragg=np.array(Bragg)
    if offmode=='mm':
        offset=np.array(offset)
    elif offmode=='pixel':
        offset=np.array(offset)*pixsize/1000.0
    else: raise CHX_utilities_Exception('Eror: offmode must be either "mm" or "pixel"')
    if distance=='dcm_bpm':    
        d=3000.0 # distance dcm-bpm in mm
    elif distance=='dcm_mbs':
        d=2697.6 #distance dcm-mbs in mm
    elif distance=='dcm_sample':
        d=16200 #distance dcm-sample in mm
    elif distance=='dcm_bds':
        d=15500 #distance dcm-bds in mm
    elif distance=='dcm_s1':
        d=12155 #distance dcm-s1 (pre-kinoform slit)
    else:
        try:
            d=float(distance)
        except:
            raise CHX_utilities_Exception('Eror: distance must be a recognized string or numerical value')    
        
    # data fitting    
    fitfunc = lambda p, x: p[0]+2*d*p[1]*np.sin(x/180.*np.pi) # Target function
    errfunc = lambda p, x, y: fitfunc(p, Bragg) - y # Distance to the target function
    p0 = [np.mean(offset), -.5] # Initial guess for the parameters
    p1, success = optimize.leastsq(errfunc, p0[:], args=(Bragg, offset))
    
    # plotting the result:    
    plt.close(1)    
    plt.figure(1)
    B = np.linspace(Bragg.min(), Bragg.max(), 100)
    plt.plot(Bragg,offset,'ro',label='measured offset')
    plt.plot(B,fitfunc(p1,B),'k-',label=r'$x_o$+2*D*$\Delta$$\Phi$*sin($\theta_B$)')
    plt.legend(loc='best')
    plt.ylabel('beam offset [mm]')
    plt.xlabel('Bragg angle  [deg.]')
    print('x_0= ',p1[0],'mm')
    print('\Delta \Phi= ',p1[1]*180.0/np.pi,'deg')
    print('movr(dcm.r,'+str(p1[1]*-180.0/np.pi)+')')
    

def get_ID_calibration_dan(gapstart,gapstop,gapstep=.2,gapoff=0):
    """
    by LW 04/20/2015
    function to automatically take a ID calibration curve_fit
    calling sequence: get_ID_calibration(gapstart,gapstop,gapstep=.2,gapoff=0)
	gapstart: minimum gap used in calibration (if <5.2, value will be set to 5.2)
	gapstop: maximum gap used in calibration
	gapstep: size of steps between two gap points
	gapoff: offset applied to calculation gap vs. energy from xfuncs.get_Es(gap-gapoff)
	thermal management of Bragg motor is automatic, waiting for cooling <80C between Bragg scans
    writes outputfile with fitted value for the center of the Bragg scan to:  '/home/xf11id/Repos/chxtools/chxtools/X-ray_database/
	changes 03/18/2016: made compatible with python V3 and latest versio of bluesky (working on it!!!)
    """
    import numpy as np
    #import xfuncs as xf
    #from dataportal import DataBroker as db, StepScan as ss, DataMuxer as dm
    import time
    from epics import caput, caget
    from matplotlib import pyplot as plt
    from scipy.optimize import curve_fit
    gaps = np.arange(gapstart, gapstop, gapstep) - gapoff   # not sure this should be '+' or '-' ...
    print('ID calibration will contain the following gaps [mm]: ',gaps)
    xtal_map = {1: 'Si111cryo', 2: 'Si220cryo'}
    pos_sts_pv = 'XF:11IDA-OP{Mono:DCM-Ax:X}Pos-Sts'
    try:
        xtal = xtal_map[caget(pos_sts_pv)]
    except KeyError:
        raise CHX_utilities_Exception('error: trying to do ID gap calibration with no crystal in the beam')
    print('using', xtal, 'for ID gap calibration')
    # create file for writing calibration data:
    fn='id_CHX_IVU20_'+str(time.strftime("%m"))+str(time.strftime("%d"))+str(time.strftime("%Y"))+'.dat'
    fpath='/tmp/'
    # fpath='/home/xf11id/Repos/chxtools/chxtools/X-ray_database/'
    try:
        outFile = open(fpath+fn, 'w')
        outFile.write('% data from measurements '+str(time.strftime("%D"))+'\n')
        outFile.write('% K colkumn is a placeholder! \n')
        outFile.write('% ID gap [mm]     K      E_1 [keV] \n')
        outFile.close()
        print('successfully created outputfile: ',fpath+fn)
    except:
        raise CHX_utilities_Exception('error: could not create output file')
    
    ### do the scanning and data fitting, file writing,....
    t_adjust=0
    center=[]
    E1=[]
    realgap=[]
    detselect(xray_eye1)
    print(gaps)
    MIN_GAP = 5.2
    for i in gaps:
        if i >= MIN_GAP: 
            B_guess=-1.0*xf.get_Bragg(xtal,xf.get_Es(i+gapoff,5)[1])[0]
        else:
            i = MIN_GAP 
            B_guess=-1.0*xf.get_Bragg(xtal,xf.get_Es(i,5)[1])[0]
        if i > 8 and t_adjust == 0:     # adjust acquistion time once while opening the gap (could write something more intelligent in the long run...)
           exptime=caget('XF:11IDA-BI{Bpm:1-Cam:1}cam1:AcquireTime')
           caput('XF:11IDA-BI{Bpm:1-Cam:1}cam1:AcquireTime',2*exptime)
           t_adjust = 1
        print('initial guess: Bragg= ',B_guess,' deg.   ID gap = ',i,' mm')
        es = xf.get_Es(i, 5)[1]
        mirror_stripe_pos = round(caget('XF:11IDA-OP{Mir:HDM-Ax:Y}Mtr.VAL'),1)
        SI_STRIPE = -7.5
        RH_STRIPE = 7.5
        if es < 9.5:
            stripe = SI_STRIPE
        elif es >= 9.5:
            stripe = RH_STRIPE
        yield from bp.abs_set(hdm.y, stripe)
        yield from bp.abs_set(foil_y, 0)  # Put YAG in beam.
        print('moving DCM Bragg angle to:', B_guess ,'deg and ID gap to', i, 'mm')
        yield from bp.abs_set(dcm.b, B_guess)
        yield from bp.abs_set(ivu_gap,i)
        print('hurray, made it up to here!')
        print('about to collect data')
        yield from ascan(dcm.b, float(B_guess-.4), float(B_guess+.4), 60,
                         md={'plan_name': 'ID_calibration',
                             'mirror_stripe': stripe})
        header = db[-1]					#retrive the data (first data point is often "wrong", so don't use
        data = get_table(header)
        B = data.dcm_b[2:]
        intdat = data.xray_eye1_stats1_total[2:] 																	
        B=np.array(B)
        intdat=np.array(intdat)
        A=np.max(intdat)          # initial parameter guess and fitting
        xc=B[np.argmax(intdat)]
        w=.2
        yo=np.mean(intdat)
        p0=[yo,A,xc,w]
        print('initial guess for fitting: ',p0)
        try:
            coeff,var_matrix = curve_fit(gauss,B,intdat,p0=p0)
            center.append(coeff[2])
            E1.append(xf.get_EBragg(xtal,-coeff[2])/5.0)
            realgap.append(caget('SR:C11-ID:G1{IVU20:1-LEnc}Gap'))
#   # append data file by i, 1 & xf.get_EBragg(xtal,-coeff[2]/5.0):
            with open(fpath+fn, "a") as myfile:
                myfile.write(str(caget('SR:C11-ID:G1{IVU20:1-LEnc}Gap'))+'    1.0 '+str(float(xf.get_EBragg(xtal,-coeff[2])/5.0))+'\n')
            print('added data point: ',caget('SR:C11-ID:G1{IVU20:1-LEnc}Gap'),' ',1.0,'     ',str(float(xf.get_EBragg(xtal,-coeff[2])/5.0)))
        except: print('could not evaluate data point for ID gap = ',i,' mm...data point skipped!')
        while caget('XF:11IDA-OP{Mono:DCM-Ax:Bragg}T-I') > 80:
            time.sleep(30)
            print('DCM Bragg axis too hot (>80C)...waiting...')
    plt.close(234)
    plt.figure(234)
    plt.plot(E1,realgap,'ro-')
    plt.xlabel('E_1 [keV]')
    plt.ylabel('ID gap [mm]')
    plt.title('ID gap calibration in file: '+fpath+fn,size=12)
    plt.grid()
 
def get_ID_calibration(gapstart,gapstop,gapstep=.2,gapoff=0):
    """
    by LW 04/20/2015

    function to automatically take a ID calibration curve_fit
    calling sequence: get_ID_calibration(gapstart,gapstop,gapstep=.2,gapoff=0)
	gapstart: minimum gap used in calibration (if <5.2, value will be set to 5.2)

	gapstop: maximum gap used in calibration
	gapstep: size of steps between two gap points
	gapoff: offset applied to calculation gap vs. energy from xfuncs.get_Es(gap-gapoff)

	thermal management of Bragg motor is automatic, waiting for cooling <80C between Bragg scans
    writes outputfile with fitted value for the center of the Bragg scan to:  '/home/xf11id/Repos/chxtools/chxtools/X-ray_database/
	changes 03/18/2016: made compatible with python V3 and latest versio of bluesky (working on it!!!)

    """
    import numpy as np
    #import xfuncs as xf
    #from dataportal import DataBroker as db, StepScan as ss, DataMuxer as dm
    import time
    from epics import caput, caget
    from matplotlib import pyplot as plt
    from scipy.optimize import curve_fit
    gaps = np.arange(gapstart, gapstop, gapstep) - gapoff   # not sure this should be '+' or '-' ...
    print('ID calibration will contain the following gaps [mm]: ',gaps)
    xtal_map = {1: 'Si111cryo', 2: 'Si220cryo'}
    pos_sts_pv = 'XF:11IDA-OP{Mono:DCM-Ax:X}Pos-Sts'
    try:
        xtal = xtal_map[caget(pos_sts_pv)]
    except KeyError:
        raise CHX_utilities_Exception('error: trying to do ID gap calibration with no crystal in the beam')
    print('using', xtal, 'for ID gap calibration')
    # create file for writing calibration data:
    fn='id_CHX_IVU20_'+str(time.strftime("%m"))+str(time.strftime("%d"))+str(time.strftime("%Y"))+'.dat'
    #fpath='/tmp/'
    fpath='/home/xf11id/Repos/chxtools/chxtools/X-ray_database/'
    try:
        outFile = open(fpath+fn, 'w')
        outFile.write('% data from measurements '+str(time.strftime("%D"))+'\n')
        outFile.write('% K colkumn is a placeholder! \n')
        outFile.write('% ID gap [mm]     K      E_1 [keV] \n')
        outFile.close()
        print('successfully created outputfile: ',fpath+fn)
    except:
        raise CHX_utilities_Exception('error: could not create output file')
    
    ### do the scanning and data fitting, file writing,....
    t_adjust=0
    center=[]
    E1=[]
    realgap=[]
    detselect(xray_eye1)
    print(gaps)
    MIN_GAP = 5.2
    for i in gaps:
        if i >= MIN_GAP: 
            B_guess=-1.0*xf.get_Bragg(xtal,xf.get_Es(i+gapoff,5)[1])[0]
        else:
            i = MIN_GAP 
            B_guess=-1.0*xf.get_Bragg(xtal,xf.get_Es(i,5)[1])[0]
        if i > 8 and t_adjust == 0:     # adjust acquistion time once while opening the gap (could write something more intelligent in the long run...)
           exptime=caget('XF:11IDA-BI{Bpm:1-Cam:1}cam1:AcquireTime')
           caput('XF:11IDA-BI{Bpm:1-Cam:1}cam1:AcquireTime',2*exptime)
           t_adjust = 1
        print('initial guess: Bragg= ',B_guess,' deg.   ID gap = ',i,' mm')
        es = xf.get_Es(i, 5)[1]
        mirror_stripe_pos = round(caget('XF:11IDA-OP{Mir:HDM-Ax:Y}Mtr.VAL'),1)
        SI_STRIPE = -7.5 
        RH_STRIPE = 7.5
        if es < 9.5:
            stripe = SI_STRIPE
        elif es >= 9.5:
            stripe = RH_STRIPE
        mov(hdm.y, stripe)
        mov(foil_y, 0)  # Put YAG in beam.
        print('moving DCM Bragg angle to:', B_guess ,'deg and ID gap to', i, 'mm')
        #RE(bp.abs_set(dcm.b, B_guess))
        mov(dcm.b, B_guess)
        #RE(bp.abs_set(ivu_gap,i))
        mov(ivu_gap,i)
        print('hurray, made it up to here!')
        print('about to collect data')
        RE(ascan(dcm.b, float(B_guess-.4), float(B_guess+.4), 60))
        header = db[-1]					#retrive the data (first data point is often "wrong", so don't use
        data = get_table(header)
        B = data.dcm_b[2:]
        intdat = data.xray_eye1_stats1_total[2:] 																	
        B=np.array(B)
        intdat=np.array(intdat)
        A=np.max(intdat)          # initial parameter guess and fitting
        xc=B[np.argmax(intdat)]
        w=.2
        yo=np.mean(intdat)
        p0=[yo,A,xc,w]
        print('initial guess for fitting: ',p0)
        pss = 0
        try:
            coeff,var_matrix = curve_fit(gauss,B,intdat,p0=p0)        
            #center.append(coeff)
            #E1.append(xf.get_EBragg(xtal,-coeff)/5.0)
            realgap.append(caget('SR:C11-ID:G1{IVU20:1-LEnc}Gap'))
#   # append data file by i, 1 & xf.get_EBragg(xtal,-coeff/5.0):
            print('passed the Gaussian trial fit, will use ps now to write data')
            ps()  #this should always work
            Bvalue = ps.cen
            E1.append(xf.get_EBragg(xtal,-Bvalue)/5.0)
            center.append(Bvalue) 
            with open(fpath+fn, "a") as myfile:
                myfile.write(str(caget('SR:C11-ID:G1{IVU20:1-LEnc}Gap'))+'    1.0 '+str(float(xf.get_EBragg(xtal,-Bvalue)/5.0))+'\n')
            print('added data point: ',caget('SR:C11-ID:G1{IVU20:1-LEnc}Gap'),' ',1.0,'     ',str(float(xf.get_EBragg(xtal,-Bvalue)/5.0)))
        except: print('could not evaluate data point for ID gap = ',i,' mm...data point skipped!')
        while caget('XF:11IDA-OP{Mono:DCM-Ax:Bragg}T-I') > 80:
            time.sleep(30)
            print('DCM Bragg axis too hot (>80C)...waiting...')
    plt.close(234)
    plt.figure(234)
    plt.plot(E1,realgap,'ro-')
    plt.xlabel('E_1 [keV]')
    plt.ylabel('ID gap [mm]')
    plt.title('ID gap calibration in file: '+fpath+fn,size=12)
    plt.grid()
   
        
class CHX_utilities_Exception(Exception):
    pass
    """
    by LW 03/19/2015
    class to raise utilities functions specific exceptions
    """   

def retrieve_latest_scan(uid='-1',det='default',suffix='default'):
    '''
        (From Lutz 95-utilities.py)
        Retrieve the latest scan results.

        Returns the x,y of scan

    '''
    # get the scan information:
    if uid == '-1':
        uid=-1
    if det == 'default':
        if db[uid].start.detectors[0] == 'elm' and suffix=='default':
            intensity_field='elm_sum_all'
        elif db[uid].start.detectors[0] == 'elm':
            intensity_field='elm'+suffix
        elif suffix == 'default':
            intensity_field= db[uid].start.detectors[0]+'_stats1_total'
        else:
            intensity_field= db[uid].start.detectors[0]+suffix
    else:
        if det=='elm' and suffix == 'default':
            intensity_field='elm_sum_all'
        elif det=='elm':
            intensity_field = 'elm'+suffix
        elif suffix == 'default':
            intensity_field=det+'_stats1_total'
        else:
            intensity_field=det+suffix 
            
    field = db[uid].start.motors[0]    
    
    #field='dcm_b';intensity_field='elm_sum_all'
    [x,y,t]=get_data(uid,field=field, intensity_field=intensity_field, det=None, debug=False)  #need to re-write way to get data
    x=np.array(x)
    y=np.array(y)
    return x, y


def get_Bragg(reflection,E=8.):
    """
     by LW 17/03/2010
     function return the Bragg angle [deg.] of a given material and reflection at a given Energy.
     Calling sequence: thetaB=get_Bragg(reflection,E),  thetaB(1)=Bragg angle[deg.] thetaB(2)=dhkl [A], thetaB(3)=I/Io [%].
     E: x-ray energy in keV (can be an array of energies),
     reflection: string, e.g. 'Si111'. Reflections implemented from http://database.iem.ac.ru/mincryst, T=25C or calculated from XOP, e.g for Si111&Si220 @80K
     type get_Bragg(\'reflections?\') for a list of currently availabel materials;
     """
    reflstr=['Si111cryo','Si220cryo','Si111', 'Si220', 'Si113', 'Si224', 'Si331', 'Si400','Ge111', 'Ge220', 'Ge113', 'Ge224', 'Ge331', 'Ge620', 'Ge531', 'Ge400', 'Ge115', 'Ge335','Ge440', 'Ge444', 'Ge333', 'C111', 'C220']
    dspace=np.array([3.13379852,1.91905183,3.13542,1.92004,1.63742,1.10854,1.24589,1.35767,3.26627,2.00018,1.70576,1.15480,1.29789,0.89451,0.95627,1.41434,1.08876,0.86274,1.00009,0.81657,1.08876,2.05929,1.26105])
    Irel=np.array([100,67.80,40.50,23.80,16.60,10.90,100,73.80,44.10,23.10,17.00,15.90,15.70,11.50,9.80,8.50,8.20,7.30,3.30,100,39.00])
    if isinstance(reflection, str): # and all(isinstance(E, (int, long, float, complex)) for item in [E,E]): # <- bug in python: check for E is numeric works in standalone function, but not in this package => don't check
        E=np.array(E)
        lam=xf.get_Lambda(E,'A')
        if reflection in reflstr:
            ind=reflstr.index(reflection)
            print (reflstr[ind] +': d_{hkl}=' + "%3.4f" %dspace[ind] +'A   I/I_o='+ "%3.4f" %Irel[ind])
            theta=np.degrees(np.arcsin(lam/2/dspace[ind]))
            ds=[];I=[]
            for l in range(0,np.size(theta)):
                ds.append(dspace[ind])
                I.append(Irel[ind])
            #return theta, ds,I
            res=np.array([np.array([theta]),np.array(ds),np.array(I)])
            return res.T
        elif reflection=='reflections?':
            print ('List of available reflections (T=25C):')
            print (reflstr )
        else: print ('error: reflection not found. Type get_Bragg("reflections?") for list of available reflections.')
    else: print ('error: reflection has to be a string and E needs to be numeric. Type get_Bragg? for help')
