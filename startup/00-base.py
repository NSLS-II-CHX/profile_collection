import nslsii
from bluesky import RunEngine
from bluesky.utils import get_history
RE = RunEngine(get_history())
nslsii.configure_base(get_ipython().user_ns, 'chx')

# Turn down super-verbose logging for caproto
import logging
logging.getLogger('caproto').setLevel('ERROR')
logging.getLogger('caproto.ch').setLevel('ERROR')
