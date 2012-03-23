# -*- coding: utf-8 -*-

import os
import cgi
import datetime
import time

import logging

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from db.dbmodel import *
from iwc.ws_base import *
import util.misc

from iwc import pages
from cube import cube_util

class ActionUpdatePosts(BasicRequestHandlerAdmin):
    def get_admin(self):
        posts = BlogPost.all()
        for post in posts:
            post.url_name = pages.createPostName(post.title)
            post.put()
            
        self.redirect('/')
        
class ActionUpdateCubeFigures(BasicRequestHandlerAdmin):
    def get_admin(self):
        figures = CubeFigure.all()
        for figure in figures:
            figure.url_name = cube_util.createCubeFigureUniqueName(figure.name)
            figure.put()
            
        self.redirect('/')