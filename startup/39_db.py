import os
from urllib.parse import unquote, urlparse


def get_sid_filenames(header):
    """Deprecated; use :func:`get_scan_uid_filenames` instead."""
    raise DeprecationWarning(
        "get_sid_filenames() never returned filenames reliably; "
        "use get_scan_uid_filenames() instead"
    )


def _asset_path(data_uri):
    parsed = urlparse(data_uri)
    if parsed.scheme != "file":
        return data_uri
    return unquote(parsed.path)


def get_scan_uid_filenames(run, detector=None):
    """Return a run's scan ID, UID, and Tiled asset filenames.

    Parameters
    ----------
    run : BlueskyRun
        A Tiled Bluesky run, for example ``db[db.keys().last()]``.
    detector : str or ophyd.Device, optional
        Limit results to fields belonging to this detector. By default, assets
        for every detector and stream are returned.

    Returns
    -------
    scan_id : int
    uid : str
    filenames : list[str]
    """
    detector_name = getattr(detector, "name", detector)
    if detector_name is not None:
        detector_name = detector_name.casefold()

    filenames = []
    matched_detector = detector is None
    for stream_name in run:
        for field in get_fields(run, stream_name=stream_name):
            normalized_field = field.casefold()
            if detector_name is not None and not (
                normalized_field == detector_name
                or normalized_field.startswith(detector_name + "_")
            ):
                continue
            matched_detector = True
            try:
                field_client = run[stream_name, field]
            except KeyError:
                # Compatibility with the Tiled v2 stream layout.
                field_client = run[stream_name]["data"][field]
            if not hasattr(field_client, "data_sources"):
                continue
            data_sources = field_client.data_sources() or []
            manifests = field_client.asset_manifest(data_sources)
            for data_source in data_sources:
                for asset in data_source.assets:
                    asset_path = _asset_path(asset.data_uri)
                    relative_paths = manifests.get(asset.id)
                    if relative_paths is None:
                        filenames.append(asset_path)
                    else:
                        filenames.extend(
                            os.path.join(asset_path, relative_path)
                            for relative_path in relative_paths
                        )

    if not matched_detector:
        raise KeyError("Detector %r is not present in this run" % detector_name)

    start_md = run.start
    return start_md["scan_id"], start_md["uid"], list(dict.fromkeys(filenames))
