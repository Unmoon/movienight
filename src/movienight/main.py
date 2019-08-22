import logging
import os
import platform
import sys
from threading import Lock
from time import sleep

import vlc
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from movienight.downloadhandler import download_file_async
from movienight.downloadhandler import get_next_filename
from movienight.synchandler import SyncHandler

log = logging.getLogger(__name__)

TITLE = "Movie Night"


class Player(QtWidgets.QMainWindow):
    """A simple Media Player using VLC and Qt."""

    def __init__(self, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle(TITLE)
        # Create a basic vlc instance
        self.instance = vlc.Instance()

        self.media = None
        self.lock = Lock()

        # Create an empty vlc media player
        self.media_player = self.instance.media_player_new()
        self.media_player.video_set_mouse_input(False)
        self.media_player.video_set_key_input(False)
        self.video_frame = None
        self.widget = None
        self.palette = None
        self.h_button_box = None
        self.play_button = None
        self.volume_slider = None
        self.subtitle_tracks_label = None
        self.subtitle_tracks = None
        self.audio_tracks_label = None
        self.audio_tracks = None
        self.audio_delay = None
        self.audio_delay_label = None
        self.v_box_layout = None
        self.timer = None
        self.create_ui()

        self.delay = 0
        self.connection = SyncHandler(
            play_callback=self.play, pause_callback=self.pause, lock=self.lock
        )

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.windowState() == QtCore.Qt.WindowFullScreen:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.volume_slider.show()
                self.audio_delay.show()
                self.play_button.show()
                self.audio_tracks_label.show()
                self.audio_tracks.show()
                self.subtitle_tracks_label.show()
                self.subtitle_tracks.show()
                self.audio_delay_label.show()
                self.audio_delay.show()
                self.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
            else:
                self.setWindowState(QtCore.Qt.WindowFullScreen)
                self.volume_slider.hide()
                self.audio_delay.hide()
                self.play_button.hide()
                self.audio_tracks_label.hide()
                self.audio_tracks.hide()
                self.subtitle_tracks_label.hide()
                self.subtitle_tracks.hide()
                self.audio_delay_label.hide()
                self.audio_delay.hide()
                self.setCursor(QtGui.QCursor(QtCore.Qt.BlankCursor))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            log.debug("is_playing: %s", self.media_player.is_playing())
            with self.lock:
                if self.media_player.is_playing() == 1:
                    self.pause()
                else:
                    self.play()

    def create_ui(self):
        """Set up the user interface, signals & slots."""
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if platform.system() == "Darwin":  # for MacOS
            self.video_frame = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.video_frame = QtWidgets.QFrame()

        self.palette = self.video_frame.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.video_frame.setPalette(self.palette)
        self.video_frame.setAutoFillBackground(True)

        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(self.media_player.audio_get_volume())
        self.volume_slider.setToolTip("Volume")
        self.volume_slider.valueChanged.connect(self.set_volume)

        self.play_button = QtWidgets.QPushButton("Play")
        self.play_button.clicked.connect(
            lambda: self.pause() if self.media_player.is_playing() == 1 else self.play()
        )

        self.subtitle_tracks_label = QtWidgets.QLabel("Subtitle Track:", self)
        self.subtitle_tracks = QtWidgets.QComboBox(self)
        self.subtitle_tracks.setMinimumWidth(200)
        self.subtitle_tracks.activated[str].connect(self.set_subtitle_track)

        self.audio_tracks_label = QtWidgets.QLabel("Audio Track:", self)
        self.audio_tracks = QtWidgets.QComboBox(self)
        self.audio_tracks.setMinimumWidth(200)
        self.audio_tracks.activated[str].connect(self.set_audio_track)

        self.audio_delay_label = QtWidgets.QLabel("Audio Delay:", self)
        self.audio_delay = QtWidgets.QLineEdit()
        self.audio_delay.setValidator(QtGui.QDoubleValidator(-5.0, 5.0, 2))
        self.audio_delay.setMaxLength(4)
        self.audio_delay.setMaximumWidth(50)
        self.audio_delay.setAlignment(QtCore.Qt.AlignRight)
        self.audio_delay.setText(str(self.media_player.audio_get_delay()))
        self.audio_delay.editingFinished.connect(
            lambda: self.set_audio_delay(
                float(self.audio_delay.text().replace(",", "."))
            )
        )

        self.h_button_box = QtWidgets.QHBoxLayout()
        self.h_button_box.addWidget(self.play_button)
        self.h_button_box.addWidget(self.audio_tracks_label)
        self.h_button_box.addWidget(self.audio_tracks)
        self.h_button_box.addWidget(self.subtitle_tracks_label)
        self.h_button_box.addWidget(self.subtitle_tracks)
        self.h_button_box.addWidget(self.audio_delay_label)
        self.h_button_box.addWidget(self.audio_delay)
        self.h_button_box.addStretch(1)
        self.h_button_box.addWidget(self.volume_slider)

        self.v_box_layout = QtWidgets.QVBoxLayout()
        self.v_box_layout.addWidget(self.video_frame)
        self.v_box_layout.addLayout(self.h_button_box)
        self.v_box_layout.setContentsMargins(0, 0, 0, 0)

        self.widget.setLayout(self.v_box_layout)

    def play(self, time=None):
        if self.media_player.is_playing() == 1:
            return
        self.media_player.play()
        self.play_button.setText("Pause")
        if time is None:
            self.send_sync(False)
        else:
            self.sync(time)

    def pause(self, time=None):
        if self.media_player.is_playing() == 0:
            return
        if time is None:
            self.send_sync(False)
        else:
            self.sync(time)
        self.media_player.pause()
        self.play_button.setText("Play")

    def set_audio_delay(self, delay):
        """Set delay in seconds for audio."""
        self.delay = int(delay * 1000000)
        if self.media_player.is_playing() == 1:
            log.debug(self.media_player.audio_set_delay(self.delay))

    def set_subtitle_track(self, subtitle_track):
        for key, value in self.media_player.video_get_spu_description():
            if str(value, "utf-8") == subtitle_track:
                self.media_player.video_set_spu(key)
                log.debug("Setting subtitle track to %s (%i)", value, key)
                return

    def set_audio_track(self, audio_track):
        for key, value in self.media_player.audio_get_track_description():
            if str(value, "utf-8") == audio_track:
                self.media_player.audio_set_track(key)
                log.debug("Setting audio track to %s (%i)", value, key)
                return

    def open_file(self, filename):
        """Open a media file in a MediaPlayer."""

        file_path = os.path.join(os.path.expanduser("~"), "Downloads", filename)

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(file_path)

        # Put the media in the media player
        self.media_player.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as window title
        self.setWindowTitle(TITLE + " - " + self.media.get_meta(0))

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux":  # for Linux using the X Server
            self.media_player.set_xwindow(int(self.video_frame.winId()))
        elif platform.system() == "Windows":  # for Windows
            self.media_player.set_hwnd(int(self.video_frame.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self.media_player.set_nsobject(int(self.video_frame.winId()))

    def set_volume(self, volume):
        """Set the volume."""
        self.media_player.audio_set_volume(volume)

    def send_sync(self, playing):
        time = max(self.media_player.get_time(), 0)
        if playing:
            log.debug("Playing at %i", time)
            self.connection.play(time)
        else:
            log.debug("Pausing at %i", time)
            self.connection.stop(time)
        log.debug("Synced server to %i", time)

    def sync(self, time):
        log.debug("Synced client to %i", time)
        self.media_player.set_time(time)

    def load_subtitle_tracks(self):
        if self.subtitle_tracks.count() < self.media_player.video_get_spu_count():
            subtitle_tracks = list()
            current_subtitle_track = self.media_player.video_get_spu()
            for key, value in self.media_player.video_get_spu_description():
                if key == current_subtitle_track:
                    current_subtitle_track = str(value, "utf-8")
                subtitle_tracks.append(str(value, "utf-8"))
            self.subtitle_tracks.insertItems(0, subtitle_tracks)
            self.subtitle_tracks.setCurrentIndex(
                self.subtitle_tracks.findText(
                    current_subtitle_track, QtCore.Qt.MatchFixedString
                )
            )

    def load_audio_tracks(self):
        if self.audio_tracks.count() < self.media_player.audio_get_track_count():
            audio_tracks = list()
            current_audio_track = self.media_player.audio_get_track()
            for key, value in self.media_player.audio_get_track_description():
                if key == current_audio_track:
                    current_audio_track = str(value, "utf-8")
                audio_tracks.append(str(value, "utf-8"))
            self.audio_tracks.insertItems(0, audio_tracks)
            self.audio_tracks.setCurrentIndex(
                self.audio_tracks.findText(
                    current_audio_track, QtCore.Qt.MatchFixedString
                )
            )


def main():
    filename = get_next_filename()
    download_file_async(filename)
    app = QtWidgets.QApplication(sys.argv)
    player = Player()
    player.show()
    player.resize(1280, 720)
    player.open_file(filename)
    player.media_player.play()
    while player.media_player.get_state() in (
        vlc.State.Opening,
        vlc.State.NothingSpecial,
    ):
        sleep(0.01)
    player.media_player.pause()
    player.load_audio_tracks()
    player.load_subtitle_tracks()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
