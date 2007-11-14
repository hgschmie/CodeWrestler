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

import os, sys
import getopt, re
from util.Pattern import Pattern
from util.CommentSplitter import CommentSplitter, CommentPart, DataPart, BlockList
from util.LicenseType import LicenseType
from util.File import load, save

from util.CallbackType import CallbackType


from util.CallbackType import CallbackType

def getCallback(cw=None):
    return TopFormatter(cw)

class TopFormatter(CallbackType):
    """Reformats the header of a java file to match the package, license, imports sequence"""
    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)

        self.pattern = Pattern()
        self.cw = cw

        try:
            opts, args = getopt.getopt(cw.module_options, "hl", ["help", "license-on-top"])
        except getopt.GetoptError:
            self.usage()
            raise ValueError("*** Parameter Error")

        self.licenseOnTop = False

        for option, value in opts:
            if option in ("-h", "--help"):
                self.usage()
                raise ValueError("*** Parameter Error")
            elif option in ("-l", "--license-on-top"):
                self.licenseOnTop = True
                continue
            else:
                self.usage()
                raise ValueError("*** Parameter Error")

    def usage(self):
        print "Usage: java.TopFormatter"
        print ""
        print "The following parameters can be supplied using the \"--modopts\" option"
        print "of the main program:"
        print ""
        print "-h, --help:           Show this help"
        print ""
        print "-l, --license-on-top: Put the license block on the very top of the file."
        print "                      Else it is put right after the package statement."
        print ""

    def callback(self, root=None, file=None, type=None):
        if type != 'java':
            return

        if self.cw.verbose:
            print "Processing %s" % file

        definition = self.pattern.getDefinition(type)

        fullfile = os.path.join(root, file)
        lines = load(fullfile)

        commentSplitter = CommentSplitter(definition)
        elementList = commentSplitter.parse(lines)

        commentBlock = None
        for block in elementList:
            if isinstance(block, CommentPart):
                commentBlock = block
                break
        else:
            raise ValueError("%s: No comment block found" % fullfile)


        licenseChecker = LicenseType(commentBlock)

        if not licenseChecker.isLicense and not licenseChecker.isCopyright:
            raise ValueError("%s: First comment block is not the license/copyright block!" % fullfile)

        newElements = BlockList()

        # Search the "package" line
        packagePattern = re.compile("^package\s+.*$")
        packageLine = None

        for packageBlock in elementList:
            if isinstance(packageBlock, CommentPart):
                continue

            for line in packageBlock:
                if packagePattern.search(line):
                    packageLine = line
                    break

            if packageLine is not None:
                break # python sucks

        newPackageBlock = DataPart()

        if self.licenseOnTop:
            newPackageBlock.append("\n")

        if packageLine is not None:
            newPackageBlock.append(packageLine)
            newPackageBlock.append("\n")

        dataBlock = DataPart()

        if self.licenseOnTop:
            newElements.append(commentBlock)
            newElements.append(newPackageBlock)
        else:
            newElements.append(newPackageBlock)
            newElements.append(commentBlock)
            dataBlock.append("\n")

        importStart = False
        importEnd = False
        importPattern = re.compile("^import\s+.*$")
        commentPattern = re.compile("^\s*\/\/.*$")

        for block in elementList:
            if block is commentBlock:
                continue # We already have this block on our new list

            # if it is a comment block and we still have an open dataBlock, add the
            # data block on the list, add the comment block and reopen the data block
            # else just add the comment block and go on
            if isinstance(block, CommentPart):
                if dataBlock is None:
                    newElements.append(block)
                else:
                    newElements.append(dataBlock)
                    newElements.append(block)
                    dataBlock = DataPart()
                continue

            # If we found a line after "import" that is neither comment nor blank line, consider
            # the import list done. Just add this block, because it is somewhere deep inside the
            # source code file
            if importEnd: # We already have copied the last block that contained "import" statements
                newElements.append(block)
                continue

            # We have not yet found the "import end". This might be a block 'before' the license (then it
            # contains the package statement or a block part that contains import lines and maybe the
            # class/interface (non-importe) line. Loop over it.
            for line in block:
                # We already have the "package" line copied
                if packagePattern.search(line):
                    continue

                # If we already fell off the list of imports, don't test any longer. Just add all the
                # lines from the block
                if not importEnd:
                    # We have not yet found an import line. Skip if it is whitespace
                    if not importStart:
                        if len(line) == 0 or line.isspace():
                            continue

                        # This is an import line. Open the import block and go on
                        if importPattern.search(line):
                            importStart = True
                        # This is neither whitespace, nor import nor comment. So we have
                        # a class without imports. Set both flags and go on
                        elif not commentPattern.search(line):
                            importStart = True
                            importEnd = True
                        else:
                            raise ValueError("%s: Strange line found between imports: %s" % (fullfile, line))
                    else:
                        if not (line.isspace() or len(line) == 0 or commentPattern.search(line) or importPattern.search(line)):
                            importEnd = True

                dataBlock.append(line)

            if importEnd:
                newElements.append(dataBlock)
                dataBlock = None

        if newElements.toString() != "".join(lines):
            print "%s: File reformatted" % fullfile
            save(fullfile, newElements.toString())
