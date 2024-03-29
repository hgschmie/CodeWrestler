CodeWrestler
============


CodeWrestler is a tool to massage a code base in different
ways. Its main function is to traverse a source tree, identify the
file types (e.g. source code, scripts, xml files, properties files)
and run different processing classes on them.

This program is 

Copyright (C) 2005 by Henning Schmiedehausen <henning@schmiedehausen.org>

Distributed under the terms of the Apache License 2.0 as described in
the etc/LICENSE.txt file in this distribution.

Download
========

This is still sort of a "work in progress". 

You can get CodeWrestler from its Subversion source repository at

https://svn.softwareforge.de/trac/browser/codewrestler/trunk/

If you find bugs or have enhancements, please put them into the
CodeWrestler issue tracker at

https://svn.softwareforge.de/trac/newticket?component=CodeWrestler


Processing module overview
==========================

* license.ListLicense
   Runs a heuristical analysis over the source files to find out
   if they contain a license, tries to identify it and list them
   
* license.CheckLicense
   Checks if all source code files contain a license and compares 
   it against a given template

* license.ReLicense
   Adds missing license entries to source files or changes
   existing license entries to match an overall license file

* format.CommentFormat
   Checks comment blocks in the source code to match the overall
   comment policy and reformat them

* format.StripBlank
   Removes trailing blanks from the source code files

* java.TopFormatter
   Reworks the sequence of package, license, import statements in
   java and java-like files.

* xml.TopFormatter
   Looks for <?xml headers in XML files. If it finds such a line, it
   makes sure that it is the very first line in the XML file. Else, it
   adds a <?xml version="1.0" encoding="UTF-8"?> line on top.


Main options
============

-h, --help:		Display global help

-v, --verbose:		Run verbose

-d, --dir:		Start directory (Default is current Directory)

-e, --excludes:		File which contains exclude patterns. If a
			relative location is given, it is relative to
			the start directory (Format see below)

-m, --module:		The processing module to select. If no module
                        has been selected, all files that have no known
                        type will be listed; if also -v or --verbose is
                        given, then all files and their type will be listed

-o, --modopts:		Supply modules specific parameters. For multiple
			parameters use --modopts='--foo --bar xxx --baz'


Examples:

python CodeWrestler.py --dir=/src/codewrestler --module=format.CommentFormat

Formats all the comment blocks as described below (Formatting model).


python CodeWrestler.py --dir=/src/codewrestler --module=format.StripBlank

Removes all trailing blank lines from the source files.


The excludes file
=================

Most code trees contain files that should not be processed by
CodeWrestler. Adding these files to an exclude file allows
CodeWrestler to skip them.

Format of the exclude file is one python regular expression per
line. Empty lines, lines that contain only whitespace or lines that
start with # in the very first column are ignored.

Each pattern is matched against
  - file name without path
  - file name with full path
  - directory name
  - full path

if one of these matches, the pattern is ignored. 

Examples:

.*\.foo$	- Ignore all files and directories that end in .foo
Foo.xxx$	- Ignore all Foo.xxx files
foo/.*$		- Ignore everything in the 'foo' subtree

In addition to the excludes file, the following patterns are always
ignored:

^.svn$		- Subversion subdirectories
^CVS$		- CVS subdirectories
^\..*$		- Unix 'hidden' files
^.*~$
^#.*#$          - emacs backup and temp files
\.pyc$ 
\.pyo$          - python bytecode files
\.png$		- PNG images
\.gif$		- GIF images
\.jpg$		
\.jpeg$		- JPEG images
\.ico$		- ICON files
\.gz$		- gzipped files
\.xcf$		- Gimp Files


File type matching
==================

File type matching is based on file names. The file contents are never
consulted to determine the type of a file. The following types are
currently known by CodeWrestler

Own line: Starting and ending comment are placed on their own line
Open:     Open Comment
Close:    Close Comment
LD:       Leader comment for each comment line
TR:       Trailer comment for each comment line

Indent: Number of spaces set 
  O = before open
  C = before close
  B = before leader
  A = after leader
  T = before trailer
  See below for a description

Empty fields mean "not defined". Types without Open and Leader comment
type have no concept of "comments" at all. This currently only applies
to text files.


Ending		|    Type    | Own  |    Open   | Close| LD  | TR | Indent  |
                |            |      |           |      |     |    |O|C|B|A|T|
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
xml xsl xslt    | xml        | yes  |    <!--   | -->  |     |    |0|0|0|2|0|
xcat xmap xconf |            |      |           |      |     |    | | | | | |
xroles roles    |            |      |           |      |     |    | | | | | |
xsp xlog        |            |      |           |      |     |    | | | | | |
xsamples xtest  |            |      |           |      |     |    | | | | | |
xweb xwelcome   |            |      |           |      |     |    | | | | | |
samplesxconf    |            |      |           |      |     |    | | | | | |
samplesxpipe    |            |      |           |      |     |    | | | | | |
svg xhtml jdo   |            |      |           |      |     |    | | | | | |
gt jx jxt meta  |            |      |           |      |     |    | | | | | |
pagesheet stx   |            |      |           |      |     |    | | | | | |
xegrm xgrm xlex |            |      |           |      |     |    | | | | | |
xmi xsd rng rdf |            |      |           |      |     |    | | | | | |
rdfs xul tld    |            |      |           |      |     |    | | | | | |
xxe ft fv xhtm  |            |      |           |      |     |    | | | | | |
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
dtd mod         | sgml       | yes  |    <!--   | -->  |     |    |0|0|0|2|0|
sgml sgm        |            |      |           |      |     |    | | | | | |
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
html htm ihtml  | html       | yes  |    <!--   | -->  |     |    |0|0|0|2|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
jsp             | jsp        | yes  |    <%--   | --%> |     |    |0|0|0|2|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
c h cpp cc cs   | c          | yes  |    /*     | */   | *   |    |0|1|1|1|0|
css egrm grm    |            |      |           |      |     |    | | | | | |
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
js javascript	| javascript | yes  |    /*     | */   | *   |    |0|1|1|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
java groovy gy  | java       | yes  |    /*     | */   | *   |    |0|1|1|1|0|
jj jjt          |            |      |           |      |     |    | | | | | |
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
jelly           | jelly      | yes  |    <!--   | -->  |     |    |0|0|0|2|0|
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
sh ccf          | sh         | no   |    #      |      | #   |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
pl pm           | perl       | no   |    #      |      | #   |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
py              | python     | no   |    #      |      | #   |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
properties rnc  | properties | no   |    #      |      | #   |    |0|0|0|1|0|
rnx             |            |      |           |      |     |    | | | | | |
properties.tmpl |            |      |           |      |     |    | | | | | |
props           |            |      |           |      |     |    | | | | | |
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
bat cmd         | dos        | no   | @echo off |      | rem |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
sql             | sql        | no   | --        |      | --  |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
vm vsl          | velocity   | no   | ##        |      | ##  |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
txt             | text       | no   |           |      |     |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+
                |            |      |           |      |     |    | | | | | |
