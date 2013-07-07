# -*- coding: utf-8 -*-
import datetime
import time

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from xml.dom import minidom

from db.dbmodel import *

import const
import common.customfilters



class RssFigures(webapp.RequestHandler):
    """RSS-поток новых невозможных фигур"""
    def get(self):
        doc = minidom.Document()
        root = doc.createElement('rss')
        root.setAttribute('version','2.0')
        doc.appendChild(root);
        
        channel = doc.createElement('channel')
        root.appendChild(channel)
        
        title = doc.createElement('title')
        title.appendChild(doc.createTextNode('Impossible figures'))
        channel.appendChild(title)
        
        link = doc.createElement('link')
        link.appendChild(doc.createTextNode('http://im-possible.appspot.com'))
        channel.appendChild(link)
        
        description = doc.createElement('description')
        description.appendChild(doc.createTextNode('Images of impossible figures of the Impossible World site community'))
        channel.appendChild(description)
        
        language = doc.createElement('language')
        language.appendChild(doc.createTextNode('en'))
        channel.appendChild(language)
        
        lastBuildDate = doc.createElement('lastBuildDate')
        lastBuildDate.appendChild(doc.createTextNode(datetime.datetime.now().isoformat()))
        channel.appendChild(lastBuildDate)
        
        figures=CubeFigure.all().order('-date').fetch(10)
        for figure in figures:
            item=doc.createElement('item')
            channel.appendChild(item)
            
            itemTitle = doc.createElement('title')
            itemTitle.appendChild(doc.createTextNode(figure.name));
            item.appendChild(itemTitle)
            
            itemLink = doc.createElement('link')
            itemLink.appendChild(doc.createTextNode('http://im-possible.appspot.com/cube/figure/image?'+figure.figure_key_param()))
            item.appendChild(itemLink)
            
            itemDescription = doc.createElement('description')
            itemDescription.appendChild(doc.createTextNode('<p>Impossible figure: "'+figure.name+'"</p>'+
                                                           '<p>'+common.customfilters.cube_figure_thumbnail(figure)+'</p>'))
            item.appendChild(itemDescription)
            
            itemAuthor = doc.createElement('author')
            itemAuthor.appendChild(doc.createTextNode(str(figure.author.nickname())))
            item.appendChild(itemAuthor)
            
            itemGuid = doc.createElement('guid')
            itemGuid.appendChild(doc.createTextNode('http://im-possible.appspot.com/cube/figure/image?'+figure.figure_key_param()))
            item.appendChild(itemGuid)
            
            itemPubDate = doc.createElement('pubDate')
            itemPubDate.appendChild(doc.createTextNode(figure.date.isoformat()))
            item.appendChild(itemPubDate)
            
        self.response.out.write(doc.toprettyxml())
