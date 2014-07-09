Manticore iOS View Generator
============================

Manticore iOS View Generator is a script to help create iOS applications using Manticore's iOS View Factory.

Reading a schema provided by the developer, this script does three things:

One: Generates all `.h`, `.m` and `.xib` files in a user speciified sub-directory.
Two: Creates a `.h` file containing all the constants needed for use with MCIntent
Three: Adds a method to the {Prefix}AppDelegate.m file to register all the VCs for the app.

Installation:
------------

Checkout this project from git into a working directory on your computer.

Basic Usage:
-----------

1. This script should be run from your project directory where you want the `.h`, `.m`, and `.xib` files to be stored. The directory should also must contain your AppDelegate.

2. Run the following command:

    `python ~/path/to/createviews.py view_schema.txt prefix {short|long}`
    
    Note: The script will be looking for a file "Prefix"AppDelegate.m, so, make sure you are using the same prefix.

where

  * view_schema.txt: conforms to a schema definition, shown below
  * prefix: any uppercase two-letter combination that uniquely identifies your project
  * {short|long}: a choice of suffix. Short suffix is `VC`. Long suffix is `ViewController`.

When the script runs, it will create all  the `.h`, `.m`, and `.xib` files in the sub-directory you provide to the script. The developer will have to drag-and-drop these files into the .xbproj in XCode after they have generated. If existing files exist, they will not be overwritten. The script will check for both long and short forms and not duplicate files.

In the - (BOOL)application:(UIApplication *)application didFinishLaunchingWithOptions:(NSDictionary *)launchOptions method, the user will need to add this line of code to actually registering all the VCs:

[self registerVCs];

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

