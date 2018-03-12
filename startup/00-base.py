import nslsii
from bluesky import RunEngine
from bluesky.utils import get_history, ts_msg_hook
RE = RunEngine(get_history())
nslsii.configure_base(get_ipython().user_ns, 'chx')

RE.msg_hook = ts_msg_hook
