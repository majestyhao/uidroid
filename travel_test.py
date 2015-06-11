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
    'WAIT': lambda dev, arg: dev.wait.update()  # wait until window update event occurs
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

def nodelist_judge_redef(nodelist):
    nodelist_judge = []
    for node in nodelist:
        nodelist_judge.append(judge_click_attributes(node))
    return nodelist_judge

def hash_window(nodelist):
    return hash(str(nodelist))

def is_new_window(nodelist):
    global window_visted, window_node_map, same_window_counter
    tmp = hash_window(nodelist)
    if not window_visted:
        window_visted.append(tmp)
        window_node_map.append(-1)
        return 0
    # return the width
    if tmp not in window_visted:
        same_window_counter = 0
        prinode = clicked_seq[len(clicked_seq) - 1]
        if prinode != -1:
            prinode_index = clicked_list.index(prinode)
            if prinode_index not in window_node_map:
                tmpcounter = 0
                for i in nodelist:
                    if i not in clicked_list:
                        tmpcounter += 1
                clicked_list_width[prinode_index] = tmpcounter
                window_visted.append(tmp)
                window_node_map.append(prinode_index)
                print 'NEEEEEEEEEEEEEEEEEEEEEEEW WINDDDDDDDDDDDDDDDDDDDOW'
                return prinode_index
    else:
        same_window_counter += 1
        tmpindex = window_visted.index(tmp)
        return window_node_map[tmpindex]


def check_clicked():
    # dump ui hierarchy into a xml file and extract info from it
    ISOTIMEFORMAT = '%m%d-%H-%M-%S'
    global clicked_list, clicked_seq, clicked_list_width
    global current_time

    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump("./data/" + current_time + "hierarchy.xml")
    # dev.screenshot("./data/" + current_time + ".png")
    dom = xml.dom.minidom.parse("./data/" + current_time + "hierarchy.xml")

    # retrieve xml elements
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')
    nodelist = nodelist_redef(nodelist)
    current_window = nodelist_judge_redef(nodelist)
    # num of nodes at new window is the width of the parent node
    parent = is_new_window(current_window)
    #print 'parent'
    print parent
    #print ' .........'

    print clicked_list_width
    for i in nodelist:
        if same_window_counter > 10:
            break
        node = judge_click_attributes(i)
        if node in clicked_list:
            node_index = clicked_list.index(node)
            if clicked_list_width[node_index] > 0:
                print node
                if node == clicked_seq[len(clicked_seq) - 1]:
                    clicked_list_width[node_index] = 0
                ui_interaction(i)
                clicked_list_width[node_index] -= 1
                if parent:
                    clicked_list_width[parent] -= 1
                clicked_seq.append(node)
                print 'what!!!!!!!!!!!!!!!!!!'
                print clicked_list_width[node_index]
                return True
        else:
            print node
            if parent:
                clicked_list_width[parent] -= 1
            clicked_seq.append(node)
            clicked_list.append(node)
            clicked_list_width.append(0)
            ui_interaction(i)
            return True
    if parent > 0:
        clicked_list_width[parent] = 0
        return False
    clicked_seq.append(-1)
    dev.press.back()
    global back_counter
    print "back2"
    back_counter += 1
    return False


def ui_interaction(node):
    arg = get_selector_attributes(node)
    if not dev(**arg).exists:
        return
    cmd = 'CLICK'
    print arg
    CMD_MAP[cmd](dev, arg)
    print 'click ' + node[2] + ' at ' + current_time


package = 'com.google.android.deskclock'
#package = 'com.android.dialer'
#package = 'com.android.settings'
#package = 'com.android.deskclock'
clicked_list = []
clicked_seq = []
nodelist = []
back_counter = 0
clicked_list_width = []
window_visted = []
window_node_map = []
tic = time.clock()
same_window_counter = 0
# per activity (not necessary a new activity, new updated window is enough)
while check_clicked() or back_counter <= 15:
    toc = time.clock()
    time.sleep(1)
    #print toc - tic
    tic = time.clock()
    pass
    #ui_interaction()