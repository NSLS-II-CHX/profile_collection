
from bluesky.plans import rel_scan
from bluesky.callbacks import LiveTable, LivePlot


subs = [LiveTable(['diff_xh', 'eiger4m_single_stats1_total', 'eiger4m_single_stats2_total']), 
        LivePlot('eiger4m_single_stats1_total', 'diff_xh')]
print ( 'The fast shutter will open/close three times, motor is diff.xh, camera is eiger4m_single')
RE(rel_scan([eiger4m_single], diff.xh, -.1, .1, 3), subs)

img = get_images(db[-1], 'eiger4m_single_image')
print('show the first image')
plt.imshow( img[0][0] )



#can we change only one mater file for the same dscan?
