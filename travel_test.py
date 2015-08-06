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
from datetime import datetime
import logging

# basic uiautomator commands
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

# retrive the details of the button and its child
def BFS_clickable(node, node_dict):
        global menu_flag, press_menu
        [node_attri, value] = redef_node(node, False)
        node_dict['node_attri'] += node_attri
        # when encounter menu button
        if menu_pattern.match(node_attri[1]):  # == 'More options':
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
            #if isinstance(node_attri1[i], float):
            if i > 0 and i % 6 == 4:
                #if difflib.SequenceMatcher(None, str(node_attri1[4]),
                 #                          str(node_attri2[4])).ratio() < 0.85:
                if isinstance(node_attri1, list) and (abs(node_attri1[i][0][0] - node_attri2[i][0][0]) > 5
                        or abs(node_attri1[i][1][0] - node_attri2[i][1][0]) > 5
                        or abs(node_attri1[i][0][1] - node_attri2[i][0][1]) > 5
                        or abs(node_attri1[i][1][1] - node_attri2[i][1][1]) > 5):
                        error += 1
                        continue
            #if difflib.SequenceMatcher(None, str(node_attri1[i]).encode('ascii', 'replace'), str(node_attri2[i]).encode('ascii', 'replace')).ratio() < 0.5:
            if node_attri1[i] != node_attri2[i]:
                error += 1
                if i == 3 or i == 2:
                    error += 1
        #print 1 - float(error) / float(node_dict2['value'])
        #print node_attri1
        #print node_attri2
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

# depth-first search in xml
def DFS_xml(node, nodelist, window, node_clk):
    global parent_width, newnode_counter, press_menu
    if node not in nodelist:
        if exit_pattern.match(node.getAttribute('text')):
            return
        if register_pattern.match(node.getAttribute('text')):
            logger.info('REGISTER FOUND HERE >>>>>>>>>>>')
        nodelist.append(node)
        if menu_pattern.match(node.getAttribute('resourceId')):
            press_menu = False
        # if meat pop that ask for exit
        if last_is_back > 2:
            if node.getAttribute('text') == 'OK' and node.getAttribute('clickable') == 'true':
                dev(text='OK').click()
        for i in node.childNodes:
            DFS_xml(i, nodelist, window, node_clk)
        if node.getAttribute('clickable') == 'true'\
                and node.getAttribute('package') == package:
            node_dict = travel_clickable(node)
            if node_dict['value'] == -1:
                return
            [index, before] = is_shown_before(node_dict)
            #print node_dict['node_attri'][4]
            #print last_xy
            if circle_flag and node_dict['node_attri'][4] == last_xy:
                # when click same button at third times, set its with as 0
                logger.info('PRIOR AGAIN>>>>>>>>>>>>>>>>>>>>')
                shown_clickable[index]['width'] = 0
            window.append(index)
            if not before:
                logger.info('NEWWWWWWWWWWWWWWWWNODE')
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
                        #upwards to all ancestors, add one width
                        #parent_index = clk_seq[len(clk_seq) - counter]
                        parent_index = parent['parent']
                        parent = shown_clickable[parent_index]
                        if parent_index > 0:
                            parent['width'] += 1
                        counter += 1
                        if len(clk_seq) - counter < 0:
                            break

            if node_dict['width'] > 0:
                # simply detect circles
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
                            # if detect two buttons concat together
                            if tmp[tmp.index((-2)) + 1] == -1:
                                logger.info('CCCCCCCCCCCCCCCCCCCIRCCCCCCCCCCCCCClEHHHHHH')
                                return
                        if tmp.index(-1) + 1 < len(tmp):
                            tmp2 = tmp[tmp.index(-1) + 1]
                        if tmp1 != -3 and tmp2 != -3:
                            if tmp1 != tmp2:
                                node_clk['node'] = node
                                node_clk['index'] = index
                                node_clk['node_attri'] = node_dict['node_attri']
                            else:
                                logger.info('CCCCCCCCCCCCCCCCCCCIRCCCCCCCCCCCCCClE')
                        else:
                            node_clk['node'] = node
                            node_clk['index'] = index
                            node_clk['node_attri'] = node_dict['node_attri']
                    #if circlecounter < 2:
                    else:
                        node_clk['node'] = node
                        node_clk['index'] = index
                        node_clk['node_attri'] = node_dict['node_attri']
                    # or 3 times shown in total 8 times


def is_same_window(window1, window2):
    if difflib.SequenceMatcher(None, str(window1), str(window2)).ratio() > 0.9:
        return True

