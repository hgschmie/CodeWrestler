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

class PatternDefinition:
    """ Defines a single pattern """

    def safeGet(self, array={}, key=''):
        try:
            return array[key]
        except KeyError:
            return None

    def safeGetArray(self, array={}, key='', index=0):
        val = self.safeGet(array, key)
        if val is None:
            return 0

        return val[index]

    def __init__(self, pattArray = {}):
        self.openComment = self.safeGet(pattArray, 'openComment')
        self.closeComment = self.safeGet(pattArray, 'closeComment')
        self.leaderComment = self.safeGet(pattArray, 'leaderComment')
        self.trailerComment = self.safeGet(pattArray, 'trailerComment')

        if self.openComment is not None and self.closeComment is None and self.leaderComment is None:
            raise ValueError("closeComment and leaderComment cannot both be None if an openComment has been defined!")

        self.openCommentMatch = None
        self.closeCommentMatch = None
        self.leaderCommentMatch = None

        if  self.openComment is not None:
            patt = '^(\s*)' + re.escape(self.openComment)

            # if we have a close comment, the open comment must be placed on its own line
            if self.closeComment is not None:
                patt += '\s*$'
            self.openCommentMatch = re.compile(patt)

        if self.closeComment is not None:
            self.closeCommentMatch = re.compile(re.escape(self.closeComment) + '\s*$')

        if self.leaderComment is not None:
            self.leaderCommentMatch = re.compile('^(\s*)' + re.escape(self.leaderComment) + '(.*)$')

        if self.trailerComment is not None:
            self.trailerCommentMatch = re.compile('(.*?)\s*' + re.escape(self.trailerComment) + '\s*$')

        self.indentBeforeOpen    = self.safeGetArray(pattArray, 'indent', 0)
        self.indentBeforeLeader  = self.safeGetArray(pattArray, 'indent', 1)
        self.indentAfterLeader   = self.safeGetArray(pattArray, 'indent', 2)
        self.indentBeforeTrailer = self.safeGetArray(pattArray, 'indent', 3)
        self.indentBeforeClose   = self.safeGetArray(pattArray, 'indent', 4)


