'''import sys
import os
from typing import Callable
from ast import literal_eval
from urllib.error import URLError
from time import sleep

from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QPushButton, QLabel, QLineEdit, \
    QWidget, QSizePolicy, QCheckBox, QMdiSubWindow, QFrame, QTextEdit, QDialog, QHBoxLayout, qApp, QGridLayout
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QKeySequence, QFont, QIcon, QPixmap, QPalette, QBrush, QColor
from qroundprogressbar import QRoundProgressBar

from pytube import YouTube
from pytube.streams import Stream
from pytube.exceptions import RegexMatchError, VideoUnavailable

from moviepy.editor import AudioFileClip


class Audio:
    """Class for converting mp4 files with no frames
    to mp3 files."""

    def __init__(self, path: str, filename: str) -> None:
        """Defines path to file."""
        self.path = self._rebuild_path(path)
        self.filename = filename
        self.mp4_location = self._build_location()

    def _build_location(self) -> str:
        """Concatenates path to folder and filename together."""
        location = os.path.join(self.path, self.filename)
        return location

    def save_as_mp3(self) -> None:
        """General function to handle conversion
        to mp3 and saving process.
        :raises: FileNotFoundError, if the path to
        file does not lead anywhere."""
        if self._check_existence():
            self._convert_and_write()


    def _convert_and_write(self):
        """Convert the mp4 file with no frames to mp3,
        write the audio file to the same folder."""
        audio = AudioFileClip(self.mp4_location)
        audio.write_audiofile(self._build_mp3_path())

    def _remove_mp4(self):
        """Remove the mp4 file with no frames
        after conversion."""
        os.remove(self.mp4_location)

    def _check_existence(self) -> bool:
        """Check if the file to convert exists,
        and the file that should be created does not.
        :raises: FileExistError, if the mp3 file, with the
        designated name already exists in the directory
        with the mp4 file
        :raises: FileNotFoundError, if the path to
        the mp4 file does not actually lead to a file."""
        mp3_file = self._build_mp3_path()
        if os.path.exists(self.mp4_location):
            return True
        else:
            raise FileNotFoundError

    def _build_mp3_path(self) -> str:
        """Build the path where mp3 file
        is going to be saved."""
        mp3_location = self.mp4_location.rsplit('.', maxsplit=1)[0] + '.mp3'
        return mp3_location

    @staticmethod
    def _rebuild_path(path: str) -> str:
        """Replace all '/' symbols,
        so path to folder and filename
        can be concatenated through os.path.join."""
        new_path = path.replace('/', '\\')
        return new_path


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(QRect(500, 100, 600, 400))
        self.setWindowTitle('PronConverterService')

        self.label = QLabel(self)
        self.label.setGeometry(QRect(20, 10, 500, 50))
        self.label.setText('Restore files in:')
        self.label.setFont(QFont('Century Gothic', 16, QFont.Normal))

        self.vid_url = QLineEdit(self)
        self.vid_url.setGeometry(QRect(30, 60, 200, 50))
        self.vid_url.setPlaceholderText('Video Url')

        self.download_btn = QPushButton(self)
        self.download_btn.setText('Download')
        self.download_btn.setGeometry(QRect(250, 60, 120, 50))
        self.download_btn.clicked.connect(self.restore_files)
        self.download_btn.setFont(QFont('Century Gothic', 16, QFont.Normal))
        self.download_btn.setStyleSheet(':hover{'
                                        'background-color: black; '
                                        'color: orange;'
                                        '}')

    def restore_files(self):
        directory = self.vid_url.text()
        print(os.listdir(directory))
        for i in os.listdir(directory):
            audio = Audio(directory, i)
            audio.save_as_mp3()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())'''
from pytube import YouTube
from time import time
ts = time()
print(f'https://youtu.be/K4TOrB7at0Y: '
      f'{YouTube("https://youtu.be/K4TOrB7at0Y").streams.get_by_itag(251)}')
print(time())