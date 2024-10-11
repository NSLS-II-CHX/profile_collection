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
    filepaths = []
    db = header.db
    # get files from assets
    res_uids = db.get_resource_uids(header)
    for uid in res_uids:
        datum_gen = db.reg.datum_gen_given_resource(uid)
        datum_kwarg_gen = (datum['datum_kwargs'] for datum in
                           datum_gen)
        filepaths.extend(db.reg.get_file_list(uid, datum_kwarg_gen))
    return header.start['scan_id'],  header.start['uid'], filepaths
