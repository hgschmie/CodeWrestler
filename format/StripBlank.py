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
    return StripBlank(cw)

class StripBlank(CallbackType):
    """ removes spaces from the line endings """
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

        lines = load(fullfile)

        result = []

        for line in lines:
            newline = line.rstrip('\n')
            if len(result) == 0 and (len(newline) == 0 or newline.isspace()):
                continue
            result.append(newline.rstrip())

        result = "\n".join(result) + "\n"

        if result != "".join(lines):
            print "%s: File reformatted" % fullfile
            save(fullfile, result)
