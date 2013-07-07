# -*- coding: utf-8 -*-
import os
import cgi
import datetime
import time
import math
import string

from google.appengine.api import users
from google.appengine.api import images
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from db.dbmodel import *
from iwc.ws_base import *
from cube_util import *

from util.misc import *

logger=LoggerWrapper()
#logger.setLevel(logging.DEBUG)


        
class PageCubeProfiles(BasicRequestHandlerAdmin):
    def get_admin(self):
        profiles = CubeProfile.all()
        
        self.write_template('html/cube-profiles.html', {'profiles':profiles})
        
        
class PageCubeProfile(BasicRequestHandlerAdmin):
    def get_admin(self):
        profile_key=self.request.get('profile_key')
        profile = None
        cubes = {}
        
        if profile_key:
            profile = CubeProfile.get(profile_key)
            cubes_list = CubeProfileItem.all().filter('profile',profile.key())
            for cube in cubes_list:
                cubes[cube.binary]=cube
                
        binaries = cube_binaries()
#        static_files = {}
#        static_files_mask='/images/cube/rgb/cube%sx.png'
#        if profile and profile.static_files_mask:
#            static_files_mask=profile.static_files_mask
        
        #Create static file URI
#        for binary in binaries:
#            static_files[binary]=static_files_mask % binary
            
        binary_items=[]
        for index in range(0,64):
            binary_items.append(CubeLibraryItem(index,binaries[index],-45*index,0))
            
            
        template_values = {
                           'profile': profile,
                           'cubes_binaries':binaries,
#                           'static_files':static_files,
                           'binary_items':binary_items,
                           'cubes':cubes
                           }
        
        self.write_template('html/cube-profile-edit.html', template_values)
        
        

                 

class ActionCubeProfileSave(BasicRequestHandlerAdmin):
    def post_admin(self):
        profile_key = self.request.get('profile_key')
        profile = None
        
        if profile_key:
            profile = CubeProfile.get(profile_key)
        else:
            profile = CubeProfile()
            
        profile.name = self.request.get('name');
        if self.request.get('default') and self.request.get('default') in ['1','on','true']:
            profile.default = True
        else:
            profile.default = False
            
        profile.cube_width = int(self.request.get('cube_width'))
        profile.cube_height = int(self.request.get('cube_height'))
        profile.cube_center_x = int(self.request.get('cube_center_x'))
        profile.cube_center_y = int(self.request.get('cube_center_y'))
        profile.grid_width = int(self.request.get('grid_width'))
        profile.grid_height = int(self.request.get('grid_height'))
        profile.static_cubes_image = self.request.get('static_cubes_image')
        profile.static_grid_image = self.request.get('static_grid_image')
        
        if self.request.get('grid_image'):
            profile.grid_image = self.request.get('grid_image')
            
        profile.put()
                
        binaries = cube_binaries()
        for binary in binaries:
            image = self.request.get('img'+binary)
            if image:
                profile_item = CubeProfileItem.all().filter('profile', profile).filter('binary =', binary).get()
                if not profile_item:
                    profile_item = CubeProfileItem()
                    profile_item.binary = binary
                    profile_item.profile = profile
                    
                profile_item.image = db.Blob(image)
                profile_item.put()
        
        self.redirect('/cube/profiles')
        

class ActionCubeProfileDelete(BasicRequestHandlerAdmin):
    """Удаление профиля кубиков"""
    def get_admin(self):
        profile_key = self.request.get('profile_key')
        if profile_key:
            profile = CubeProfile.get(profile_key)
            if profile:
                profile.delete()
        
        self.redirect('/cube/profiles')

        
class ImageCubeProfile(webapp.RequestHandler):
    """Обработчик возвращает изображение кубика из профиля"""
    def get(self):
        profile_key = self.request.get('profile_key')
        if profile_key:
            profile = CubeProfile.get(profile_key)
            cube_binary = self.request.get('binary')
            profile_item = CubeProfileItem.all().filter('profile', profile).filter('binary =', cube_binary).get()
            if profile_item:
#                canvas = PNGCanvas(1,1)
#                canvas.load(StringFile(profile_item.image))
#                for i in range(0,20):
#                    canvas.point(i, 10, [0,0,0,0xff])
#                    
#                self.response.headers['Content-Type']='image/png'
#                self.response.out.write(canvas.dump())
                self.response.headers['Content-Type']='image/png'
                self.response.out.write(profile_item.image)
            else:
                self.response.set_status(404)
        else:
            self.response.set_status(404)
       
class PageCubeConstructor(BasicRequestHandler):
    """Обработчик страницы, отображающей окно конструктора невозможных фигур"""
    def get(self):
        binaries = cube_binaries();
        figure = getCubeFigureFromRequest(self)
        
        if not figure:
            figure = CubeFigure()
            figure.name = ''
            
        profile = get_default_cube_profile()     

#        static_files = {}
#        static_files_mask=profile.static_files_mask #'/images/cube/rgb/cube%sx.png'
        
        #Create static file URI
        binary_items=[]
        for index in range(0,64):
            binary_items.append(CubeLibraryItem(index,binaries[index],-profile.cube_width*index,0))
            
#        for binary in binaries:
#            static_files[binary]=static_files_mask % binary
            
        figure_cubes=[]
        for item in figure.cubes:
            strs=string.split(item, ',')
            figure_cubes.append('"'+strs[0]+'",'+strs[1]+','+strs[2])
        
        template_values = {
                           'binary_items': binary_items,
                           'binaries': binaries,
#                           'static_files': static_files,
                           'profile': profile,
                           'figure': figure,
                           'figure_cubes':figure_cubes
                           }
        
        self.write_template('html/cube-constructor.html', template_values)
        
        
