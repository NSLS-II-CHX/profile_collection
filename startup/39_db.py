def get_sid_filenames(header):
    """YG. Dev Jan, 2016
    ---------------- DEPRECATED -----------------
    Get a bluesky scan_id, unique_id, filename by giveing uid
        
    Parameters
    ----------
    header: a header of a bluesky scan, e.g. db[-1]
        
    Returns
    -------
    scan_id: integer
    unique_id: string, a full string of a uid
    filename: sring
    
    Usuage:
    sid,uid, filenames   = get_sid_filenames(db[uid])
    
    """   
    start = get_run_start(header)
    return start['scan_id'],  start['uid'], []
