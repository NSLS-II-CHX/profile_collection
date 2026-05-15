def save_timepix(fn):

    caput("TPX3-TEST:cam1:RawFileTemplate", fn+"_")
    caput("TPX3-TEST:cam1:WriteRaw", 1)
    caput("TPX3-TEST:cam1:WriteData", 1)

    fast_sh.open()

    caput("TPX3-TEST:cam1:Acquire", 1)
    time.sleep(2)

    while (caget("TPX3-TEST:cam1:DetectorState_RBV") == 1):
        time.sleep(1)


    fast_sh.close()
    print("Acquisition complete!")

    caput("TPX3-TEST:cam1:RawFileTemplate", "none_")
    caput("TPX3-TEST:cam1:WriteRaw", 0)
    caput("TPX3-TEST:cam1:WriteData", 0)

def omega_series(fn, positions):

    for i, position in enumerate(positions):
        print(f"Moving to omega = {position}")
        RE(mv(diff.om,position))
        print(f"Saving to schema {fn}_{i}")
        save_timepix(f"{fn}_{i}_")
    
    print("All scans complete.")



