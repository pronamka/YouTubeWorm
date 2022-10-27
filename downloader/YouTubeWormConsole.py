import os
from collections import namedtuple
from typing import Callable
from urllib.error import URLError
from queue import Queue
from threading import Thread

from pytube import YouTube
from pytube.streams import Stream
from pytube.exceptions import RegexMatchError, VideoUnavailable

from moviepy.editor import AudioFileClip


class InvalidResolution(AttributeError):
    ...


exception_messages = {FileExistsError:
                          'File with the name "{}" already exists in "{}"',
                      URLError:
                          'The app could not establish internet connection. '
                          'Please check your network settings, ensure that '
                          'you have internet and try again.'
                          'If it did not help, contact me at defender0508@gmail.com',
                      FileNotFoundError:
                          'Location "{}" does not exist.',
                      RegexMatchError:
                          'The link "{}" does not lead anywhere. '
                          'It was excluded from the request.',
                      VideoUnavailable:
                          'The video "{}" either '
                          'does not exist or unavailable for some reason. '
                          'It was excluded from the request.',
                      InvalidResolution:
                          'The video you chose to download does not have '
                          'resolution you have given. The video was downloaded '
                          'with the highest resolution possible.'
                      }


class FileForDownloading:
    @staticmethod
    def _build_location(path: str, filename: str) -> str:
        """Concatenates path to folder and filename together."""
        location = os.path.join(path, filename)
        return location

    @staticmethod
    def _rebuild_path(path: str) -> str:
        """Replace all '/' symbols,
        so path to folder and filename
        can be concatenated through os.path.join."""
        new_path = path.replace('/', '\\')
        return new_path


