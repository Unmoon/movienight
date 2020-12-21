import logging
import socket
import struct
import threading

from .config import config

log = logging.getLogger("movienight")


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
        self._socket.sendall(struct.pack(">??I?", True, True, time, False))

    def stop(self, time):
        log.debug("SET STOP: %i", time)
        self._socket.sendall(struct.pack(">??I?", True, False, time, False))

    def get(self):
        self._socket.sendall(struct.pack(">??I?", False, False, 0, False))

    def heartbeat(self):
        self._socket.sendall(struct.pack(">??I?", False, False, 0, True))

    def _listener(self):
        while True:
            data = self._socket.recv(1024)
            log.debug(data)
            playing, time, heartbeat = struct.unpack(">?I?", data)
            if heartbeat:
                log.debug("Heartbeat received!")
                self.heartbeat()
                log.debug("Heartbeat sent.")
                continue
            with self.lock:
                if playing:
                    log.debug("GET PLAY: %i", time)
                    self._play_callback(time)
                else:
                    log.debug("GET STOP: %i", time)
                    self._pause_callback(time)
