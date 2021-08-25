# -*- coding: utf-8 -*-

import sys
import os
import codecs
import shutil

def copy_file(pars, from_file, to_file):
    """
    Копиране на файл с име from_file, като файл с име to_file.
    В речник pars може да има два параметъра, които могат да се ползват
    при копирането. Техните ключове са както следва:
    'from_file_dir' - ако съществува и стойността е отлична от '', пълното
        име на файла се получава с функцията
        os.path.join(pars['from_file_dir'],from_file)
        в този случай pars['from_file_dir'] трябва да е директория
    'to_file_dir' - ако съществува и стойността е отлична от '', пълното
        име на файла се получава с функцията
        os.path.join(pars['to_file_dir'],to_file)
        в този случай pars['to_file_dir'] трябва да е директория
    Функцията връща резултат
    'OK - <допълнително пояснение>', ако копирането е успешно и
    'ERR - <име на грешката>', ако копирането не е успяло
    Ако копирането не е успяло в pars['err_found'] се вписва true
    
    pars може да съдържа следните параметри:
    - 'dont_override' - ако съществува и е true забранява подмяната
        на to_file, ако последния е файл и съществува
    - 'to_directory' - ако съществува и е true изисква to_file да e
        директория
    """
    if type(pars).__name__ != 'dict':
        return 'ERR - pars is not a dictionary'
    dont_override = false
    if pars.has_key('dont_override'):
        dont_override = pars['dont_override']
    
    from_file_dir = ''
    to_file_dir = ''
    if pars.has_key('from_file_dir'):
        from_file_dir = pars['from_file_dir']
    
    if pars.has_key('to_file_dir'):
        to_file_dir=pars['to_file_dir']

    if from_file_dir == '':
        from_file_dir = from_file
    else:
        from_file_dir = os.path.join(from_file_dir, from_file)

    if to_file_dir == '':
        to_file_dir = to_file
    else:
        to_file_dir = os.path.join(to_file_dir, to_file)

    if not os.access(from_file_dir, os.F_OK):
        pars['err_found'] = true
        return "ERR - source file '" + from_file_dir + "' don't exists"
    
    if not os.access(from_file_dir, os.R_OK):
        pars['err_found'] = true
        return "ERR - source file '" + from_file_dir + "' don't has read permission"
    to_directory = false
    if pars.has_key('to_directory'):
        to_directory = pars['to_directory']
    if to_directory:
        if os.access(to_file_dir, os.F_OK):
            pars['err_found'] = true
            return "ERR - destination path '" + to_file_dir + "' dont exists"
        if not os.path.isdir(to_file_dir):
            pars['err_found'] = true
            return "ERR - destination path '" + to_file_dir + "' is not directory"
        if os.access(to_file_dir, os.W_OK):
            pars['err_found'] = true
            return "ERR - destination directory '" + to_file_dir + "' has no write permissions"


    else:
        if os.access(to_file_dir, os.F_OK) and dont_override:
            pars['err_found'] = true
            return "ERR - destination file '" + to_file_dir + "' exists"
    
        if os.access(to_file_dir, os.F_OK) and os.access(to_file_dir, os.W_OK):
            pars['err_found'] = true
            return "ERR - destination file '" + to_file_dir + "' exists and has no write permission to be overriden"
    
    try:
        shutil.copy2(from_file_dir, to_file_dir)
        return "OK - successfully copyed '" + from_file_dir + "' to '" + \
                to_file_dir + "'"
    except:
        pars['err_found'] = true
        return "ERR - exception copying '" + from_file_dir + "' to '" + \
                to_file_dir + "' --> " + str( sys.exc_info()[0])
        
    
        
