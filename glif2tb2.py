#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 2016 - Walter Bender <walter@sugarlabs.org>
# How to use: glif2tb2.py <glif-file>.glif <tb-file>.tb

# This script will mine a glif file for contours and export the
# results into a tb file compatible with Turtle Blocks JS. Each
# contour is saved as an individual stack. Each knot or control point
# is assigned a turtle.

import os
import re
import sys

XOFF = 200
YOFF = 400

def from_glif_to_tb(gliffile, tbfile):
    knotpoints = []
    controlpoint1s = []
    controlpoint2s = []

    gliffd = open(gliffile, "r")
    tbfd = open(tbfile, "w")

    block_count = 0
    contour_count = 0
    save_first_xy = False
    first_point_is_a_curve = False
    control_point = 0;
    #
    tbfd.write('[')

    for line in gliffd:
        parts = line.split()
        if parts[0] == '<contour>':
            print ('new contour %d' % contour_count)
            # output a new action block and label
            tbfd.write('[%d,["action",{"collapsed":false}],%d,200,[null,%d,%d,null]],' % (
                block_count, contour_count * 200 + 100, block_count + 1, block_count + 2))
            tbfd.write('[%d,["text",{"value":"contour%d"}],0,0,[%d]],' % (
                block_count + 1, contour_count, block_count))
            # raise pen
            tbfd.write('[%d,["penup",{}],0,0,[%d,%d]],' % (
                block_count + 2, block_count, block_count + 3))
            block_count += 3
            save_first_xy = True
            # increment the contour_count
            contour_count += 1
        elif parts[0] == '</contour>':
            # Write out savex, savey
            if first_point_is_a_curve:
                # What are the control points for this curve?
                print (":bezier %d %d" % (
                    block_count, block_count - 5))
                tbfd.write('[%d,["bezier",{}],0,0,[%d,%d,%d,null]],' % (
                    block_count, block_count - 5,
                    block_count + 1, block_count + 3))
            else:
                print (":setxy %d %d" % (
                    block_count, block_count - 5))
                tbfd.write('[%d,["setxy",{}],0,0,[%d,%d,%d,null]],' % (
                    block_count, block_count - 5,
                    block_count + 1, block_count + 3))
            tbfd.write('[%d,"xturtle",0,0,[%d,%d]],' % (
                block_count + 1, block_count, block_count + 2))
            tbfd.write('[%d,["text",{"value":"knotpoint%d"}],0,0,[%d]],' % (
                block_count + 2, len(knotpoints), block_count + 1))
            tbfd.write('[%d,"yturtle",0,0,[%d,%d]],' % (
                block_count + 3, block_count, block_count + 4))
            tbfd.write('[%d,["text",{"value":"knotpoint%d"}],0,0,[%d]],' % (
                block_count + 4, len(knotpoints), block_count + 3))
            knotpoints.append([savex, savey])
            block_count += 5
        elif parts[0] == '<point':
            # It is either type line, type curve, or just a control point.
            # In every case we need the x, y values
            x = int(parts[1][3:-1]) - XOFF
            if len(parts) == 3:
                y = int(parts[2][3:-3]) - YOFF
                # It is a control point, but which one?
                if control_point == 0:
                    print (".controlpoint1 %d %d" % (
                        block_count, block_count - 5 + delta))
                    tbfd.write('[%d,["controlpoint1",{}],0,0,[%d,%d,%d,%d]],'\
                               % (block_count, block_count - 5 + delta,
                                  block_count + 1, block_count + 3,
                                  block_count + 5))
                    tbfd.write('[%d,"xturtle",0,0,[%d,%d]],' % (
                        block_count + 1, block_count, block_count + 2))
                    tbfd.write(
                        '[%d,["text",{"value":"controlpoint1%d"}],0,0,[%d]],'\
                        % (
                        block_count + 2, len(controlpoint1s), block_count + 1))
                    tbfd.write('[%d,"yturtle",0,0,[%d,%d]],' % (
                        block_count + 3, block_count, block_count + 4))
                    tbfd.write(
                        '[%d,["text",{"value":"controlpoint1%d"}],0,0,[%d]],'\
                        % (
                        block_count + 4, len(controlpoint1s), block_count + 3))
                else:
                    print (".controlpoint2 %d %d" % (
                        block_count, block_count - 5 + delta))
                    tbfd.write('[%d,["controlpoint2",{}],0,0,[%d,%d,%d,%d]],'\
                               % (block_count, block_count - 5 + delta,
                                  block_count + 1, block_count + 3,
                                  block_count + 5))
                    tbfd.write('[%d,"xturtle",0,0,[%d,%d]],' % (
                        block_count + 1, block_count, block_count + 2))
                    tbfd.write(
                        '[%d,["text",{"value":"controlpoint2%d"}],0,0,[%d]],'\
                        % (
                        block_count + 2, len(controlpoint2s), block_count + 1))
                    tbfd.write('[%d,"yturtle",0,0,[%d,%d]],' % (
                        block_count + 3, block_count, block_count + 4))
                    tbfd.write(
                        '[%d,["text",{"value":"controlpoint2%d"}],0,0,[%d]],'\
                        % (
                        block_count + 4, len(controlpoint2s), block_count + 3))
                if control_point == 0:
                    controlpoint1s.append([x, y])
                else:
                    controlpoint2s.append([x, y])
                control_point = 1 - control_point
                block_count += 5
            else:
                y = int(parts[2][3:-1]) - YOFF
                if save_first_xy:
                    if parts[3] == 'type="curve"' or \
                       parts[3] == 'type="curve"/>':
                        first_point_is_a_curve = True
                    else:
                        first_point_is_a_curve = False
                    print (">setxy %d %d" % (
                        block_count, block_count - 1))
                    tbfd.write('[%d,["setxy",{}],0,0,[%d,%d,%d,%d]],' % (
                        block_count, block_count - 1,
                        block_count + 1, block_count + 3,
                        block_count + 5))
                elif parts[3] == 'type="curve"' or \
                     parts[3] == 'type="curve"/>':
                    print (".bezier %d %d" % (
                        block_count, block_count - 5 + delta))
                    tbfd.write('[%d,["bezier",{}],0,0,[%d,%d,%d,%d]],' % (
                        block_count, block_count - 5 + delta,
                        block_count + 1, block_count + 3,
                        block_count + 5))
                else:
                    print (".setxy %d %d" % (
                        block_count, block_count - 5 + delta))
                    tbfd.write('[%d,["setxy",{}],0,0,[%d,%d,%d,%d]],' % (
                        block_count, block_count - 5 + delta,
                        block_count + 1, block_count + 3,
                        block_count + 5))
                # We need to write out x,y regardless.
                tbfd.write('[%d,"xturtle",0,0,[%d,%d]],' % (
                    block_count + 1, block_count, block_count + 2))
                tbfd.write('[%d,["text",{"value":"knotpoint%d"}],0,0,[%d]],'\
                           % (
                    block_count + 2, len(knotpoints), block_count + 1))
                tbfd.write('[%d,"yturtle",0,0,[%d,%d]],' % (
                    block_count + 3, block_count, block_count + 4))
                tbfd.write('[%d,["text",{"value":"knotpoint%d"}],0,0,[%d]],'\
                           % (
                    block_count + 4, len(knotpoints), block_count + 3))
                block_count += 5
                knotpoints.append([x, y])

            if save_first_xy:
                savex = x
                savey = y
                save_first_xy = False

                # lower pen
                tbfd.write('[%d,["pendown",{}],0,0,[%d,%d]],' % (
                    block_count, block_count - 5, block_count + 1))
                block_count += 1
                delta = 4
            else:
                delta = 0
            print delta

    for i in range(len(knotpoints)):
        tbfd.write('[%d,["start",{}],0,0,[null,%d,null]],' % (
            block_count, block_count + 1))
        tbfd.write('[%d,"setturtlename",0,0,[%d,%d,%d,%d]],' % (
            block_count + 1, block_count, block_count + 2, block_count + 3,
            block_count + 4))
        tbfd.write('[%d,"turtlename",0,0,[%d]],' % (
            block_count + 2, block_count + 1))
        tbfd.write('[%d,["text",{"value":"knotpoint%d"}],0,0,[%d]],' % (
            block_count + 3, i, block_count + 1))
        tbfd.write('[%d,"turtleshell",0,0,[%d,%d,%d,%d]],' % (
            block_count + 4, block_count + 1, block_count + 5, block_count + 6,
            block_count + 7))
        tbfd.write('[%d,["number",{"value":20}],0,0,[%d]],' % (
            block_count + 5, block_count + 4))
        tbfd.write('[%d,["text",{"value":"http://people.sugarlabs.org/walter/images/square.svg"}],0,0,[%d]],' % (
            block_count + 6, block_count + 4))
        tbfd.write('[%d,"penup",0,0,[%d,%d]],' % (
            block_count + 7, block_count + 4, block_count + 8))
        tbfd.write('[%d,"setxy",0,0,[%d,%d,%d,null]],' % (
            block_count + 8, block_count + 7, block_count + 9, block_count + 10
            ))
        tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
            block_count + 9, knotpoints[i][0], block_count + 8))
        tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
            block_count + 10, knotpoints[i][1], block_count + 8))
        block_count += 11

    for i in range(len(controlpoint1s)):
        tbfd.write('[%d,["start",{}],0,0,[null,%d,null]],' % (
            block_count, block_count + 1))
        tbfd.write('[%d,"setturtlename",0,0,[%d,%d,%d,%d]],' % (
            block_count + 1, block_count, block_count + 2, block_count + 3,
            block_count + 4))
        tbfd.write('[%d,"turtlename",0,0,[%d]],' % (
            block_count + 2, block_count + 1))
        tbfd.write('[%d,["text",{"value":"controlpoint1%d"}],0,0,[%d]],' % (
            block_count + 3, i, block_count + 1))
        tbfd.write('[%d,"turtleshell",0,0,[%d,%d,%d,%d]],' % (
            block_count + 4, block_count + 1, block_count + 5, block_count + 6,
            block_count + 7))
        tbfd.write('[%d,["number",{"value":20}],0,0,[%d]],' % (
            block_count + 5, block_count + 4))
        tbfd.write('[%d,["text",{"value":"http://people.sugarlabs.org/walter/images/circle.svg"}],0,0,[%d]],' % (
            block_count + 6, block_count + 4))
        tbfd.write('[%d,"penup",0,0,[%d,%d]],' % (
            block_count + 7, block_count + 4, block_count + 8))
        tbfd.write('[%d,"setxy",0,0,[%d,%d,%d,null]],' % (
            block_count + 8, block_count + 7, block_count + 9, block_count + 10
            ))
        tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
            block_count + 9, controlpoint1s[i][0], block_count + 8))
        tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
            block_count + 10, controlpoint1s[i][1], block_count + 8))
        block_count += 11

    for i in range(len(controlpoint2s)):
        tbfd.write('[%d,["start",{}],0,0,[null,%d,null]],' % (
            block_count, block_count + 1))
        tbfd.write('[%d,"setturtlename",0,0,[%d,%d,%d,%d]],' % (
            block_count + 1, block_count, block_count + 2, block_count + 3,
            block_count + 4))
        tbfd.write('[%d,"turtlename",0,0,[%d]],' % (
            block_count + 2, block_count + 1))
        tbfd.write('[%d,["text",{"value":"controlpoint2%d"}],0,0,[%d]],' % (
            block_count + 3, i, block_count + 1))
        tbfd.write('[%d,"turtleshell",0,0,[%d,%d,%d,%d]],' % (
            block_count + 4, block_count + 1, block_count + 5, block_count + 6,
            block_count + 7))
        tbfd.write('[%d,["number",{"value":20}],0,0,[%d]],' % (
            block_count + 5, block_count + 4))
        tbfd.write('[%d,["text",{"value":"http://people.sugarlabs.org/walter/images/circle.svg"}],0,0,[%d]],' % (
            block_count + 6, block_count + 4))
        tbfd.write('[%d,"penup",0,0,[%d,%d]],' % (
            block_count + 7, block_count + 4, block_count + 8))
        tbfd.write('[%d,"setxy",0,0,[%d,%d,%d,null]],' % (
            block_count + 8, block_count + 7, block_count + 9, block_count + 10
            ))
        tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
            block_count + 9, controlpoint2s[i][0], block_count + 8))
        if i == len(controlpoint2s) - 1:
            tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]]' % (
                block_count + 10, controlpoint2s[i][1], block_count + 8))
        else:
            tbfd.write('[%d,["number",{"value":%d}],0,0,[%d]],' % (
                block_count + 10, controlpoint2s[i][1], block_count + 8))
        block_count += 11

    tbfd.write(']')

    gliffd.close()
    tbfd.close()


if __name__ == '__main__':
    ini = from_glif_to_tb(sys.argv[1], sys.argv[2])
