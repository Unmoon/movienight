import logging
import os
import threading

import requests

from .config import config

log = logging.getLogger(__name__)

SERVER = config.get("file_server")


def get_next_filename():
    r = requests.get(SERVER + "NEXT")
    return str(r.content, "utf-8").strip()


def download_file_async(filename, progress_callback):
    file_path = os.path.join(config.get("download_directory"), filename)
    file_url = SERVER + filename
    file_size = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
    headers = dict(Range="bytes={}-".format(file_size))

    buffer_event = threading.Event()

    log.debug("URL is '%s'", file_url)
    log.debug("File path is '%s'", file_path)
    log.debug("Request headers are: '%s'", headers)

    r = requests.head(file_url, headers=headers)
    if "Content-Range" not in r.headers:
        log.debug("Server says we already got everything.")
        progress_callback(filename, 100)
        buffer_event.set()
        return buffer_event
    log.debug("Download size: %s", r.headers["Content-Length"])

    thread = threading.Thread(
        target=download_file_sync,
        kwargs={
            "filename": filename,
            "file_path": file_path,
            "headers": headers,
            "buffer_event": buffer_event,
            "progress_callback": progress_callback,
        },
    )
    thread.daemon = True
    thread.start()
    return buffer_event


def download_file_sync(filename, file_path, headers, buffer_event, progress_callback):
    r = requests.get(SERVER + filename, headers=headers, stream=True)
    total_size = int(r.headers["Content-Range"].split("/")[1])
    downloaded = os.path.getsize(file_path) if os.path.isfile(file_path) else 0
    log.debug("Download size: %i", total_size)
    log.debug("Downloaded: %i", downloaded)
    log.debug("Progress: %f", (downloaded / total_size) * 100)
    last_progress = 0
    with open(file_path, "ab") as file:
        for chunk in r.iter_content(8192):
            file.write(chunk)
            downloaded += len(chunk)
            if downloaded > 1e7 and not buffer_event.is_set():
                buffer_event.set()
            current_progress = int((downloaded / total_size) * 100)
            if last_progress < current_progress:
                progress_callback(filename, current_progress)
                last_progress = current_progress
    log.debug("Download complete")


def delete_file(filename):
    os.remove(os.path.join(config.get("download_directory"), filename))
