def set_lm(motor,lowlimit,highlimit,verbose=False):
    """
    set limits on a single axis
    motor: str, opyd object representing motorized axis, e.g. 'diff.xh'
    lowlimit: float or None -> set low limit (user SP) to lowlimit, if None, don't change existing limit
    highlimit: float or None -> set high limit (user SP) to highlimit, if None, don't change existing limit
    """
    try:
        caput(eval('%s.prefix'%motor)+'.HLM',highlimit)
        if verbose:
            print('successfully set %s high limit user SP to %s'%(motor,highlimit))
        caput(eval('%s.prefix'%motor)+'.LLM',lowlimit)
        if verbose:
            print('successfully set %s low limit user SP to %s'%(motor,lowlimit))
    except:
        print('WARNING: setting lmits for %s failed!!!!'%motor)


def lock_axis(axis, tol=.1,verbose=False):
    """
    'locks' an axis like e.g. 'diff.xh'  by setting upper and lower limits just around current axes positions
    axis: str, e.g. 'diff.xh'
    tol: float, tolerance of limits, e.g. if tol=.1 limits will be set to +/-.1 (in axis units) around current position 
    """
    try:
        cur_pos = eval('%s'%axis+'.user_readback.value')
        if verbose:
            print('current position of %s: %s -> limits will be set to [%s, %s]'%(axis,cur_pos,cur_pos-tol,cur_pos+tol))
        set_lm(axis,cur_pos-tol,cur_pos+tol,verbose=verbose)
    except:
        print('WARNING: locking %s failed!!!!'%axis)


def lock_device(device,tol=.1,verbose=True):
    """
    'locks' a device like e.g. 'diff' (diffractometer) by setting upper and lower limits just around current axes positions
    device: str, e.g. 'diff'
    tol: float, tolerance of limits, e.g. if tol=.1 limits will be set to +/-.1 (in axis units) around current position 
    """
    # check if device is ineed a device:
    assert '__main__' in str(type(eval(device))), "ERROR: %s does NOT seem to be a device (class)...use lock_axis to lock individual motors."
    # get list of individial axes
    ra=eval('%s'%device+'.read_attrs')
    ax_list = []
    for r in ra:
        if '.' not in r:
            ax_list.append(str(r))
    for a in ax_list:
        lock_axis('%s.%s'%(device,a))
    if verbose:
        print('successfully locked axes %s of device %s'%(ax_list,device) )
