from bluesky.plans import count
from bluesky.callbacks import LiveTable, LivePlot



for aq_t, aq_p in zip([1, 1], [1, 1]):
    eiger4m_single.cam.acquire_time.value = aq_t
    eiger4m_single.cam.acquire_period.value = aq_p
    eiger4m_single.cam.num_images.value = 5
    eiger4m.tr.num_images.value = 1
    print("collect five images")
    RE(count([eiger4m_single]), 
       LiveTable(['eiger4m_single_stats1_total', 'eiger4m_single_stats2_total']))

img = get_images(db[-1], 'eiger4m_single_image');print('show the first image');plt.imshow( img[0][0] )
