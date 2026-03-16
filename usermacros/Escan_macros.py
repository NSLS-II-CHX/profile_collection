import numpy as np
def Escan_and_oemga(En):
	En = np.arange(11.18, 11.26, 0.002)
	for i, En0 in enumerate(En):
		move_E(En0, harm = 7)
		det = [elm]
		RE(dscan(det,ivu_gap,-50,50,40))
		ps()
		RE(mv(ivu_gap,ps.peak))
		det=[eiger1m_single]
		RE(dscan(det,diff.om,-0.3,0.3,30))
		ps()
		RE(mv(diff.om,ps.peak))
		
#def Escan(En):
	#En = np.arange(11.19, 11.25, 0.002)
	#for i, En0 in enumerate(En):
		#move_E(En0, harm = 7)
		#det = [elm]
		#RE(dscan(det,ivu_gap,-50,50,40))
		#ps()
		#RE(mv(ivu_gap,ps.peak))
		#det=[eiger1m_single]
