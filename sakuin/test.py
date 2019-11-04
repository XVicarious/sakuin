#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tables import DB, MediaItem, Manga, Source, Title
import json
import sys

tracks = [
    'MyAnimeList',
    'AniList',
    'Kitsu',
]

sources = {
    2499283573021220255: {
        'idreg': lambda x: x.split('/')[2],
    },
}

data = None
with open(sys.argv[1]) as file:
    data = json.load(file)

for manga in data['mangas']:
    m_source = manga['manga'][2]
    if m_source not in sources.keys():
        continue
    m_title = manga['manga'][1]
    try:
        m_id = sources[m_source]['idreg'](manga['manga'][0])
    except:
        continue
    source = DB.session.query(Source).filter(Source.name == 'MangaDex').first()
    if not source:
        source = Source()
        source.name = 'MangaDex'
        DB.session.add(source)
    title = DB.session.query(Title).filter(Title.name == m_title).first()
    if not title:
        title = Title()
        title.name = m_title
        DB.session.add(title)
    instances = [MediaItem(m_id, title.name, source.name)]
    if 'track' not in manga:
        continue
    for track in manga['track']:
        if not track:
            continue
        try:
            t_id = track['u'].split('/')[-1]
        except:
            continue
        t_title = track['t']
        t_source = tracks[track['s'] - 1]
        source = DB.session.query(Source).filter(Source.name == t_source).first()
        if not source:
            source = Source()
            source.name = t_source
            DB.session.add(source)
        title = DB.session.query(Title).filter(Title.name == t_title).first()
        if not title:
            title = Title()
            title.name = t_title
            DB.session.add(title)
        instances += [MediaItem(t_id, title.name, source.name)]
    mango = Manga()
    mango.title = m_title
    mango.objects = instances
    DB.session.add(mango)
DB.session.commit()
