#!/usr/bin/python
# Software License Agreement (BSD License)
#
# Copyright (c) 2013, Juergen Sturm, TUM
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#  * Neither the name of TUM nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Requirements:
# sudo apt-get install python-argparse
"""
The Kinect provides the color and depth images in an un-synchronized way. This means that the set of time stamps from the color images do not intersect with those of the depth images. Therefore, we need some way of associating color images to depth images.
For this purpose, you can use the ''associate.py'' script. It reads the time stamps from the rgb.txt file and the depth.txt file, and joins them by finding the best matches.
"""

import argparse
import sys
import os
import numpy


def read_file_list(filename):
    """
    Reads a timestamped dataset from a text file.
    File format:
    The file format is "stamp d1 d2 d3 ...", where stamp denotes the time stamp (to be matched)
    and "d1 d2 d3.." is arbitary data (e.g., a 3D position and 3D orientation) associated to this timestamp. 
    Input:
    filename -- File name
    Output:
    dict -- dictionary of (stamp,data) tuples
    """
    file = open(filename)
    data = file.read()
    lines = data.replace(",", " ").replace("\t", " ").split("\n")
    list = [[v.strip()
             for v in line.split(" ")
             if v.strip() != ""]
            for line in lines
            if len(line) > 0 and line[0] != "#"]
    list = [(float(l[0]), l[1:]) for l in list if len(l) > 1]
    return dict(list)


def associate(first_list, second_list, offset, max_difference):
    """
    Associate two dictionaries of (stamp,data). As the time stamps never match exactly, we aim 
    to find the closest match for every input tuple.
    Input:
    first_list -- first dictionary of (stamp,data) tuples
    second_list -- second dictionary of (stamp,data) tuples
    offset -- time offset between both dictionaries (e.g., to model the delay between the sensors)
    max_difference -- search radius for candidate generation
    Output:
    matches -- list of matched tuples ((stamp1,data1),(stamp2,data2))
    """
    first_keys = list(first_list.keys())
    second_keys = list(second_list.keys())
    potential_matches = [(abs(a - (b + offset)), a, b)
                         for a in first_keys
                         for b in second_keys
                         if abs(a - (b + offset)) < max_difference]
    potential_matches.sort()
    matches = []
    for diff, a, b in potential_matches:
        if a in first_keys and b in second_keys:
            first_keys.remove(a)
            second_keys.remove(b)
            matches.append((a, b))

    matches.sort()
    return dict(matches)


def merge_associations(depth_dict, rgb_dict, gt_dict, depth_rgb_assoc,
                       depth_gt_assoc):
    lst_depth_rgb = []
    lst_depth_gt = []

    for ts in depth_rgb_assoc.keys():
        if ts in depth_gt_assoc.keys():
            ts_d = ts
            ts_rgb = depth_rgb_assoc[ts_d]
            ts_gt = depth_gt_assoc[ts_d]
            lst_depth_rgb.append(
                (ts_d, depth_dict[ts_d], ts_rgb, rgb_dict[ts_rgb]))
            lst_depth_gt.append((ts_d, depth_dict[ts_d], ts_gt, gt_dict[ts_gt]))

    return lst_depth_rgb, lst_depth_gt


if __name__ == '__main__':
    # parse command line
    parser = argparse.ArgumentParser(description='''
    This script takes two data files with timestamps and associates them   
    ''')
    parser.add_argument(
        'dataset',
        help=
        'path to the dataset containing rgb.txt, depth.txt, and groundtruth.txt'
    )
    parser.add_argument(
        '--offset',
        type=float,
        help='time offset added to the timestamps of the second file',
        default=0.0)
    parser.add_argument(
        '--max_difference',
        type=float,
        help='maximally allowed time difference for matching entries',
        default=0.02)
    args = parser.parse_args()

    # Lists to maps
    depth_dict = read_file_list(args.dataset + '/depth.txt')
    rgb_dict = read_file_list(args.dataset + '/rgb.txt')
    gt_dict = read_file_list(args.dataset + '/groundtruth.txt')

    # Maps to assocs
    depth_rgb_assoc = associate(depth_dict, rgb_dict, args.offset,
                                args.max_difference)
    depth_gt_assoc = associate(depth_dict, gt_dict, args.offset,
                               args.max_difference)
    lst_depth_rgb, lst_depth_gt = merge_associations(depth_dict, rgb_dict,
                                                     gt_dict, depth_rgb_assoc,
                                                     depth_gt_assoc)

    # Assocs to filelists and logs
    with open(args.dataset + '/assoc_depth_rgb.txt', 'w') as f:
        for ts_d, fname_d, ts_rgb, fname_rgb in lst_depth_rgb:
            f.write('{:.6f} {} {:.6f} {}\n'.format(ts_d, fname_d[0], ts_rgb,
                                                   fname_rgb[0]))
    with open(args.dataset + '/groundtruth_assoc_depth_rgb.txt', 'w') as f:
        f.write('# ground truth trajectory for associated depth and rgb\n')
        f.write('# dummy\n')
        f.write('# timestamp tx ty tz qx qy qz qw\n')
        for ts_d, fname_d, ts_gt, data_gt in lst_depth_gt:
            f.write('{:.6f} {}\n'.format(ts_gt, ' '.join(data_gt)))
