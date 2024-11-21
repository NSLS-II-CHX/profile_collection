class collection_uid:
    """
    class to create and broadcast collection uids via EPICS PV
    .new_col_uid: created new collection uid and broadcasts it to EPICS PV col_uid_pv
    .get_col_uid: get collection uid from EPICS PV
    .reset_col_uid: reset EPICS PV to ''
    """
    col_uid_pv = 'XF:11ID-CT{ES:1}ai6.DESC' # this is temporary while we don't have EPICS string records implemented

    def new_col_uid(output=False):
        col_uid=uuid.uuid4().hex
        caput(collection_uid.col_uid_pv, col_uid)
        print('new collection uid: %s'%col_uid)
        if output:
            return col_uid
    def get_col_uid():
        return  caget(collection_uid.col_uid_pv)
    def reset_col_uid():
        caput(collection_uid.col_uid_pv,'')
        print('reset collection uid to None')
    def get_col_uid_pv():
        return collection_uid.col_uid_pv