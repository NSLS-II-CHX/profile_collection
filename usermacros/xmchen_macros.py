
# att2.set_T(1)
# series(det='eiger1m',expt=1,imnum=200,auto_compression=True,feedback_on=True)
# att2.set_T(.04)
# series(det='eiger1m',expt=1,imnum=200,auto_compression=True,feedback_on=True)
# att2.set_T(.04)
# series(det='eiger1m',expt=1,imnum=1800,auto_compression=True,feedback_on=True)
# att2.set_T(.001)
# series(det='eiger1m',expt=1,imnum=1800,auto_compression=True,feedback_on=True)

# series(det='eiger1m',expt=0.1,imnum=3000, feedback_on=True,auto_compression=Tru
#     ...: e,OAV_mode='none',comment='AUTO_COMMENT')
# series(det='eiger1m',expt=1,imnum=1800, feedback_on=True,auto_compression=Tru
#     ...: e,OAV_mode='none',comment='AUTO_COMMENT')




det=[eiger1m_single]

def fillLN2():
	caput('XF:11IDA-UT{Cryo:1-IV:19}Pos-SP', 100)
	RE(sleep(10))
	print('waiting for cro-cooler refill...')
	while caget('XF:11IDA-UT{Cryo:1-IV:19}Sts-Sts') !=0:
		RE(sleep(10))
	print('cryo-cooler refill completed!')

def XPCS_att2_series():		
	att2.set_T(0.1)
	series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	RE(mvr(diff.xv2,0.005))
	att2.set_T(0.2)
	series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	RE(mvr(diff.xv2,0.005))
	att2.set_T(1)
	series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')


def XPCS(comment = 'XPCS scan'):
	while True:
		series(det='eiger1m',expt=0.5,imnum=3600,feedback_on=True, auto_compression=True,comment=comment)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

		# Move +5 microns in X direction
		RE(mv(diff.xh,0.005))

    # caput('XF:11IDA-OP{Mir:HDM-Ax:P}Sts:FB-Sel',1) #turns mono feedback on
    # time.sleep(60)
    # series(det='eiger1m',expt=1,imnum=1800,feedback_on=True,
            # auto_compression=True,comment=comment)
    # caput('XF:11IDA-OP{Mir:HDM-Ax:P}Sts:FB-Sel',1) #turns mono feedback on
	#caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1) # 3 lines of setting detector count time, period and aquire time
	#caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	#caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)


def temperature_new(Te, wait):
	set_temperature(Te, heat_ramp = 1) # set temp in C
	time.sleep(wait)
	RE(dscan(det,diff.phh,-0.05,0.05,30))
	ps()
	RE(mv(diff.phh,ps.peak))

	RE(dscan(det,diff.xh,-0.05,0.05,20))
	ps()
	RE(mv(diff.xh,ps.peak))

	RE(dscan(det,diff.zh,-0.05,0.05,20))
	ps()
	RE(mv(diff.zh,ps.peak))

def go():
	temps = np.array([130,140,150,160,170]) - 273
	
	for temp in temps:
		temperature_new(temp, wait = 1800)
		XPCS()

def T_series():
	for Ti in [85, 80, 75, 70, 65, 60, 55]:
		caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Ti) #set tenperature
		time.sleep(600)
		RE(dscan(det,diff.om,-1,1,100))

