class collection_uid:
    """
    class to create and broadcast collection uids via EPICS PV
    .new_col_uid: created new collection uid and broadcasts it to EPICS PV col_uid_pv
    .get_col_uid: get collection uid from EPICS PV
    .reset_col_uid: reset EPICS PV to ''
    """
    col_uid_pv = 'XF:11ID-CT{ES:1}ai6.DESC'
    
    def new_col_uid():
        col_uid=uuid.uuid4().hex
        caput(collection_uid.col_uid_pv, col_uid)
        try_N=20;tt=0
        while caget(collection_uid.col_uid_pv) != col_uid and tt<try_N:
            RE(sleep(.2));tt+=1
        print('new collection uid: %s'%col_uid)

       
    def get_col_uid():
        return  caget(collection_uid.col_uid_pv)

        
    def reset_col_uid():
        caput(collection_uid.col_uid_pv,'')
        print('reset collection uid to None')
