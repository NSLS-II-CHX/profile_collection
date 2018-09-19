
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['dcm_b', 'xray_eye3_stats1_total', 'xray_eye3_stats2_total']), 
        LivePlot('xray_eye3_stats1_total', 'dcm_b')]
print(dcm.b.read())
RE(rel_scan([xray_eye3], dcm.b, -.1, .1, 3), subs)
print(dcm.b.read())
