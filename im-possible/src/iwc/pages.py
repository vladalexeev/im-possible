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

logger=LoggerWrapper()

class PagePosts(BasicRequestHandler):
    """Страница для отображения постов"""
    def get(self):
        start_index=0
        if (self.request.get("start")):
            start_index=int(self.request.get("start"))
            
        page_size=10
        
        template_values=getPosts(start_index, page_size)
        self.write_template('html/posts.html', template_values)
    

class PageMain(BasicRequestHandler):
    """ Главная страницами с постами """
    def get(self):
        start_index=0
        page_size=10
        
        template_values=getPosts(start_index, page_size)
        
        figures = CubeFigure.all().filter("rating >",5).order('-rating').order("-date").fetch(3, 0)
        
        template_values['figures']=figures
        
        self.write_template('html/index.html', template_values)

        
class PagePostDetails(BasicRequestHandler):
    """ Страница с постом и комментариями """
    def get(self):
        blogpost = getPostFromRequestOrLast(self)
        
        if not blogpost:
            self.response.set_status(404)
            return
        
        if not blogpost.visible and not users.is_current_user_admin():
            logger.error('Access to invisible post')
            self.response.set_status(403)
            return
        
        comments = BlogPostComment.all().filter('reference', blogpost).filter('visible =', True).order('date')
        
        template_values= {
                          'blogpost': blogpost,
                          'comments': comments
                          }
        
        self.write_template('html/post-details.html', template_values)
        
class PageBannedUsers(BasicRequestHandler):
    """ Страница с забаннеными пользователями """
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return
        
        bannedusers=UserParams.all().filter('banned',True)
        template_values= {
                          'bannedusers': bannedusers,
                         }
        
        self.write_template('html/banned-users.html', template_values)
        
        
class PagePostEdit(BasicRequestHandler):
    """ Страница для редактирования или добавления поста """
    def get(self):
#        blogpost_name=self.request.get(const.param_post_name)
#        blogpost = None
#        if blogpost_name:
#            blogpost = getPostByName(blogpost_name)
            
        blogpost = getPostFromRequest(self)
            
        if not blogpost or blogpost.author==users.get_current_user() or users.is_current_user_admin():
            attach_cube_figure = self.request.get('attach_cube_figure')
            
            now_rating = int(time.time())
            
            template_values= {
                              'blogpost': blogpost,
                              'attach_cube_figure': attach_cube_figure,
                              'now_rating': now_rating
                             }
            
            self.write_template('html/post-edit.html', template_values)
        else:
            logger.error('Changing other\'s post')
            self.response.set_status(403)
            

class PagePostCommentEdit(BasicRequestHandler):
    """Страница для редактирования комментария"""
    def get(self): 
        if not self.user_info.admin:
            logger.error('Not admin')
            self.response.set_status(403)
            return
        
        comment = BlogPostComment.get(self.request.get(const.param_comment_key))
        if comment:
            template_values= {
                              'comment': comment,
                              }
        
            self.write_template('html/comment-edit.html', template_values)
        else:
            self.response.set_status(404)
            
            
class ActionPostCommentEdit(BasicRequestHandler):
    """Сохранение комментария после редактирования"""
    def post(self):
        if not self.user_info.admin:
            logger.error('Not admin')
            self.response.set_status(403)
            return
        
        comment = BlogPostComment.get(self.request.get(const.param_comment_key))
        if comment:
            comment.content=self.request.get('content')
            comment.put();
            self.redirect('/post?'+comment.reference.post_key_param())
        else:
            self.response.set_status(404)
        

