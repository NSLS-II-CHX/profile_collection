t = "{start[plan_name]} ['{start[uid]:.6}'] (scan num: {start[scan_id]})"

def f(header, factory):
    start = get_run_start(header)
    plan_name = start['plan_name']
    if plan_name in ('dscan', 'relative_scan'):
        motor, = start['motors']
        data_keys = get_fields(header)
        for key in data_keys:
            if key.endswith('stats1_total'):
                break
        fig = factory("stats1_total vs {}".format(motor))
        ax = fig.gca()
        table = get_table(header, fields=[motor, key])
        ax.plot(table[motor], table[key])


def browse():
    return BrowserWindow(db, f, t)
