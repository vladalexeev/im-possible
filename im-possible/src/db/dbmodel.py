# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.api import users
#from png.pngc import *

import const

#__name__='dbmodel'

class BlogPost(db.Expando):
    """ Post of the blog """
    author = db.UserProperty()
    title = db.StringProperty()
    content = db.TextProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    language = db.StringProperty()
    rating = db.IntegerProperty()
    visible = db.BooleanProperty()
    votes = db.ListProperty(users.User)
    comments_enabled = db.BooleanProperty()
    url_name = db.StringProperty()
    
    def votes_count(self):
        if self.votes:
            return len(self.votes)
        else:
            return 0
    
    def post_key_param(self):
        return 'post_key='+str(self.key())
    
    def post_details_url(self):
        return '/post?'+self.post_key_param()
    
    
class BlogPostComment(db.Model):
    """ Blog post comment """
    reference = db.ReferenceProperty(reference_class=BlogPost)
    author = db.UserProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    content = db.TextProperty()
    visible = db.BooleanProperty()
    
    def comment_key_param(self):
        return 'comment_key='+str(self.key())
    

class UserParams(db.Model):
    """Дополнительная информация о пользователях сайта"""
    user = db.UserProperty()
    banned = db.BooleanProperty()

#class BannedUser(db.Model):
#    """ Banned user """
#    user = db.UserProperty()
#    ban_date = db.DateTimeProperty()
    
class Config(db.Model):
    """Конфигурация системы"""
    show_ads = db.BooleanProperty();
    show_analytics = db.BooleanProperty();
    
    
class CubeProfile(db.Model):
    """Профиль кубиков    
       Для профиля по-умолчанию RGB параметры следующие
       
       cube_width = 45
       cube_height = 49
       cube_center_x = 22
       cube_center_y = 23       
       grid_width = 62
       grid_height = 36
    """
    name = db.StringProperty()
    internal_name = db.StringProperty()
    cube_width = db.IntegerProperty()
    cube_height = db.IntegerProperty()
    cube_center_x = db.IntegerProperty()
    cube_center_y = db.IntegerProperty()
    
    grid_width = db.IntegerProperty()
    grid_height = db.IntegerProperty()
    grid_image = db.BlobProperty()
    
    static_cubes_image = db.StringProperty()
    static_grid_image = db.StringProperty()
    
    default = db.BooleanProperty()
    
    def profile_key_param(self):
        return 'profile_key='+str(self.key())

class CubeProfileItem(db.Model):
    """Один кубик профиля кубиков"""
    profile = db.ReferenceProperty(reference_class=CubeProfile)
    binary = db.StringProperty()
    image = db.BlobProperty()
    
class CubeFigure(db.Model):
    """Фигура из кубиков"""
    author = db.UserProperty()
    name = db.StringProperty()
    cubes = db.StringListProperty()
    date = db.DateTimeProperty(auto_now_add=True)
    url_name = db.StringProperty()
    
    full_image = db.BlobProperty()
    small_image = db.BlobProperty()
    
    rating = db.IntegerProperty();
    
    def figure_key_param(self):
        if self.has_key():
            return const.param_cube_figure_key+'='+str(self.url_name)
        else:
            return ''
