from typing import Sequence, Literal 
from itertools import chain 
from pathlib import Path
import time

from blop.ax import Agent, RangeDOF, Objective, OutcomeConstraint
from blop.protocols import EvaluationFunction, AcquisitionPlan
from bluesky.utils import plan 
import bluesky.plans as bp 
import bluesky.plan_stubs as bps 
import bluesky.preprocessors as bpp 
import numpy as np
from scipy.interpolate import UnivariateSpline
# from tpx3awkward import convert_tpx3_files
import pandas as pd

# SPDC Optimization 

# dofs 

# objectives 

# spdc_count = Objective(name="SPDC count", minimize=False) 

# constraints 

# evaluation function 

# class SPDCEvaluation(EvaluationFunction): 

#     def __init__(self, tiled_client): 
#         self.tiled_client = tiled_client 
    
#     def _compute_stats(self): 
#         ... 
    
#     def __call__(self, uid: str, suggestions) -> list[dict]: 
#         outcomes = [] 
#         run = self.tiled_client[uid] 
        
#         suggestion_ids = [suggestion["_id"] for suggestion in run.metadata["start"]["blop_suggestions"]] 
        
#         for idx, sid in enumerate(suggestion_ids): 
#             spdc_count = self._compute_stats() 
        
#             outcome = { 
#                 "_id": sid, 
#                 "spdc_count": spdc_count 
#             } 
#             outcomes.append(outcome) 
        
#         return outcomes 
 

# agent definition 

# def optimize_diamond_spot(): 
#     agent = Agent( ... ) 

#     return agent.get_besat 
 

# Bragg peak Optimization (2 step) 
# first step: find bragg peak (maximize intensity by moving diamond) 
# second step: center beam on detector (moving detector mount) 

# dofs 
gonzo_y = RangeDOF(actuator=gonzo.y, bounds=(-7.9, -6.14), parameter_type="float") 
gonzo_x = RangeDOF(actuator=gonzo.x, bounds=(2.46, 3.04), parameter_type="float") 

# objectives 

rc_peak_intensity = Objective(name="rc_peak_intensity", minimize=False) # total intensity on detector tpx3_stats1_total 
rc_fwhm = Objective(name="rc_fwhm", minimize=True) 
# rc_npeaks = Objective(name="rc_npeaks", minimize=True) # TODO make scalarized objective? 

# beam_dx = Objective(name="beam_dx", minimize=True) # x distance from center 
# beam_dy = Objective(name="beam_dy", minimize=True) # y distance from center 

first_step_objectives = [rc_peak_intensity, rc_fwhm] 

# second_step_objectives = [ beam_dx, beam_dy ]

# constraints 
...

# evaluation function 

class BraggPeakFirstEvaluation(EvaluationFunction): 

    def __init__(self, tiled_client): 
        self.tiled_client = tiled_client 
    
    def _compute_stats(self, thetas, intensities): 
        spline = UnivariateSpline(thetas, intensities, s=0) 
        
        interp_thetas = np.linspace(min(thetas), max(thetas), 1000) 
        interp_intensities = spline(interp_thetas) 
        
        peak_idx = np.argmax(interp_intensities) 
        peak_intensity_thetas = interp_thetas[peak_idx] # actual bragg peak
        peak_intensity = interp_intensities[peak_idx] 
        
        baseline = np.min(interp_intensities) 
        half_max = baseline + 0.5 * (peak_intensity - baseline) 
        
        diff = interp_intensities - half_max 
        crossings = np.where(np.diff(np.sign(diff)) != 0)[0] 
        
        if len(crossings) >= 2: 
            i1, i2 = crossings[0], crossings[-1] 
        
            x_left = np.interp(half_max, [interp_intensities[i1], interp_intensities[i1+1]], 
                                [interp_thetas[i1], interp_thetas[i1+1]]) 
                
            x_right = np.interp(half_max, [interp_intensities[i2], interp_intensities[i2+1]], 
                                [interp_thetas[i2], interp_thetas[i2+1]]) 
                
            fwhm = x_right - x_left 
        else: 
            x_left = np.nan 
            x_right = np.nan 
            fwhm = np.nan 
            
        return peak_intensity, fwhm
    
    def __call__(self, uid: str, suggestions) -> list[dict]: 
        outcomes = [] 
        run = self.tiled_client[uid]
        
        suggestion_ids = [suggestion["_id"] for suggestion in run["start"]["blop_suggestions"]] 
        
        for idx, sid in enumerate(suggestion_ids): 
            thetas = tiled_client[uid]._run['primary/data/gonzo_theta'].read()
            intensities = tiled_client[uid]._run['primary/data/tpx3_stats1_total'].read()
            peak_intensity, fwhm = self._compute_stats(thetas, intensities) 
        
            outcome = { 
                "_id": sid, 
                "rc_peak_intensity": np.sqrt(peak_intensity), 
                "rc_fwhm": fwhm,
            } 
            outcomes.append(outcome) 
        
        return outcomes  
 

