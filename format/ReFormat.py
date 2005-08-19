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
from license.LicenseType import LicenseType
from util.File import load, save

def getCallback(cw=None):
    return ReFormat(cw)

class ReFormat(CallbackType):
    """ formats existing comment blocks to match the global comment style """
    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

        self.pattern = Pattern()
        self.cw = cw

    def callback(self, root=None, file=None, type=None):

        definition = self.pattern.getDefinition(type)
        # types that have no openComment have no comment
        # syntax at all. Therefore it is useless to check for
        # a license.
        if definition.openComment is None:
            return

        fullfile = os.path.join(root, file)

        if self.cw.verbose:
            print "Reformatting %s (%s)..." % (file, type)

        lines = load(fullfile)

        if self.cw.verbose:
            print "%s has %d lines" % (file, len(lines))

        commentSplitter = CommentSplitter(definition)
        elementList = commentSplitter.parse(lines)

        if self.cw.verbose:
            print "%s has %d blocks" % (file, len(elementList))

        if elementList.toString() != "".join(lines):
            print "%s: File reformatted" % fullfile
            save(fullfile, elementList.toString())
