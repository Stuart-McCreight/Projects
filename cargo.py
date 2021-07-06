#!/usr/bin/env python3
import json
import os
import sys
import struct
import binascii
from struct import *
from ctypes import create_string_buffer
import functools
import collections
from collections import OrderedDict
import argparse
import subprocess
import shlex
from pprint import pprint
import sys
import argparse
import avg_sketch
import math
import statistics

#User input to specify bucket, file to download, and filename to write to
parser = argparse.ArgumentParser()
parser.add_argument('-b', '--bucket', dest = 'bucket', type = str, nargs = 1, help = "Bucket to extract from")
parser.add_argument('-s', '--sample', dest = 'sample', type = int, nargs = 1, help = "Fetch a random sample of n files from a bucket to process")
parser.add_argument('-d', '--download', dest = 'download', type = str, nargs = '*', help = "Specify files to download and decompress (requires .bz2 extension)")
parser.add_argument('-l', '--stored_locally', dest = 'local', type = str, nargs = '*', help = "Process local sketch files")
parser.add_argument('-v', '--volumetrics', action = 'store_true', help = "Download entire sketch file for volumetrics analysis")
parser.add_argument('-lsk2', '--lsk2', action = 'store_true', help = "Locally stored files are entire sk2 files")
#parser.add_argument('-t', '--tiny_sections', action = 'store_true', help = "Show every populated section, even those with portions approaching zero")
parser.add_argument('-a', '--average', action = 'store_true', help = "Return the average section size accross all processed sketch files")
parser.add_argument('-sd', '--standard_dev', action = 'store_true', help = "Return the standard deviation of each section")
args = parser.parse_args()

check = 0

if args.sample:
    filename = []
    random = ("~/notos/apps/synk -b {} -1 | grep sketch.bz2 | shuf -n {} > filelist".format(args.bucket[0], args.sample[0]))
    subprocess.call(random, shell = True)
    file1 = open("filelist", 'r')
    lines = file1.readlines()

    if args.bucket[0] == "voreas-sketch-02" or args.volumetrics:
        check = 1
        for line in lines:
            store = line[:-5]
            filename.append(store)
            largs = ("aws s3api get-object --bucket {} --key {} /dev/stdout 2> /dev/null | lbunzip2 -c > {}".format(args.bucket[0], line.strip(), store))
            subprocess.call(largs, shell = True)

    else:
        for line in lines:
            store = line[:-5]
            filename.append(store)
            largs = ("aws s3api get-object --bucket {} --key {} /dev/stdout 2> /dev/null | lbunzip2 -c | head -c 1024 > {}".format(args.bucket[0], line.strip(), store))
            subprocess.call(largs, shell = True)

if args.download:
    filename = [w[:-4] for w in args.sketch]

    if args.bucket[0] == "voreas-sketch-02" or args.volumetrics:
        check = 1
        for i, args.download in enumerate(args.sketch):
            margs = ("aws s3api get-object --bucket {} --key {} /dev/stdout 2> /dev/null | lbunzip2 -c > {}".format(args.bucket[0], args.download, filename[i]))
            subprocess.call(margs, shell = True)
    else:
        for i, args.download in enumerate(args.sketch):
            margs = ("aws s3api get-object --bucket {} --key {} /dev/stdout 2> /dev/null | lbunzip2 -c | head -c 1024 > {}".format(args.bucket[0], args.download, filename[i]))
            subprocess.call(margs, shell = True)

if args.local:
    if args.volumetrics or args.lsk2:
         check = 1
    filename = args.local

all_res = []
all_header = []

