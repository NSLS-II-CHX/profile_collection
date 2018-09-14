from bluesky.plans import count
from bluesky.callbacks import LiveTable, LivePlot


# hardware problem if exposure_time == acquire_period
for aq_t, aq_p in zip([1], [2]):
    eiger4m.tr.exposure_time.value = aq_t
    eiger4m.tr.acquire_period.value = aq_p
    eiger4m.tr.num_images.value = 10 
    print("The fast shutter should open and close for 10 times")
    RE(count([eiger4m]), 
       LiveTable(['eiger4m_stats1_total', 'eiger4m_stats2_total']))

img = get_images(db[-1], 'image');print('show the first image');plt.imshow( img[0][0] )

