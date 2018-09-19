
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['diff_xh', 'xray_eye3_stats1_total', 'xray_eye3_stats2_total']), 
        LivePlot('xray_eye3_stats1_total', 'diff_xh')]
print ( 'Motor is diff.xh, camera is xray_eye3 with saving images')
RE(rel_scan([xray_eye3_writing], diff.xh, -.1, .1, 3), subs)


img = get_images(db[-1], 'xray_eye3_image')
print('show the first image')
plt.imshow( img[0] )