for fname in filename:   
    patter = []
    header = []
    a = ["HEADER_OIDS" ,"HEADER_DOMAINS", "HEADER_XTRS", "HEADER_IPV6", "HEADER_CIDR4", "HEADER_CIDR6", "HEADER_ACTUARY", "HEADER_TRAFFIC", "HEADER_IPV4", 
         "HEADER_BLOBS", "HEADER_ETLDS", "HEADER_CHECKSUMS", "HEADER_PROCNAMES", "HEADER_MACS", "ASSOC_DOMAIN_NS", "ASSOC_NS_DOMAIN", "ASSOC_DOMAIN_XTR", 
         "ASSOC_DOMAIN_REC4", "ASSOC_REC4_DOMAIN", "ASSOC_DOMAIN_STUB4", "ASSOC_STUB4_DOMAIN", "ASSOC_DOMAIN_HOST4", "ASSOC_HOST4_DOMAIN", "ASSOC_NX_STUB4", 
         "ASSOC_STUB4_NX", "ASSOC_DOMAIN_ECS4", "ASSOC_ECS4_DOMAIN", "ASSOC_REC4_ECS4", "ASSOC_ECS4_REC4", "ASSOC_DOMAIN_REC6", "ASSOC_REC6_DOMAIN", 
         "ASSOC_DOMAIN_STUB6", "ASSOC_STUB6_DOMAIN", "ASSOC_DOMAIN_HOST6", "ASSOC_HOST6_DOMAIN", "ASSOC_NX_STUB6", "ASSOC_STUB6_NX", "ASSOC_DOMAIN_ECS6", 
         "ASSOC_ECS6_DOMAIN", "ASSOC_REC6_ECS6", "ASSOC_ECS6_REC6", "ASSOC_SRC4_DST4_CONN", "ASSOC_DST4_SRC4_CONN", "ASSOC_SRC4_DST4_FAIL", 
         "ASSOC_DST4_SRC4_FAIL", "ASSOC_SRC6_DST6_CONN", "ASSOC_DST6_SRC6_CONN", "ASSOC_SRC6_DST6_FAIL", "ASSOC_DST6_SRC6_FAIL", "ASSOC_DOMAIN_BLOB", 
         "ASSOC_IP4_BLOB", "ASSOC_IP6_BLOB", "ASSOC_LOCIP4_PROCSUM", "ASSOC_PROCSUM_LOCIP4", "ASSOC_LOCIP6_PROCSUM", "ASSOC_PROCSUM_LOCIP6", 
         "ASSOC_DOMAIN_PROCSUM", "ASSOC_PROCSUM_DOMAIN", "ASSOC_PROCSUM_PROCNAME", "ASSOC_PROCNAME_PROCSUM", "ASSOC_IP4_MAC", "ASSOC_MAC_IP4", 
         "ASSOC_IP6_MAC", "ASSOC_MAC_IP6", "ASSOC_STUB4_REC4", "ASSOC_REC4_STUB4", "ASSOC_STUB6_REC6", "ASSOC_REC6_STUB6"]
    sums = {}
    sk = OrderedDict()

    with open(fname, 'rb') as fp:
        for i in range(0,128):
            data = fp.read(8)
            offset = (struct.unpack(">Q", data))
            header.append(offset[0])
            patter = header[1:15] + header[20:35] + header[40:80]
            head_off = OrderedDict(zip(a, patter))

        if check == 1:
            size = os.path.getsize(fname)
        else:
            if header[127] > 0:
                size = header[127]
            else:
                set = max(patter)
                estimate = (min(set + set / 50 + 2 ** 28, set * 8))
                size = estimate                 

        for key in list(head_off.keys()):
            if head_off[key] == 0:
                del head_off[key] 

        sort = sorted(head_off.items(), key=lambda x: x[1])           
        position = []
        section = []

        for tup in sort:

            position.append(tup[1])
            section.append(tup[0])
            all_header.append(tup[0])

        if check == 1:           
            position.append(size)
        else:
           if header[127] > 0:
                position.append(header[127])
           else:
                position.append(estimate)

        portion = [position[i + 1] - position[i] for i in range(len(position)-1)]
        res = OrderedDict(zip(section, portion))
        sk[fname] = res

        pprint(fname)

        for result in sk.values():
           for key, val in result.items():
                sums[key] = sums.get(key, 0) + val / size

        for key, value in sums.items():
#            if args.tiny_sections:
            print (key, ":", "{:.2%}".format(value))
            all_res.append((key, "{:.50}".format(value)))
        
#                if args.tiny_sections is None:

#                if value > .001:

#                    print (key, ":", "{:.2%}".format(value))

#                    all_res.append((key, "{:.50}".format(value)))

        pprint("-------------------------------------------------------------------------------------") 


all_header = list(dict.fromkeys(all_header))
means = []

def average():

    print('Average Section Size')

    for head in all_header:
        sum_list = []
        for tup in all_res:
            if head == tup[0]:
                sum_list.append(tup[1])

        res_sum = sum(float(sub) for sub in sum_list)
        average = res_sum / len(sum_list)
        means.append((head, average))

        print (head, ":", "{:.2%}".format(average))
    print('---------------------------------------')



def std_dev():
    
    print('Standard Deviation')     

    for head in all_header:
        list = []
        for tup in all_res:
            if head == tup[0]:
                list.append(float(tup[1]))
                stdv = statistics.pstdev(list)

        print (head, ":", stdv)
    print('---------------------------------------')


if args.average:    
    average()

if args.standard_dev:
    std_dev()