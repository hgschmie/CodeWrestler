#! /usr/bin/python

# ======================================================================
#
# Copyright 2005 Henning Schmiedehausen <henning@schmiedehausen.org>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you
# may not use this file except in compliance with the License.
#
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.
#
# ======================================================================

import os,sys
import getopt, re

from util.CallbackType import CallbackType
from util.Pattern import Pattern
from util.CommentSplitter import CommentSplitter, CommentPart
from util.File import load

def getCallback(cw=None):
    return CheckLicense(cw)

class CheckLicense(CallbackType):
    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

        self.pattern = Pattern()
        self.cw = cw

        try:
            opts, args = getopt.getopt(cw.module_options, "f:ht:", ["file=", "help", "type="])
        except getopt.GetoptError:
            self.usage()
            raise ValueError("Parameter Error")

        filename = None
        type = "text"

        for option, value in opts:
            if option in ("-h", "--help"):
                self.usage()
                raise ValueError("Parameter Error")
            elif option in ("-f", "--file"):
                filename = value
                continue
            elif option in ("-t", "--type"):
                type = value
                continue

        if filename is None:
            raise ValueError("You must supply a license file name")

        if not os.path.isabs(filename):
            filename = os.path.join(self.cw.dirtree, filename)

        if self.cw.verbose:
            print "License file is at %s" % filename

        self.license = CommentPart(self.pattern.getDefinition(type), load(filename))

        if len(self.license) == 0:
            raise ValueError("License file is empty or could not be read")


    def usage(self):
        print "Usage: license.CheckLicense"
        print "-h, --help:          Show this help"
        print ""
        print "-f, --file:          The license file to check. If name is not absolute,"
        print "                     check relative to the working directory"
        print "-t, --type:          Type of the license file. Default is text. If you want"
        print "                     to use e.g. a checkstyle-license file, you may need 'java'"


    def callback(self, root=None, file=None, type=None):

        definition = self.pattern.getDefinition(type)
        # types that have no openComment have no comment
        # syntax at all. Therefore it is useless to check for
        # a license.
        if definition.openComment is None:
            return

        fullfile = os.path.join(root, file)

        if self.cw.verbose:
            print "Checking License for %s (%s)" % (file, type)

        lines = load(fullfile)

        if self.cw.verbose:
            print "%s has %d lines" % (file, len(lines))

        commentSplitter = CommentSplitter(self.pattern.getDefinition(type))
        elementList = commentSplitter.parse(lines)

        if self.cw.verbose:
            print "%s has %d blocks" % (file, len(elementList))

        commentBlock = None
        for block in elementList:
            if isinstance(block, CommentPart):
                commentBlock = block
                break
        else:
            print "%s: No comment block found! (No copyright notice either!)" % fullfile
            return


        if len(commentBlock) != len(self.license):
            print "%s: line numbers don't match: %d vs. %d lines" % (fullfile, len(commentBlock), len(self.license))
            return

        space = re.compile("^\s+$")
        for i in range(0, len(commentBlock)):
            patt = re.compile("^(.*?)" + re.escape(self.license[i]) + "(.*?)$")
            match = patt.search(commentBlock[i])
            if match:
                if match.group(1) and not space.search(match.group(1)):
                    print "%s: line %d has leading text: %s" % (fullfile, i + 1, match.group(1))
                if match.group(2) and not space.search(match.group(2)):
                    print "%s: line %d has trailing text: %s" % (fullfile, i + 1, match.group(2))
            else:
                print "%s: line %d does not match" % (fullfile, i + 1)
