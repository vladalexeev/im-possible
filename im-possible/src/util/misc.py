# -*- coding: utf-8 -*-

from google.appengine.api import users
import logging

russianLetters=set(u'абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ')

class LoggerWrapper:
    def _prefix(self):
        if users.get_current_user():
            return '['+str(users.get_current_user().email())+'] '
        else:
            return '[anonymous] '
        
    def debug(self, message):
        logging.debug(self._prefix()+message)
        
    def error(self, message):
        logging.error(self._prefix()+message)
        
    
def determineLanguage(str):
    """Определение языка сообщения: english и russian"""
    if set(str).intersection(russianLetters):
        return 'russian'
    else:    
        return 'english'
    
def removeHtmlTags(text,allowed_tags=[]):
    """ Удаление всех HTML_тегов из текста 
    за исключением указанных в allowed_tags"""
    result_text=''
    for c in text:
        if c=='<' or c=='>':
            continue
        else:
            result_text+=c
            
    return result_text

def removeDangerousHtmlTags(text):
    """ Удаление всех потенциально опасных HTML тегов """
    return removeHtmlTags(text, ['i','b','em','strong'])


class StringFile:
    """Объект, оборачивающий строку в виде входного потока,
       так что его можно использовать в файловых операциях
    """
    __pos = -1;
    def __init__(self,str):
        self.str = str
        
    def read(self,length=1):
        result = ''
        for index in range(0,length):
            self.__pos += 1
            if self.__pos>=len(self.str):
                break
            
            result += self.str[self.__pos]
            
        return result

def list_table(list, row_len):
    """Функция преобразует линейный список в табличный
       со строками длиной row_len
    """
    result=[]
    index=0
    
    while index<len(list):
        if index+row_len<=len(list):
            result.append(list[index:index+row_len])
            index+=row_len
        else:
            result.append(list[index:len(list)])
            index=len(list)
            
    return result


translit_map={u'а':'a', u'б':'b', u'в':'v', u'г':'g', u'д':'d', u'е':'e',
              u'ё':'yo', u'ж':'zh', u'з':'z', u'и':'i', u'й':'j', u'к':'k',
              u'л':'l', u'м':'m', u'н':'n', u'о':'o', u'п':'p', u'р':'r',
              u'с':'s', u'т':'t', u'у':'u', u'ф':'f', u'х':'h', u'ц':'c',
              u'ч':'ch', u'ш':'sh', u'щ':'sch', u'ъ':'-', u'ы':'y', u'ь':'-',
              u'э':'ae', u'ю':'yu', u'я':'ya',
              u'А':'A', u'Б':'B', u'В':'V', u'Г':'G', u'Д':'D', u'Е':'E',
              u'Ё':'YO', u'Ж':'ZH', u'З':'Z', u'И':'I', u'Й':'J', u'К':'K',
              u'Л':'L', u'М':'M', u'Н':'N', u'О':'O', u'П':'P', u'Р':'R',
              u'С':'S', u'Т':'T', u'У':'U', u'Ф':'F', u'Х':'H', u'Ц':'C',
              u'Ч':'CH', u'Ш':'SH', u'Щ':'SCH', u'Ъ':'-', u'Ы':'Y', u'Ь':'-',
              u'Э':'AE', u'Ю':'YU', u'Я':'YA'
              }

allowed_url_chars=set(u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_.')

def convert_title_to_url_name(title):
    """Преобразование названия объекта в название для URL"""
    del_chars = set(u' \\/&@#%\'"')
    result = ''
    for c in title:
        if c in del_chars:
            result += '-'
        elif translit_map.has_key(c):
            result += translit_map[c]
        elif c in allowed_url_chars:
            result += c
        else:
            result +=str(ord(c))
    return result