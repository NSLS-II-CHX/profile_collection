import nslsii
from bluesky import RunEngine
from bluesky.utils import get_history, ts_msg_hook
RE = RunEngine(get_history())
# bes=True means enable best effort callback
nslsii.configure_base(get_ipython().user_ns, 'chx', bec=True)

# use this to enable verbose printing of messages
#RE.msg_hook = ts_msg_hook
