Manticore iOS View Generator
============================

Manticore iOS View Generator is a script to help create iOS applications using Manticore's iOS View Factory.

Installation
------------

Checkout this project from git into a working directory on your computer.

Basic Usage
-----------

1. This script should be run from your project directory where `.h`, `.m`, and `.xib` files are stored.

2. Run the following command:

    `python ~/path/to/createviews.py view_schema.txt prefix {short|long}`

where

  * view_schema.txt: conforms to a schema definition, shown below
  * prefix: any uppercase two-letter combination that uniquely identifies your project
  * {short|long}: a choice of suffix. Short suffix is `VC`. Long suffix is `ViewController`.

When the script runs, it will create all  the `.h`, `.m`, and `.xib` files. The developer will have 
to drag-and-drop these files into the .xbproj in XCode. If existing files exist, they will not be
overwritten. The script will check for both long and short forms and not duplicate files.

The developer will also copy-and-paste the console output into a `.h` file for `#define` and 
`:application:application:didFinishLaunchingWithOptions` for `[factory registerView:]`.

Schema Definition
-----------------

The schema file is a plain text file in the following format, shown below:

    Section1:
       View1A
       View1B

    Section2:
       View2A
       View2B

Sections should correspond to a user interface's hierarchical views. Sections correspond to tabs in an application. Prefixes and suffixes should be omitted.

A single-level hierarchy should be created with one section and several views.

