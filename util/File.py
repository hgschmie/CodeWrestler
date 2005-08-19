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

def load(filename=None):

    if filename is None:
        raise ValueError("Need a file name!")

    try:
        workfile = open(filename, "r")
    except IOError:
        raise ValueError("File %s could not be opened!" % filename)

    lines = workfile.readlines()
    workfile.close()

    return lines

def save(filename=None, lines=None):

    if filename is None or lines is None:
        raise ValueError("Need a filename and some content")

    try:
        os.unlink(filename + ".bak")
    except OSError, error:
        if error.errno != 2:  # ENOENT
            raise ValueError("%s: Could not write file" % filename)

    os.rename(filename, filename + ".bak")

    try:
        workfile = open(filename, "w")
        workfile.write(lines)
        workfile.flush()
        workfile.close()
    except IOError:
        try:
            os.unlink(filename)
        finally:
            pass

        os.rename(filename + ".bak", filename)
        raise ValueError("%s: Could not write file" % filename)
    else:
        try:
            os.unlink(filename + ".bak")
        except OSError:
            raise ValueError("%s: Could not remove backup file" % filename)





