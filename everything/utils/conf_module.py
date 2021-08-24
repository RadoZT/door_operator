# -*- coding: utf-8 -*-
import sys
import os
import codecs

def load_conf(filename):
    """
    The function loads data from configuration file with path 'filename'
    
    'filename' is the fully qualified path to the configuration file
    The configuration file consists from rows containing key value pairs
    delimited with equal sign '='. The blank signs before the equal sign and the
    key are removed. The key can not contain blank signs and can not be with zero
    length. The value part can include and can be surrounded with blank signs.
    Every key must be unique in the configuration file.

    There can be any number of rows starting with # - comment rows. Such
    rows are skipped.

    The function returns a dictionary with the loaded key/value pairs.

    If 'filename' is None or is with zero length the path is determined as
    sys.path[0] + '/conf.conf'
    """
    #print(filename)
    resultd = {}
    uline = None
    f = None
    mfilename = filename
    if mfilename == None:
        mfilename = os.path.join(sys.path[0],'conf.conf')
    elif filename == '':
        mfilename = os.path.join(sys.path[0],'conf.conf')
    
    if not os.access(mfilename, os.F_OK):
        return resultd
        
    try:
        #f = open(mfilename, 'rb') #, "cp1251")
        f = codecs.open(mfilename, 'rU', "utf-8")

    except:
        #Не може да бъде отворен файлът
        # за в бъдеще трябва да се различат случаите (
        # на липсващ файл и на дефектен или блокиран файл
        return resultd
    
    #unicodebom = unicode( codecs.BOM_UTF8, "utf-8" )
    
    for uline in f:
        #print ('inline=' , uline)
        if len(uline) == 0: continue
        #if uline[0:1] == unicodebom:
        #    uline = uline[1:]
        uline = uline.replace('\r', '')
        uline = uline.replace('\n', '')
        if len(uline) == 0: continue
        if uline[0:1] == '#':
            #print ('comment ' , uline)
            continue
        eqsign = None
        for i in range(len(uline)):
            if uline[i] == '=':
                eqsign = i
                break
        if eqsign == None:
            #print 'No equal sign'
            continue
        else:
            
            keypart = uline[0:eqsign].strip()
            valpart = uline[eqsign+1:]
            if keypart in resultd.keys():
                continue
            else:
                resultd[keypart]=valpart
                #print 'placed in resultd ', keypart, '=' , valpart
    f.close()
    #print(resultd)
    return resultd

