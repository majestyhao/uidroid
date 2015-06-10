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
    #tmpi = []
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
                        node_bounds, node_index] # add width property
                nodelist_new.append(node)
    #             if node_class == 'android.app.ActionBar$Tab':
    #                 #tmpnode.append(node) # transmit address not value
    #                 tmpi.append(len(nodelist_new) - 1)
    # nodelist_length = len(nodelist_new)
    # for i in range(len(tmpi)):
    #     print nodelist_length - i - 1, i
    #     index = tmpi[i]
    #     tmpnode = nodelist_new[nodelist_length - i - 1]
    #     nodelist_new[nodelist_length - i - 1] = nodelist_new[index]
    #     nodelist_new[index] = tmpnode
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

def judge_click_attributes(node):
    newnode = []
    newnode.append(node[6])  # bounds
    newnode.append(node[2])
    newnode.append(node[3])
    # newnode.append(node[1])
    return newnode


def is_subset(a, b):
    if not a:
        return True
    for i in a:
        if i not in b:
           return False
    return True

def nodelist_judge_redef(nodelist):
    nodelist_judge = []
    for node in nodelist:
        nodelist_judge.append(judge_click_attributes(node))
    return nodelist_judge


def is_new_window(prior_window, nodelist):
    if not is_subset(prior_window, nodelist) \
            and not is_subset(nodelist, prior_window):
        return len(nodelist)
    else:
        return 1

def is_circle(node):
    if len(clicked_seq) - 2 < 0:
        return  False
    priprinode = clicked_seq[len(clicked_seq) - 2]
    print 'pripri:'
    print priprinode
    if priprinode != node:
        return False
    else:
        return True

def check_clicked():
    # dump ui hierarchy into a xml file and extract info from it
    ISOTIMEFORMAT = '%m%d-%H-%M-%S'
    global clicked_list, clicked_seq, clicked_list_width, prior_window
    global tic, toc, current_time
    tic = toc
    toc = time.clock()
    print toc - tic
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump("./data/" + current_time + "hierarchy.xml")
    # dev.screenshot("./data/" + current_time + ".png")
    dom = xml.dom.minidom.parse("./data/" + current_time + "hierarchy.xml")
    global flag_start_logcat
    global flag_start_activity
    global flag_destroy_activity

    # retrieve xml elements
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')
    nodelist = nodelist_redef(nodelist)
    current_window = nodelist_judge_redef(nodelist)
    # num of nodes at new window is the width of the parent node
    width = is_new_window(prior_window, current_window)
    prior_window = current_window
    #print width
    prinode_index = -1
    if len(clicked_seq) > 0:
        prinode = clicked_seq[len(clicked_seq) - 1]
        if prinode != -1:
            prinode_index = clicked_list.index(prinode)
    if width > 1:
        if prinode == -1:
            print 'ffffffffffffffffback'

        if prinode != -1 and clicked_list_width[prinode_index] != -1:
            clicked_list_width[prinode_index] = width

    print clicked_list_width
    for i in nodelist:
        node = judge_click_attributes(i)
        # if i[2] == 'android.app.ActionBar$Tab':
        #     print i[2]
        #     print i[7]

        if node in clicked_list:
            node_index = clicked_list.index(node)
            if clicked_list_width[node_index] > 0:
                if is_circle(node):
                    if prinode != -1 and prinode_index != -1:
                        clicked_list_width[prinode_index] = -1
                        print 'oa'
                clicked_list_width[node_index] -= 1
                clicked_seq.append(node)
                ui_interaction(i)
                print 'what!!!!!!!!!!!!!!!!!!'
                return True
        else:
            clicked_seq.append(node)
            print node
            clicked_list.append(node)
            clicked_list_width.append(0)
            ui_interaction(i)
            return True
    clicked_seq.append(-1)
    dev.press.back()
    global flag_back, back_counter
    flag_back = True
    print "back2"
    back_counter += 1
    return False


def ui_interaction(node):
    arg = get_selector_attributes(node)
    if not dev(**arg).exists:
        return
    #pop_logcat_starter = pop_logcat()
    #pop_logcat_starter.start()
    # perform click
    cmd = 'CLICK'
    print arg
    # start logcat
    #flag_start_logcat = True
    CMD_MAP[cmd](dev, arg)
    print 'click ' + node[2] + ' at ' + current_time
    # dev.wait.idle()
    # time.sleep(1)  # wait 30 secs more to retrieve all asked permission
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
    # dev.swipe()  # swipe from left to right to cover the case like Wechat
    #dev.press.back()  # press back when all clickable have been clicked

package = 'com.google.android.deskclock'
#package = 'com.android.dialer'
#package = 'com.android.settings'
# do ui interactions
clicked_list = []
clicked_seq = []
prior_window = []
nodelist = []
back_counter = 0
clicked_list_width = []
toc = time.clock()
# per activity (not necessary a new activity, new updated window is enough)
while check_clicked() or back_counter <= 5:
    pass
    #ui_interaction()