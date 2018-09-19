
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['mbs_xc', 'xray_eye3_stats1_total', 'xray_eye3_stats2_total']), 
        LivePlot('xray_eye3_stats1_total', 'mbs_xc')]
print(mbs.xc.read())
RE(rel_scan([xray_eye3], mbs.xc, -.1, .1, 3), subs)
print(mbs.xc.read())
