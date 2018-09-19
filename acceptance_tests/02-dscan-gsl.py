from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot
subs = [LiveTable(['gsl_xc', 'xray_eye3_stats4_total', 'xray_eye3_stats4_total']), 
        LivePlot('xray_eye3_stats4_total', 'gsl_xc')]
print(gsl.xc.read())
RE(rel_scan([xray_eye3], gsl.xc, -.1, .1, 3), subs)
print(gsl.xc.read())
