# -*- coding: utf-8 -*-
from flask import Flask
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sakuin.db'
DB = SQLAlchemy(APP)
API = Api(APP)


class Title(DB.Model):
    """Title for media in the database."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    _id = DB.Column('id', DB.Integer, primary_key=True)
    name = DB.Column(DB.Unicode)


class Source(DB.Model):
    """Source of manga."""

    __tablename__ = 'source'

    _id: DB.Column = DB.Column('id', DB.Integer, primary_key=True)
    name: DB.Column = DB.Column(DB.Unicode)


class MediaItem(DB.Model):
    """Base class for all other media, defining like keys."""

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    _id: DB.Column = DB.Column('id', DB.Integer, primary_key=True)
    db_id: DB.Column = DB.Column(DB.Integer, ForeignKey('sakuin_manga.id'))
    site_id: DB.Column = DB.Column(DB.Integer)
    main_title: DB.Column = DB.Column(DB.Unicode, ForeignKey('.'.join([Title.__tablename__, Title.name.name])))
    source: DB.Column = DB.Column(DB.Unicode, ForeignKey('.'.join([Source.__tablename__, Source.name.name])))
    titles = relationship(Title.__name__)

    def __init__(self, site_id: int, main_title: str, source: str):
        self.site_id = site_id
        self.main_title = main_title
        self.source = source

    def __repr__(self) -> str:
        return '<MediaItem title={0}, source={1}>'.format(self.main_title, self.source)


class Manga(DB.Model):
    """"""

    __tablename__ = 'sakuin_manga'

    _id = DB.Column('id', DB.Integer, primary_key=True)
    title = DB.Column(DB.Unicode, ForeignKey('.'.join([Title.__tablename__, Title.name.name])))
    objects = relationship(MediaItem.__name__, backref=__tablename__)

    @property
    def num_links(self) -> int:
        return len(self.objects)

    def __repr__(self) -> str:
        return '<Manga title={0}, num_links={1}>'.format(self.title, self.num_links)


class ApiManga(Resource):
    def get(self, source_id: int, manga_id: int):
        manga = DB.session.query(MediaItem).join(Source).filter(Source._id == source_id, MediaItem.site_id == manga_id).first()
        return {
            'title': manga.main_title,
        }

API.add_resource(ApiManga, '/<string:source_id>/<string:manga_id>')

if __name__ == '__main__':
    APP.run(debug=True, host='0.0.0.0')
