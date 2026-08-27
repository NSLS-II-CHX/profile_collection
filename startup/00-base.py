import os
import nslsii
from bluesky import RunEngine
import time
import numpy as np
import pandas as pd
from redis_json_dict import RedisJSONDict
from tiled.client import from_profile
from ophyd.signal import EpicsSignalBase

EpicsSignalBase.set_defaults(timeout=60, connection_timeout=60)  # new style

from IPython import get_ipython
from IPython.terminal.prompts import Prompts, Token

# Configure a Tiled writing client
tiled_writing_client = from_profile("nsls2", api_key=os.environ["TILED_BLUESKY_WRITING_API_KEY_CHX"])["chx"]["raw"]
tiled_writing_client.context.http_client.headers['tiled-qos'] = 'acquisition'


class TiledInserter:

    name = "chx"

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

nslsii.configure_base(get_ipython().user_ns,
                      tiled_inserter,
                      redis_url="xf11id1-chx-redis1.nsls2.bnl.gov",
                      redis_port=6380,
                      redis_ssl=True,
                      publish_documents_with_kafka=True)

print("Initializing Tiled reading client...\nMake sure you check for duo push.")
tiled_reading_client = from_profile("nsls2", username=None, include_data_sources=True)["chx"]["raw"]
tiled_reading_client.context.http_client.headers['tiled-qos'] = 'acquisition'

db = tiled_reading_client


def get_run_start(run):
    return run.metadata["start"]


def get_run_data(run, stream_name="primary"):
    return run[stream_name]["data"]


def get_fields(run, stream_name="primary"):
    return list(get_run_data(run, stream_name).keys())


def get_table(run, fields=None, stream_name="primary"):
    ds = get_run_data(run, stream_name)
    keys = list(ds.keys()) if fields is None else fields
    data = {}
    for key in keys:
        value = ds[key].read().squeeze()
        array = value.to_numpy() if hasattr(value, "to_numpy") else np.asarray(value)
        if fields is None and array.ndim > 1:
            continue
        data[key] = np.atleast_1d(array)
    return pd.DataFrame(data)


def get_images(run, field, stream_name="primary"):
    return get_run_data(run, stream_name)[field].read()

# set plot properties for 4k monitors
plt.rcParams["figure.dpi"] = 200


# Setup the path to the secure assets folder for the current proposal
def assets_path():
    return f"/nsls2/data/chx/proposals/{RE.md['cycle']}/{RE.md['data_session']}/assets/"


class ProposalIDPrompt(Prompts):
    def in_prompt_tokens(self, cli=None):
        return [
            (
                Token.Prompt,
                f"{RE.md.get('data_session', 'N/A')} [",
            ),
            (Token.PromptNum, str(self.shell.execution_count)),
            (Token.Prompt, "]: "),
        ]


ip = get_ipython()
ip.prompts = ProposalIDPrompt(ip)
