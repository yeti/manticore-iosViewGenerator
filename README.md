Manticore iOS View Generator
============================

manticore-iosviewgenerator is a script to help create iOS applications using Manticore's iOSViewFactory.

Installation
------------

Copy and paste the .py script and .template into the working directory of your project.

Basic Usage
-----------

    python manticore-iosviewgenerator.py view_schema.txt prefix short/long

where

  * view_schema.txt: conforms to a schema definition, shown below
  * prefix: any two-letter combination that uniquely identifies your project
  * short/long: a choice of suffix. Short suffix is VC. Long suffix is ViewController.

When the script runs, it will create all  the .h, .m, and .xib files. The developer will have to drag-and-drop
these files into the .xbproj in XCode.

The developer will also copy-and-paste the console output into a .h file for `#define` and 
YourAppDelegate.h `:application:application:didFinishLaunchingWithOptions` for `[factory registerView:]`.

Schema Definition
-----------------

The schema file is a plain text file in the following format, shown below:

    Section1:
       View1A
       View1B

    Section2:
       View2A
       View2B

Sections should correspond to a user interface's tabs and views should correspond to the pages
seens within a tab. Prefixes and suffixes are not included in the schema definition.

Sections can also be shown without any views if a single-level hierarchy, but to keep consistency
a single view should be created for that section.


