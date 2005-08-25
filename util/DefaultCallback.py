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

from util.CallbackType import CallbackType

import os.path

class DefaultCallback(CallbackType):
    def __init__(self, cw=None):
        CallbackType.__init__(self, cw)
        self.cw = cw

    def callback(self, root=None, file=None, type=None):
        fullfile = os.path.join(root, file)

        if self.cw.verbose:
            print "%s: Is a %s file" % (fullfile, type)
        else:
            if type is None:
                print "%s: unknown type" % fullfile

def getCallback(cw=None):
    return DefaultCallback(cw)