def overnight_TIT():

	print('Beginning of End')
	
	
	RE(grid_scan(det, diff.xv2, 151.85, 151.91, 5, diff.zv, -0.795, -0.695, 7, diff.om, -18.45, -17.45, 25))	# 1.5 h
	print('Go back to the flake')
	RE(mv(diff.om,-17.9466))
	RE(mv(diff.zv,-0.745))
	RE(mv(diff.xv2,151.88))

	time.sleep(300)
	print('Time series of the flake at 30 K')
	series(det='eiger1m',expt=1.0,imnum=1800, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
	print('Go to 70 K')
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',70) #set tenperature
	time.sleep(1800)
	print('x/z/om mesh')
	RE(grid_scan(det, diff.xv2, 151.85, 151.91, 5, diff.zv, -0.795, -0.695, 7, diff.om, -18.45, -17.45, 25))
	print('Go back to the flake')
	RE(mv(diff.om,-17.9466))
	RE(mv(diff.zv,-0.745))
	RE(mv(diff.xv2,151.88))

	time.sleep(300)
	print('End of beginning')	


def overnight_TIT_2():
	print('Beginning of End')
	
	att2.set_T(0.1)

	print('Go to 250 K')
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',250) #set tenperature
	time.sleep(300)
	print('Time series of the flake at 250 K')
	series(det='eiger1m',expt=1.0,imnum=7200, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	print('Go to 255 K')
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',255) #set tenperature
	time.sleep(300)
	print('Time series of the flake at 255 K')
	series(det='eiger1m',expt=1.0,imnum=7200, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)


	print('Go to 260 K')
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',260) #set tenperature
	time.sleep(300)
	print('Time series of the flake at 260 K')
	series(det='eiger1m',expt=1.0,imnum=7200, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	print('End of beginning')	

def fluence_ls():
	print('Fluence dependence')
	att.set_T(0.5)
	series(det='eiger1m',expt=1.0,imnum=1800, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h
	time.sleep(60)
	att.set_T(0.1)
	series(det='eiger1m',expt=1.0,imnum=1800, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h



def temperature_old(Te):
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Te) #set tenperature
	time.sleep(2500)
	#XPCS()

	RE(dscan(det,diff.om,-0.15,0.15,30))
	ps()
	RE(mv(diff.om,ps.peak))

	RE(dscan(det,diff.xv2,-0.15,0.15,20))
	ps()
	RE(mv(diff.xv2,ps.peak))

	RE(dscan(det,diff.yv,-0.12,0.12,35))
	
	RE(mv(diff.yv,ps.cen))

	#RE(dscan(det,diff.phv, -0.5, 0.5,20))
	#ps()
	#RE(mv(diff.phv,ps.peak))

	RE(dscan(det,diff.om,-0.2,0.2,40))
	ps()
	RE(mv(diff.om,ps.peak))
	#XPCS()

	RE(dscan(det,diff.xv2,-0.15,0.15,20))
	ps()
	RE(mv(diff.xv2,ps.peak))

def test():
	RE(dscan(det,diff.xv2, -.05,.05,30))
	ps()
	RE(mv(diff.xv2,ps.cen))
	RE(dscan(det,diff.om,-0.2,0.2,20))
	ps()
	RE(mv(diff.om,ps.peak))
	XPCS()


def gogogo():
	for i in range(10):
		print(f'Starting XPCS scan')
		series(det='eiger1m',expt = 1,imnum=3600,feedback_on=True, auto_compression=True,comment=comment)

		caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

		RE(dscan(det,diff.om,-0.8,0.8,30))

def overnight_YEAH():

	print('Beginning of End')
	
	temps = [230,235,240,245,250,255,260,261,262,263,264,265,266,267,268,269,270,271,272,273]

	for temp in temps:
		caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',temp) #set tenperature
		if temp>230:
			time.sleep(300)
		
		# centering the sample
		att2.set_T(0.001)
		#RE(dscan(det,diff.om,-0.2,0.2,40))
		#ps()
		#RE(mv(diff.om,ps.cen))
		RE(dscan(det,diff.xv2,-0.3,0.3,60))
		ps()
		RE(mv(diff.xv2,ps.peak))
		RE(dscan(det,diff.om,-0.2,0.2,40))
		ps()
		RE(mv(diff.om,ps.cen))
		om0 = ps.cen # Bragg center
		om0_CDW_1 = om0 + 0.797  # CDW CENTER 1
		om0_CDW_2 = om0 - 0.845  # CDW CENTER 2
	
		# om scan
		att2.set_T(1.)
		RE(mv(diff.om,om0_CDW_1))
		RE(dscan(det,diff.om,-0.3,0.3,80))
		RE(mv(diff.om,om0_CDW_2))
		RE(dscan(det,diff.om,-0.3,0.3,80))
		RE(mv(diff.om,om0)) # move back to the nominal bragg center




	
	RE(grid_scan(det, diff.xv2, 151.85, 151.91, 5, diff.zv, -0.795, -0.695, 7, diff.om, -18.45, -17.45, 25))	# 1.5 h
	print('Go back to the flake')
	RE(mv(diff.om,-17.9466))
	RE(mv(diff.zv,-0.745))
	RE(mv(diff.xv2,151.88))

	time.sleep(300)
	print('Time series of the flake at 30 K')
	series(det='eiger1m',expt=1.0,imnum=1800, feedback_on=True,auto_compression=True,OAV_mode='none',comment='WAXS '+'AUTO_COMMENT')	# 0.5 h
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
	print('Go to 70 K')
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',70) #set tenperature
	time.sleep(1800)
	print('x/z/om mesh')
	RE(grid_scan(det, diff.xv2, 151.85, 151.91, 5, diff.zv, -0.795, -0.695, 7, diff.om, -18.45, -17.45, 25))
	print('Go back to the flake')
	RE(mv(diff.om,-17.9466))
	RE(mv(diff.zv,-0.745))
	RE(mv(diff.xv2,151.88))

	time.sleep(300)
	print('End of beginning')	