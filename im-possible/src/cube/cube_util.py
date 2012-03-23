# -*- coding: utf-8 -*-

import math
import string

from google.appengine.api import images

from db.dbmodel import *
from util import misc

def convert_to_binary_string(value, digit_count):
    """Перевод числа в двоичную форму с заданным количеством знаков"""
    digits = 0
    result = ''
    while value>0 or digits<digit_count:
        mod = value % 2
        value = math.floor(value / 2)
        digits = digits + 1
        if mod==0:
            result = '0' + result
        else:
            result = '1' + result
        
    return result


def cube_binaries():
    """Возвращает список двоичных идентификаторов кубиков"""
    return [convert_to_binary_string(num, 6) for num in range(0,64)]


class CubeLibraryItem:
    """Элемент библиотеки кубиков
       index - индекс кубика в библиотеке
       binary - бинарный код кубика
       map_x - координата X в карте кубиков
       map_y - координата Y в карте кубиков
    """
    index = 0 
    binary = '000000'
    map_x = 0
    max_y = 0
    
    def __init__(self,index,binary,map_x,map_y):
        self.index = index
        self.binary = binary
        self.map_x = map_x
        self.map_y = map_y
        
        
        
class CubePoint:
    """Точка, описывающая один кубик фигуры
       binary - бинарный код кубика
       na - смещение линии сетки, идущей вправо-вниз
       nb - смещение линии сетки, идущей влево-вниз
       
       x - координата X изображения кубика
       y - координата Y изображения кубика
    """
    binary = '000000'
    na = 0
    nb = 0
    
    x = 0
    y = 0
    
    def __init__(self,binary,na,nb):
        self.binary = binary
        self.na = na
        self.nb = nb
        
        
class CubeFigureParseError(Exception): pass

class CubeBinaryParseError(Exception): pass

def test_binary(binary,binary_length):
    """Проверка корректности двочиного кода"""
    if len(binary)!=binary_length:
        return False
    
    for c in binary:
        if c!='0' and c!='1':
            return False
        
    return True
        
def parse_cube_point(str):
    """ Парсинг строки, описывающей один кубик фигур.
        Формат строки binary,na,nb
    """
    ss = string.split(str, ',')
    if len(ss)!=3:
        raise CubeFigureParseError
    
    if not test_binary(ss[0],6):
        raise CubeBinaryParseError
    
    return CubePoint(ss[0], int(ss[1]), int(ss[2]))

def get_default_cube_profile():
    """Получение профиля кубиков по-умолчанию"""
    return CubeProfile.all().filter('default',True).get()

def get_profile_cube(profile, binary):
    """Получение одного кубика из профиля"""
    return CubeProfileItem.all().filter('profile', profile).filter('binary =', binary).get().image

def create_figure_image(profile, figure):
    """Создание изображения фигуры из кубиков
       Функция возвращает список из следующих элементов
       [изображение, ширина изображения, высота изображения]
    """
    cube_points=[]
    top = left = right = bottom = -1
    grid_aspect = float(profile.grid_width) / float(profile.grid_height)
    
    cube_images={}
        
    for str in figure.cubes:
        p = parse_cube_point(str)
        nna = p.na * profile.grid_width
        nnb = p.nb * profile.grid_width
            
        p.x = int(round((nna + nnb) / 2))
        p.y = int(round((p.x - nna) / grid_aspect))
            
        cube_points.append(p)
            
        if left < 0 or p.x < left:
            left = p.x
                
        if top < 0 or p.y < top:
            top = p.y
                
        if right < 0 or p.x > right:
            right = p.x
                
        if bottom <0 or p.y > bottom:
            bottom = p.y
            
        if not cube_images.has_key(p.binary):
            cube_images[p.binary] = get_profile_cube(profile, p.binary)
            
        
    
    top -= 10
    left -= 10
    right += profile.cube_width+10
    bottom += profile.cube_height+10
    
    figure_image_width = right - left
    figure_image_height = bottom - top
    
    image_inputs = []
    
    max_composites = images.MAX_COMPOSITES_PER_REQUEST
    
    comp_image = None
    
    for cube_point in cube_points:
        image_inputs.append((
                             cube_images[cube_point.binary],
                             cube_point.x - left,
                             cube_point.y - top,
                             1.0,
                             images.TOP_LEFT))
        
        if len(image_inputs) == images.MAX_COMPOSITES_PER_REQUEST:
            comp_image = images.composite(image_inputs, figure_image_width, figure_image_height, 0, images.PNG)
            image_inputs=[(comp_image,0,0,1.0,images.TOP_LEFT)]
            
    if (comp_image and len(image_inputs)>1) or (not comp_image and len(image_inputs)>0):
        comp_image = images.composite(image_inputs, figure_image_width, figure_image_height, 0, images.PNG),
    
    return [
            images.composite(image_inputs, figure_image_width, figure_image_height, 0, images.PNG),
            figure_image_width,
            figure_image_height
            ]


def getCubeFigure(name):
    """Получение фигуры по имени из url_name"""
    if name:
        return CubeFigure.all().filter('url_name =', name).get()
    else:
        return None
    
def getCubeFigureFromRequest(request_handler):
    """получение фигуры из запроса"""
    name = request_handler.request.get(const.param_cube_figure_key)
    if name:
        return getCubeFigure(name)
    else:
        return None

def createCubeFigureUniqueName(title):
    """Создание уникального имени фигуры"""
    name = misc.convert_title_to_url_name(title)
    figure = getCubeFigure(name)
    
    if figure:
        index = 0
        base_name = name
        while figure:
            index = index+1
            name = base_name + str(index)
            figure = getCubeFigure(name)
            
    return name

def getLastCubeFigure():
    """Получение последней нарисованной фигуры"""
    return CubeFigure.all().order('-date').get()

if __name__=='__main__':
    print cube_binaries()
#    for num in range(0,64):
#        print str(num)+' = '+convert_to_binary_string(num, 6) 