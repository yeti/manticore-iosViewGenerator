# Manticore iOS View Generator
# Copyright (C) 2013, Richard H Fung at Yeti LLC

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# This utility generates the define statements and mapping statements
# for view controllers for MCViewFactory.h/m.
#
# Assumptions:
#    * Run from the project directory
#    * Template files exist:
#          * TemplateSectionViewController.{xib,h,m}.template
#          * TemplateViewController.{xib,h,m}.template
#    * Input file schema is formatted as YAML:
#          Section1:
#               View1A
#               View1B
#
#          Section2:
#               View2A
#               View2B
#
# The output should be copied and pasted into the appropriate place in the source code.
#

import sys
import os
import os.path
import string
from datetime import date
import logging

SECTION_SUFFIX = "SectionViewController"
VIEW_SUFFIX = "ViewController"
SHORT_SECTION_SUFFIX = "SectionVC"
SHORT_VIEW_SUFFIX = "VC"

def write_define(schema):
    i = 1
    for s in schema:
        append = ""
        if i % 5 == 0:
            append = " // " + str(i)
        print '{:<30}'.format("#define " + s["variable_name"]) +  ' @"' +  s["mapped_to"] + '" ' + append
        i = i + 1

def write_register(schema):
    i = 1
    for s in schema:
        append = ""
        if i % 5 == 0:
            append = " // " + str(i)
        print "[factory registerView:" + s["variable_name"] + "];" + append
        i = i + 1


def prefix_remover(name, prefix):
    if len(prefix):
        if name[0:len(prefix)] == prefix:
            return name[2:]
    
    return name

def special_names(name):
    if name == "MCMain":
        return "Builtin_Main"
    elif name == "MCError":
        return "Builtin_Error"
    else:
        return name


def walk_directory(prefix=""):
    views = []
    sections = []

    for dirname, dirnames, filenames in os.walk('.'):

        for filename in filenames:

            filepart, fileExtension = os.path.splitext(filename)
            pos = filepart.find("ViewController")
            if string.lower(fileExtension) == ".xib" and  pos > 0:
                # read file contents
                f = open(dirname + "/" + filename, 'r')
                contents = f.read()
                f.close()

                # identify identifier part
                vc_name = prefix_remover(filepart[0:pos], prefix)
                vc_name = special_names(vc_name)

                if string.find(contents, "MCSectionViewController") != -1 or string.find(contents, "SectionViewController") != -1:
                    sections.append({ "type" : "section", "variable_name": "SECTION_"  + string.upper(vc_name), "mapped_to" : filepart})
                else:
                    views.append({ "type" : "view", "variable_name": "VIEW_" + string.upper(vc_name), "mapped_to" : filepart })

    return sections, views


def parse_view_schema(filename, prefix="", length="long"):


    sections = []
    views = []

    current_section = ""

    f = open(filename, "r")
    with f:
        line = f.readline() 
        while line != "":
            line = string.strip(line) # remove whitespace

             # ignore blank lines and comments
            if len(line) == 0 or line[0:1] == "#" or line[0:1] == "/" or line[0:1] == "'" or line[0:1] == "`":
                line = f.readline()
                continue

             # remove whitespace
            is_section = False
            if line[-1:] == ":":
                is_section = True
                line = line[:-1] # remove last character

            # automatically remove proper extensions, including everything thereafter
            pos = line.find(SECTION_SUFFIX)
            if pos < 0:
                pos = line.find(VIEW_SUFFIX)
            if pos < 0:
                pos = line.find(SHORT_SECTION_SUFFIX)
            if pos < 0:
                pos = line.find(SHORT_VIEW_SUFFIX)

            if pos < 0: # default, only the unique name is provided
                pos = len(line)
                if length=="long":
                    if is_section: # append the decscriptive full name as necessary
                        line = line + SECTION_SUFFIX
                    else:
                        line = line + VIEW_SUFFIX
                else:
                    if is_section: # append the decscriptive full name as necessary
                        line = line + SHORT_SECTION_SUFFIX
                    else:
                        line = line + SHORT_VIEW_SUFFIX

            # identify the unique name
            vc_name = prefix_remover(line[0:pos], prefix)
            vc_name = special_names(vc_name)

            if is_section:
                current_section = vc_name
            else:
                if vc_name.find(current_section) == -1:
                    logging.warning("View name should have the same prefix as its owning section: %s" % vc_name)

            if is_section or line[-len(SECTION_SUFFIX):].lower() == SECTION_SUFFIX.lower():
                sections.append({ "type" : "section", "variable_name": "SECTION_"  + string.upper(vc_name), "mapped_to" : prefix + line, "vc_name" : prefix + vc_name })
            else:
                views.append({ "type" : "view", "variable_name": "VIEW_" + string.upper(vc_name), "mapped_to" : prefix + line,  "vc_name" : prefix + vc_name })

            # read the next line
            line = f.readline()


    return sections, views

def replace_in_file(template, output, dict):

    # this statement is now guared by the caller
    if os.path.isfile(output):
        logging.warning("Skipping " + output)
        return False

    logging.info("Creating " + output)

    f = open(template, "r")
    g = open(output, "w")
    contents = f.read()
    for (key, value) in dict.items():
        contents = string.replace(contents, "{{ %s }}" % key, str(value))

    g.write(contents)
    g.close()
    f.close()

    return True

def get_project_name_from_dir():
    full_dir = os.getcwd()
    dir_parts = full_dir.split("/")
    return dir_parts[-1]

