import sys
import os
from typing import Callable, Literal
from ast import literal_eval
from urllib.error import URLError
from time import sleep, time
from queue import Queue
from threading import Thread
from PyQt5.QtWidgets import QApplication, QMainWindow, QShortcut, QPushButton, QLabel, QLineEdit, QWidget, QSizePolicy, QCheckBox, QMdiSubWindow, QFrame, QTextEdit, QDialog, QHBoxLayout, qApp, QGridLayout
from PyQt5.QtCore import QRect, Qt, QTimer
from PyQt5.QtGui import QKeySequence, QFont, QIcon, QPixmap, QPalette, QBrush, QColor
from qroundprogressbar import QRoundProgressBar
from pytube import YouTube
from pytube.streams import Stream
from pytube.exceptions import RegexMatchError, VideoUnavailable
from moviepy.editor import AudioFileClip
class InvalidResolution(AttributeError):
    ...
class CircularProgressBar(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setObjectName("TestWidget")
        self.resize(300, 400)
        self.horizontal_layout = QHBoxLayout(self)
        self.horizontal_layout.setContentsMargins(11, 11, 11, 11)
        self.horizontal_layout.setSpacing(6)
        self.horizontal_layout.setObjectName("horizontal_layout")
        self.grid_layout = QGridLayout()
        self.grid_layout.setContentsMargins(11, 11, 11, 11)
        self.grid_layout.setSpacing(6)
        self.grid_layout.setObjectName("gridLayout_3")
        self.RoundBar6 = QRoundProgressBar(self)
        palette = QPalette()
        brush = QBrush(QColor(170, 170, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush)
        self.RoundBar6.setPalette(palette)
        self.RoundBar6.setObjectName("RoundBar6")
        self.grid_layout.addWidget(self.RoundBar6, 2, 2, 1, 1)
        self.horizontal_layout.addLayout(self.grid_layout)
        self.grid_layout.setContentsMargins(11, 11, 11, 11)
        self.grid_layout.setSpacing(4)
        self.label = QLabel(self)
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(size_policy)
        font = QFont('Century Gothic', 16, QFont.Normal)
        self.label.setFont(font)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("label_4")
        self.grid_layout.addWidget(self.label, 3, 2, 1, 1)
        self.setWindowFlags(Qt.CustomizeWindowHint)
        self.RoundBar6.setDecimals(1)
        self.RoundBar6.setBarStyle(QRoundProgressBar.BarStyle.LINE)
        self.RoundBar6.setOutlinePenWidth(18)
        self.RoundBar6.setDataPenWidth(10)
        self.timer = Timer()
    def set_progress(self, progress: int) -> None:
        self.RoundBar6.setValue(progress)
        qApp.processEvents()
    def quick_progress(self, start_point: int,
                       stop_point: int,
                       step: int,
                       waiting_time: int) -> None:
        for i in range(start_point, stop_point, step):
            self.RoundBar6.setValue(i)
            qApp.processEvents()
            self.timer.start_timer(waiting_time)
    def set_label_text(self, text: str) -> None:
        self.label.setText(text)
        self.label.update()
    @property
    def get_current_progress(self) -> int:
        return self.RoundBar6.m_value.real
class Settings:
    with open('pronamka_downloader_settings.txt') as settings_file:
        all_settings: dict = literal_eval(settings_file.read())
        default_download_path: dict = all_settings.get('DefaultDownloadPath')
    def get_path_for(self, f_type: Literal['audio', 'video']):
        return self.default_download_path.get(f_type, None)
    @classmethod
    def change_settings(cls, key: str, value: str) -> None:
        cls.default_download_path[key] = value
        with open('pronamka_downloader_settings.txt', mode='w') as settings_file:
            settings_file.write("{'DefaultDownloadPath': " +
                                f'{cls.default_download_path}' + '}')
class Label(QLabel):
    default_settings = ''
    def __init__(self, application: QWidget, geometry: QRect, text: str, font: QFont = None) -> None:
        super(Label, self).__init__()
        self.font = QFont() if font is None else font
        self.setParent(application), self.setFont(self.font)
        self.default_style_sheet = self.styleSheet()
        self.setGeometry(geometry)
        self.setWordWrap(True)
        self.setIndent(10)
        self.setText(text)
    def set_default_style(self) -> None:
        self.setStyleSheet(self.default_style_sheet)
    def set_size_policy_and_adjustment(self) -> None:
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        size_policy.setHorizontalStretch(0), size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(size_policy)
        self.setAlignment(Qt.AlignCenter)
class PushButton(QPushButton):
    def __init__(self, parent: QWidget, geometry: QRect, text: str, func: Callable) -> None:
        super(PushButton, self).__init__()
        self.setParent(parent)
        self.setGeometry(geometry)
        self.setText(text)
        self.clicked.connect(func)
class LineEdit(QLineEdit):
    def __init__(self, application: QWidget, geometry: QRect, text: str = None) -> None:
        super(LineEdit, self).__init__()
        self.setParent(application)
        self.setGeometry(geometry)
        self.setPlaceholderText(text)
class SettingsWindow(QMdiSubWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle('Settings')
        self.move(600, 200)
        self.setFixedSize(600, 400)
        self.video_default_path = QTextEdit(self)
        self.video_default_path.setGeometry(175, 80, 400, 90)
        self.video_default_path.setText(Settings().get_path_for('video'))
        self.video_default_path.setFont(QFont('Century Gothic', 10, QFont.Normal))
        self.audio_default_path = QTextEdit(self)
        self.audio_default_path.setGeometry(175, 230, 400, 90)
        self.audio_default_path.setFont(QFont('Century Gothic', 10, QFont.Normal))
        self.audio_default_path.setText(Settings().get_path_for('audio'))
        self.main_menu_label = Label(self, QRect(10, 25, 90, 200), 'Default Downlo- ading Paths:', QFont('Calibri', 16, QFont.Normal))
        self.main_menu_label.setAlignment(Qt.AlignTop)
        Label(self, QRect(165, 30, 200, 50), 'Video:', QFont('Roboto', 16, QFont.StyleItalic))
        Label(self, QRect(165, 180, 200, 50), 'Audio', QFont('Roboto', 16, QFont.StyleItalic))
        PushButton(self, QRect(470, 350, 100, 30), 'OK', lambda: self.__save_changes())
        self.sep = QFrame(self)
        self.sep.setFrameShape(QFrame.VLine)
        self.sep.setGeometry(QRect(100, 0, 100, self.height()))
    def __save_changes(self) -> None:
        new_video_path = self.video_default_path.toPlainText()
        new_audio_path = self.audio_default_path.toPlainText()
        self._save_video(new_video_path)
        self._save_audio(new_audio_path)
        self.close()
    def _save_video(self, path: str) -> None:
        if not os.path.isdir(path):
            warning_dialog = WarningDialog(self)
            warning_dialog.show_warning(FileNotFoundError(path))
        elif path and path != Settings().get_path_for('video'):
            Settings.change_settings('video', path)
    def _save_audio(self, path: str) -> None:
        if not os.path.isdir(path):
            warning_dialog = WarningDialog(self)
            warning_dialog.show_warning(FileNotFoundError(path))
        elif path and path != Settings().get_path_for('audio'):
            Settings.change_settings('audio', path)
class WarningDialog(QDialog):
    exceptions_images = {FileExistsError: 'images/warning_sign.png',URLError: 'images/no_connection.png',FileNotFoundError: 'images/warning_sign.png',RegexMatchError: 'images/broken_link.png',VideoUnavailable: 'images/video_unavailable.png',InvalidResolution: 'images/invalid_resolution.png'}
    exception_messages = {FileExistsError:'File with the name "{}" already exists in "{}"',URLError:'The app could not establish internet connection. Please check your network settings, ensure that you have internet and try again. If it did not help, contact me at defender0508@gmail.com',FileNotFoundError:'Location "{}" does not exist.',RegexMatchError:'The link you have given does not lead anywhere.',VideoUnavailable:'The video you are trying to download either does not exist or unavailable for some reason.',InvalidResolution: 'The video you chose to download does not have resolution you have given. The video was downloaded with the highest resolution possible.'}
    def __init__(self, parent: QWidget = None):
        if parent:
            super().__init__(parent)
        self.setGeometry(700, 300, 700, 300)
        self.button_box = QPushButton(self)
        self.button_box.setGeometry(580, 260, 100, 30)
        self.button_box.setText('Ok')
        self.button_box.clicked.connect(self.reject)
        self.layout = QHBoxLayout()
        self.pixmap_label = Label(self, QRect(10, 45, 225, 225), '')
        self.pixmap_label.set_size_policy_and_adjustment()
        self.warning_label = QLabel(self)
        self.warning_label.setText('')
        self.warning_label.setFont(QFont('Roboto', 16, QFont.Cursive))
        self.warning_label.adjustSize()
        self.warning_label.setMinimumWidth(300)
        self.warning_label.setMaximumHeight(self.height() - 40)
        self.warning_label.setWordWrap(True)
        self.layout.addWidget(self.pixmap_label)
        self.layout.addWidget(self.warning_label, alignment=Qt.AlignTop)
        self.layout.addWidget(self.button_box, alignment=Qt.AlignBottom)
        self.setLayout(self.layout)
    def show_warning(self, exception: Exception) -> None:
        self.set_up_warning(exception.__class__, exception.args)
        self.show()
    def set_up_warning(self, exception_type, info) -> None:
        self.set_up_pixmap(exception_type)
        self.set_up_label(exception_type, info)
    def set_up_label(self, exception_type, info) -> None:
        self.warning_label.setText(self.exception_messages.get(exception_type).format(*info))
    def set_up_pixmap(self, exception_type) -> None:
        warning_sign = QPixmap(self.exceptions_images.get(exception_type, None))
        self.pixmap_label.setPixmap(warning_sign.scaled(225, 225,Qt.KeepAspectRatio, Qt.SmoothTransformation))
class Timer(QTimer):
    def __init__(self) -> None:
        super().__init__()
    def start_timer(self, milliseconds: int) -> None:
        self.start(milliseconds)
class FileForDownloading:
    @staticmethod
    def _build_location(path: str, filename: str) -> str:
        location = os.path.join(path, filename)
        return location
    @staticmethod
    def _rebuild_path(path: str) -> str:
        new_path = path.replace('/', '\\')
        return new_path
class Audio(FileForDownloading):
    def __init__(self, audio_file: Stream, path: str) -> None:
        self.audio = audio_file
        self.path = self._rebuild_path(path)
        self.filename = audio_file.default_filename
        self.mp4_location = self._build_location(self.path, self.filename)
    def download_file(self):
        self._save_as_mp4()
        self._save_as_mp3()
    def _save_as_mp4(self):
        self.audio.download(self.path)
    def _save_as_mp3(self) -> None:
        if self._check_existence():
            self._convert_and_write()
            self._remove_mp4()
    def _convert_and_write(self):
        ts = time()
        audio = AudioFileClip(self.mp4_location)
        audio.write_audiofile(self._build_mp3_path(),)
        print(time()-ts)
    def _remove_mp4(self):
        os.remove(self.mp4_location)
    def _check_existence(self) -> bool:
        mp3_file = self._build_mp3_path()
        if os.path.exists(self.mp4_location) and not os.path.exists(mp3_file):
            return True
        elif os.path.exists(mp3_file):
            os.remove(self.mp4_location)
            mp3_filename = mp3_file.rsplit('\\', maxsplit=1)[1]
            raise FileExistsError(mp3_filename, self.path)
        else:
            print(self.path)
            raise FileNotFoundError(self.path)
    def _build_mp3_path(self) -> str:
        mp3_location = self.mp4_location.rsplit('.', maxsplit=1)[0] + '.mp3'
        return mp3_location
class Video(FileForDownloading):
    def __init__(self, video_file: YouTube, path: str, resolution: str):
        self.video = video_file
        self.path = self._rebuild_path(path)
        self.resolution = resolution
        self.errors = []
    def download_file(self) -> None:
        video = self._check_resolution()
        if not video:
            video = self._get_in_highest_resolution()
        video.download(self.path)
        if self.errors:
            raise self.errors.pop()
    def _check_resolution(self) -> [YouTube, None]:
        if self.resolution:
            if not (video := self.video.streams.get_by_resolution('resolution')):
                return video
            else:
                self.errors.append(InvalidResolution)
    def _get_in_highest_resolution(self) -> Stream:
        return self.video.streams.get_highest_resolution()
class Downloader(Thread):
    def __init__(self, queue: Queue, errors: list, progress: int):
        Thread.__init__(self)
        self.queue = queue
        self.errors = errors
        self.progress = progress
    def run(self):
        while True:
            try:self.download_file(self.queue.get())
            except (FileNotFoundError, FileExistsError, URLError,
                    RegexMatchError, VideoUnavailable, InvalidResolution) as e: self.errors.append(e)
            finally:
                current_progress = downloading_progress.get_current_progress
                downloading_progress.quick_progress(current_progress,current_progress + self.progress,1, 1000)
                self.queue.task_done()
    @staticmethod
    def download_file(download_options: tuple):
        f_type, path, file, options = download_options
        if f_type == 'audio':
            file = file.streams.get_audio_only()
            Audio(file, path).download_file()
        else:
            Video(file, path, options).download_file()


class ParallelDownloader:
    def __init__(self, queries: str, options: dict):
        self.errors = []
        self.requested_videos = queries.split('\n')
        self.options = options
        self.requested_type = self.options.get('type')
        self.path = self._get_path(self.requested_type)
        self.queue = Queue()
    def download_all(self):
        ts = time()
        if self.errors:
            return self.errors
        for i in range(len(self.requested_videos)):
            self.start_thread()
        self._build_queue()
        print(time() - ts)
        return self.errors
    def _build_queue(self):
        for i in self.get_videos():
            self.queue.put((self.requested_type, self.path, i,
                            self.options.get('preferred_resolution', None)))
        downloading_progress.quick_progress(11, 21, 1, 1000)
        downloading_progress.set_label_text('Receiving and saving...')
        self.queue.join()
    def start_thread(self):
        a = Downloader(self.queue, self.errors, 70//len(self.requested_videos))
        a.daemon = True
        a.start()
    def get_videos(self):
        for i in self.requested_videos:
            yield YouTube(i)
    def _get_path(self, for_type: Literal['audio', 'video']) -> str:
        if path := self._check_custom_path():
            return path
        else:
            return Settings().get_path_for(for_type)
    def _check_custom_path(self):
        if not (location := self.options.get('custom_download_path')):
            return None
        if not os.path.isdir(location):
            self.errors.append(FileNotFoundError(location))
            return None
        else:
            return location
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(QRect(500, 100, 600, 400))
        self.setWindowTitle('PronConverterService')
        self.setWindowIcon(QIcon('youtube_downloader_icon.webp'))
        self.quit_shortcut = QShortcut(QKeySequence('Ctrl+D'), self)
        self.quit_shortcut.activated.connect(QApplication.instance().quit)
        Label(self, QRect(20, 10, 500, 50),'Download video(s):', QFont('Century Gothic', 16, QFont.Normal))
        Label(self, QRect(20, 180, 500, 50), 'Additional options:',QFont('Century Gothic', 16, QFont.Normal))
        Label(self, QRect(20, 270, 300, 40),'Choose specific resolution:', QFont('Century Gothic', 16, QFont.Normal))
        Label(self, QRect(20, 310, 300, 40),'Specify download location:', QFont('Century Gothic', 16, QFont.Normal))
        self.vid_url = QTextEdit(self)
        self.vid_url.setGeometry(QRect(30, 60, 250, 100))
        self.vid_url.setPlaceholderText('Video Url')
        self.download_btn = PushButton(self, QRect(300, 60, 120, 50),'Download', self.download_file)
        self.download_btn.setFont(QFont('Century Gothic', 16, QFont.Normal))
        self.download_btn.setStyleSheet(':hover{''background-color: black; color: orange;}')
        self.only_audio = QCheckBox(self)
        self.only_audio.setText('Download only audio')
        self.only_audio.setFont(QFont('Century Gothic', 16, QFont.Normal))
        self.only_audio.setGeometry(QRect(20, 230, 500, 30))
        self.only_audio.setObjectName('only_audio')
        self.setStyleSheet("""QCheckBox#only_audio:checked{font-size: 10px; color: green;}""")
        self.pref_resolution = LineEdit(self, QRect(330, 275, 150, 30), 'Resolution')
        self.custom_download_location = LineEdit(self, QRect(340, 315, 150, 30), 'Location')
        self.change_settings = PushButton(self,QRect(self.width() - 90, 10, 50, 50), '',func=self._reload_and_show_settings)
        self.change_settings.setIcon(QIcon('settings_gear.png'))
        self.settings_window = SettingsWindow()
        self.downloading_progress = CircularProgressBar()
        self.warning_dialog = WarningDialog(self)
    def _reload_and_show_settings(self):
        self.settings_window.__init__()
        self.settings_window.show()
    def download_file(self):
        try:
            downloading_progress.show()
            downloading_progress.set_label_text('Defining query options...')
            a = ParallelDownloader(*self._build_data_package()).download_all()
            for i in a:
                WarningDialog(self).show_warning(i)
        finally:
            self.restore_default_inputs()
            downloading_progress.quick_progress(91, 101, 1, 1000)
            downloading_progress.set_label_text('Done!')
            sleep(0.5)
            downloading_progress.close()
    def _build_data_package(self):
        query = self.vid_url.toPlainText()
        options = {}
        if self.only_audio.isChecked():
            options['type'] = 'audio'
        else:
            options['type'] = 'video'
        options['custom_download_path'] = self.custom_download_location.text()
        options['preferred_resolution'] = self.pref_resolution.text()
        downloading_progress.quick_progress(0, 11, 1, 1000)
        downloading_progress.set_label_text('Making requests...')
        return query, options
    def restore_default_inputs(self):
        self.custom_download_location.setText('')
        self.only_audio.setChecked(False)
        self.pref_resolution.setText('')
        self.vid_url.setText('')
if __name__ == '__main__':
    app = QApplication(sys.argv)
    downloading_progress = CircularProgressBar()
    window = MainApp()
    window.show()
    sys.exit(app.exec_())
