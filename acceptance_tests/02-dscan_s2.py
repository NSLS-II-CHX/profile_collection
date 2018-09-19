
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['s1_xc', 'xray_eye3_stats1_total', 'xray_eye3_stats2_total']), 
        LivePlot('xray_eye3_stats1_total', 's1_xc')]
print(s1.xc.read())
RE(rel_scan([xray_eye3], s1.xc, -.1, .1, 3), subs)
print(s1.xc.read())
