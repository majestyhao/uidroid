#!/usr/bin/env python2
#-*-encoding:utf-8-*-
__author__ = 'Hao'
from uiautomator import device as dev
import xml.dom.minidom
import os
import time
import difflib

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

def DFS(node, nodelist):
    if node not in nodelist:
        nodelist.append(node)
        print node
        for i in node.childNodes:
            DFS(i, nodelist)

def node_details(node):
    node_text = node.getAttribute('text')
    node_resid = node.getAttribute('resource-id')
    node_class = node.getAttribute('class')
    node_package = node.getAttribute('package')
    node_contentdesc = node.getAttribute('content-desc')
    node_clickable = node.getAttribute('clickable')
    node_bounds = node.getAttribute('bounds')
    node_index = node.getAttribute('index')

    if node.getAttribute('clickable') == 'true':
        if node_class == 'android.widget.EditText':
                continue

        if node_package == package:
            node = [node_text, node_contentdesc,
                node_class, node_resid, node_package, node_clickable,
                    node_bounds, node_index] # add width property

    return node

def travel_xml(root):

def is_new_node(node):
    # check whether is a new node


def is_new_window(nodelist):
    # whether is a new window
    # if not: same_window++
    # return the number nodes have not been clicked

def is_samewindow_similar_parent(node, parent):

def samewindow_threshold():



def nodelist_redef(nodelist):
    # only retrieve GUI components belong to target pkg
    # and only interested attributes enough to figure out the unique one
    nodelist_new = []
    flag = True
    #tmpi = []
    for i in range(len(nodelist)):
        node = nodelist[i]
        if flag and node.getAttribute('text'):
            print "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTOPIC"
            print node.getAttribute('text')
            flag = False

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

def window_nodes_map(current_window, nodelist):
    window = []
    tmp = 0
    for i in current_window:
        nodeful = nodelist[tmp]
        [node, j] = is_sub_node(nodeful, shown_clickable_details)
        if node != -1:
            node_index = shown_clickable_details.index(j)
            shown_clickable_details[node_index] = nodeful
            if shown_clickable_width[node_index] > 0:
                window.append(node_index)
        else:
            shown_clickable.append(i)
            shown_clickable_width.append(1)
            shown_clickable_details.append(nodelist[tmp])
            window.append(len(shown_clickable) - 1)
        tmp += 1
    return window

def is_common_node(node1, node2):
    node1 = [node1[0], node1[1], node1[2], node1[3], node1[6]]
    node2 = [node2[0], node2[1], node2[2], node2[3], node2[6]]
    if difflib.SequenceMatcher(None, str(node1), str(node2)).ratio() > 0.95:
        return True

def is_sub_node(node, nodelist):
    for i in nodelist:
        if is_common_node(node, i):
            return [node, i]
    return [-1, -1]

def is_new_window(nodelist):
    global window_visited, window_parent, same_window_counter
    current_window = nodelist_judge_redef(nodelist)
    tmp = hash_window(current_window)
    window = window_nodes_map(current_window, nodelist)
    if not window_visited:
        window_visited.append(tmp)
        window_parent.append(-1)
        return [0, window]
    # return the width
    if tmp not in window_visited:
        for j in window_visited_details:
            print difflib.SequenceMatcher(None, str(nodelist), str(j)).ratio()
            if difflib.SequenceMatcher(None, str(nodelist), str(j)).ratio() > 0.5:
                print 'gotTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT you!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
                same_window_counter += 1
                tmpindex = window_visited_details.index(j)
                newwindow = []
                for k in window:
                    node = shown_clickable_details[k]
                    if is_sub_node(node, j) != [-1, -1]:
                        newwindow.append(k)
                if not newwindow:
                    print window
                    print nodelist
                    print j
                    exit(1)
                return [window_parent[tmpindex], newwindow]
        same_window_counter = 0
        prinode = clicked_seq[len(clicked_seq) - 1]
        print prinode
        if prinode != -1:
            if prinode not in window_parent:
                shown_clickable_width[prinode] = len(window)
                print '++++++'
                print len(window)
                print '++++++'
                window_visited.append(tmp)
                window_parent.append(prinode)
                window_visited_details.append(nodelist)
                print 'NEEEEEEEEEEEEEEEEEEEEEEEW WINDDDDDDDDDDDDDDDDDDDOW'

        return [prinode, window]
    else:
        same_window_counter += 1
        tmpindex = window_visited.index(tmp)
        return [window_parent[tmpindex], window]


def check_clicked():
    # dump ui hierarchy into a xml file and extract info from it
    ISOTIMEFORMAT = '%m%d-%H-%M-%S'
    global clicked_list, clicked_seq, clicked_list_width
    global current_time, nodelist

    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump("./data/" + current_time + "hierarchy.xml")
    # dev.screenshot("./data/" + current_time + ".png")
    dom = xml.dom.minidom.parse("./data/" + current_time + "hierarchy.xml")

    # retrieve xml elements
    root = dom.documentElement
    nodelist = root.getElementsByTagName('node')
    nodelist = nodelist_redef(nodelist)

    # num of nodes at new window is the width of the parent node
    [parent, window] = is_new_window(nodelist)
    print window
    #print 'parent'
    #print parent
    #print ' .........'

    print shown_clickable_width

    if not window_visited:
        print 'ffffffffffffffffffffffffffff'
        return True
    if not window or same_window_counter > 30:
        clicked_seq.append(-1)
        dev.press.back()
        global back_counter
        print "back2"
        back_counter += 1
        return False
    for i in window:
        if parent:
            shown_clickable_width[parent] -= 1
        if clicked_seq != [] and i == clicked_seq[len(clicked_seq) - 1]:
            shown_clickable_width[i] = 0
            continue
        clicked_seq.append(i)
        shown_clickable_width[i] -= 1
        ui_interaction(shown_clickable_details[i])
        return True
    if parent > 0:
            shown_clickable_width[parent] = 0




def ui_interaction(node):
    arg = get_selector_attributes(node)
    if not dev(**arg).exists:
        print 'not found'
        return
    cmd = 'CLICK'
    print arg
    CMD_MAP[cmd](dev, arg)
    print 'click ' + node[0] + ' at ' + current_time


package = 'com.google.android.deskclock'
#package = 'com.android.dialer'
#package = 'com.android.settings'
#package = 'com.android.deskclock'
shown_clickable = []
shown_clickable_details = []
clicked_seq = []
back_counter = 0
shown_clickable_width = []
window_visited = [] # save the hash
window_visited_details = [] # save the nodes it contained
window_parent = [] # parent node of the window
tic = time.clock()
same_window_counter = 0
# per activity (not necessary a new activity, new updated window is enough)
while check_clicked() or back_counter <= 15:
    toc = time.clock()
    #if clicked_seq[len(clicked_seq) - 1] == -1:

    #print toc - tic
    tic = time.clock()

    pass
    #ui_interaction()
