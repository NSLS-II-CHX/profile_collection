
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['diff_xh', 'xray_eye1_stats1_total', 'xray_eye1_stats2_total']), 
        LivePlot('xray_eye1_stats1_total', 'diff_xh')]
RE(rel_scan([xray_eye1], diff.xh, -.1, .1, 3), subs)
