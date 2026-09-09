t = "{start[plan_name]} ['{start[uid]:.6}'] (scan num: {start[scan_id]})"


def f(header, factory, fields=None):
    start_md = header.start
    plan_name = start_md['plan_name']
    if plan_name in ('dscan', 'relative_scan'):
        motor, = start_md['motors']
        data_keys = get_fields(header)
        field_metadata = {
            key: metadata
            for descriptor in header['primary'].descriptors
            for key, metadata in descriptor['data_keys'].items()
        }
        scalar_keys = {
            key for key in data_keys if not field_metadata.get(key, {}).get('shape')
        }
        if fields is None:
            detectors = [name.casefold() for name in start_md.get('detectors', [])]
            fields = [
                key
                for key in data_keys
                if key != motor
                and key in scalar_keys
                and any(
                    key.casefold() == detector
                    or key.casefold().startswith(detector + '_')
                    for detector in detectors
                )
            ]
            if not fields:
                fields = [
                    key
                    for key in data_keys
                    if key not in (motor, 'time') and key in scalar_keys
                ]
        elif isinstance(fields, str):
            fields = [fields]
        missing = set(fields) - set(data_keys)
        if missing:
            raise KeyError('Fields are not present in this run: %s' % sorted(missing))
        nonscalar = set(fields) - scalar_keys
        if nonscalar:
            raise ValueError('Only scalar fields can be plotted: %s' % sorted(nonscalar))
        if not fields:
            return
        fig = factory("{} vs {}".format(', '.join(fields), motor))
        ax = fig.gca()
        table = get_table(header, fields=[motor, *fields])
        for field in fields:
            ax.plot(table[motor], table[field], label=field)
        if len(fields) > 1:
            ax.legend()


def browse(fields=None):
    return BrowserWindow(db, lambda header, factory: f(header, factory, fields), t)
