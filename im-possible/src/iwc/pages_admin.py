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

class PageConfig(BasicRequestHandler):
    def get(self):
        if not users.is_current_user_admin():
            self.response.set_status(403)
            return
        
        self.write_template('html/config-edit.html', {})
        

class ActionConfigSave(webapp.RequestHandler):
    def post(self):
        if not users.is_current_user_admin():
            self.response.set_status(403)
            return

        config=Config.all().get()
        config.show_ads=bool(self.request.get('chk_show_ads'))
        config.show_analytics=bool(self.request.get('chk_show_analytics'))
        config.put()
        
        self.redirect('/config')