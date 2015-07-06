#!/usr/bin/env python2
#-*-encoding:utf-8-*-

__author__ = 'hao'
from uiautomator import device as dev
import xml.dom.minidom
import os
import time
import difflib
import subprocess
import re

CMD_MAP = {
    'CLICK': lambda dev, arg: dev(**arg).click(),
    'TOUCH': lambda dev, arg: dev.click(**arg),
    'DRAG': lambda dev, arg: dev.drag(**arg),
    'PRESS': lambda dev, arg: dev.press(**arg),
    'WAIT': lambda dev, arg: dev.wait.update()  # wait until window update event occurs
    }

def redef_node(node, childFlag):
    node_text = node.getAttribute('text')
    node_resid = node.getAttribute('resource-id')
    node_class = node.getAttribute('class')
    node_contentdesc = node.getAttribute('content-desc')
    node_bounds = node.getAttribute('bounds')
    node_bounds = node_bounds[1: len(node_bounds) - 1]
    node_bounds = node_bounds.split('][')
    node_bounds[0] = node_bounds[0].split(',')
    node_bounds[0] = map(float, node_bounds[0])
    node_bounds[1] = node_bounds[1].split(',')
    node_bounds[1] = map(float, node_bounds[1])
    node_size = [node_bounds[0][0] - node_bounds[1][0],
                 node_bounds[0][1] - node_bounds[1][1]]
    node_clickable = node.getAttribute('clickable')
    if node_clickable == 'true' and childFlag:
        return [None, -1]

    node = [node_text, node_contentdesc,
            node_class, node_resid,
                    node_bounds, node_size]
    # add relative attributes
    value = 6
    return [node, value]

def BFS_clickable(node, node_dict):
        global menu_flag, press_menu
        [node_attri, value] = redef_node(node, False)
        node_dict['node_attri'] += node_attri
        if node_attri[1] == 'More options':
            press_menu = False
            menu_flag = True
        node_dict['value'] += value
        for i in node.childNodes:
            [node_attric, value] = redef_node(i, True)
            if value == -1:
                node_dict['node_attri'] = node_attri
                node_dict['value'] = -1
                return
            node_attric[4] = [[node_attri[4][0][0] - node_attric[4][0][0],
                              node_attri[4][0][1] - node_attric[4][0][1]],
                              [node_attri[4][1][0] - node_attric[4][1][0],
                              node_attri[4][1][1] - node_attric[4][1][1]]]
            node_dict['node_attri'] += node_attric
            node_dict['value'] += value

def is_same_node(node_dict1, node_dict2):
    if abs(node_dict1['value'] - node_dict2['value']) >= 6:
        return False
    else:
        error = 0
        node_attri1 = node_dict1['node_attri']
        node_attri2 = node_dict2['node_attri']
        for i in range(len(node_attri1)):
            if isinstance(node_attri1[i], float):
                if not isinstance(node_attri2[i], float):
                    error += 1
                    continue
                if abs(node_attri1[i][0] - node_attri2[i][0]) > 5 \
                        or abs(node_attri1[i][1] - node_attri2[i][1]) > 5:
                        error += 1
                        continue
            #if difflib.SequenceMatcher(None, str(node_attri1[i]).encode('ascii', 'replace'), str(node_attri2[i]).encode('ascii', 'replace')).ratio() < 0.5:
            if node_attri1[i] != node_attri2[i]:
                error += 1
        print 1 - float(error) / float(node_dict2['value'])
        print node_attri1
        print node_attri2
        if 1 - float(error) / float(node_dict2['value']) > 0.83:
            return True
        else:
            return False

def is_shown_before(node_dict):
    global menu_flag, menu_index
    for i in shown_clickable:
        if is_same_node(node_dict, i):
            node_dict['width'] = i['width']
            return [shown_clickable.index(i), True]
    shown_clickable.append(node_dict)
    if menu_flag and menu_index == -1:
        menu_index = len(shown_clickable) - 1
    return [len(shown_clickable) - 1, False]

def travel_clickable(node):
    node_dict = {'node_attri': [], 'value': 0, 'width': 1, 'parent': 0}
    BFS_clickable(node, node_dict)
    return node_dict

