#!/usr/bin/python

import re
import subprocess


def scanner():

    p_output = subprocess.Popen('sudo iwlist wlan0 scan', shell = True, stdout = subprocess.PIPE)
    iwlist_stdout, iwlist_stderr = p_output.communicate()

    cell_dict = {}

    BSS_REGEX = re.compile('\s*Cell [0-9]+ - Address: (?P<bss>[0-9a-f:]{17})', re.IGNORECASE)
    QLY_REGEX = re.compile('\s*Quality=(?P<qval>[0-9]+)/(?P<qmax>[0-9]+)\s*Signal level=(?P<dbm>[0-9-]+) dBm', re.IGNORECASE)
    ESS_REGEX = re.compile('\s*ESSID:"(?P<name>.*)"', re.IGNORECASE)
    FRQ_REGEX = re.compile('\s*Frequency:(?P<Ghz>[0-9\.]{5})', re.IGNORECASE)
    CHN_REGEX = re.compile('\s*Channel:(?P<channel>[0-9])', re.IGNORECASE)

    current_bss = ""
    for line in iwlist_stdout.splitlines(True):
        match = BSS_REGEX.match(line)
        if match:
            current_bss = match.group('bss')
            cell_dict[current_bss] = {}
            continue

        match = QLY_REGEX.match(line)
        if match:
            cell_dict[current_bss]["quality"] = match.group("dbm")
            continue

        match = ESS_REGEX.match(line)
        if match:
            cell_dict[current_bss]["essid"] = match.group("name")
            continue

        match = FRQ_REGEX.match(line)
        if match:
            cell_dict[current_bss]["frequency"] = match.group("Ghz")
            continue

        match = CHN_REGEX.match(line)
        if match:
            cell_dict[current_bss]["Channel"] = match.group("channel")
            continue

    return cell_dict

