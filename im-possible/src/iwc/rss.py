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



class RssPosts(webapp.RequestHandler):
    """RSS-поток постов"""
    def get(self):
        doc = minidom.Document()
        root = doc.createElement('rss')
        root.setAttribute('version','2.0')
        doc.appendChild(root);
        
        channel = doc.createElement('channel')
        root.appendChild(channel)
        
        title = doc.createElement('title')
        title.appendChild(doc.createTextNode('Impossible World site community'))
        channel.appendChild(title)
        
        link = doc.createElement('link')
        link.appendChild(doc.createTextNode('http://im-possible.appspot.com'))
        channel.appendChild(link)
        
        description = doc.createElement('description')
        description.appendChild(doc.createTextNode('Posts of the Impossible World site community'))
        channel.appendChild(description)
        
        language = doc.createElement('language')
        language.appendChild(doc.createTextNode('en'))
        channel.appendChild(language)
        
        lastBuildDate = doc.createElement('lastBuildDate')
        lastBuildDate.appendChild(doc.createTextNode(datetime.datetime.now().isoformat()))
        channel.appendChild(lastBuildDate)
        
        posts=BlogPost.all().order('-date').fetch(10)
        for post in posts:
            item=doc.createElement('item')
            channel.appendChild(item)
            
            itemTitle = doc.createElement('title')
            itemTitle.appendChild(doc.createTextNode(post.title));
            item.appendChild(itemTitle)
            
            itemLink = doc.createElement('link')
            itemLink.appendChild(doc.createTextNode('http://im-possible.appspot.com'+post.post_details_url()))
            item.appendChild(itemLink)
            
            itemContent=post.content
            if hasattr(post,'attached_cube_figure'):
                itemContent+='<p>'+common.customfilters.cube_figure_thumbnail(post.attached_cube_figure)+'</p>'
#                itemContent+='<p><img src="http://im-possible.appspot.com/cube/figure/image?figure_key='+post.attached_cube_figure+'&image_type=small" /></p>'
            
            itemDescription = doc.createElement('description')
            itemDescription.appendChild(doc.createTextNode(itemContent))
            item.appendChild(itemDescription)
            
            itemAuthor = doc.createElement('author')
            itemAuthor.appendChild(doc.createTextNode(str(post.author.nickname())))
            item.appendChild(itemAuthor)
            
            itemGuid = doc.createElement('guid')
            itemGuid.appendChild(doc.createTextNode('http://im-possible.appspot.com'+post.post_details_url()))
            item.appendChild(itemGuid)
            
            itemPubDate = doc.createElement('pubDate')
            itemPubDate.appendChild(doc.createTextNode(post.date.isoformat()))
            item.appendChild(itemPubDate)
            

#        logger.debug(doc.toprettyxml(indent=' '))
        self.response.out.write(doc.toprettyxml())
        