# -*- coding: utf-8 -*-
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from db.dbmodel import CubeFigure

from util import misc

logger=misc.LoggerWrapper()

def contains(x,element):
    """Фильтр для шаблонов, определяющий находится ли элемент 
    внутри списка. """    
    return element in x

def splitlongwords(x,word_length=50):
    """Фильтр разбивает слова в строке пробелами, 
    если они по длине больше чем word_length"""
    last_space_index=0
    result=''
    in_tag=False
    
    for i in range(0,len(x)):
        c=x[i]
        if not in_tag:
            if c=='<':
                in_tag=True
            elif c==' ' or c=='\n' or c=='\r' or c=='\t':
                last_space_index=i
            else:
                if i-last_space_index > word_length:
                    result+=' '
                    last_space_index=i
        elif c=='>':
            in_tag=False
            last_space_index=i
        
        result+=c
        
    return result



def truncatetext(x,text_length=500):
    """Фильтр обрезает строку по последнему слову,
    которое не больше длины text_length"""
    if len(x)<=text_length:
        return x
    
    word=''
    result=''
    
    for i in range(0,min(text_length,len(x))):
        c=x[i]
        if c==' ' or c=='\n' or c=='\r' or c=='\t':
            result+=word+c
            word=''
        else:
            word+=c
            
    result+='...'
            
    return result;

def hash(h,key):
    """Фильтр для получения значения из словаря"""
    return h[key]

def equal(x,arg):
    """Фильтр проверки равенства двух аргументов"""
    return x == arg


def cube_figure_thumbnail(figure):
    """Фильтр для вывода эскиза фигры из кубиков"""
    if not figure:
        return ''
    
    logger.error('cube_figure_thumbnail')
    
    if not isinstance(figure, CubeFigure):
        key=db.Key(figure)
        figure = CubeFigure.get(key)
        
    if not figure:
        return '<small><b>Figure not found</b></small>'
    else:    
        return '<a href="/cube/figure/image/'+figure.url_name+'">'+\
            '<img src="/cube/figure/thumbnail/'+figure.url_name+'" border="0" alt="'+\
            figure.name+'" title="'+figure.name+'"/></a>'

def div_decorate(text):
    if text:
        return '<div>'+text+'</div>'
    else:
        return ''
    
def show_hyperlinks(text):
    """Функция выделяет тегами <a> гиперссылки, начинающиеся на http://"""
    result = ''
    while len(text) > 0:
        index = text.find('http://')
        if index >= 0:
            index2 = len(text)
            for i in range(index,len(text)):
                if text[i] in (' ','\n','\r'):
                    index2 = i
                    break
                
            anchor = text[index:index2]
            result += text[0:index]+'<a href="'+anchor+'">'+anchor+'</a>'
            text = text[index2:]
        else:
            result += text
            text='' 
             
    return result  


register = template.create_template_register()
register.filter(contains)
register.filter(splitlongwords)
register.filter(truncatetext)
register.filter(hash)
register.filter(equal)

register.filter(cube_figure_thumbnail)
register.filter(div_decorate)
register.filter(show_hyperlinks)

