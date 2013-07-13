# -*- coding: utf-8 -*-
#import os
#import cgi
#import datetime
#import time
#import wsgiref.handlers

#import logging

from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

#from common.customfilters import *
#from utils import *

#import const
#from iwc import config

from db.dbmodel import *
from iwc.ws_base import *

from iwc import rss
from iwc import pages
from iwc import pages_admin

from cube import cube_pages
from cube import cube_rss

from util import update

#import logging
#logger=logging.getLogger('test')
#logger.setLevel(logging.DEBUG)
#logger.debug("test")


application = webapp.WSGIApplication([
                                      ('/', pages.PageMain),
                                      ('/posts/(.*)', pages.PagePostDetails2),
                                      ('/posts', pages.PagePosts),
                                      ('/post/sign', pages.ActionPostSign),
                                      ('/post', pages.PagePostDetails),
                                      ('/post/vote',pages.ActionPostVote),                                      
                                      ('/post/edit',pages.PagePostEdit),
                                      ('/post/delete',pages.ActionPostDelete),
                                      ('/post/comments_enable',pages.ActionPostCommentsEnable),
                                      ('/post/comments_disable',pages.ActionPostCommentsDisable),
                                      ('/post/show',pages.ActionPostShow),
                                      ('/post/hide',pages.ActionPostHide),
                                      ('/comment/sign',pages.ActionPostCommentSign),
                                      ('/comment/delete',pages.ActionPostCommentDelete),
                                      ('/comment/edit',pages.PagePostCommentEdit),
                                      ('/comment/change',pages.ActionPostCommentEdit),
                                      ('/comment/all',pages.PageLatestComments),
                                      ('/admin/user/ban',pages.ActionUserBan),
                                      ('/admin/user/unban',pages.ActionUserUnban),
                                      ('/admin/user/banned',pages.PageBannedUsers),
                                      ('/rss/posts',rss.RssPosts),
                                      ('/config',pages_admin.PageConfig),
                                      ('/config/save',pages_admin.ActionConfigSave),
                                      ('/privacy',pages.PagePrivacyPolicy),
                                      
                                      ('/cube/profiles', cube_pages.PageCubeProfiles),
                                      ('/cube/profile', cube_pages.PageCubeProfile),
                                      ('/cube/profile/image', cube_pages.ImageCubeProfile),
                                      ('/cube/profile/save', cube_pages.ActionCubeProfileSave),
                                      ('/cube/profile/delete', cube_pages.ActionCubeProfileDelete),
                                      ('/cube/figures/user', cube_pages.PageCubeFiguresUser),
                                      ('/cube/figures/all', cube_pages.PageCubeFiguresAll),
                                      ('/cube/figures/best', cube_pages.PageCubeFiguresBest),
                                      ('/cube/constructor', cube_pages.PageCubeConstructor),
                                      ('/cube/figure/save', cube_pages.ActionCubeFigureSave),
                                      ('/cube/figure/delete', cube_pages.ActionCubeFigureDelete),
                                      ('/cube/figure/image/(.*)', cube_pages.ImageFigureRequest),
                                      ('/cube/figure/thumbnail/(.*)', cube_pages.ThumbnailFigureRequest),
                                      ('/cube/figure/rating', cube_pages.ActionCubeFigureRating),
                                      ('/rss/cube',cube_rss.RssFigures),
                                      
                                      ('/update/posts',update.ActionUpdatePosts),
                                      ('/update/figures', update.ActionUpdateCubeFigures)
                                     ], debug=True)

webapp.template.register_template_library('common.customfilters')


#def main():
#    wsgiref.handlers.CGIHandler().run(application)
#
#
#if __name__ == '__main__':
#    main()