def DFS_xml(node, nodelist, window, node_clk):
    global parent_width, newnode_counter
    if node not in nodelist:
        nodelist.append(node)
        for i in node.childNodes:
            DFS_xml(i, nodelist, window, node_clk)
        if node.getAttribute('clickable') == 'true'\
                and node.getAttribute('package') == package:
            node_dict = travel_clickable(node)
            if node_dict['value'] == -1:
                return
            [index, before] = is_shown_before(node_dict)
            window.append(index)
            if not before:
                print 'NEWWWWWWWWWWWWWWWWNODE'
                newnode_counter += 1
                parent_width += 1
                counter = 2
                if len(clk_seq):
                    parent_index = clk_seq[len(clk_seq) - 1]
                    node_dict['parent'] = parent_index
                    parent = shown_clickable[parent_index]
                    if parent_index > 0:
                        parent['width'] += 1
                    #while parent['parent'] == clk_seq[len(clk_seq) - counter]:
                    while parent['parent']:
                        print 'just add it !!!!!!!!!!!!!! on'
                        #parent_index = clk_seq[len(clk_seq) - counter]
                        parent_index = parent['parent']
                        parent = shown_clickable[parent_index]
                        if parent_index > 0:
                            parent['width'] += 1
                        counter += 1
                        if len(clk_seq) - counter < 0:
                            break
            #print node_dict
            #print node.getAttribute('text')
            if node_dict['width'] > 0:
                #parent_width += 1
                # simple detect circles
                if node_clk['index'] == -1:
                    circlecounter = 0
                    if len(clk_seq) > 6:
                        tmp = []
                        for i in range(0, 5):
                            tmp.append(clk_seq[len(clk_seq) - i - 1])
                        while index in tmp:
                            tmp[tmp.index(index)] = -1
                            circlecounter += 1
                    if circlecounter > 1:
                        tmp1 = -3
                        tmp2 = -3
                        if tmp.index(-1) + 1 < len(tmp):
                            tmp1 = tmp[tmp.index(-1) + 1]
                            tmp[tmp.index(-1)] = -2
                            if tmp[tmp.index((-2)) + 1] == -1:
                                print 'CCCCCCCCCCCCCCCCCCCIRCCCCCCCCCCCCCClHHHHHH'
                                return
                        if tmp.index(-1) + 1 < len(tmp):
                            tmp2 = tmp[tmp.index(-1) + 1]
                        if tmp1 != -3 and tmp2 != -3:
                            if tmp1 != tmp2:
                                node_clk['node'] = node
                                node_clk['index'] = index
                            else:
                                print 'CCCCCCCCCCCCCCCCCCCIRCCCCCCCCCCCCCCl'
                        else:
                            node_clk['node'] = node
                            node_clk['index'] = index
                    #if circlecounter < 2:
                    else:
                        node_clk['node'] = node
                        node_clk['index'] = index
                    # or 3 times shown in total 8 times


def is_same_window(window1, window2):
    if difflib.SequenceMatcher(None, str(window1), str(window2)).ratio() > 0.9:
        return True

def handle_window():
    #dev.wait.idle()
    global clk_seq, back_counter, parent_width, newnode_counter
    global menu_index, menu_flag, last_is_back
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump("./data/" + current_time + "hierarchy.xml")
    dom = xml.dom.minidom.parse("./data/" + current_time + "hierarchy.xml")
    root = dom.documentElement
    nodelist = []
    node_clk = {'node': None, 'index': -1}
    window = []
    parent_width = 0
    newnode_counter = 0
    menu_flag = False
    DFS_xml(root, nodelist, window, node_clk)
    if newnode_counter > 3:
        #if press_menu:
         #   dev.press.menu()
        if menu_flag:
        # indicates new window
            print 'MENU FOUND>>>>>>>>>>>>>'
            if shown_clickable[menu_index]['width'] == 0:
                shown_clickable[menu_index]['width'] += 1
                print 'MMMMMMMMMMMMMMMMMMMMMMMMMENU AGAINNNNNNNN'

    #print node_clk['index']
    print window
    #print shown_clickable
    print clk_seq

    if len(clk_seq):
        prinode_index = clk_seq[len(clk_seq) - 1]
        prinode = shown_clickable[prinode_index]
        print parent_width

    # if not is_same_window(window, priwindow):
    #     flag = 0
    #     for i in window_list:
    #         if is_same_window(window, i):
    #             flag = 1
    #             break
    #     if flag == 0:
    #         window_list.append(window)
    # else:
    #     samewindow += 1
    #print node_clk['index']
    #priwindow = window
    if node_clk['index'] != -1:
        node = shown_clickable[node_clk['index']]
        ui_interaction(node_clk['node'], current_time)
        print node['node_attri']
        node['width'] -= 1
        if clk_seq:
            parent_index = node['parent']
            parent = shown_clickable[parent_index]
            parent['width'] -= 1
            while parent['parent']:
                parent_index = parent['parent']
                parent = shown_clickable[parent_index]
                parent['width'] -= 1
                print 'just do it !!!!!!!!!!!!!! on '
                print parent_index

        clk_seq.append(node_clk['index'])
        last_is_back -= 1
        if last_is_back < -15:
            dev.press.back()
            last_is_back = 1
        return True
    else:
        #clk_seq.append(-1)
        dev.press.back()
        print 'back'
        prinode['width'] = 0
        back_counter += 1
        last_is_back += 1
        return False

