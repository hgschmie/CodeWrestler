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

class Traverse:
    """ Method called by the TreeBuilder to process the various files"""
    def __init__(self, callback=None, mod_opts='', opts=''):
        self.pattern = Pattern()

        if callback is None:
            raise ValueError("callback must be defined!")

        self.callback = callback

    def traverse(self, root=None, file=None):
        if root is None or file is None:
            raise ValueError("traverse with illegal root or file!")

        type = self.pattern.getType(file)

        self.callback.callback(root, file, type)

class TreeBuilder:
    """builds a tree of files to traverse"""
    def __init__(self, tree=None, excludes=()):
        if tree is None:
            raise ValueError("No directory for traversing supplied")
        self.tree = tree
        self.ex_pattern = map(re.compile, excludes)
        self.verbose = False

    def setVerbose(self, verbose=False):
        self.verbose = verbose

    def traverse(self, traverse=None):
        """runs through the directory tree, execute traverse on it"""

        if traverse is None:
            raise ValueError("traversing class must be defined!")

        for root, dirs, files in os.walk(self.tree):

            # step 1: Remove all Directories that should not be parsed
            dirloop = dirs[:]
            for dir in dirloop:
                for patt in self.ex_pattern:
                    if patt.search(dir) or patt.search(os.path.join(root, dir)):
                        dirs.remove(dir)

                        if self.verbose:
                            print "Removed %s" % dir

                        break

            # step 2: Remove all Files that should not be parsed
            fileloop = files[:]
            for file in fileloop:
                for patt in self.ex_pattern:
                    if patt.search(file) or patt.search(os.path.join(root, file)):
                        files.remove(file)

                        if self.verbose:
                            print "Removed %s" % file

                        break

            # step 3: Process the remaining files
            for file in files:
                traverse.traverse(root, file)
