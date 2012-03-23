# -*- coding: utf-8 -*-
from util import misc

def main():
    print misc.translit_map.has_key(u'ж')
    print misc.translit_map[u'ж']
    print misc.convert_title_to_url_name(u'as ä лоролропло f@s///adf')
    
if __name__=='__main__':
    main()    
    
