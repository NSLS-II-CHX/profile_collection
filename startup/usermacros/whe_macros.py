
#att2.set_T(1)
#series(det='eiger1m',expt=1,imnum=200,auto_compression=True,feedback_on=True)
#att2.set_T(.04)
#series(det='eiger1m',expt=1,imnum=200,auto_compression=True,feedback_on=True)
#att2.set_T(.04)
#series(det='eiger1m',expt=1,imnum=1800,auto_compression=True,feedback_on=True)
#att2.set_T(.001)
#series(det='eiger1m',expt=1,imnum=1800,auto_compression=True,feedback_on=True)

#series(det='eiger1m',expt=0.1,imnum=3000, feedback_on=True,auto_compression=Tru
#     ...: e,OAV_mode='none',comment='AUTO_COMMENT')
#series(det='eiger1m',expt=1,imnum=1800, feedback_on=True,auto_compression=Tru
#     ...: e,OAV_mode='none',comment='AUTO_COMMENT')






det=[eiger1m_single]

def fillLN2():
	caput('XF:11IDA-UT{Cryo:1-IV:19}Pos-SP', 100)
	RE(sleep(10))
	print('waiting for cro-cooler refill...')
	while caget('XF:11IDA-UT{Cryo:1-IV:19}Sts-Sts') !=0:
		RE(sleep(10))
	print('cryo-cooler refill completed!')
	

	
def XPCS_att2_seri():		
	att2.set_T(0.5)
	series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	RE(mvr(diff.xv2,0.005))
	att2.set_T(0.1)
	series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	RE(mvr(diff.xv2,0.005))
	att2.set_T(0.2)
	series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')


def XPCS(comment = 'XPCS scan'):
	while True:
		series(det='eiger1m',expt=10,imnum= 180,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
		caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
		series(det='eiger1m',expt=1,imnum= 1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
		caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
		caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

		# Move +5 microns in X direction
		# RE(mv(diff.xh,0.005))

    # caput('XF:11IDA-OP{Mir:HDM-Ax:P}Sts:FB-Sel',1) #turns mono feedback on
    # time.sleep(60)
    # series(det='eiger1m',expt=1,imnum=1800,feedback_on=True,
            # auto_compression=True,comment=comment)
    # caput('XF:11IDA-OP{Mir:HDM-Ax:P}Sts:FB-Sel',1) #turns mono feedback on
	#caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1) # 3 lines of setting detector count time, period and aquire time
	#caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	#caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

def XPCS_bragg(comment = 'XPCS scan'):
	series(det='eiger1m',expt=1,imnum= 1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

def XPCS_bragg_fast(comment = 'XPCS scan'):
	series(det='eiger1m',expt=.2,imnum= 3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

def macronight():
	Temps = np.array([10,14,18,20])
	for Temp in Temps:
		caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Temp) #set tenperature
		if Temp == 10:
			for i in range(0,3):
				olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
				series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
			att2.set_T(0.1)
			series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
			att2.set_T(1)
		else:
			time.sleep(600)
			for i in range(3):
				olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
				series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')



def macroday():
	Temps = np.array([38,40])
	for Temp in Temps:
		caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Temp) #set tenperature
		time.sleep(600)
		for i in range(3):
			olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
			series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')

		
def macrosecnight():
	Temps = np.array([47.5, 50, 52.5])
	for Temp in Temps:
		caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Temp) #set tenperature
		time.sleep(600)
		for i in range(3):
			olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
			series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')


def macroNessundorma():
	for i in range(2):
		olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
		series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',150) #set tenperature
	time.sleep(900)
	RE(mv(diff.om,-7.408))
	for i in range(3):
		olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
		series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')


def singleXPCS():
	for i in range(3):
		olog_entry('Temperature = ' + str(caget('XF:11IDB-ES{Env:02}LS340:TC1:Control')) + 'K - ' + str(i))
		series(det='eiger1m',expt=1,imnum=3000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')

	
def go():
	temps = np.array([130,140,150,160,170]) - 273
	
	for temp in temps:
		temperature_new(temp, wait = 1800)
		XPCS()
	

def temperature_old(Te):
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Te) #set tenperature
	time.sleep(600)
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
	XPCS()

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

def Rocking_on(Temperature_K, start_scan, om0, om1, i):
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Temperature_K) #set tenperature
	if i == 0:
		time.sleep(3)
	else: 
		time.sleep(300)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	att2.set_T(0.005) 
	
	# Go to (0 0 4)
	RE(mv(diff.om, om0))
	RE(mv(diff.gam, -24.49))
	RE(dscan(det,diff.om, -0.2, 0.2, 41))
	ps(start_scan+6*i+1)
	RE(mv(diff.om,ps.cen))
	om0 = ps.cen

	RE(dscan(det,diff.xv2, -1.4, 0.6, 101))
	ps(start_scan+6*i+2)
	xv20 = ps.peak + 0.962
	
	RE(mv(diff.xv2,xv20))
	
	# Measure 1/3 peak
	if Temperature_K <= 101:
		att2.set_T(0.03)	## add if statement for higher temp
	else:
		att2.set_T(1)

	RE(mv(diff.om, om1))
	RE(mv(diff.gam, -39.79))
	RE(dscan(det,diff.om, -0.5, 0.5, 41))
	ps(start_scan+6*i+3)
	RE(mv(diff.om,ps.peak))
	om1 = ps.peak
	RE(dscan(det,diff.xv2, -1.4, 0.6, 101))

	# Measure 1/2 peak
	# att2.set_T(1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages', 1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod', 10)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime', 10)

	RE(mv(diff.om, -9.538))
	RE(mv(diff.gam, -40.85))
	RE(dscan(det,diff.om, -3, 2, 51))
	# RE(dscan(det,diff.xv2, -1.4, 0.6, 101))
	RE(dscan(det,diff.xv2, -.2, .2, 51))

