# Manticore iOSViewFactory Framework
# March 2013, rhfung
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
                    sections.append({ "type" : "section", "variable_name": "SECTION_"  + string.upper(vc_name), "mapped_to" : filepart })
                else:
                    views.append({ "type" : "view", "variable_name": "VIEW_" + string.upper(vc_name), "mapped_to" : filepart })

    return sections, views


def parse_view_schema(filename, prefix="", length="long"):
    SECTION_SUFFIX = "SectionViewController"
    VIEW_SUFFIX = "ViewController"

    sections = []
    views = []

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
            pos = line.find("SectionViewController")
            if pos <= 0:
                pos = line.find("ViewController")

            if pos <= 0: # default, only the unique name is provided
                pos = len(line)
                if length=="long":
                    if is_section: # append the decscriptive full name as necessary
                        line = line + "SectionViewController"
                    else:
                        line = line + "ViewController"
                else:
                    if is_section: # append the decscriptive full name as necessary
                        line = line + "SectionVC"
                    else:
                        line = line + "VC"


            # identify the unique name
            vc_name = prefix_remover(line[0:pos], prefix)
            vc_name = special_names(vc_name)

            if is_section or line[-len(SECTION_SUFFIX):].lower() == SECTION_SUFFIX.lower():
                sections.append({ "type" : "section", "variable_name": "SECTION_"  + string.upper(vc_name), "mapped_to" : prefix + line })
            else:
                views.append({ "type" : "view", "variable_name": "VIEW_" + string.upper(vc_name), "mapped_to" : prefix + line })

            # read the next line
            line = f.readline()


    return sections, views

def replace_in_file(template, output, dict):

    if os.path.isfile(output):
        print "Skipping " + output
        return False

    print "Creating " + output

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
        for ext in ("xib", "h", "m"):
            replace_in_file(template % ext, entry["mapped_to"] + "." + ext, dict)

#(sections, views) = walk_directory("WM")

def main_script(schema, prefix, mode):

    (sections, views) = parse_view_schema("view_schema.txt", "WM", "short")

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
