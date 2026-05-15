det = [tpx3]

def chi_theta_iter(num_iter):
    for i in range(num_iter):
        RE(dscan(det,diff.phh,-.1,.1,60))
        ps()
        print(f'Found peak at diff.phh = {ps.peak}, iter={i+1}/{num_iter}')
        RE(mv(diff.phh,ps.peak))
        RE(dscan(det,diff.chh,-.1,.1,60))
        ps()
        RE(mv(diff.chh,ps.peak))
        print(f'Found peak at diff.chh = {ps.peak}, iter={i+1}/{num_iter}')

def overnight_one(nominal_phh):
    fast_sh.open()
    for detuning in [0.032, 0.027, 0.029, 0.030, 0.031, 0.033, 0.035, 0.037]:
        RE.md['del_theta'] = detuning
        RE(mv(diff.phh, nominal_phh-detuning))
        for i in range(2):
            print(f"On detuning {detuning}, run {i+1}/2...")
            RE(count(det)) 
    fast_sh.close()

def day_two(nominal_phh):
    fast_sh.open()
    for detuning in [0.032, 0.028, 0.036, 0.04]:
        RE.md['del_theta'] = detuning
        RE(mv(diff.phh, nominal_phh-detuning))
        for i in range(1):
            print(f"On detuning {detuning}, run {i+1}/1...")
            RE(count(det)) 
    fast_sh.close()

def rocking_curve(rel_min, rel_plus, num_points):
    fast_sh.open()
    RE(dscan(det, diff.phh, rel_min, rel_plus, num_points))
    fast_sh.close()

def rocking_curves():
    rocking_curve(-0.05, 0.05, 40)
    ps()
    RE(mv(diff.phh,ps.peak))
    rocking_curve(-0.02, 0.02, 40)
    ps()
    RE(mv(diff.phh,ps.peak))
    return ps.peak

def repeat_rocking_curves():
    for i in range(3):
        rocking_curve(-0.02, 0.02, 41)
        ps()
        RE(mv(diff.phh,ps.com))
    
def overnight_two(nominal_phh, num_iter):
    fast_sh.open()
    for i in range(num_iter):
        print(f"Overnight collection! On run {i+1}/{num_iter}")
        RE.md['current_phh'] = float(diff.phh.user_readback.value)
        RE.md['del_theta'] = abs( float(diff.phh.user_readback.value - nominal_phh) )
        RE(count(det))
    fast_sh.close()

def spdc_run(auto_pipeline = None):
    RE.md['auto_pipeline'] = auto_pipeline
    uid_add, = RE(count(det))
    if auto_pipeline is not None:
        uid_list=data_acquisition_collection.find_one({'_id':'general_list'})['uid_list']
        uid_list.append(uid_add)          
        data_acquisition_collection.update_one({'_id': 'general_list'},{'$set':{'uid_list' : uid_list}})
        print('Added uid %s to list for automatic compression!'%uid_add)

python convert.py --directory_list="['/nsls2/data/chx/proposals/2025-1/pass-316251/assets/timepix-1/2025/02/11','/nsls2/data/chx/proposals/2025-1/pass-316251/assets/timepix-1/2025/02/12']" --num_workers=24
conda activate /nsls2/conda/envs/2023-3.0-py310-tiled
