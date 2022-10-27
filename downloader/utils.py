'''import requests
from threading import Thread
import concurrent.futures
import logging
import os
from queue import Queue
from threading import Thread
from time import time
from time import time
from queue import Queue

class Downloader(Thread):
    def __init__(self, queue: Queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        from pytube import YouTube
        while True:
            # Get the work from the queue and expand the tuple
            file = YouTube(self.queue.get())
            print(file)
            try:
                print(file.streams.get_audio_only())
            finally:
                self.queue.task_done()
def get_file(url_address):
    from pytube import YouTube
    print(YouTube(url_address).streams.get_audio_only())
urls = ['https://youtu.be/K4TOrB7at0Y',
        'https://youtu.be/a3ICNMQW7Ok',
        'https://youtu.be/2pCb8is4DnM']
with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as app:
    res = {app.submit(get_file, url): url for url in urls}
    for future in concurrent.futures.as_completed(res):
        url = res[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))

import concurrent.futures
import urllib.request
from multiprocessing import Pool
from functools import partial
from threading import Thread
import pytube
import asyncio
from time import time
from moviepy.editor import AudioFileClip
import os
URLS = ['https://youtu.be/K4TOrB7at0Y',
        'https://youtu.be/a3ICNMQW7Ok',
        'https://youtu.be/2pCb8is4DnM']

# Retrieve a single page and report the URL and contents
def load_url(url):
    from pytube import YouTube
    conn = YouTube(url)
    print(f'{url}: YouTube instance created. Time: {time()}')
    conn = conn.streams.get_audio_only()
    print(f'{url}: Fetched audio. Time: {time()}')
    conn.download('C:\\Users\\prona\\Desktop\\youtube_music_d'
              'ownloader\\Lib\\downloader\\files\\audio')
    print(f'{url}: Saved as mp4. Time: {time()}')
    aud = AudioFileClip(os.path.join('C:\\Users\\prona\\Desktop\\youtube_music_d'
              'ownloader\\Lib\\downloader\\files\\audio', conn.default_filename))
    aud.write_audiofile(os.path.join('C:\\Users\\prona\\Desktop\\youtube_music_d'
              'ownloader\\Lib\\downloader\\files\\audio',
                                     conn.default_filename.rsplit('.', maxsplit=1)[0]+'.mp3'))
    print(f'{url}: Saved as mp3. Time: {time()}')



if __name__ == '__main__':
    a = time()
    with Pool(3) as p:
        p.map(load_url, URLS)
    print(time() - a)'''
"""
import asyncio
from pytube import YouTube
from time import time
import aiohttp
from ast import literal_eval

urls = ['https://youtu.be/K4TOrB7at0Y',
        'https://youtu.be/a3ICNMQW7Ok',
        'https://youtu.be/2pCb8is4DnM']

async def get_file():
    start_time = time()
    async with aiohttp.ClientSession() as session:
        for i in urls:
            resp = await session.get(i)
            resp_cont = await resp.content.

            print(resp_cont)
            print(time() - start_time)

async def hub():
    await get_file()

if __name__ == '__main__':
    asyncio.run(hub())




from multiprocessing import Pool
from time import time
import asyncio
import aiohttp
import os
from requests import get
from pytube import YouTube
from moviepy.editor import AudioFileClip
import aiofiles
import concurrent.futures
from threading import Thread
import subprocess
from tempfile import SpooledTemporaryFile, TemporaryFile
import av


urls= ['https://youtu.be/a3ICNMQW7Ok',
       'https://youtu.be/xcJtL7QggTI',
       'https://youtu.be/LXb3EKWsInQ']


async def load_url(url_name):
    url = url_name[0]
    name = url_name[1]
    conn = YouTube(url)
    conn = conn.streaming_data
    req = ''
    for i in conn.get('adaptiveFormats'):
        if i.get('itag') == 251:
            req = i
    with open('tests/'+name+'.mp3', mode='wb') as file:
        file.write(get(req.get('url')).content)
    #print(f'{url}: Fetched audio. Time: {time()}; Size: {conn.filesize}')


def build_url(raw_url):
    conn = YouTube(raw_url).streaming_data.get('adaptiveFormats')
    for i in conn:
        if i.get('itag') == 251:
            return i.get('url')


def load_normally(aud_url):
    a = YouTube(aud_url).streams.get_audio_only()



if __name__ == '__main__':
    a = time()
    res = []
    for i in urls:
        res.append(Thread(load_normally(i)).start())

    '''with concurrent.futures.ProcessPoolExecutor(3) as p:
        p.map(load_normally, urls)'''
    print(time() - a)




 1)  616785
        3134467
        5199817
        158.15220475196838
        
    2) 50.460721015930176
    3) 39.4
    4) 83.52244901657104"""

"""async def download_files(aud_urls):
    print(aud_urls)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in aud_urls:
            tasks.append(asyncio.create_task(session.get(i)))
        res = await asyncio.gather(*tasks)
        return [await i.content.read() for i in res]"""

"""async def download_files(aud_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(aud_url) as resp:
            file = await aiofiles.open('tests/'+str(4)+'.mp3', mode='wb')
            await file.write(await resp.read())
            await file.close()
def load_normally(aud_url):
    a = get(aud_url).content
    print(a)

def write_file(name_binary_data):
    name, binary_data = name_binary_data
    with open('tests/'+str(name)+'.mp3', mode='wb') as file:
        file.write(binary_data)


if __name__ == '__main__' :
    a = time()

    c = 0
    with Pool(3) as p:
        URLS = p.map(build_url, urls)
    load_normally(URLS[0])
    
    asyncio.run(download_files(URLS[0]))
    names_bins = {c+1: i for i in bins}
    with Pool(3) as p:
        p.map(write_file, names_bins.items())
    print(time() - a)"""
from collections import namedtuple
from typing import NamedTuple
from pytube import YouTube
data_pack = namedtuple('Data', 'f_type path file options')
data = data_pack('audio', 'c', 'file', options={})
data_pack_v2 = NamedTuple('Data', 'f_type path file options')