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

from util.CallbackType import CallbackType
from util.Pattern import Pattern
from util.CommentSplitter import CommentSplitter, CommentPart
from util.File import load

from license.LicenseType import LicenseType

def getCallback(cw=None):
    return ListLicense(cw)

class ListLicense(CallbackType):
    """checks whether a file contains a copyright or license message and reports the type of license"""

    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

        self.cw = cw
        self.pattern = Pattern()

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


        licenseChecker = LicenseType(commentBlock)

        if not licenseChecker.isCopyright:
            print "%s: Has no copyright" % fullfile

        if not licenseChecker.isLicense:
            print "%s: Has no license" % fullfile
        else:
            if licenseChecker.license is None:
                print "%s: License Type is unknown" % fullfile
            else:
                print "%s: Licensed under %s" % (fullfile, licenseChecker.license)