class Audio(FileForDownloading):
    """Class for downloading and converting mp4 files with no frames
    to mp3 files."""

    def __init__(self, audio_file: Stream, path: str) -> None:
        self.audio = audio_file
        self.path = self._rebuild_path(path)
        self.filename = audio_file.default_filename
        self.mp4_location = self._build_location(self.path, self.filename)

    def download_file(self) -> None:
        """General function to handle
        file downloading."""
        self._save_as_mp4()
        self._save_as_mp3()

    def _save_as_mp4(self) -> None:
        """Save file on the disk in mp4 format,
        so it can be converted to mp3 later."""
        self.audio.download(self.path)

    def _save_as_mp3(self) -> None:
        """General function to handle conversion
        to mp3 and saving process."""
        if self._check_existence():
            self._convert_and_write()
            self._remove_mp4()

    def _convert_and_write(self) -> None:
        """Convert the mp4 file with no frames to mp3,
        write the audio file to the same folder."""
        audio = AudioFileClip(self.mp4_location)
        audio.write_audiofile(self._build_mp3_path(), )

    def _remove_mp4(self) -> None:
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
        the mp4 file does not actually lead to a file.
        (should never happen, as the path was checked previously)"""
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
        """Build the path where mp3 file
        is going to be saved."""
        mp3_location = self.mp4_location.rsplit('.', maxsplit=1)[0] + '.mp3'
        return mp3_location


class Video(FileForDownloading):
    """Class for downloading videos."""

    def __init__(self, video_file: YouTube, path: str, resolution: str) -> None:
        self.video = video_file
        self.path = self._rebuild_path(path)
        self.resolution = resolution
        self.errors = []

    def download_file(self) -> None:
        """General function to handle downloading process.
        :raises: InvalidResolution, if the requested video
        does not have the resolution user provided.
        (the exception is not raised immediately in order to finish
        downloading process(with the highest resolution possible))"""
        video = self._check_resolution()
        if not video:
            video = self._get_in_highest_resolution()
        video.download(self.path)
        if self.errors:
            raise self.errors.pop()

    def _check_resolution(self) -> [YouTube, None]:
        """Check if the user provided a specific
        resolution and the requested video has that resolution.
        :returns: Stream, if the requested video has provided resolution"""
        if self.resolution:
            if not (video := self.video.streams.get_by_resolution('resolution')):
                return video
            else:
                self.errors.append((InvalidResolution, self.resolution))

    def _get_in_highest_resolution(self) -> Stream:
        """Get the Stream with the highest resolution."""
        return self.video.streams.get_highest_resolution()


class Downloader(Thread):
    """A thread to download files,
    that are of pytube.YouTube or pytube.Stream
    type, and that are added to the queue"""

    def __init__(self, queue: Queue, errors: list, progress: int) -> None:
        """Create a new thread.
        :param queue: queue.Queue instance, can be
                    empty. The process will start
                    as soon as something appears in the queue.
        :param errors: a list to which errors that may
                    occur during the downloading process are
                    added.
        :param progress: int that tells how much progress
                    should be added to the progress bar
                    after finishing the task."""
        Thread.__init__(self)
        self.queue = queue
        self.errors = errors
        self.progress = progress

    def run(self) -> None:
        """Run the thread. If the queue is empty,
        the thread will be running anyways, waiting
        for something to appear in the queue."""
        data_form = namedtuple('Data', 'f_type path file url options')
        while True:
            options = data_form(*self.queue.get())
            try:
                self.download_file(options)
            except (FileNotFoundError, FileExistsError, URLError,
                    RegexMatchError, VideoUnavailable, InvalidResolution) as e:
                self.errors.append((e.__class__, options.url))
            finally:
                self.queue.task_done()

    @staticmethod
    def download_file(download_options: tuple) -> None:
        f_type, path, file, url, options = download_options
        if f_type == 'audio':
            file = file.streams.get_audio_only()
            Audio(file, path).download_file()
        else:
            Video(file, path, options).download_file()


class ParallelDownloader:
    """Class for downloading multiple
    file at once using threading."""

    def __init__(self, queries: str, options: dict) -> None:
        """Initialize the downloader.
        :param queries: a string containing urls
        that lead to YouTube videos, separated one
        from another by line breaks."""
        self.errors = []
        self.requested_videos = queries.split(', ')
        self.options = options
        self.requested_type = self.options.get('type')
        self.path = self._get_path()
        self.queue = Queue()

    def download_all(self) -> list:
        """Download all videos links to
        which were given when initializing the object."""
        if self.errors:
            return self.errors
        for i in range(len(self.requested_videos)):
            self.start_thread()
        self._build_queue()
        return self.errors

    def _build_queue(self) -> None:
        """Add task to queue, so active
        threads can start working with it's contains."""
        for item, url in self.get_videos():
            self.queue.put((self.requested_type, self.path, item, url,
                            self.options.get('preferred_resolution', None)))
        self.queue.join()

    def start_thread(self) -> None:
        """Start a thread that will download videos
        util the queue is empty."""
        a = Downloader(self.queue, self.errors, 70 // len(self.requested_videos))
        a.daemon = True
        a.start()

    def get_videos(self) -> tuple[YouTube, str]:
        """Get YouTube instances of requested files."""
        for i in self.requested_videos:
            try:
                yield YouTube(i), i
            except RegexMatchError:
                self.errors.append((RegexMatchError, i))

    def _get_path(self) -> str:
        """Check the if there user provided a
        custom downloading path. If he did, the path
        will be checked in order to make sure it exists.
        If he did not, default path for downloading the
        designated file type will be used."""
        if path := self._check_custom_path():
            return path
        else:
            return os.path.curdir

    def _check_custom_path(self) -> [None, str]:
        """Check if a custom path is provide
        and if it is real.
        :returns: None, if the custom path is not provided.
        :returns: str, if it is and it's valid.
        :raises: FileNotFoundError, if it is and it's invalid."""
        if not (location := self.options.get('to')):
            return None
        if not os.path.isdir(location):
            self.errors.append((FileNotFoundError, location))
            return None
        else:
            return location


def get_help() -> str:
    return f"""The download command syntax:
    Optional arguments (in the order they 
    should be described in your requests): 
        -type:  
            defines the type, in which you want to
            download the file. Can be audio (that way the 
            output file will be in .mp3 format) or 
            video (file will be in .mp4 format)
            Default value: video
        -resolution: 
            the resolution, in which you want to 
            download a video. Does not matter if
            you are downloading audio. 
            Note that you should put full resolution,
            as it described on YouTube (e.g. 720p or 
            2160p60, not 720 or 2160.)
            Default value: highest resolution, the 
            requested video has.
        -to:
            relative or absolute path to a folder 
            on your device, to which you want to
            download file.
            Default value: current directory ({os.getcwd()})
    Obligatory arguments:
        -links: 
            urls to YouTube videos you want to 
            download. You can provide as many as 
            you want, but it will increase the 
            downloading time.
    
    Examples of using the 'download' command:
        download -type audio -resolution 720p -links https://youtu.be/video, https://youtu.be/another_video
        download -links https://youtu.be/video"""


def handle_exception(exception) -> None:
    """Print an exception message,
    if the exception type is covered in
    exception_messages dict.
    :param exception: a tuple of two:
        an exception type and optional information."""
    print(exception_messages.get(exception[0]).format(exception[1]))


def download(urls: str, options) -> None:
    """General function to handle
    downloading process."""
    a = ParallelDownloader(urls, options).download_all()
    for i in a:
        handle_exception(i)


def inspect_parameters(options: str) -> tuple[str, dict]:
    """Formalize parameters.
    :param options: a sting containing parameters,
        doesn't have a command name in it.
    :raises: SyntaxError if the parameters were
        provided in a wrong way.
    :returns: tuple of two: a string, containing
    video urls, and a dict with other parameters."""
    options = options.split('-')[1:]
    params = {}
    for i in options:
        try:
            key, value = i.split(' ', maxsplit=1)
            params[key] = value.strip()
        except ValueError:
            raise SyntaxError(f'Invalid syntax at "{i}"')
    return check_parameters(params)


def check_parameters(parameters: dict) -> tuple[str, dict]:
    """Check what parameters were provided
    in the user's request and formalize
    arguments.
    :param parameters: dict with parameters.
    :raises: SyntaxError, if there user have not
    provided any video urls.
    :returns: tuple of two: a string, containing
    video urls, and a dict with other parameters."""
    default_values = {'type': 'video', 'resolution': None, 'to': os.curdir}
    for key, value in default_values.items():
        if key not in parameters.keys():
            parameters[key] = value
    if (links := parameters.get('links')) is None:
        raise SyntaxError('Syntax Error: '
                          'You have not provided any video urls to download.')
    parameters.pop('links')
    return links, parameters


def get_command_type(cmd: str) -> tuple[Callable, str]:
    """Get a function to handle the user request.
    :param cmd: a string containing full command.
    :returns: a tuple of two: Callable, and
    a dict with request parameters.
    :raises: ValueError, if the cmd does not have any
    spaces.
    :raises: SyntaxError, if the command is not
    identified."""
    commands = {'help': get_help,
                'download': download}
    cmd = cmd.split(' ', maxsplit=1)
    if len(cmd) < 2:
        raise ValueError("You have not provided any valid commands or arguments. "
                         "Type help if you don't know the command syntax.")
    command, request_options = cmd
    executable = commands.get(command, None)
    if not executable:
        raise SyntaxError("Unidentified command. Type help "
                          "if you don't know the command syntax.")
    return executable, request_options


def read_command(cmd: str) -> None:
    """General function to process a command.
    :param cmd: a string containing full command."""
    try:
        executable, options = get_command_type(cmd)
        executable(*inspect_parameters(options))
    except (SyntaxError, ValueError) as e:
        print(e)


if __name__ == '__main__':
    print("If you don't know what to do, type help.")
    while True:
        full_command = input('Enter command: ')
        if full_command.strip() == 'help':
            print(get_help())
        else:
            read_command(full_command)
