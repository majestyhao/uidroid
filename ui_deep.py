#!/usr/bin/env python2
#-*-encoding:utf-8-*-
from uiautomator import device as dev
import xml.dom.minidom
import time
import os

print dev.info
dev.screen.on()
os.system('rm -r -f data')
os.system('mkdir data')


CMD_MAP = {
    'CLICK': lambda dev, arg: dev(**arg).click(),
    'TOUCH': lambda dev, arg: dev.click(**arg),
    'DRAG': lambda dev, arg: dev.drag(**arg),
    'PRESS': lambda dev, arg: dev.press(**arg),
    'WAIT': lambda dev, arg: dev.wait.update() # wait until window update event occurs
    }

import Queue
import subprocess
import threading
import re # reg exp

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
            if not flag_start_logcat:
                return
            self._queue.put(line)

    def eof(self):
        '''Check whether there is no more content to expect.'''
        return not self.is_alive() and self._queue.empty()

class pop_logcat(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
         # add any command line arguments here.
        process = subprocess.Popen(['adb', '-s', '014E233C1300800B', 'logcat', '|', 'grep', "My"],
                stdout=subprocess.PIPE)

        # Launch the asynchronous readers of the process' stdout.
        stdout_queue = Queue.Queue()
        stdout_reader = AsynchronousFileReader(process.stdout, stdout_queue)
        stdout_reader.start()
        global flag_start_activity
        global flag_start_logcat
        global flag_stop_activity
        # Check the queues if we received some output (until there is nothing more to get).
        log_backup = []
        while not stdout_reader.eof():
            while not stdout_queue.empty():
                # global line
                line = stdout_queue.get()
                log_backup.append(line)
                print line
                if is_start_activity(line):
                    flag_start_activity = True
                if is_stop_activity(line):
                    flag_stop_activity = True
                    #print 'logcat backup \n' + log_backup
                     # clear logcat
        stdout_reader.join()
        subprocess.Popen(['adb', '-s', '014E233C1300800B', 'logcat', '-c'],
                                 stdout=subprocess.PIPE)
        return


def nodelist_redef(nodelist):
    # only retrieve GUI components belong to target pkg
    # and only interested attributes enough to figure out the unique one
    nodelist_new = []
    tmpnode = []
    tmpi = []
    for i in range(len(nodelist)):
        node = nodelist[i]
        if node.getAttribute('clickable') == 'true':
            # node_index = node.getAttribute('index')
            node_text = node.getAttribute('text')
            node_resid = node.getAttribute('resource-id')
            node_class = node.getAttribute('class')
            if node_class == 'android.widget.EditText':
                continue
            node_package = node.getAttribute('package')
            node_contentdesc = node.getAttribute('content-desc')
            node_clickable = node.getAttribute('clickable')
            node_bounds = node.getAttribute('bounds')
            node_index = node.getAttribute('index')
            if node_package == package:
                node = [node_text, node_contentdesc,
                    node_class, node_resid, node_package, node_clickable,
                        node_bounds, node_index]
                nodelist_new.append(node)
                if node_class == 'android.app.ActionBar$Tab':
                    tmpnode.append(node)
                    tmpi.append(len(nodelist_new) - 1)
    nodelist_length = len(nodelist_new)
    for i in range(len(tmpi)):
        index = tmpi[i]
        nodelist_new[index] = nodelist_new[nodelist_length - i - 1]
        nodelist_new[nodelist_length - i - 1] = tmpnode[i]
    return nodelist_new

def get_selector_attributes(node):
    attributes = dict()
    if node[0] != '':
        print node[0]
        attributes['text'] = node[0]
    #if node[1] != '':
        # print node[1]
        # attributes['description'] = node[1] # for clock, its description change frequently
    if node[2] != '':
        attributes['className'] = node[2]
    if node[3] != '':
        attributes['resourceId'] = node[3]
    # attributes['bounds'] = node[6]
    attributes['index'] = node[7]
    return attributes

def is_click(line):
    if len(line) > 250:
        return False
    # pattern = re.compile('.*android.view.View$PerformClick.*') # Looper
    pattern = re.compile('.*performButtonClick.*')
    match = pattern.search(line)
    if match:
        # print match.group()
        return True
    return False

def is_stop_activity(line):
    if len(line) > 250:
        return False
    pattern = re.compile('.*activityStopped.*')
    match = pattern.search(line)
    if match:
        # print match.group()
        print "StopAct"
        return True
    return False

def is_start_activity(line):
    if len(line) > 250:
        return False
    pattern = re.compile('.*startActivity*')
    match = pattern.search(line)
    if match:
        # print match.group()
        print "StartAct"
        return True
    return False

def handle_start_activity(activity_id):

    # save the node is going to trigger activity
    visted_activities.append(activity_id)
    return activity_id

def handle_stop_activity(node):
    # after decting activity stopped by clicking a button
    # re-enter previous activity
    arg = get_selector_attributes(node)
    if dev(**arg).exists:
        dev(**arg).click()
        if check_clicked(clicked_list):
            ui_interaction()


def check_clicked(clicked_list):
    global back_counter
    global dev
    os.system('adb start-server')
    #time.sleep(5)
    from uiautomator import device as dev
    dev.info
    # dump ui hierarchy into a xml file and extract info from it
    ISOTIMEFORMAT = '%m%d-%H-%M-%S'
    global current_time, nodelist
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump("./data/" + current_time + "hierarchy.xml")
    dev.screenshot("./data/" + current_time + ".png")
    dom = xml.dom.minidom.parse("./data/" + current_time + "hierarchy.xml")

    global flag_start_logcat
    global flag_start_activity
    global flag_stop_activity

    # 得到xml文档元素对象
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')
    nodelist = nodelist_redef(nodelist)
    for i in nodelist:
        if i not in clicked_list:
            return nodelist
    dev.press.back()
    global flag_back
    flag_back = True
    print "back2"
    back_counter += 1
    return []

back_counter = 0
flag_back = False

def ui_interaction():
    global current_window, nodelist
    global flag_start_activity, flag_stop_activity, flag_start_logcat, flag_back
        #if not check_subset(current_window, nodelist):
         #   if not check_subset(nodelist, current_window):
          #      return False
    current_window = nodelist
    for i in range(len(nodelist)):
        node = nodelist[i]
        if node[5] == 'true':
            arg = get_selector_attributes(node)
            if node not in clicked_list:
                # perform click
                cmd = 'CLICK'
                print arg
                # start logcat
                flag_start_logcat = True
                CMD_MAP[cmd](dev, arg)
                clicked_list.append(node)
                print 'click ' + ' at ' + current_time
                # dev.wait.idle()
                pop_logcat_starter = pop_logcat()
                pop_logcat_starter.start()
                time.sleep(6)  # wait 30 secs more to retrieve all asked permission
                flag_start_logcat = False
                pop_logcat_starter.join()
                if flag_start_activity:
                    # save_node = handle_start_activity(node)
                    print save_node
                    flag_start_activity = False
                if flag_stop_activity:
                    # handle_stop_activity(save_node)
                    print save_node
                    flag_stop_activity = False
                return True
    # dev.swipe()  # swipe from left to right to cover the case like Wechat
    dev.press.back()  # press back when all clickable have been clicked
    flag_back = False
    return True

flag_start_activity = False
flag_start_logcat = False
flag_stop_activity = False
package = 'com.android.dialer'
save_node = None
#line = ''
visted_activities = []

# two subthreads, one for ui-interaction, another for logcat reading
# do ui interactions
clicked_list = []
current_window = []
nodelist = []
# per activity (not necessary a new activity, new updated window is enough)
while check_clicked(clicked_list) or back_counter <= 5:
    if flag_back:
        flag_back = False
        continue
    ui_interaction()

















# find all clickable and put them into a list
# click them one by one
# wait for update of activity
# wait 30 secs more after click happens
# rec permission and file access