class Pattern:
    """Holds all the well known pattern types and offers matching methods to find out what type of file a file name is"""

    pattern_def = {
        'xml': ( '\.xml$', '\.xsl$', '\.xslt$', '\.xcat$',
                 '\.xmap$', '\.xconf$', '\.xroles$', '\.roles$', '\.xsp$',
                 '\.xlog$', '\.xsamples$', '\.xtest$', '\.xweb$', '\.xwelcome$',
                 '\.samplesxconf$', '\.samplesxpipe$', '\.svg$', '\.xhtml$', '\.jdo$', '\.gt$', '\.jx$',
                 '\.jxt$', '\.meta$', '\.pagesheet$', '\.stx$', '\.xegrm$', '\.xgrm$', '\.xlex$', '\.xmi$',
                 '\.xsd$', '\.rng$', '\.rdf$', '\.rdfs$', '\.xul$', '\.tld$', '\.xxe$', '\.ft$', '\.fv$',
                 '\.xhtm$', '\.launch$', '^\.classpath$', '^\.project$',
                 ),

        'sgml': ( '\.dtd$', '\.mod$', '\.sgml$', '\.sgm$',
                  ),

        'html': ( '\.html$', '\.htm$', '\.ihtml$',
                  ),

        'jsp': ( '\.jsp$',
                 ),

        'c': ( '\.c$', '\.h$', '\.cpp$', '\.cc$', '\.cs$', '\.css$', '\.egrm$', '\.grm$',
               ),

        'javascript': ( '\.js$', '\.javascript$',
                        ),

        'java': ( '\.java$', '\.groovy$', '\.gy', '\.jj$', '\.jjt$',
                  ),

        'jelly': ( '\.jelly$',
                        ),

        'sh': ( '\.sh$', '\.ccf$',
                ),

        'perl': ('\.pl$', '\.pm$',
                 ),

        'python': ( '\.py$',
                    ),

        'properties': ( '\.properties$', '\.rnc$', '\.rnx$', '\.properties\.tmpl$', '\.props$'
                        ),

        'dos': ( '\.bat$', '\.cmd$',
                 ),

        'sql': ( '\.sql$',
                 ),

        'velocity': ( '\.vm$', '\.vsl$'
                      ),

        'text': ( '\.txt$',
                      ),
        }

    #
    # openComment: We must match this code to establish a comment start
    # closeComment: This code concludes a comment. This also implies that
    # the starting comment must be placed on a single line
    # and the lines itself don't need to have a leading comment
    # indent: five numbers denominating the number of spaces for the comments:
    # - before open (only if open is on its own line)
    # - before leader (for leader != None)
    # - after leader (for leader != None)
    # - before trailer (for trailer != None)
    # - before close (closeComment != None)
    #
    # leaderComment and trailerComment are used when adding new comments
    #
    definitions = {
        'xml': PatternDefinition({ 'openComment': '<!--',
                                   'closeComment': '-->',
                                   'indent': ( 0, 0, 2, 0, 0 ),
                                   }),
        'sgml': PatternDefinition({ 'openComment': '<!--',
                                    'closeComment': '-->',
                                    'indent': ( 0, 0, 2, 0, 0 ),
                                    }),
        'html': PatternDefinition({ 'openComment': '<!--',
                                    'closeComment': '-->',
                                    'indent': ( 0, 0, 2, 0, 0 ),
                                    }),
        'jsp': PatternDefinition({ 'openComment': '<%--',
                                   'closeComment': '--%>',
                                   'indent': ( 0, 0, 2, 0, 0 ),
                                   }),
        'c': PatternDefinition({ 'openComment': '/*',
                                 'leaderComment': '*',
                                 'closeComment': '*/',
                                 'indent': ( 0, 1, 1, 0, 1 ),
                                 }),
        'javascript': PatternDefinition({ 'openComment': '/*',
                                          'leaderComment': '*',
                                          'closeComment': '*/',
                                          'indent': ( 0, 1, 1, 0, 1 ),
                                          }),
        'java': PatternDefinition({ 'openComment': '/*',
                                    'leaderComment': '*',
                                    'closeComment': '*/',
                                    'indent': ( 0, 1, 1, 0, 1 ),
                                    }),
        'jelly': PatternDefinition({ 'openComment': '<!--',
                                   'closeComment': '-->',
                                   'indent': ( 0, 0, 2, 0, 0 ),
                                   }),
        'sh': PatternDefinition({ 'openComment': '#',
                                  'leaderComment': '#',
                                  'indent': ( 0, 0, 1, 0, 0 ),
                                  }),
        'perl': PatternDefinition({ 'openComment': '#',
                                    'leaderComment': '#',
                                    'indent': ( 0, 0, 1, 0, 0 ),
                                    }),
        'python': PatternDefinition({ 'openComment': '#',
                                      'leaderComment': '#',
                                      'indent': ( 0, 0, 1, 0, 0 ),
                                      }),
        'properties': PatternDefinition({ 'openComment': '#',
                                          'leaderComment': '#',
                                          'indent': ( 0, 0, 1, 0, 0 ),
                                          }),
        'dos': PatternDefinition({ 'openComment': '\@echo off',
                                   'leaderComment': 'rem',
                                   'indent': ( 0, 0, 1, 0, 0 ),
                                   }),
        'sql': PatternDefinition({ 'openComment': '--',
                                   'leaderComment': '--',
                                   'indent': ( 0, 0, 1, 0, 0 ),
                                   }),
        'velocity': PatternDefinition({ 'openComment': '##',
                                        'leaderComment': '##',
                                        'indent': ( 0, 0, 1, 0, 0 ),
                                        }),

        'text': PatternDefinition({}),

        # This one is returned for unknown types or None passed to getDefinition
        'None': PatternDefinition({}),
        }

    def __init__(self):
        self.pattern = {}
        for pattern, pattlist in self.pattern_def.items():
            for ending in pattlist:
                self.pattern[re.compile(ending)] = pattern


    def getType(self, file=None):
        """returns the file type for a given file name"""
        if file is None:
            raise ValueError("No file name supplied")

        for patterns, type in self.pattern.items():
            if patterns.search(file):
                return type

        return None

    def getDefinition(self, type=None):
        """returns the comment defitinitions for a given file type"""

        if type is None:
            return self.definitions['None']
        try:
            return self.definitions[type]
        except KeyError:
            return self.definitions['None']