# Checks to ensure that the file hasn't already been created by this script
# regardless of what the script might think is the extension, e.g., ViewController or VC.
# The file already exists if either suffix is found. 
#
# Special code is added to detect for SectionViewController and SectionVC, 
# which can have the same name as ViewController and VC though not recommended.
#
# extension should include .
def check_file_exists(name, extension):
    if name.endswith(SECTION_SUFFIX): # if is a section
        test_root = name[:-len(SECTION_SUFFIX)]
        return os.path.isfile(test_root + SECTION_SUFFIX + extension) or  os.path.isfile(test_root + SHORT_SECTION_SUFFIX + extension)
    elif name.endswith(SHORT_SECTION_SUFFIX): 
        test_root = name[:-len(SHORT_SECTION_SUFFIX)]

        return os.path.isfile(test_root + SECTION_SUFFIX + extension) or  os.path.isfile(test_root + SHORT_SECTION_SUFFIX + extension)
    elif name.endswith(VIEW_SUFFIX) :
        test_root = name[:-len(VIEW_SUFFIX)]

        return os.path.isfile(test_root + VIEW_SUFFIX + extension) or  os.path.isfile(test_root + SHORT_VIEW_SUFFIX + extension)
    elif name.endswith(SHORT_VIEW_SUFFIX):
        test_root = name[:-len(SHORT_VIEW_SUFFIX)]
        
        return os.path.isfile(test_root + VIEW_SUFFIX + extension) or  os.path.isfile(test_root + SHORT_VIEW_SUFFIX + extension)
    else:
        assert False        

def which_file_exists(name, extension):
    if name.endswith(SECTION_SUFFIX): # if is a section
        test_root = name[:-len(SECTION_SUFFIX)]
        if os.path.isfile(test_root + SECTION_SUFFIX + extension):
            return test_root + SECTION_SUFFIX + extension
        elif  os.path.isfile(test_root + SHORT_SECTION_SUFFIX + extension):
            return test_root + SHORT_SECTION_SUFFIX + extension
        else:
            return ""
    elif name.endswith(SHORT_SECTION_SUFFIX): 
        test_root = name[:-len(SHORT_SECTION_SUFFIX)]

        if os.path.isfile(test_root + SECTION_SUFFIX + extension):
            return test_root + SECTION_SUFFIX + extension
        elif os.path.isfile(test_root + SHORT_SECTION_SUFFIX + extension):
            return test_root + SHORT_SECTION_SUFFIX + extension
        else:
            return ""
    elif name.endswith(VIEW_SUFFIX) :
        test_root = name[:-len(VIEW_SUFFIX)]
        if os.path.isfile(test_root + VIEW_SUFFIX + extension):
            return test_root + VIEW_SUFFIX + extension
        elif  os.path.isfile(test_root + SHORT_VIEW_SUFFIX + extension):
            return test_root + SHORT_VIEW_SUFFIX + extension
        else:
            return ""
    elif name.endswith(SHORT_VIEW_SUFFIX):
        test_root = name[:-len(SHORT_VIEW_SUFFIX)]
        if os.path.isfile(test_root + VIEW_SUFFIX + extension):
            return test_root + VIEW_SUFFIX + extension
        elif os.path.isfile(test_root + SHORT_VIEW_SUFFIX + extension):
            return test_root + SHORT_VIEW_SUFFIX + extension
        else:
            return ""
    else:
        return ""   

def create_templates_from_schema(schema):
    for entry in schema:
        template = ""
        base_class = ""

        # choose templates and base classes
        if entry["type"] == "section":
            template = "TemplateSectionViewController.%s.template"
            base_class = "MCSectionViewController"
        elif entry["type"] == "view":
            template = "TemplateViewController.%s.template"
            base_class = "MCViewController"
        else:
            print "Unknown type - " + entry["type"]
            continue

        # need to check special cases for MCMain and MCError
        if entry["mapped_to"] == "MCMain":
            base_class = "MCMainViewController"
        elif entry["mapped_to"] == "MCError":
            base_class = "MCErrorViewController"

        # define variable names to replace in the template file
        # if variable names are in the template and not listed here, they won't be replaced
        dict = {"viewName" : entry["mapped_to"],
                "projectName" : get_project_name_from_dir(),
                "date" : date.today().isoformat(),
                "year" : date.today().year,
                "baseClass" : base_class, }

        # create the files
        template_dir = os.path.dirname(os.path.realpath(__file__)) + "/"
        for ext in ("xib", "h", "m"):
            if check_file_exists(entry["mapped_to"], "." + ext):
                first_choice = entry["mapped_to"] + "." + ext
                actual_file = which_file_exists(entry["mapped_to"], "." + ext)
                if first_choice != actual_file:
                    logging.warning("Skipping %s because of %s" % (first_choice, actual_file))
                else:
                    logging.warning("Skipping %s" % first_choice)
            else:
                logging.info("Writing " + entry["mapped_to"] + "." + ext)
                replace_in_file(template_dir + (template % ext), entry["mapped_to"] + "." + ext, dict)


def main_script(schema_file, prefix, mode):
    (sections, views) = parse_view_schema(schema_file, prefix, mode)

    create_templates_from_schema(sections)
    create_templates_from_schema(views)
    print

    print "// Include the following lines in a reusable header file"
    write_define(sections)
    write_define(views)
    print
    print "// Include the following lines in application:didFinishLaunchingWithOptions:"
    print "MCViewFactory *factory = [MCViewFactory sharedFactory];"
    write_register(sections)
    write_register(views)

if len(sys.argv) != 4:
    print "Usage: %s <schema_file> <file_prefix> {short|long}" % sys.argv[0]
    print "       where short suffix is VC and long suffix is ViewController"
else:
    main_script(sys.argv[1], sys.argv[2], sys.argv[3])
