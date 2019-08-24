import logging
import socket
import struct
import threading

from .config import config

log = logging.getLogger(__name__)


class SyncHandler:
    def __init__(self, play_callback, pause_callback, lock):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((config.get("sync_server"), 9512))
        self._play_callback = play_callback
        self._pause_callback = pause_callback
        self.lock = lock
        self._thread = threading.Thread(target=self._listener)
        self._thread.daemon = True
        self._thread.start()

    def play(self, time):
        log.debug("SET PLAY: %i", time)
        self._socket.sendall(struct.pack(">??I", True, True, time))

    def stop(self, time):
        log.debug("SET STOP: %i", time)
        self._socket.sendall(struct.pack(">??I", True, False, time))

    def get(self):
        self._socket.sendall(struct.pack(">??I", False, False, 0))

    def _listener(self):
        while True:
            data = self._socket.recv(1024)
            log.debug(data)
            playing, time = struct.unpack(">?I", data)
            with self.lock:
                if playing:
                    log.debug("GET PLAY: %i", time)
                    self._play_callback(time)
                else:
                    log.debug("GET STOP: %i", time)
                    self._pause_callback(time)
