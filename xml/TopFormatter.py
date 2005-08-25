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

import os, re
from util.Pattern import Pattern
from util.CommentSplitter import CommentSplitter, DataPart, BlockList
from util.File import load, save

from util.CallbackType import CallbackType

def getCallback(cw=None):
    return TopFormatter(cw)

class TopFormatter(CallbackType):
    """Reformats the header of a xml file to make sure that the ?xml line is on top"""
    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

        self.pattern = Pattern()
        self.cw = cw

    def callback(self, root=None, file=None, type=None):
        if type != 'xml' and type != 'jelly':
            return

        if self.cw.verbose:
            print "Processing %s" % file

        definition = self.pattern.getDefinition(type)

        fullfile = os.path.join(root, file)
        lines = load(fullfile)

        commentSplitter = CommentSplitter(definition)
        elementList = commentSplitter.parse(lines)

        # Search the "?xml" line
        xmlDefPattern = re.compile("^\s*\<\?xml\s")

        testLine = False
        foundLine = None

        for block in elementList:
            if isinstance(block, DataPart):
                for line in block:
                    if len(line) == 0 or line.isspace():
                        continue
                    testLine = True
                    if xmlDefPattern.search(line):
                        foundLine = line
                        break
            if testLine or foundLine is not None:
                break # python sucks
                

        newXmlDefBlock = DataPart()

        if foundLine is None:
            newXmlDefBlock.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
        else:

            if self.cw.verbose:
                print "Found line: %s" % foundLine
            newXmlDefBlock.append(foundLine)

        newElements = BlockList()
        newElements.append(newXmlDefBlock)

        for block in elementList:
            if isinstance(block, DataPart):
                dataBlock = DataPart()
                for line in block:
                    # We already have the "?xml" line copied
                    if xmlDefPattern.search(line):
                        continue

                    dataBlock.append(line)
                block = dataBlock

            newElements.append(block)

        if newElements.toString() != "".join(lines):
            print "%s: File reformatted" % fullfile
            save(fullfile, newElements.toString())
