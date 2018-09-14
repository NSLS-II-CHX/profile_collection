from bluesky.plans import count
from bluesky.callbacks import LiveTable, LivePlot


# hardware problem if exposure_time == acquire_period
for aq_t, aq_p in zip([1], [2]):
    eiger1m.tr.exposure_time.value = aq_t
    eiger1m.tr.acquire_period.value = aq_p
    eiger1m.tr.num_images.value = 10 
    print("describe what to see")
    RE(count([eiger1m]), 
       LiveTable(['eiger1m_stats1_total', 'eiger1m_stats2_total']))
