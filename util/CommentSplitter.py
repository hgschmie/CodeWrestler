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

import re

class CommentPart(list):
    """Represents a comment block inside a file"""
    def __init__(self, pattern=None, lines=None):
        list.__init__(self)
        if pattern is None:
            raise ValueError("You must supply a pattern object")
        self.pattern = pattern
        self.foundCloseComment = False
        self.foundOpenComment = False
        self.prefix = ''

        if lines is not None:
            for line in lines:
                self.append(line)

        self.finish()

    def append(self, object=None):
        if self.pattern.closeComment:
            # implies that openComment is on its own line
            if self.pattern.openComment is not None:
                match = self.pattern.openCommentMatch.search(object)
                if match and not self.foundOpenComment:
                    self.prefix = match.group(1) # Prefix before the first comment character
                    self.foundOpenComment = True
                    return
            if self.pattern.closeCommentMatch.search(object):
                self.foundCloseComment = True
                return

        if self.pattern.leaderComment:
            match = self.pattern.leaderCommentMatch.search(object)
            if match:
                # If we have a match and no closeComment,
                # this implies that a leadingComment also opens the
                # comment block because the openComment does not have
                # to be on its own line
                if not self.pattern.closeComment and not self.foundOpenComment:
                    self.prefix = match.group(1) # Prefix before the first comment line
                    self.foundOpenComment = True

                object = match.group(2)
                if self.pattern.trailerComment:
                    match = self.pattern.trailerCommentMatch.search(object)

                    if match:
                        object = match.group(1)
            else:
                # If we had an opening match before, then this non-leader line
                # closes the block unless we have a closingComment element
                if self.foundOpenComment and not self.pattern.closeComment:
                    self.foundCloseComment = True
        else:
            # If we have no open and no leader comment, then every line will
            # be added to the comment buffer. This might be the attempt to read
            # in a comment file as "text". Ignore leading blank lines.
            if not self.pattern.openComment and not object.isspace():
                self.foundOpenComment = True

        # Ignore everything before the opening comment
        if not self.foundOpenComment:
            return

        # Ignore everything after the closing comment
        if self.foundCloseComment:
            return

        list.append(self, object.rstrip('\n'))

    def toString(self):
        result = []

        if self.pattern.openComment and self.pattern.closeComment:
            result.append(self.prefix + (' ' * self.pattern.indentBeforeOpen) + self.pattern.openComment + "\n")

        for lines in self:
            line = ''
            if self.pattern.leaderComment:
                line = self.prefix + (' ' * self.pattern.indentBeforeLeader) + self.pattern.leaderComment

                if len(lines) > 0 and self.pattern.indentAfterLeader > 0:
                    # spaceCount: Max number of blanks to insert
                    spaceCount = self.pattern.indentAfterLeader

                    # we count from 'first char' to 'number of chars to insert at max'
                    for i in range(1, self.pattern.indentAfterLeader + 1):
                        # if counter is still below the length of line and
                        # the char at the position to check is not a space, then break out
                        if i < len(lines) and not lines[i-1].isspace():
                            break
                        spaceCount -= 1

                    line += (' ' * spaceCount)

            line += lines

            if self.pattern.trailerComment:
                line += (' ' * self.pattern.indentBeforeTrailer) + self.pattern.trailerComment

            result.append(line + "\n")

        if self.pattern.closeComment:
            result.append(self.prefix + (' ' * self.pattern.indentBeforeClose) + self.pattern.closeComment + "\n")

        return ''.join(result)

    def finish(self):
        pass

    def copy(self, pattern=None):
        if pattern is None:
            res = CommentPart(self.pattern)
        else:
            res = CommentPart(pattern)

        res.foundOpenComment = self.foundOpenComment
        res.foundCloseComment = self.foundCloseComment
        res.prefix = self.prefix

        for lines in self:
            list.append(res, lines)

        return res

class DataPart(list):
    """Represents a non-comment / code block inside a file"""
    def __init__(self, ignoreBlankLines=False):
        list.__init__(self)
        self.ignoreBlankLines = ignoreBlankLines

    def append(self, object):
        if object is None:
            raise ValueError("You cannot add None to a block!")

        # ignore leading blank lines
        if self.ignoreBlankLines and len(self) == 0 and len(object) > 0 and object.isspace():
            return

        list.append(self, object.rstrip('\n'))

    def finish(self):
        if self.ignoreBlankLines:
            for i in range(self.len(), 0, -1):
                if self[i].isspace():
                    del(self[i])
                else:
                    return


    def toString(self):
        result = []
        for lines in self:
            result.append(lines + "\n")

        return ''.join(result)

class BlockList(list):
    """ holds all the parts of a file """
    def __init__(self):
        list.__init__(self)

    def append(self, object):
        """ ignores empty objects """

        # dies here if this is not an comment or data block
        object.finish()
        if len(object) > 0:
            list.append(self, object)

    def toString(self):
        res = ''
        for elements in self:
            res += elements.toString()

        return res


class CommentSplitter:
    """splits a file into comment and code blocks and returns a list of elements"""

    def __init__(self, pattern=None):
        if pattern is None:
            raise ValueError("no pattern given")

        self.pattern = pattern

    def parse(self, lines=None):

        if lines is None:
            raise ValueError("no lines given")

        resultList = BlockList()
        currentObject = None

        for line in lines:
            if not isinstance(currentObject, CommentPart):
                # This is currently a data object
                if self.pattern.openComment is not None and self.pattern.openCommentMatch.search(line):
                    if currentObject is not None:
                        resultList.append(currentObject)

                    currentObject = CommentPart(self.pattern)
                else:
                    if currentObject is None:
                        currentObject = DataPart()

            else:
                # This is currently a comment object

                # The type has no closeComment
                if self.pattern.closeComment is None:
                    # line does matches the leaderComment: This is a line which must go
                    # into a new data object. If it matches, it will go into the comment
                    # object
                    if not self.pattern.leaderCommentMatch.search(line):
                        resultList.append(currentObject)
                        currentObject = DataPart()
                else:
                    if self.pattern.closeCommentMatch.search(line):
                        # closeComment finishes the comment. The next line will go into a
                        # new object. The current line goes into the comment object
                        currentObject.append(line)
                        resultList.append(currentObject)
                        currentObject = None
                        continue

            currentObject.append(line)

        if currentObject is not None:
            resultList.append(currentObject)

        return resultList