class ActionPostSign(BasicRequestHandler):
    """ Сохранение поста """
    def post(self):
        if not self.user_info.user:
            logger.error('Try to sign post by anonymous user');
            self.response.set_status(403);
            return;
        
        if self.user_info.banned:
            logger.error('Try to sign post by banned user')
            self.response.set_status(403)
            return        
        
        blogpost = None
        if self.request.get(const.param_post_key):
            blogpost = getPostFromRequest(self)
            if not blogpost:
                self.response.set_status(404)
                return
                
            if blogpost.author!=users.get_current_user() and not users.is_current_user_admin():
                logger.error('Changing other\'s post')
                self.response.set_status(403)
                return
            
            if not blogpost.visible and not users.is_current_user_admin():
                logger.error('Changing invisible post')
                self.response.set_status(403)
                return
                            
        else:
            blogpost = BlogPost()
            blogpost.visible=True
            blogpost.rating = int(time.time())  
            blogpost.url_name = createPostName(self.request.get('title'))          
            if users.get_current_user():
                blogpost.author = users.get_current_user()
            
        blogpost.title = self.request.get('title')
        blogpost.content = self.request.get('content')
        blogpost.language = util.misc.determineLanguage(self.request.get('content'))
        if self.request.get('attach_cube_figure'):
            blogpost.attached_cube_figure = self.request.get('attach_cube_figure')
            
        if self.user_info.admin and self.request.get('rating'):
            blogpost.rating = int(self.request.get('rating')) 
        
        blogpost.comments_enabled = True;
        
        if blogpost.content and blogpost.title:             
            blogpost.put()
            
        self.redirect('/post?'+blogpost.post_key_param())
        
        
class ActionPostDelete(webapp.RequestHandler):
    """ Удаление поста и всех комментарием связанных с ним """
    def get(self):
        if users.is_current_user_admin():
            blogpost = getPostFromRequest(self)
            BlogPost.delete(blogpost)
            
        self.redirect('/')
        
class ActionPostCommentSign(BasicRequestHandler):
    """ Создание комментария к посту """
    def post(self):
        if not self.user_info.user or self.user_info.banned:
            logger.error('No user or banned')
            self.response.set_status(403)
            return
        
        blogpost=getPostFromRequest(self)
        
        if not blogpost.visible and not self.user_info.admin:
            logger.error('Commenting to invisible post')
            self.response.set_status(403)
            return 
        
        if not blogpost.comments_enabled:
            logger.error('Commenting to post with disabled comments')
            self.response.set_status(403)
            return            
            
        content=util.misc.removeDangerousHtmlTags(self.request.get('content'))
        if blogpost and content:        
            comment = BlogPostComment()
            comment.reference=blogpost
            comment.author=users.get_current_user()
            comment.content=content
            comment.visible=True
            comment.put()
            
        self.redirect(blogpost.post_details_url())
        
        
class ActionPostCommentDelete(webapp.RequestHandler):
    """ Удаление комментария администратором """
    def get(self):
        if (users.is_current_user_admin()):
            comment = BlogPostComment.get(self.request.get(const.param_comment_key))
            BlogPostComment.delete(comment)
        
        blogpost = getPostFromRequest(self)
        self.redirect(blogpost.post_details_url())
        
        
class ActionPostVote(webapp.RequestHandler):
    """ Голосование за пост """
    def get(self):
        blogpost = getPostFromRequest(self)
        user = users.get_current_user()
        
        self.response.headers['Content-Type'] = 'text/plain'
                
        if user and blogpost and  blogpost.author!=user and not user.nickname() in blogpost.votes:
            blogpost.votes+=[user]
            blogpost.put()
            self.response.out.write('doneVote("'+str(blogpost.key())+'",'+str(len(blogpost.votes))+')')
        else:
            self.response.out.write('')
                

class ActionUserBan(webapp.RequestHandler):
    """ Бан пользователя администратором """
    def get(self):
        if not users.is_current_user_admin():
            logger.error('No admin')
            self.response.set_status(403)
            return
        
        self.response.headers['Content-Type'] = 'text/plain'
        user_to_ban=None
        if self.request.get(const.param_comment_key):
            comment=BlogPostComment.get(self.request.get(const.param_comment_key));
            user_to_ban=comment.author
        elif self.request.get(const.param_post_key):
            blogpost=getPostFromRequest(self);
            user_to_ban=blogpost.author
            
        if user_to_ban:
            user_params = UserParams.all().filter('user', user_to_ban).get()
            
            if not user_params:
                user_params = UserParams()
                user_params.user = user_to_ban
                user_params.banned = True
                user_params.put() 
            else:
                user_params.banned = True
                user_params.put()            
              
        self.response.out.write('doneBanUser("'+user_to_ban.email()+'")')
            
class ActionUserUnban(webapp.RequestHandler):
    """ Отмена бана пользователя со страницы забанненых пользователей """
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return
        
        banned_user_key=self.request.get('banned_user_key');
        banned_user = UserParams.get(banned_user_key)
        banned_user.banned = False;
        banned_user.put()
        
        self.redirect('/admin/user/banned')
        
        
