import logging
import socket
import struct
import threading

log = logging.getLogger(__name__)

SERVER = "unmoon.com"


class SyncHandler:
    def __init__(self, set_time_callback, play_callback, pause_callback, lock):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((SERVER, 9512))
        self._set_time_callback = set_time_callback
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
                    self._play_callback()
                    self._set_time_callback(time)
                else:
                    log.debug("GET STOP: %i", time)
                    self._set_time_callback(time)
                    self._pause_callback()