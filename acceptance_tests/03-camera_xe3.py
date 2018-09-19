
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['diff_xh', 'xray_eye3_stats1_total', 'xray_eye3_stats2_total']), 
        LivePlot('xray_eye3_stats1_total', 'diff_xh')]
print ( 'Motor is diff.xh, camera is xray_eye3')

#print ( 'The fast shutter will open/close three times, motor is diff.xh, camera is xray_eye3')
RE(rel_scan([xray_eye3], diff.xh, -.1, .1, 3), subs)
