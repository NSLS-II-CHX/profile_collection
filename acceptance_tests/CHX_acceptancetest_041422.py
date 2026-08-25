### A sequence of acceptance tests to be run after software deployment 
### AF August 2020 (modfied older code by YZ)

#1. Simple counts and short series with CHX detectors

# Eiger1M
print('Taking data with the Eiger1M detector')
eiger1m_single.cam.num_images.value = 1  
eiger1m_single.cam.acquire_time.value = 1  
eiger1m_single.cam.acquire_period.value = 1  

RE(count([eiger1m_single]),Measurement='Deployment test')

img = get_images(db[-1], 'eiger1m_single_image');
print('showing the first image');
plt.imshow( img[0][0] )

series(det='eiger1m',expt=0.1,imnum=5)

img = get_images(db[-1], 'eiger1m_single_image');
print('showing the first image');
plt.imshow( img[0][0] )

# Eiger4M
print('Taking data with the Eiger4M detector')
eiger4m_single.cam.num_images.value = 1  
eiger4m_single.cam.acquire_time.value = 1  
eiger4m_single.cam.acquire_period.value = 1  

RE(count([eiger4m_single]),Measurement='Deployment test')
img = get_images(db[-1], 'eiger4m_single_image');
print('showing the first image');
plt.imshow( img[0][0] )

series(det='eiger4m',expt=0.1,imnum=5)

img = get_images(db[-1], 'eiger4m_single_image');
print('showing the first image');
plt.imshow( img[0][0] )

# Eiger500k

print('Taking data with the Eiger500k detector')
eiger500k_single.cam.num_images.value = 1  
eiger500k_single.cam.acquire_time.value = 1  
eiger500k_single.cam.acquire_period.value = 1  

RE(count([eiger500k_single]),Measurement='Deployment test')

img = get_images(db[-1], 'eiger500K_single_image');
print('showing the first image');
plt.imshow( img[0][0] )

series(det='eiger500k',expt=0.1,imnum=5)

img = get_images(db[-1], 'eiger500K_single_image');
print('showing the first image');
plt.imshow( img[0][0] )

print('Test of Eiger detectors completed without errors')

#---------------------

print('Taking a few example scans:')

print('A few test scans with the xray_eye3 detector')
RE(rel_scan([xray_eye3], dcm.b, -.1, .1, 3))
#RE(rel_scan([xray_eye3], ivu_gap, -.1, .1, 3))
RE(rel_scan([xray_eye3], mbs.yc, -.1, .1, 3))
RE(rel_scan([xray_eye3], diff.xh, -.1, .1, 3))
RE(rel_scan([xray_eye3], gsl.xc, -.1, .1, 3))

print('A scan with the xray_eye3_writing detector')
uid_scan, = RE(rel_scan([xray_eye3_writing], diff.xh, -.1, .1, 3))

img = get_images(db[uid_scan], 'xray_eye3_image');
print('timestamp issue needs to be fixed...')
#plt.imshow( img[0] )

print('Taking a few alignment scans (with the elm):')
det = [elm]  #using the elm detector
uid_dcmp, = RE(dscan(det,dcm.p,-.002,.002,20))
#ps(uid_dcmp) #wont work without beam
RE(dscan(det,dcm.b,-.2,.2,50))


