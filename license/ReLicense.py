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
from util.LicenseType import LicenseType
from util.File import load, save

def getCallback(cw=None):
    return ReLicense(cw)

class ReLicense(CallbackType):
    """ Replaces existing licenses with a given license file and/or adds a license to files"""
    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

        self.pattern = Pattern()
        self.cw = cw

        try:
            opts, args = getopt.getopt(cw.module_options, "ef:hnt:", ["existing-only", "file=", "help", "new-only", "type="])
        except getopt.GetoptError:
            self.usage()
            raise ValueError("*** Parameter Error")

        filename = None
        type = "text"

        self.existingOnly = False
        self.newOnly = False

        for option, value in opts:
            if option in ("-h", "--help"):
                self.usage()
                raise ValueError("*** Parameter Error")
            elif option in ("-e", "--existing-only"):
                self.existingOnly = True
                continue
            elif option in ("-f", "--file"):
                filename = value
                continue
            elif option in ("-n", "--new-only"):
                self.newOnly = True
                continue
            elif option in ("-t", "--type"):
                type = value
                continue

        if filename is None:
            self.usage()
            raise ValueError("*** You must supply a license file name")

        if not self.existingOnly and not self.newOnly:
            self.usage()
            raise ValueError("*** No Action has been selected!")

        if not os.path.isabs(filename):
            filename = os.path.join(self.cw.dirtree, filename)

        if self.cw.verbose:
            print "License file is at %s" % filename

        self.license = CommentPart(self.pattern.getDefinition(type), load(filename))

        if len(self.license) == 0:
            raise ValueError("License file is empty or could not be read")


    def usage(self):
        print "Usage: license.ReLicense"
        print ""
        print "The following parameters must be supplied using the \"--modopts\" option"
        print "of the main program:"
        print ""
        print "-h, --help:          Show this help"
        print ""
        print "-e, --existing-only: Replace only existing licenses. If a file has no"
        print "                     license, don't touch it"
        print "-n, --new-only:      Only add licenses to a file which does not already"
        print "                     has one"
        print "-f, --file:          The license file to check. If name is not absolute,"
        print "                     check relative to the working directory"
        print "-t, --type:          Type of the license file. Default is text. If you want"
        print "                     to use e.g. a checkstyle-license file, you may need 'java'"
        print ""

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

        commentSplitter = CommentSplitter(definition)
        elementList = commentSplitter.parse(lines)

        if self.cw.verbose:
            print "%s has %d blocks" % (file, len(elementList))

        commentBlock = None
        commentIndex = -1
        firstIndex = -1
        for i in range(0, len(elementList)):
            if isinstance(elementList[i], CommentPart):
                firstIndex = i
                licenseChecker = LicenseType(elementList[i])
                if licenseChecker.isLicense or licenseChecker.isCopyright:
                    commentBlock = elementList[i]
                    commentIndex = i
                    break
        else:
            if firstIndex == -1:
                # if the file has no comment block, then we squeeze a new copyright block on
                # top of it
                if self.newOnly:
                    elementList[:0] = [ self.license.copy(definition) ]
                    print "%s: Added License" % fullfile
                    save(fullfile, elementList.toString())
                return
            else:
                # we did find a comment block but none of the comment blocks was actually a license
                # block
                commentIndex = firstIndex
                commentBlock = elementList[firstIndex]

        licenseChecker = LicenseType(commentBlock)
        if not licenseChecker.isLicense and not licenseChecker.isCopyright:
            if self.newOnly:
                elementList[:0] = [ self.license.copy(definition) ]
                print "%s: Added License" % fullfile
                save(fullfile, elementList.toString())
        else:
            if self.existingOnly:
                elementList[commentIndex] = self.license.copy(definition)

                if commentBlock.toString() != elementList[commentIndex].toString():
                    print "%s: Replaced License" % fullfile
                    save(fullfile, elementList.toString())

