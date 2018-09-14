from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot
subs = [LiveTable(['gsl_xc_readback', 'xray_eye3_stats1_total', 'xray_eye3_stats2_total']), 
        LivePlot('xray_eye3_stats1_total', 'gsl_xc_readback')]
print(gsl.xc.read())
RE(rel_scan([xray_eye3], gsl.xc, -.1, .1, 10), subs)
print(gsl.xc.read())

print( 'here' )
