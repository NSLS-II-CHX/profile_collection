import numpy as np
print("Hello")
def Escan_and_omega(En):
	# The way this function is defined, you pass in En from bluesky. If you leave the line below, it will get redefined every time. 
	# So probably best to leave it commented out and pass it in, unless you always just want to do from 11.18 to 11.26
	#En = np.arange(11.18, 11.26, 0.002)
	for i, En0 in enumerate(En):
		En0 = float(En0)
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


