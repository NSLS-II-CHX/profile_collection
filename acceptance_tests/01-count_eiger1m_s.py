from bluesky.plans import count
from bluesky.callbacks import LiveTable, LivePlot



for aq_t, aq_p in zip([1, 1], [1, 2]):
    eiger1m_single.cam.acquire_time.value = aq_t
    eiger1m_single.cam.acquire_period.value = aq_p
    eiger1m_single.cam.num_images.value = 10 
    print("describe what to see")
    RE(count([eiger1m_single]), 
       LiveTable(['eiger1m_single_stats1_total', 'eiger1m_single_stats2_total']))
