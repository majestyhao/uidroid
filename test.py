#!/usr/bin/env python2
#-*-encoding:utf-8-*-
import re

__author__ = 'hao'
console_file = open('UiDroid-Console.log', 'r')
console_list = console_file.readlines()
ps_pattern = re.compile(r'.*?USER     PID.*?')
pkg_list_pattern = re.compile(r'.*?\[\'com.*?')
pkg_name = 'com.mylocaltv.wsmvdroid'
pkg_name_pattern = re.compile(r'.*?' + pkg_name + '.*?')
for line in console_list:
    if ps_pattern.match(line):
        line = line.split(',')
        for sub_ps in line:
            if pkg_name_pattern.match(sub_ps):
                pid = sub_ps.split('    ')[1]
                pid = pid.split(' ')[0]
                print sub_ps
                print pid
    elif pkg_list_pattern.match(line):
        line = line.split(',')
        for sub_pl in line:
            if pkg_name_pattern.match(sub_pl):
                uid = sub_pl.split(' ')[2]
                print sub_pl
                print uid
