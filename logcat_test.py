__author__ = 'hao'
import Queue
import subprocess
import threading
import re

class AsynchronousFileReader(threading.Thread):
    '''
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    '''

    def __init__(self, fd, queue):
        assert isinstance(queue, Queue.Queue)
        assert callable(fd.readline)
        threading.Thread.__init__(self)
        self._fd = fd
        self._queue = queue

    def run(self):
        '''The body of the tread: read lines and put them on the queue.'''
        for line in iter(self._fd.readline, ''):
            if flag:
                return
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()

line = ''
class pop_logcat(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global series,line, flag
         # add any command line arguments here.
        process = subprocess.Popen(['adb', '-s', series, 'logcat', '|', 'grep', 'UiDroid'],
                stdout=subprocess.PIPE)

        # Launch the asynchronous readers of the process' stdout.
        stdout_queue = Queue.Queue()
        stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
        stdout_reader.start()
        # Check the queues if we received some output (until there is nothing more to get).
        counter = 0
        while not stdout_reader.eof():
            while not stdout_queue.empty():
                if counter == 100:
                    flag = True
                    return
                counter += 1
                line = stdout_queue.get()
                print int(re.search((r'\d+'), line).group())
                print line
            #if counter == 2:
             #   return



class mytest2(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        #global line
        while 1:
            if line != line:
                line = line.split(', ')
                print line

# clickflag => read buffer => do click
#series = '014E233C1300800B'
series = '01b7006e13dd12a1'
flag = False
c = pop_logcat()
c.start()
c.join()
print flag

p = subprocess.Popen(['adb', '-s', series, 'logcat', '-c'],
                    stdout=subprocess.PIPE)
p.wait()
c = pop_logcat()
c.start()
c.join()
print flag
# flag = True
#cs = mytest2()
#cs.start()
#while 1:
 #   pass
# while not stdout_reader.eof():
#         while not stdout_queue.empty():
#             #global line
#             line = stdout_queue.get()
#             print line