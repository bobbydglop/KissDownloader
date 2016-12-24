#!/usr/bin/env python

# INCOMPLETE
# To add async download

import asyncio, urllib.request, tqdm, sys
from tqdm import tqdm, trange
from docopt import docopt
from time import sleep

@asyncio.coroutine
def get(url):
    with tqdm(unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]) as t:
        urllib.request.urlretrieve(url, filename='/dev/null', reporthook=hook(t), data=None)

# make @asyncio.coroutine using tnrange (multiple download bars)
def hook(t):
  last_b = [0]
  def inner(b=1, bsize=1, tsize=None):
    if tsize is not None:
        t.total = tsize
    t.update((b - last_b[0]) * bsize)
    last_b[0] = b
  return inner

urls = ['https://i.imgur.com/oAneswZ.jpg', 'https://i.imgur.com/oAneswZ.jpg', 'https://i.imgur.com/oAneswZ.jpg', 'https://i.imgur.com/oAneswZ.jpg', 'https://i.imgur.com/oAneswZ.jpg']
sem = asyncio.Semaphore(5)
loop = asyncio.get_event_loop()
f = asyncio.wait([get(d) for d in urls])
loop.run_until_complete(f)