def get_touch_attributes(node):
    attributes = dict()
    node_bounds = node.getAttribute('bounds')
    node_bounds = node_bounds[1: len(node_bounds) - 1]
    node_bounds = node_bounds.split('][')
    node_bounds[0] = node_bounds[0].split(',')
    node_bounds[0] = map(float, node_bounds[0])
    node_bounds[1] = node_bounds[1].split(',')
    node_bounds[1] = map(float, node_bounds[1])
    print node_bounds[0]
    print node_bounds[1]
    attributes['x'] = 0.5 * (node_bounds[1][0] - node_bounds[0][0]) + node_bounds[0][0]
    attributes['y'] = 0.5 * (node_bounds[1][1] - node_bounds[0][1]) + node_bounds[0][1]
    print attributes['x']
    print attributes['y']
    return attributes

def get_selector_attributes(node):
    attributes = dict()
    if node.getAttribute('text') != '':
        attributes['text'] = node.getAttribute('text')
    #if node[1] != '':
        # print node[1]
        # attributes['description'] = node[1] # for clock, its description change frequently
    if node.getAttribute('content-desc') != '':
        attributes['description'] = node.getAttribute('content-desc')
    if node.getAttribute('class') != '':
        attributes['className'] = node.getAttribute('class')
    if node.getAttribute('resource-id') != '':
        attributes['resourceId'] = node.getAttribute('resource-id')
    # attributes['bounds'] = node[6]
    attributes['index'] = node.getAttribute('index')
    return attributes

def ui_interaction(node_clk, current_time):
    arg = get_selector_attributes(node_clk)
    if not dev(**arg).exists:
        print 'not found'
        return
    #cmd = 'CLICK'
    print arg
    dev.wait.idle()
    if not dev(**arg).exists:
        print 'not found'
        return
    arg = get_touch_attributes(node_clk)
    cmd = 'TOUCH'
    CMD_MAP[cmd](dev, arg)
    print 'click ' + node_clk.getAttribute('resource-id') + ' at ' + current_time

# 获取设备中的所有包名
def appName():
    cmd = 'adb -s ' + series + ' shell pm list packages'
    app_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, shell = True)
    #p = check_output(cmd, shell = True)
    app_process.wait()
    output = app_process.stdout.readlines()
    output = set(x.split(':')[1].strip() for x in output)
    return output

#series = 'emulator-5554'
series = '014E233C1300800B'
os.system('rm -r -f data')
os.system('mkdir data')
#package = 'com.google.android.deskclock'
#package = 'com.android.settings'
ISOTIMEFORMAT = '%m%d-%H-%M-%S'
filelist = os.listdir('.') # list files at current dir
# set threashold large to check behaviors underware
pattern = re.compile(r'.*apk')
for fline in filelist:
    match = pattern.match(fline)
    if not match:
        continue
    os.system('adb devices')
    before = appName()
    os.system('adb -s ' + series +' install ' + fline)
    after = appName()
    applist = after - before
    if len(applist) != 1:
        print fline
        print applist
        print 'error! not a single app selected!'
        # break
        continue
    for package in applist:
        os.system('adb -s ' + series +' shell monkey -p ' + package + ' --ignore-crashes 1')
        time.sleep(10)
        print dev.info
        dev.screen.on()
        shown_clickable = []
        clk_seq = []
        window_list = []
        samewindow = 0
        priwindow = []
        parent_width = 0
        back_counter = 0
        menu_index = -1
        press_menu = True
        last_is_back = 0
        while handle_window() and back_counter <= 100:
            time.sleep(1)
            suck = []
            for i in shown_clickable:
                suck.append(i['width'])
            print 'width:'
            print suck
            print menu_index
            if last_is_back == 2:
                press_menu = False
            if press_menu:
                print 'press menu'
                dev.press.menu()
        os.system('adb -s ' + series +' shell am force-stop ' + package)
        os.system('adb -s ' + series +' uninstall ' + package)
        print 'done uninstall'