def handle_window():
    #dev.wait.idle()
    global clk_seq, back_counter, parent_width, newnode_counter
    global menu_index, menu_flag, last_is_back
    current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    dev.dump(dir_data + current_time + "hierarchy.xml")
    dev.screenshot(dir_data + current_time + ".png")
    logger.info('screen shot at ' + current_time)
    dom = xml.dom.minidom.parse(dir_data + current_time + "hierarchy.xml")
    root = dom.documentElement
    nodelist = []
    node_clk = {'node': None, 'index': -1, 'node_attri': {}}
    window = []
    parent_width = 0
    newnode_counter = 0
    menu_flag = False
    DFS_xml(root, nodelist, window, node_clk)
    if newnode_counter > 3:
        #if is a new window
        if menu_flag:
        # and meet with menu again
            logger.info('MENU FOUND>>>>>>>>>>>>>')
            if shown_clickable[menu_index]['width'] == 0:
                shown_clickable[menu_index]['width'] += 1
                logger.info('MMMMMMMMMMMMMMMMMMMMMMMMMENU AGAINNNNNNNN')
    # print node_clk['index']
    #print window  # useful for debug...
    # print shown_clickable
    #print clk_seq   # useful for debug...

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
    # print node_clk['index']
    # priwindow = window
    if node_clk['index'] != -1:
        node = shown_clickable[node_clk['index']]
        ui_interaction(node_clk['node'], current_time)
        logger.info(node_clk['node_attri'])
        #print node_clk['index']
        #print node['node_attri']
        node['width'] -= 1
        if clk_seq:
            parent_index = node['parent']
            parent = shown_clickable[parent_index]
            parent['width'] -= 1
            while parent['parent']:
                parent_index = parent['parent']
                parent = shown_clickable[parent_index]
                parent['width'] -= 1
                #print 'just do it !!!!!!!!!!!!!! on '
                #print parent_index

        clk_seq.append(node_clk['index'])
        last_is_back -= 1
        if last_is_back < -15:
            dev.press.back()
            last_is_back = 1
        return True
    else:
        #clk_seq.append(-1)
        dev.press.back()
        logger.info('press back')
        if len(clk_seq):
            prinode_index = clk_seq[len(clk_seq) - 1]
            prinode = shown_clickable[prinode_index]
            prinode['width'] = 0
        back_counter += 1
        if last_is_back < 0:
            last_is_back = 0
        last_is_back += 1
        return False

def get_touch_attributes(node):
    global last_xy, circle_flag
    attributes = dict()
    node_bounds = node.getAttribute('bounds')
    node_bounds = node_bounds[1: len(node_bounds) - 1]
    node_bounds = node_bounds.split('][')
    node_bounds[0] = node_bounds[0].split(',')
    node_bounds[0] = map(float, node_bounds[0])
    node_bounds[1] = node_bounds[1].split(',')
    node_bounds[1] = map(float, node_bounds[1])
    #print node_bounds[0]
    if [node_bounds[0], node_bounds[1]] == last_xy:
        circle_flag = True
    last_xy = [node_bounds[0], node_bounds[1]]
    #print node_bounds[1]
    attributes['x'] = 0.5 * (node_bounds[1][0] - node_bounds[0][0]) + node_bounds[0][0]
    attributes['y'] = 0.5 * (node_bounds[1][1] - node_bounds[0][1]) + node_bounds[0][1]
    #print attributes['x']
    #print attributes['y']
    return attributes

def get_selector_attributes(node):
    attributes = dict()
    if node.getAttribute('text') != '':
        attributes['text'] = node.getAttribute('text')
    if node.getAttribute('content-desc') != '':
        attributes['description'] = node.getAttribute('content-desc')
    if node.getAttribute('class') != '':
        attributes['className'] = node.getAttribute('class')
    if node.getAttribute('resource-id') != '':
        attributes['resourceId'] = node.getAttribute('resource-id')
    attributes['index'] = node.getAttribute('index')
    return attributes

def ui_interaction(node_clk, current_time):
    arg = get_selector_attributes(node_clk)
    if not dev(**arg).exists:
        logger.info('not found')
        return
    #cmd = 'CLICK'
    logger.info(arg)
    # dev.wait.idle()
    if not dev(**arg).exists:
        logger.info('not found')
        return
    arg = get_touch_attributes(node_clk)
    cmd = 'TOUCH'
    CMD_MAP[cmd](dev, arg)
    logger.info('click ' + node_clk.getAttribute('resource-id') + ', ' + datetime.now().strftime('%H:%M:%S'))


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
#series = '014E233C1300800B'
series = '01b7006e13dd12a1'
#os.popen('rm -r -f data')
os.popen('mkdir data')
#package = 'com.google.android.deskclock'
#package = 'com.android.settings'
ISOTIMEFORMAT = '%m%d-%H-%M-%S'
filelist = os.listdir('.') # list files at current dir
# set threashold large to check behaviors underware
logger = logging.getLogger('UiDroid-Console')
logger.setLevel(logging.DEBUG)

consolehandler = logging.StreamHandler()
consolehandler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
consolehandler.setFormatter(formatter)


logger.addHandler(consolehandler)

