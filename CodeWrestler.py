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

import getopt, sys
import os.path
from util.TreeBuilder import TreeBuilder, Traverse

########################################################################
#
# Author: Henning Schmiedehausen <henning@schmiedehausen.org>
# Version : $Id$
#
# #######################################################################
#
# A general purpose Source tree traverser which can call an action to be
# performed on the source files.
#
# Usage examples are
# - adding / stripping of copyright and license notices
# - updating of copyright dates
# - reformatting source code
# - adding / removing empty lines
#

class CodeWrestler:

    # Well known skip patterns to skip every time
    known_excludes = (
        "^\.svn$",                 # Subversion
        "^CVS$",                   # CVS
        "^\..*$",                  # hidden files
        "^.*~$", "^#.*#$",         # emacs Backup files
        "\.pyc$", "\.pyo$",        # python bytecode files
        "\.png$", "\.gif$", "\.jpg$", "\.jpeg$", "\.ico$", "\.gz$", # various known binary files
        "\.xcf",                   # Gimp Files
        )

    def usage(self):
        print "Usage:"
        print "-h, --help:          Show this help"
        print "-v, --verbose:       Run verbose"
        print ""
        print "-d, --dir:           Define directory to traverse (default: .)"
        print "-m, --module:        Define module to use as callback module"
        print "-o, --modopts:       Options to be passed to the callback module"
        print "-e, --excludes:      Define a file with additional patterns to exclude"

    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "d:e:hm:o:v", ["dir=", "excludes=", "help", "module=", "modopts=", "verbose" ])
        except getopt.GetoptError:
            self.usage()
            sys.exit(2)
        #
        # Variable Defaults
        self.verbose = False
        self.dirtree = "."

        module_name = None
        self.module_options = ''

        excludes = list(self.known_excludes)
        excludefilename = None

        for option, value in opts:
            if option in ("-h", "--help"):
                self.usage()
                sys.exit()

            elif option in ("-v", "--verbose"):
                self.verbose = True
                continue

            elif option in ("-d", "--dir"):
                self.dirtree = value
                continue

            elif option in ("-e", "--excludes"):
                excludefilename = value

            elif option in ("-m", "--module"):
                module_name = value
                continue

            elif option in ("-o", "--modopts"):
                self.module_options = value.split()
                continue

        if not os.path.isabs(self.dirtree):
            self.dirtree = os.path.abspath(self.dirtree)

        if excludefilename is not None:
            if not os.path.isabs(excludefilename):
                excludefilename = os.path.join(self.dirtree, excludefilename)

            excludefile = open(excludefilename)
            for line in excludefile.readlines():
                line = line.rstrip('\n')
                if len(line) == 0 or line.isspace() or line[0] == '#':
                    continue
                excludes.append(line.strip())

        if self.verbose:
            print "Traversed tree:  %s" % self.dirtree
            if module_name is not None:
                print "Selected Module: %s" % module_name

            for ex in excludes:
                print "Exclude: %s" % ex

        if module_name is None:
            module_name = "util.DefaultCallback"

        index = module_name.find('.')

        try:
            if index < 0:
                mod = __import__(module_name)
            else:
                package = module_name[:index]
                mod = __import__(module_name, globals(), locals(), [ package ])
        except ImportError:
            print "Could not load Module %s" % module_name
            sys.exit(1)

        try:
            builder = getattr(mod, 'getCallback')
            module = apply(builder, [self])
        except AttributeError:
            print "Module %s is not a CodeWrestler Module" % module_name
            sys.exit(1)
        except ValueError, msg:
            print msg
            sys.exit(1)

        self.treebuilder = TreeBuilder(self.dirtree, excludes)
        self.treebuilder.setVerbose(self.verbose)

        trav = Traverse(module)
        try:
            self.treebuilder.traverse(trav)
        except ValueError, msg:
            print msg
            sys.exit(1)

if __name__ == "__main__":
    cw = CodeWrestler()
    cw.main()
