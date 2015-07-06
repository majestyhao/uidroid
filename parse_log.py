__author__ = 'Hao Fu'

import datetime
import re

def diff_times_in_seconds(t1, t2):
    # caveat emptor - assumes t1 & t2 are python times, on the same day and t2 is after t1
    h1, m1, s1 = t1.hour, t1.minute, t1.second
    h2, m2, s2 = t2.hour, t2.minute, t2.second
    t1_secs = s1 + 60 * (m1 + 60 * h1)
    t2_secs = s2 + 60 * (m2 + 60 * h2)
    return t2_secs - t1_secs

def get_pid_uid():
    global pid, uid
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

perform_pattern = re.compile(r'.*?performButton.*?')
click_pattern = re.compile(r'.*?click.*?')
log_file = open('com.mylocaltv.wsmvdroid0623-18-43-17.log', 'r')
console_file = open('UiDroid-Console.log', 'r')
log_list = log_file.readlines()
console_list = console_file.readlines()
ps_pattern = re.compile(r'.*?USER     PID.*?')
pkg_list_pattern = re.compile(r'.*?\[\'com.*?')
pkg_name = 'com.mylocaltv.wsmvdroid'
pkg_name_pattern = re.compile(r'.*?' + pkg_name + '.*?')
check_uid_permi_pattern = re.compile(r'.*?checkUidPermission, uid=(.*?),.*?')
content_provider_pattern = re.compile(r'.*?ContentProvider.*?uid=(.*?)')
system_out_pattern = re.compile(r'.*?System.out.*?')
activity_manager_service_pattern = re.compile(r'.*?ActivityManagerService.*?')
contextimpl_pattern = re.compile('.*?UiDroid_ContextImpl.*?')
taint_pattern = re.compile('.*?Taint.*?')
broadcast_intent_pattern = re.compile(r'.*?broadcastIntent.*?')
activity_manager_native_pattern = re.compile('.*?ActivityManagerNative.*?')
package_manager_pattern = re.compile(r'.*?PackageManager.*?')


get_pid_uid()


for log_line in log_list:
    check_uid_permi_match = check_uid_permi_pattern.match(log_line)
    content_provider_pattern_match = content_provider_pattern.match(log_line)
    if check_uid_permi_match:
        tuid = check_uid_permi_match.group(0)
        if tuid == uid:
            print log_line
    elif package_manager_pattern.match(log_line):
        if re.search(pkg_name, log_line):
            print log_line
    elif activity_manager_native_pattern.match(log_line):
        if re.search(pid, log_line):
            print log_line
    elif broadcast_intent_pattern.match(log_line):
        if re.search(pkg_name, log_line):
            print log_line
    elif taint_pattern.match(log_line):
        if re.search(pkg_name, log_line):
            print log_line
    elif contextimpl_pattern.match(log_line):
        if re.search(pkg_name, log_line) or re.search(pid, log_line):
            print log_line
    elif activity_manager_service_pattern.match(log_line):
        if re.findall(pkg_name, log_line):
            print log_line
    elif system_out_pattern.match(log_line):
        # show access not-my-self dir access
        if re.findall(pid, log_line) and not re.search(pkg_name, log_line):
            print log_line
    elif content_provider_pattern_match:
        if re.search(uid, log_line):
            print log_line
    elif perform_pattern.match(log_line):
        log_line = log_line.split('   ')
        log_line_time = log_line[0].split(' ')[1]
        log_line_time = log_line_time.split('.')[0]
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>.>>'
        print log_line
        for line in console_list:
            if click_pattern.match(line):
                # "adb logcat -v threadtime" - Display the date, invocation time, priority, tag,
                #  and the PID and TID of the thread issuing the message.
                line = line.split('   ')
                line_time = line[0].split(' ')[1]
                line_time = line_time.split(',')[0]
                diff_time = diff_times_in_seconds(datetime.datetime.strptime(log_line_time, '%H:%M:%S').time(),
                                      datetime.datetime.strptime(line_time, '%H:%M:%S').time())
                if abs(diff_time) < 2:
                    #print line
                    print line
                    break