everything else | -          | no   |           |      |     |    |0|0|0|1|0|
                |            |      |           |      |     |    | | | | | |
----------------+------------+------+-----------+------+-----+----+-+-+-+-+-+


Module options
==============

For each module that takes parameters, you can request a module
specific help by using the --module=<module name> --modopts=--help
option. This displays the module specific help message.


license.CheckLicense
--------------------

This module checks all source files in your tree against a license
template.

-h, --help:		Display module help

-f, --file:		File that contains the license. If this is a
			relative location, it is treated as relative
			to the start directory

-t, --type:		Type of the license file. Default is "text". As
			the license is compared against a comment
			block, it is also preprocessed as a comment
 			using a given syntax.

			If your license file is formatted in another
			comment syntax (e.g. java syntax for the maven
			checkstyle license file), use this type to
			use the license file.

Example:

python CodeWrestler.py --dir=/src/codewrestler --module=license.CheckLicense \
			--modopts="--file=etc/boilerplate.txt"

checks the codewrestler code base against its included boilerplate
license file.

python CodeWrestler.py --dir=/src/javaproject --module=license.CheckLicense \
			--modopts="--file=conf/checkstyle-license.txt --type=java"

checks a project against a maven checkstyle plugin license file by
parsing it as a java comment.


license.ReLicense
-----------------

This module replaces license blocks inside a code tree with a given license template.

-h, --help:		Display module help

-f, --file:		File that contains the license. If this is a
			relative location, it is treated as relative
			to the start directory

-t, --type:		Type of the license file. Default is "text". As
			the license is compared against a comment
			block, it is also preprocessed as a comment
 			using a given syntax.

			If your license file is formatted in another
			comment syntax (e.g. java syntax for the maven
			checkstyle license file), use this type to
			use the license file.

-n, --new-only:		Add a license block only to files that don't already have
                        a license.

-e, --existing-only:    Only process files that already have a license block, replacing
                        the existing license block with the template.
                
Example:

python CodeWrestler.py --dir=/src/codewrestler --module=license.CheckLicense \
			--modopts="--file=etc/boilerplate.txt --new-only"

Checks for new files in the codewrestler code base and adds license
files apropriately.


java.TopFormatter
-----------------

This module reworks the position of the package statement of java
files (either before or right after the license) and cleans up blank
lines surrounding the license block.

This plugin is intended to clean up your source files for the maven
checkstyle plugin.

-h, --help:           Show this help

-l, --license-on-top: Put the license block on the very top of the file.
                      Else it is put right after the package statement.


The comment indent model
========================

Some CodeWrestler modules parse the comment blocks in the source code
files and reformats them according to the rules given above. The
following formatting model is used:

Overall comment block:

----- start of comment block ------
----- (optional) open comment line ------

comment block

----- (optional) close comment line -----
----- end of comment block ------

Everything before the open comment line and after the close comment
line is ignored.

If the file type defines an open and close comment line, then this
line is searched. Everything between open and close is treated as
comment line. In this case, the open and close comment are put on
their own lines.

If a file type does not define a close line, then the open comment is
treated as "start of a line" type comment (like e.g. shell scripts or
property files). If a line matches the open comment, then every
following line that matches the leading comment will be treated as
part of the comment block. For these types, the open comment and the
leading comment are usually the same (but there are exceptions,
e.g. the "dos" type).


Comment Open lines:
|-------|open comment
  (1)

1: "before open indent"

Comment lines:

|-------|comment leader|-----|comment|[----|comment trailer]
   (2)                   (3)           (4)

2: "before leader indent"
3: "after leader indent". If the comment already contains
   leading blanks (e.g. commented out code), then the
   "after leader indent" is subtracted from these blanks and
   the remaining blanks are kept
4: If a comment trailer is defined, then the "before trailer"
   indent and the trailer are added 

Comment Close lines:
|-------|close comment
  (5)

5: "before close comment" indent

The comment types and their indexes are defined in the util/Pattern.py
file.


Writing your own modules
========================

If you are interested in writing your own CodeWrestler modules, you
can use the util/DefaultCallback.py file as your starting point. A
CodeWrestler module must supply a getCallback() method that gets
called by the core with the CodeWrestler main object passed to it (for
accessing configuration information etc.).

This method must return an object instance that extends
util.CallbackType, which in turn offers the callback method which
implements the functionality. callback will be passed the current
directory path (as root), the current file (as file) and the type of
file (as type) which can be "None" for unknown file types.

