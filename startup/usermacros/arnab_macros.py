

def energy_two_theta_scan(energies):

    starting_energy = dcm.en.user_readback.value
    starting_ivu_gap = ivu_gap.gap.user_readback.value
    starting_gam = diff.gam.user_readback.value
    starting_om = diff.om.user_readback.value

    for i, energy in enumerate(energies):

        print(f"Moving to {energy} keV: run {i+1}/{len(energies)}")

        move_E(energy, harm = 7)
        det = [elm]
        RE(dscan(det, ivu_gap, -40, 40, 50))
        ps()
        RE(mv(ivu_gap, ps.peak))
        det = [eiger1m_single]
        #RE(dscan(det, diff.gam, -0.2, 0.2, 40))
        #ps()
        #RE(mv(diff.gam, ps.cen))
        RE(dscan(det, diff.om, -0.2, 0.2, 40))
        ps()
        RE(mv(diff.om, ps.peak))

    move_E(starting_energy/1000, harm = 7)
    det = [elm]
    RE(dscan(det, ivu_gap, -40, 40, 50))
    ps()
    RE(mv(ivu_gap, ps.peak))
    RE(mv(diff.om, starting_om))
    RE(mv(diff.gam, starting_gam))


^Itime.sleep(600)
      ...: ^Iseries(det='eiger1m',expt=1,imnum=2000,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
      ...: ^Iseries(det='eiger1m',expt=0.01,imnum=4500,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')



def overnight():
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
     time.sleep(5)
     RE(mv(diff.xv2,149.2536))
     time.sleep(5)
     RE(mv(diff.yv,2.8924))
     time.sleep(5)

     att2.set_T(1)
     time.sleep(5)

     RE(rel_grid_scan(det,diff.xv2,-15 * 0.002,15 * 0.002,30,diff.yv,-15 * 0.002,15 * 0.002,30,True))
     time.sleep(5)

     RE(grid_scan(det,diff.xv2,148.5,149.0,72,diff.yv,2.3,2.8,72,True))
     time.sleep(5)

     att2.set_T(0.2)
     time.sleep(5)

     RE(mv(diff.xv2,149.2536))
     time.sleep(5)
     RE(mv(diff.yv,2.8924))
     time.sleep(5)
     while True:
        caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
        caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
        caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
        time.sleep(10)
        series(det='eiger1m',expt=1,imnum=1800,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')

def overnight_2():
     att2.set_T(1)
     time.sleep(1)
     RE(rel_grid_scan(det,diff.xv2,0,0.24,15,diff.yv,-0.24,0,15,True))
     time.sleep(2)
     att2.set_T(0.05)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
     time.sleep(10)
     series(det='eiger1m',expt=1,imnum=3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
     time.sleep(10)
     series(det='eiger1m',expt=1,imnum=3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
     time.sleep(10)
     series(det='eiger1m',expt=1,imnum=3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
     time.sleep(10)
     series(det='eiger1m',expt=1,imnum=3600,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
     time.sleep(10)

     att2.set_T(1)
     time.sleep(5)

     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)

     time.sleep(5)
     # 2.5 hr
     RE(grid_scan(det,diff.xv2,148.8,149.3,40,diff.yv,2.7,3.2,40,True))





        
def overnight_test():
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
     caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
     time.sleep(5)
     RE(mv(diff.xv2,149.2536))
     time.sleep(5)
     RE(mv(diff.yv,2.8924))
     time.sleep(5)

     att2.set_T(1)
     time.sleep(5)
     
     RE(rel_grid_scan(det,diff.xv2,-15 * 0.002,15 * 0.002,2,diff.yv,-15 * 0.002,15 * 0.002,2,True))
     time.sleep(5)

     RE(grid_scan(det,diff.xv2,148.5,149.0,2,diff.yv,2.3,2.8,2,True))
     time.sleep(5)

     att2.set_T(0.2)
     time.sleep(5)

     RE(mv(diff.xv2,149.2536))
     time.sleep(5)
     RE(mv(diff.yv,2.8924))
     time.sleep(5)
     while True:
        caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquireTime',1)
        caput('XF:11IDB-ES{Det:Eig1M}cam1:AcquirePeriod',1)
        caput('XF:11IDB-ES{Det:Eig1M}cam1:NumImages',1)
        time.sleep(10)
        series(det='eiger1m',expt=1,imnum=100,feedback_on=True, auto_compression=True,comment='AUTO_COMMENT')
        



