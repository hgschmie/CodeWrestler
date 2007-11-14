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

from util.CommentSplitter import CommentPart

import re

NONE = 0

# lic_type
UNKNOWN = 0
APACHE = 1
PUBLIC_DOMAIN = 2
GPL = 3

# lic_flags
APACHE_10 = 1
APACHE_11 = 2
APACHE_12 = 4
APACHE_20 = 8

OR_LATER = 1
LGPL_20 = 2
LGPL_21 = 4
GPL_2   = 8


class LicenseType:
    def __init__(self, comment=None):

        if comment is None:
            raise ValueError("A comment block to check must be passed in")

        lines = " ".join(comment)

        self.isLicense = bool(re.search('\sli[c|s]ense', lines, re.I))
        self.isCopyright = bool(re.search('\s*copyright\s', lines, re.I)) or bool(re.search('\s\(c\)\s', lines, re.I))

        self.license = None
        self.lic_type = UNKNOWN
        self.lic_flags = NONE

        if not self.isLicense:
            return

        if re.search('Licensed under the Apache License.*Version 2.0', lines):
            self.lic_type = APACHE
            self.lic_flags = APACHE_20

            if re.search('Apache Software Foundation or its licensors', lines):
                self.license = 'Apache 2.0a'
                return
            else:
                self.license = 'Apache 2.0'
                return

        elif re.search('The Apache Software License.*Version 1.2', lines):
            self.lic_type = APACHE
            self.lic_flags = APACHE_12
            self.license = 'Apache 1.2'
            return

        elif re.search('The Apache Software License.*Version 1.1', lines):
            self.lic_type = APACHE
            self.lic_flags = APACHE_11
            self.license = 'Apache 1.1'
            return

        elif re.search('Copyright.*The Apache Group', lines):
            self.lic_type = APACHE
            self.lic_flags = APACHE_10
            self.license = 'Apache 1.0'
            return

        elif re.search('public domain', lines, re.I):
            self.lic_type = PUBLIC_DOMAIN
            self.license = 'public domain'
            return

        elif re.search('GNU Lesser General Public License', lines):
            if re.search('version 2\.1', lines):
                if re.search('or +\(at +your +option\) +any +later +version', lines):
                    self.lic_type = GPL
                    self.lic_flags = LGPL_21 | OR_LATER
                    self.license =  "LGPL 2.1 or later"
                    return

                else:
                    self.lic_type = GPL
                    self.lic_flags = LGPL_21
                    self.license = "LGPL 2.1"
                    return

            elif re.search('version 2(\.0)?', lines):
                if re.search('or +\(at +your +option\) +any +later +version', lines):
                    self.lic_type = GPL
                    self.lic_flags = LGPL_20 | OR_LATER
                    self.license = "LGPL 2.0 or later"
                    return
                else:
                    self.lic_type = GPL
                    self.lic_flags = LGPL_20
                    self.license = "LGPL 2.0"
                    return
        elif re.search('GNU General Public License', lines):
            if re.search('Version 2(\.0)?', lines):
                if re.search('or +\(at +your +option\) +any +later +version', lines):
                    self.lic_type = GPL
                    self.lic_flags = GPL_2 | OR_LATER
                    self.license =  "GPL 2 or later"
                    return
                else:
                    self.lic_type = GPL
                    self.lic_flags = GPL_2
                    self.license = "GPL 2"
                    return
        return