SAMPLE_SUGGESTIONS_RUN_KEY: Literal["sample_suggestions"] = "sample_suggestions" 

# acquisition plan 

class RockingCurveAcquisition(AcquisitionPlan): 
    def __call__( self, suggestions, actuators, sensors, md=None): 
        point = suggestions[0] 
        positions = [point[a.name] for a in actuators] 
        md = {"blop_suggestions": suggestions, "run_key": SAMPLE_SUGGESTIONS_RUN_KEY} 
        yield from bps.mv(*chain.from_iterable(zip(actuators,positions))) 
        return ( # TODO: fix argument type in bluesky.plans.list_scan 
            yield from bpp.set_run_key_wrapper(bp.rel_scan( sensors, gonzo.theta, -.008, .008, num = 70, md=md, ), SAMPLE_SUGGESTIONS_RUN_KEY, ) ) # updated to wider range

# agent function 

tiled_client = db # TODO init tiled client 

bragg_peak_agent = Agent( sensors=[tpx3],
                         dofs=[gonzo_y, gonzo_x], 
                         objectives=first_step_objectives, 
                         evaluation_function=BraggPeakFirstEvaluation(tiled_client), 
                         acquisition_plan=RockingCurveAcquisition())

## STEP 2

# dofs
diff_gamma = RangeDOF(actuator=diff.gam, bounds=(11.5-.5, 11.5+.25), parameter_type="float")
diff_del = RangeDOF(actuator=diff.Del, bounds=(23.4996-4, 23.4996+4), parameter_type="float")

# objective
beam_dx = Objective(name="beam_dx", minimize=True) # x distance from center 
beam_dy = Objective(name="beam_dy", minimize=True) # y distance from center 
intensity = Objective(name="intensity", minimize=False)

second_step_objectives = [beam_dx, beam_dy, intensity]

# constraints
beam_dx_constraint = OutcomeConstraint("x <= 3", x=beam_dx)
beam_dy_constraint = OutcomeConstraint("x <= 3", x=beam_dy)
intensity_constraint = OutcomeConstraint("x >= 10", x=intensity)

# acquisition
# default acquire

# evaluation
class BraggPeakSecondEvaluation(EvaluationFunction): 

    def __init__(self, tiled_client): 
        self.tiled_client = tiled_client
    
    def _compute_stats(self, tpx3_raw_fpaths):
        # TODO confirm acquisition plan only produces one raw file
        if len(tpx3_raw_fpaths) > 1:
            print("more than 1 file")
        output_directory = Path("/nsls2/data/chx/legacy/analysis/2024_1/qmicroscope/nrusso1/blop/processed/")
        parquet_fpath = Path(str((output_directory / Path(tpx3_raw_fpaths[0]).stem)) + "_cent.parquet")
        print(parquet_fpath)
        while True:
            time.sleep(0.5)
            if parquet_fpath.exists():
                time.sleep(1)
                break
        
        cent_df = pd.read_parquet(parquet_fpath)
        mean_xc = cent_df["xc"].mean()
        mean_yc = cent_df["yc"].mean()

        return abs(256-mean_xc), abs(256-mean_yc), np.sqrt(len(cent_df))
    
    def __call__(self, uid: str, suggestions) -> list[dict]: 
        outcomes = [] 
        run = self.tiled_client[uid]
        
        suggestion_ids = [suggestion["_id"] for suggestion in run["start"]["blop_suggestions"]] 
        
        for idx, sid in enumerate(suggestion_ids): 
            tpx3_raw_fpaths = self.tiled_client[uid]._run['primary/data/tpx3_files_raw_filepaths'].read()[0]
            print(tpx3_raw_fpaths)
            tpx3_raw_fpaths_clean = [x[5:] for x in tpx3_raw_fpaths]
            print(tpx3_raw_fpaths_clean)
            beam_dx, beam_dy, intensity = self._compute_stats(tpx3_raw_fpaths_clean)
        
            outcome = { 
                "_id": sid, 
                "beam_dx": beam_dx, 
                "beam_dy": beam_dy,
                "intensity": intensity,
            } 
            outcomes.append(outcome) 
        
        return outcomes  

