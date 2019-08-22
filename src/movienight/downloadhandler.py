import logging
import os
import threading

import requests

log = logging.getLogger(__name__)

SERVER = "https://unmoon.com/dl/"


def get_next_filename():
    r = requests.get(SERVER + "NEXT")
    return str(r.content, "utf-8").strip()


def download_file_async(filename):
    file_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)
    file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
    headers = dict(Range="bytes={}-".format(file_size))

    log.debug("File path is '%s'", file_path)
    log.debug("Request headers are: '%s'", headers)

    r = requests.head(SERVER + filename, headers=headers)
    if "Content-Range" not in r.headers:
        log.debug("Server says we already got everything.")
        return
    log.debug("Download size: %s", r.headers["Content-Length"])

    buffer_event = threading.Event()

    thread = threading.Thread(
        target=download_file_sync,
        kwargs={
            "filename": filename,
            "file_path": file_path,
            "headers": headers,
            "buffer_event": buffer_event,
        },
    )
    thread.daemon = True
    thread.start()
    buffer_event.wait()


def download_file_sync(filename, file_path, headers, buffer_event):
    r = requests.get(SERVER + filename, headers=headers, stream=True)
    total_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
    session_size = 0
    with open(file_path, "ab") as file:
        for chunk in r.iter_content(8192):
            file.write(chunk)
            session_size += len(chunk)
            if total_size + session_size > 1e7 and not buffer_event.is_set():
                buffer_event.set()
    log.debug(
        "Download complete, total bytes written: %i (total size %i)",
        session_size,
        total_size + session_size,
    )
