from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot
subs = [LiveTable(['diff_xh', 'xray_eye1_stats1_total', 'xray_eye1_stats2_total']), 
        LivePlot('xray_eye1_stats1_total', 'diff_xh')]
print ( 'Motor is diff.xh, camera is xray_eye1 with saving images')
RE(rel_scan([xray_eye1_writing], diff.xh, -.1, .1, 3), subs)

img = get_images(db[-1], 'xray_eye1_image')
print('show the first image')
plt.imshow( img[0] )

