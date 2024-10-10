import nslsii
import redis

import time
from redis_json_dict import RedisJSONDict
from tiled.client import from_profile
from ophyd.signal import EpicsSignalBase

EpicsSignalBase.set_defaults(timeout=60, connection_timeout=60)  # new style


class TiledInserter:
    def insert(self, name, doc):
        ATTEMPTS = 20
        error = None
        for _ in range(ATTEMPTS):
            try:
                tiled_writing_client.post_document(name, doc)
            except Exception as exc:
                print("Document saving failure:", repr(exc))
                error = exc
            else:
                break
            time.sleep(2)
        else:
            # Out of attempts
            raise error

tiled_inserter = TiledInserter()

# The function below initializes RE
nslsii.configure_base(get_ipython().user_ns,
               tiled_inserter,
               publish_documents_with_kafka=True)

tiled_writing_client = from_profile("nsls2", api_key=os.environ["TILED_BLUESKY_WRITING_API_KEY_CHX"])["chx"]["raw"]

print("Initializing Tiled reading client...\nMake sure you check for duo push.")
db = tiled_reading_client = from_profile("nsls2")["tes"]["raw"]

# set plot properties for 4k monitors
plt.rcParams['figure.dpi']=200

# Set the metadata dictionary
RE.md = RedisJSONDict(redis.Redis("info.chx.nsls2.bnl.gov"), prefix="")

# Setup the path to the secure assets folder for the current proposal
assets_path = f"/nsls2/data/chx/proposals/{RE.md['cycle']}/{RE.md['data_session']}/assets/"