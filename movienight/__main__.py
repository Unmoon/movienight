import logging
import os
import sys
import time

import vlc
from PyQt5 import QtGui
from PyQt5 import QtWidgets

from movienight.gui.downloadmanager import DownloadManager
from movienight.gui.videoplayer import VideoPlayer

log = logging.getLogger("movienight")


# Translate asset paths to usable format for PyInstaller
# https://blog.aaronhktan.com/posts/2018/05/14/pyqt5-pyinstaller-executable
def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(resource_path("Movie Night.ico")))
    download_manager = DownloadManager()
    video_player = VideoPlayer()

    center = QtWidgets.QApplication.desktop().availableGeometry().center()
    download_manager.move(
        int(center.x() - download_manager.width() * 0.5),
        int(center.y() - download_manager.height() * 0.5),
    )
    video_player.move(
        int(center.x() - video_player.width() * 0.5),
        int(center.y() - video_player.height() * 0.5),
    )

    download_manager.show()
    video_player.show()

    if download_manager.reload_needed:
        download_manager.reload_files()

    # Wait for file to buffer enough (100MB)
    download_manager.file_ready.wait()
    filename = download_manager.get_next_filename()
    video_player.open_file(filename)
    video_player.media_player.play()
    # Wait for VLC to parse the subtitle/audio tracks
    while video_player.media_player.get_state() in (
        vlc.State.Opening,
        vlc.State.NothingSpecial,
    ):
        time.sleep(0.001)
    video_player.media_player.pause()
    video_player.load_audio_tracks()
    video_player.load_subtitle_tracks()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
