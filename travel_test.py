#!/usr/bin/env python2
#-*-encoding:utf-8-*-
__author__ = 'Hao'
from uiautomator import device as dev
import xml.dom.minidom
import os
import time

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

def check_subset(a, b):
    if not a:
        return True
    c = []
    for i in b:
        #if i[3]:
        c.append(i[6])
    print 'damn:'
    print c
    for i in a:
        if a not in b:
            if i[6] in c:
                continue
            print i
            return False
    return True

def check_clicked(clicked_list):
     # dump ui hierarchy into a xml file and extract info from it
    ISOTIMEFORMAT = '%m%d-%H-%M-%S'
    global current_time, nodelist
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump("./data/" + current_time + "hierarchy.xml")
    # dev.screenshot("./data/" + current_time + ".png")
    dom = xml.dom.minidom.parse("./data/" + current_time + "hierarchy.xml")

    global flag_start_logcat
    global flag_start_activity
    global flag_destroy_activity

    # 得到xml文档元素对象
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')
    nodelist = nodelist_redef(nodelist)
    for i in nodelist:
        if i not in clicked_list:
            return nodelist
    return []


def ui_interaction():
        global current_window
        global nodelist
        #if not check_subset(current_window, nodelist):
         #   if not check_subset(nodelist, current_window):
          #      return False
        current_window = nodelist
        for i in range(len(nodelist)):
            node = nodelist[i]
            if node[5] == 'true':
                arg = get_selector_attributes(node)
                if node not in clicked_list:
                    #pop_logcat_starter = pop_logcat()
                    #pop_logcat_starter.start()
                    # perform click
                    cmd = 'CLICK'
                    print arg
                    # start logcat
                    flag_start_logcat = True
                    CMD_MAP[cmd](dev, arg)
                    clicked_list.append(node)
                    print 'click ' + node[1] + ' at ' + current_time
                    dev.wait.idle()
                    time.sleep(1)  # wait 30 secs more to retrieve all asked permission
                # flag_start_logcat = False
                # pop_logcat_starter.join()
                # if flag_start_activity:
                #     save_node = handle_start_activity(node)
                #     print save_node
                #     flag_start_activity = False
                # if flag_destroy_activity:
                #     handle_destroy_activity(save_node)
                #     print save_node
                #     flag_destroy_activity = False
                    return True
        # dev.swipe()  # swipe from left to right to cover the case like Wechat
        dev.press.back()  # press back when all clickable have been clicked
        return True

package = 'com.android.deskclock'
# do ui interactions
clicked_list = []
current_window = []
nodelist = []
# per activity (not necessary a new activity, new updated window is enough)
while check_clicked(clicked_list):
    ui_interaction()