class ActionCubeFigureSave(BasicRequestHandler):
    """Действие по сохранению фигуры"""
    def post(self):
        figure_name = self.request.get('figure_name')
        if not figure_name:
            logger.error('Figure name is empty')
            self.response.set_status(403)
            return
        
        if len(figure_name)>30:
            logger.error('Figure name length > 30')
            self.response.set_status(500)
            return
        
        
        figure=getCubeFigureFromRequest(self)
        
        if figure:
            if figure.author != users.get_current_user():
                logger.error('User does not equal to figure author')
                self.response.set_status(403)
                return
        else:
            figure=CubeFigure()
            figure.author = users.get_current_user()
            figure.url_name = createCubeFigureUniqueName(figure_name)
            
        figure.name = figure_name
        
        figure_compiled = self.request.get('figure_comp')
        figure.cubes = string.split(figure_compiled)

        profile = get_default_cube_profile()
        
        full_image, image_width, image_height = create_figure_image(profile, figure)
        
        if image_width > image_height:
            small_image_width = 150
            small_image_height = (image_height * 150) / image_width
        else:
            small_image_height = 150
            small_image_width = (image_width * 150) / image_height
        
        figure.full_image = full_image
        figure.small_image = images.resize(full_image, small_image_width, small_image_height, images.PNG)         
        
        figure.put()
        
        self.redirect('/cube/figures/user')
        
        
class ActionCubeFigureDelete(BasicRequestHandler):
    """Действие удаления фигуры"""
    def get(self):
        figure = getCubeFigureFromRequest(self)
        if not figure:
            logger.error('No figure to delete')
            self.response.set_status(403)
            return
        
        if not figure:
            logger.error('Figure not found')
        
        if not self.user_info.admin and self.user_info.user!=figure.author:
            logger.error('Deleting another\'s figure')
            self.response.set_status(403)
            return
        
        CubeFigure.delete(figure)
        
        self.redirect('/cube/figures/user')


class ActionCubeFigureRating(BasicRequestHandler):
    """Действие назначения рейтинга фигуре администратором"""
    def get(self):
        if not self.user_info.admin:
            logger.error("Set rating is allowed for admins only")
            
        figure = getCubeFigureFromRequest(self)
        if not figure:
            logger.error('No figure to set rating')
            self.response.set_status(403)
            return
        
        if not figure:
            logger.error('Figure not found')
            
        rating=int(self.request.get("rating"));
        figure.rating=rating
        CubeFigure.save(figure);
        
        self.response.out.write(str(rating))

class ImageFigureRequest(webapp.RequestHandler):
    """Обработчик запроса, возвращающий изображение фигуры"""
    def get(self):
        figure = getCubeFigureFromRequest(self)
        if not figure:
            self.response.set_status(404)
            return 
                
        image_type = self.request.get('image_type')

        self.response.headers['Content-Type']='image/png'        
        
        
        if not image_type or image_type == 'full':
            self.response.out.write(figure.full_image)
        else:
            self.response.out.write(figure.small_image)


class PageCubeFiguresBase(BasicRequestHandler):
    """Базовый класс для страниц, отображающих списки кубиков
    """
    
    def get_cube_query(self):
        pass
    
    def get_page_title(self):
        pass
    
    def get_page_uri(self):
        pass
    
    def get(self):
        figures_query = self.get_cube_query()
        if not figures_query:
            self.response.set_status(404)
            return
        
        start_index = 0;
        if self.request.get('start'):
            start_index = int(self.request.get('start')) 
        
        page_size = 12
        
        figures = figures_query.fetch(page_size+1, start_index)
        
        next_page_url = None
        prev_page_url = None
        
        if start_index > 0:
            prev_start = start_index - page_size
            if prev_start <= 0:
                prev_page_url = self.get_page_uri()
            else:
                prev_page_url = self.get_page_uri() + '?start=' + str(prev_start)
                
        if len(figures)>page_size:
            next_page_url = self.get_page_uri() + '?start=' + str(start_index + page_size)
            figures = figures[:-1]
        
        figures_page_title = self.get_page_title()
        
        template_values = {
                           'figures': figures,
                           'figures_table': list_table(figures,3),
                           'figures_page_title': figures_page_title,
                           'cube_next_page_url': next_page_url,
                           'cube_prev_page_url': prev_page_url
                           }
        
        self.write_template('html/cube-figures-user.html', template_values)
    
            
class PageCubeFiguresUser(PageCubeFiguresBase):
    """Страница с фигурами пользователя"""
    def get_cube_query(self):
        if not users.get_current_user():            
            return None
            
        return CubeFigure.all().filter('author',users.get_current_user()).order('-date')
        
    def get_page_title(self):
        return 'My figures'
    
    def get_page_uri(self):
        return '/cube/figures/user'
    
            
class PageCubeFiguresAll(PageCubeFiguresBase):
    """Страница, показывающая фигуры всех пользователей по хронологии"""
    def get_cube_query(self):
        return CubeFigure.all().order('-date')
    
    def get_page_title(self):
        return 'All figures'
    
    def get_page_uri(self):
        return '/cube/figures/all'
    
class PageCubeFiguresBest(PageCubeFiguresBase):
    """Страница, показывающая ЛУЧШИЕ фигуры всех пользователей по хронологии"""
    def get_cube_query(self):
        return CubeFigure.all().filter("rating >",5).order('-rating').order("-date")
    
    def get_page_title(self):
        return 'Best figures'
    
    def get_page_uri(self):
        return '/cube/figures/best'
        
