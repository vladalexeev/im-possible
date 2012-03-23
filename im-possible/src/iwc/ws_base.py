# -*- coding: utf-8 -*-

import os
import cgi
import datetime
import time

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import const

from db.dbmodel import *

from util.misc import *

logger=LoggerWrapper()

class UserInfo:
    """ Информация о пользователе для страницы """
    user=None
    user_name=''
    admin=False
    login_url=None
    login_url_text=None
    banned=False
    
    url_my_cubic_figures = None
    url_create_cubic_figure = None
    url_add_post = None
    
    def __init__(self,request_uri):
        self.user=users.get_current_user()
        if users.get_current_user():
            self.user_name=users.get_current_user().nickname()
            self.admin=users.is_current_user_admin()
            self.login_url=users.create_logout_url('/')
            self.login_url_text='Logout'
            self.url_my_cubic_figures='/cube/figures/user'
            self.url_create_cubic_figure='/cube/constructor'
            
            user_params = UserParams.all().filter('user', self.user).get()
            if user_params and user_params.banned:
                self.banned=True
                self.admin=False            
        else:
            self.login_url=users.create_login_url(request_uri)
            self.login_url_text='Login into Google account'
            self.url_my_cubic_figures=users.create_login_url('/cube/figures/user')
            self.url_create_cubic_figure=users.create_login_url('/cube/constructor')
            
    def url_add_post(self):
        if users.get_current_user():
            return '/post/edit'
        else:
            return users.create_login_url('/post/edit')
            
class BasicRequestHandler(webapp.RequestHandler):
    def initialize(self, request, response):
        webapp.RequestHandler.initialize(self, request, response)
        self.user_info=UserInfo(self.request.uri)
#        self.config=config.Config()
        self.config=Config.all().get()
        if not self.config:
            self.config=Config()
            self.config.show_ads=True
            self.config.show_analytics=True
            self.config.put()
        
    def write_template(self,template_name,template_values):
        """Вывод шаблона в выходной поток"""
        template_values['user_info']=self.user_info
        template_values['config']=self.config
        path = os.path.join(os.path.dirname(__file__), "../"+template_name)
        self.response.out.write(template.render(path, template_values))
        
class BasicRequestHandlerAdmin(BasicRequestHandler):
    """Обработчик запроса, проверяющий права администратора автоматически"""
    def get_admin(self):
        pass

    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return
        
        self.get_admin()
        
    def post_admin(self):
        pass
   
    def post(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return
        
        self.post_admin()
        
