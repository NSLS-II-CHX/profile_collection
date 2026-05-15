def lock_axis(axis, verbose = False):
    """
    axis: single axis (e.g. diff.xh) or device (e.g. diff)
    gets current readback_value and sets limits +/- .005 from this value
    """
    RBV = axis.user_readback.value
    axis.high_limit_travel.set(RBV+.005)
    axis.low_limit_travel.set(RBV-.005)
    if verbose:
        print('set soft limits for %s: [%s,%s]'%(axis.name,np.round(RBV-.005,4),np.round(RBV+.005,4)))


def lock_device(device, verbose=False):
        device_dict = {'diff':[diff.Del,diff.gam,diff.om,diff.phi,diff.xb,diff.yb,diff.chh,diff.thh,diff.phh,diff.xh,diff.yh,diff.zh,diff.chv,diff.phv,diff.xv,diff.yv,diff.zv,diff.xv2]
                      }
        for d in device_dict[device]:
            lock_axis(d,verbose=verbose)
    
