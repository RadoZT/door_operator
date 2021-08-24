
import os, sys, time


def write_log(log, maxloglen, message, lock_for_log=None):
    if (lock_for_log != None):
        lock_for_log.acquire()
    
    logfile = None
    if log != '':
        try:
            logfile = open(log,'ab')
            logfile.write(time.strftime("%Y/%m/%d %H:%M:%S: ", time.localtime()).encode( "utf-8" ))
            logfile.write(message.encode( "utf-8" ))
            logfile.write('\n'.encode( "utf-8" ))
            #logfile.write(os.linesep)
            logfile.close()
            if os.path.getsize(log) > maxloglen:
                if os.path.isfile(log + '.back'):
                    os.remove(log + '.back')
                os.rename(log, log + '.back')
        except Exception as error:
            if logfile != None:
                if logfile.closed:
                    pass
                else:
                    logfile.close()
    if (lock_for_log != None):
        lock_for_log.release()


if __name__=="__main__":
    write_log(os.path.join(sys.path[0], 'test.log'), 1000000, 'first')
    write_log(os.path.join(sys.path[0], 'test.log'), 1000000, u'втори')
    write_log(os.path.join(sys.path[0], 'test.log'), 1000000, u'трети')
