from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot
subs = [LiveTable(['s4_xc', 'xray_eye3_stats4_total', 'xray_eye3_stats4_total']), 
        LivePlot('xray_eye3_stats4_total', 's4_xc')]
print(s4.xc.read())
RE(rel_scan([xray_eye3], s4.xc, -.1, .1, 3), subs)
print(s4.xc.read())