center_bragg_agent = Agent(
    sensors=[tpx3],
    dofs=[diff_gamma, diff_del],
    objectives=second_step_objectives,
    evaluation_function=BraggPeakSecondEvaluation(tiled_client),
    outcome_constraints=[beam_dx_constraint, beam_dy_constraint, intensity_constraint]
)

from functools import partial
# def grid_overnight(det=[tpx3],motors=[gonzo.x,gonzo.y],boundx=(2.4,2.93),boundy=(-7.9,-6.14),npoints=(16,40)):  INITIAL!!!!
def grid_overnight(det=[tpx3],motors=[gonzo.x,gonzo.y],boundx=(2.4,3.05),boundy=(-7.9,-6.14),npoints=(9,20)):

    #closure = partial(bps.one_nd_step, take_reading = bp.rel_scan(det,gonzo.theta,-.008,.008,70))
    closure = partial(bps.one_nd_step, take_reading = lambda x : bpp.stub_wrapper(bp.rel_scan(det,gonzo.theta,-.005,.005,55))) #,-.003,.008,55

    yield from bp.grid_scan(det,motors[0],boundx[0],boundx[1],npoints[0],motors[1],boundy[0],boundy[1],npoints[1],per_step=closure)

    print("grid scan done, closing shutters ....")
    # if foe_sh.is_open:
    foe_sh.close()
    print("Goonight beamline, boo morning shift")
    return 0

def outer_loop_grid(det=[tpx3],npx=16,npy=20,opt_iter=200,boundx = gonzo_x.bounds,boundy = gonzo_y.bounds):
    for x in np.linspace(*boundx,num=npx):
        RE(bps.mv(gonzo.x,x))
        for y in np.linspace(*boundy,num=npy):
            RE(bps.mv(gonzo.y,y))
            RE(dscan(det,gonzo.theta,-.008,.008,70))
            plt.close()
        ps()
        RE(mv(gonzo.theta,ps.peak))
    
    RE(bragg_peak_agent.optimize(iterations=opt_iter))
    print("grid scan done, closing shutters ....")
    foe_sh.close()
    print("Goodnight beamline, boo morning shift")



positions = np.array([[2.53,-6.57],[2.1625,-7.206],[2.505,-7.1415],[2.53,-6.57],[2.1625,-7.206],[2.505,-7.1415]])

def spdc_morning_macro(det=[tpx3], positions=positions ,del_theta=0.0125, theta = 11.576):

    print("Start Macro")

    RE.md['del_theta'] = del_theta
    RE.md['theta'] = theta

    RE.md['sample'] = 'CVD Diamond (111) Mounted'

    RE.md['xc'] = 256
    RE.md['yc'] = 256

    RE.md['Epump'] = 15

    RE.md['dd'] = 54 # will be close enough, +/- 1 cm

    for i, position in enumerate(positions):

        new_x = position[0]
        new_y = position[1]
        RE.md['spot'] = [new_x, new_y]

        RE(mv(gonzo.x,new_x))
        RE(mv(gonzo.y,new_y))

        print(f"Moved to x = {new_x}, and y = {new_y}")
        print("Acquiring SPDC ")


        RE(count(det))

    print("goodnight beamline")
    foe_sh.close()