logger.info(dev.info)
dev.screen.on()
menu_pattern = re.compile(r'.*(enu|ore).*') # if see any res-id contains menu
exit_pattern = re.compile(r'.*(xit|uit).*')
package_pattern = re.compile(r'.*apk')
register_pattern = re.compile(r'.*(Regis|REGIS|Sign|SIGN).*')


for fline in filelist:
    fmatch = package_pattern.match(fline)
    if not fmatch:
        continue
    os.popen('adb devices')
    before = appName()
    os.popen('adb -s ' + series +' install ' + fline)
    after = appName()
    applist = after - before
    if len(applist) != 1:
        logger.info(fline)
        logger.info(applist)
        logger.info('error! not a single app selected!')
        # break
        continue
    for package in applist:
        os.popen('adb -s ' + series + ' shell am start -n org.appanalysis/.TaintDroidNotifyController')
        current_time = time.strftime(ISOTIMEFORMAT, time.localtime())
        os.popen('adb -s ' + series + ' shell "su 0 date -s `date +%Y%m%d.%H%M%S`"')
        cmd = 'adb -s ' + series + ' shell /data/local/tcpdump -p -vv -s 0 -w /sdcard/' + package + current_time +'.pcap'
        subprocess.Popen(cmd, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, shell=True)
        logger.info('tcpdump begins')
        os.popen('adb logcat -c')
        logger.info('clear logcat')
        os.popen('adb -s ' + series + ' shell "logcat -v threadtime | grep --line-buffered UiDroid > /sdcard/' + package + current_time +'.log " &')
        logger.info('logcat start')
        os.popen('adb -s ' + series + ' shell monkey -p ' + package + ' --ignore-crashes 1')
        time.sleep(30)
        package_list = os.popen('adb -s ' + series + ' shell cat /data/system/packages.list')
        logger.info(package_list.readlines())
        ps_list = os.popen('adb -s ' + series + ' shell ps')
        logger.info(ps_list.readlines())
        shown_clickable = []  # all shown clickable widgets
        clk_seq = []  # save the clk sequence
        # window_list = [] # save the window context
        # samewindow = 0
        # priwindow = []
        parent_width = 0  # width of parent node
        back_counter = 0  # the number of total back pressed
        menu_index = -1  # the init index of menu button
        press_menu = True  # init set press menu as true
        last_is_back = 0  # if last op is back rathen than click
        last_xy = [0, 0]  # last clicked coordinate
        circle_flag = False  # if detect any circle in clk_seq
        dir_data = 'data/' + package + current_time + '/'
        os.popen('mkdir ' + dir_data)
        filehandler = logging.FileHandler(dir_data + '/UiDroid-Console.log')
        filehandler.setLevel(logging.DEBUG)
        logger.addHandler(filehandler)
        filehandler.setFormatter(formatter)

        while handle_window() or back_counter <= 50:
            time.sleep(5)
            # dev.wait.update()
            # suck = []
            # for i in shown_clickable:
            #     suck.append(i['width'])
            # print 'width:'
            # print suck
            # print menu_index
            if last_is_back == 2:
                press_menu = False
            if press_menu:
                logger.info('press menu')
                dev.press.menu()
            if last_is_back > 6:
                break
        time.sleep(60)
        package_list = os.popen('adb -s ' + series + ' shell cat /data/system/packages.list')
        logger.info(package_list.readlines())
        ps_list = os.popen('adb -s ' + series + ' shell ps')
        logger.info(ps_list.readlines())
        os.popen('adb -s ' + series + ' shell am force-stop ' + package)
        os.popen('adb -s ' + series + ' uninstall ' + package)
        logger.info('uninstall')
        os.popen('adb logcat -c')
        kill_status = os.popen('adb -s ' + series + ' shell ps | grep logcat | awk \'{print $2}\' | xargs adb -s ' + series + ' shell kill')
        logger.info(kill_status.readlines())
        kill_status = os.popen('adb -s ' + series + ' shell ps | grep tcpdump | awk \'{print $2}\' | xargs adb -s ' + series + ' shell kill')
        logger.info(kill_status.readlines())
        kill_status = os.popen('adb -s ' + series + ' shell am force-stop org.appanalysis')
        logger.info(kill_status.readlines())
        pull_status = os.popen('adb -s ' + series + ' pull /sdcard/' + package + current_time + '.pcap ' + dir_data)
        logger.info(pull_status.readlines())
        os.popen('adb -s ' + series + ' shell rm /sdcard/' + package + current_time + '.pcap')
        pull_status = os.popen('adb -s ' + series + ' pull /sdcard/' + package + current_time + '.log ' + dir_data)
        logger.info(pull_status.readlines())
        os.popen('adb -s ' + series + ' shell rm /sdcard/' + package + current_time + '.log')
        os.system('mv ' + fline + ' ' + dir_data)