def Bragg_XPCS(Temperature_K, start_scan, om0, i):
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Temperature_K) #set tenperature
	if i == 0:
		time.sleep(3)
	else: 
		time.sleep(300)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	att2.set_T(0.005) 
	
	# Go to (0 0 4)
	RE(mv(diff.om, om0))
	RE(mv(diff.gam, -24.49))
	RE(dscan(det,diff.om, -0.2, 0.2, 41))
	ps(start_scan+4*i+1)
	RE(mv(diff.om,ps.cen)) 
	om0 = ps.cen

	RE(dscan(det,diff.xv2, -1.1, -0.9, 41))
	ps(start_scan+4*i+2)
	xv20 = ps.peak + 0.962
	
	RE(mv(diff.xv2,xv20))
	om_XPCS = om0+0.02635
	RE(mv(diff.om, om_XPCS))
	att2.set_T(0.1)

	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	series(det='eiger1m',expt=1,imnum= 3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	series(det='eiger1m',expt=1,imnum= 3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)


def Rocking_on_v2(Temperature_K, start_scan, om0, i):
	caput('XF:11IDB-ES{Env:02}LS340:TC1:wr_SP1',Temperature_K) #set tenperature
	if i == 0:
		time.sleep(3)
	else: 
		time.sleep(300)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)

	att2.set_T(0.005) 
	
	# Go to (0 0 4)
	RE(mv(diff.om, om0))
	RE(mv(diff.gam, -24.49))
	RE(dscan(det,diff.om, -0.2, 0.2, 41))
	ps(start_scan+4*i+1)
	RE(mv(diff.om,ps.cen)) 
	om0 = ps.cen

	RE(dscan(det,diff.xv2, -1.1, -0.9, 41))
	ps(start_scan+4*i+2)
	xv20 = ps.peak + 0.962
	
	RE(mv(diff.xv2,xv20))
	# Measure 1/2 peak
	# att2.set_T(1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages', 1)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod', 10)
	caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime', 10)

	RE(mv(diff.om, -9.538))
	RE(mv(diff.gam, -40.85))
	RE(dscan(det,diff.om, -3, 2, 51))
	# RE(dscan(det,diff.xv2, -1.4, 0.6, 101))
	if (i%4==0):
		
		RE(dscan(det,diff.xv2, -.01, .2, 61))
	

def First_Night():
	start_scan = 174662
	om0 = -10.772
	om1 = -8.38

	T_list = np.array([110, 115, 120, 130])
	for i, Temperature_K in enumerate(T_list):
		Rocking_on(Temperature_K, start_scan, om0, om1, i)

def Second_Night():
	start_scan = 174712 # cahnge this as well
	om0 = -10.773

	T_list = np.array([70, 95, 110, 125, 150])
	# T_list = np.array([70])
	for i, Temperature_K in enumerate(T_list):
		Bragg_XPCS(Temperature_K, start_scan, om0, i)

def Third_Day():
	start_scan = 174
	om0 = -10.773
	
	T_list = np.array([150, 140, 130, 120, 115, 110, 100, 90, 80, 70])
	for i, Temperature_K in enumerate(T_list):
		Rocking_on_v2(Temperature_K, start_scan, om0, i)



att2.set_T(0.5)

series(det='eiger1m',expt=1,imnum= 3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
series(det='eiger1m',expt=1,imnum= 3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)