class PageLatestComments(BasicRequestHandler):
    """Страница с последними комментариями в порядке убывания времени"""
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return

        page_size=20
        start_index=0
        if (self.request.get('start')):
            start_index=int(self.request.get('start'))
            
        comment_query=BlogPostComment.all().order('-date')
        comments=comment_query.fetch(page_size+1,offset=start_index)
        
        prev_page_url=None
        next_page_url=None
        
        if start_index>0:
            index=start_index-page_size;
            if index<0:
                index=0;
                
            prev_page_url='/comment/all?start='+str(index)
            
        if len(comments)>page_size:
            next_page_url='/comment/all?start='+str(start_index+page_size)
        
        template_values= {
                          'comments': comments,
                          'prev_page_url': prev_page_url,
                          'next_page_url': next_page_url
                         }
        
        self.write_template('html/latest-comments.html', template_values)
 
 
        
class ActionPostCommentsEnable(webapp.RequestHandler):
    """Включение возможности комментирования"""
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return

        blogpost = getPostFromRequest(self)
        blogpost.comments_enabled=True
        blogpost.put()

        self.redirect(blogpost.post_details_url())
        
            
class ActionPostCommentsDisable(webapp.RequestHandler):
    """Включение возможности комментирования"""
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return

        blogpost = getPostFromRequest(self)
        blogpost.comments_enabled=False
        blogpost.put()

        self.redirect(blogpost.post_details_url())
        
        

class ActionPostShow(webapp.RequestHandler):
    """Показ поста"""
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return

        blogpost = getPostFromRequest(self)
        blogpost.visible=True;
        blogpost.put()
        
        self.redirect(blogpost.post_details_url())
        
class ActionPostHide(webapp.RequestHandler):
    """Скрытие поста"""
    def get(self):
        if not users.is_current_user_admin():
            logger.error('Not admin')
            self.response.set_status(403)
            return

        blogpost = getPostFromRequest(self)
        blogpost.visible=False
        blogpost.put()
        
        self.redirect(blogpost.post_details_url())
        
        
class PagePrivacyPolicy(BasicRequestHandler):
    """Страница с политикой конфиженциальности"""
    def get(self):
        self.write_template('html/privacy.html', {})

def getPostFromRequestOrLast(request_handler):
    """Получение поста, на основе параметров запроса"""
    post_key=request_handler.request.get(const.param_post_key)
    if post_key:
        return getPostByName(post_key)
    else: 
        return getLastPost()
        
def getPostFromRequest(request_handler):
    """Получение поста, на основе параметров запроса"""
    post_key=request_handler.request.get(const.param_post_key)
    if post_key:
        return getPostByName(post_key)
    else: 
        return None
        
def getPostByName(name):
    """ Получение поста по имени"""
    posts = BlogPost.all().filter('url_name =', name)
    if posts:
        return posts.get()
    else:
        return None
        
def createPostName(title):
    """Создание уникального имени поста"""
    name = convert_title_to_url_name(title)
    post = getPostByName(name)
    if post:
        index = 0
        base_name = name
        while post:
            index = index+1
            name = base_name+str(index)
            post = getPostByName(name)
    
    return name

def getLastPost():
    """Получение последнего поста"""
    return BlogPost.all().filter('visible =', True).order('-date').get()

def getPosts(start_index, page_size):
    """Получение постов для страничного отображения.
       Возвращает словарь с тремя параметрами: blogposts,prev_page_url,next_page_url
    """
    blogposts_query=BlogPost.all()
        
    if not users.is_current_user_admin():
        blogposts_query = blogposts_query.filter('visible =',True)

    blogposts_query = blogposts_query.order('-rating')
            
    blogposts = blogposts_query.fetch(page_size+1,start_index)

    if start_index == 0:
        prev_page_url = None
    elif start_index-page_size <= 0:
        prev_page_url = '/'
    else:
        prev_page_url = '/posts?start='+str(start_index-page_size)

    if len(blogposts) > page_size:
        next_page_url = '/posts?start='+str(start_index+page_size)
    else:
        next_page_url = None
            
    if len(blogposts) > page_size:
        visible_posts = blogposts[:-1]
    else:
        visible_posts = blogposts

    template_values = {
                        'blogposts': visible_posts,
                        'posts_prev_page_url': prev_page_url,
                        'posts_next_page_url': next_page_url
                      }
    
    return template_values