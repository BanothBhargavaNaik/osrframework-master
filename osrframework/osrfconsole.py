#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
################################################################################
#
#    Copyright 2016-2017 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This program is part of OSRFramework. You can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################


__author__ = "Felix Brezo, Yaiza Rubio "
__copyright__ = "Copyright 2016-2017, i3visio"
__credits__ = ["Felix Brezo", "Yaiza Rubio"]
__license__ = "AGPLv3+"
__version__ = "v6.0"
__maintainer__ = "Felix Brezo, Yaiza Rubio"
__email__ = "contacto@i3visio.com"


import argparse
import cmd as cmd
import json
import os
import sys

import osrframework.utils.configuration as configuration
import osrframework.utils.banner as banner
import osrframework.utils.general as general
import osrframework.utils.platform_selection as platform_selection
import osrframework.utils.regexp_selection as regexp_selection

import osrframework.domainfy as domainfy
import osrframework.entify as entify
import osrframework.mailfy as mailfy
import osrframework.phonefy as phonefy
import osrframework.searchfy as searchfy
import osrframework.usufy as usufy

UTILS = [
    "domainfy",
    "entify", #: regexp_selection.getAllRegexpNames(),
    "mailfy", # mailfy.EMAIL_DOMAINS,
    "phonefy",
    "searchfy",
    "usufy", # platform_selection.getAllPlatformNames("usufy"),
]

################################################################################
# Defining the abstract class of the utils that will be managed                #
################################################################################

class OSRFConsoleUtil(cmd.Cmd):
    """
    Simple class from which of a msfconsole-like interactive interface
    """
    # Setting up the name of the module
    UNAME = "Abstract Util"

    intro = ""
    # Defining the prompt
    prompt = 'osrf (' + UNAME + ') > '
    # Defining the character to create hyphens
    ruler = '-'

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["OPTION"] = {
        "DESCRIPTION" : "An example of option.",
        "CURRENT_VALUE" : "Hello",
        "DEFAULT_VALUE" : "Hello",
        "REQUIRED" : False,
        "OPTIONS" : ["world", "people"]
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : "./",
        "DEFAULT_VALUE" : "./",
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : "csv",
        "DEFAULT_VALUE" : "csv",
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }

    def _checkIfRequiredAreSet(self):
        """
        Internal function to check if the required parameters have been set
        """
        details = ""
        for key in self.CONFIG.keys():
            if self.CONFIG[key]["REQUIRED"] and self.CONFIG[key]["CURRENT_VALUE"] == None:
                return False
        return True

    def _getOptionsDescription(self):
        """
        Internal function to collect the description of each and every parameter

        Returns:
        --------
            string: a string containing the description of each option.
        """
        details = ""
        for key in self.CONFIG.keys():
            details += "\t- " + key + ". " + self.CONFIG[key]["DESCRIPTION"] + "\n"
        return details

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = ["-h"]
        return params

    def do_set(self, line):
        """
        Setting the variables defined in CONFIG

        You can check their values at any time by typing 'show options'.

        Args:
        -----
            line: the string of the line typed.
        """
        try:
            parameter, value = line.split(" ", 1)
            # Setting the parameter
            if parameter in self.CONFIG.keys():
                # Verifying if the parameter is in the options
                if len(self.CONFIG[parameter]["OPTIONS"]) > 0:
                    splittedValues = value.split(" ")

                    for s in splittedValues:
                        if s not in self.CONFIG[parameter]["OPTIONS"]:
                            raise Exception("ERROR: the value provided is not valid.")
                # Setting the value
                self.CONFIG[parameter]["CURRENT_VALUE"] = value
                print(general.info(parameter + "=" + str(value)))
            else:
                raise Exception("ERROR: parameter not valid.")
        except Exception as e:
            print(general.error("[!] ERROR: Not enough parameters provided. Usage: set OPTION VALUE."))
            print(general.error(str(e)))

    def complete_set(self, text, line, begidx, endidx):
        # First, we will try to get the available parameters
        if len(line.split(" ")) == 2:
            if not text:
                completions = self.CONFIG.keys()
            else:
                completions = [ f
                    for f in self.CONFIG.keys()
                    if f.startswith(text.upper())
                ]
        # We are setting the value
        elif len(line.split(" ")) >= 3:
            # First, we get the given parameter
            parameter = line.split(" ")[1]
            if not text:
                completions = self.CONFIG[parameter]["OPTIONS"]
            else:
                completions = [ f
                    for f in self.CONFIG[parameter]["OPTIONS"]
                    if f.startswith(text.lower())
                ]
        return completions

    def do_unset(self, line):
        """
        Unsetting the variables defined in CONFIG

        You can check their values at any time by typing 'show options' and
        unsetting all the options at once by typing 'unset all'.

        Args:
        -----
            line: the string of the line typed.

        Raises:
        -------
            ValueError: if the parameter is not valid.
        """
        try:
            parameter = line.split(" ")[0]
            # Getting the parameter
            if parameter in self.CONFIG.keys():
                # Unsetting the value
                self.CONFIG[parameter]["CURRENT_VALUE"] = self.CONFIG[parameter]["DEFAULT_VALUE"]
                print(general.info(parameter + " reseted to '" + str(self.CONFIG[parameter]["DEFAULT_VALUE"]) + "'."))
            elif parameter == "all":
                for p in self.CONFIG.keys():
                    # Unsetting all the values
                    self.CONFIG[p]["CURRENT_VALUE"] = self.CONFIG[p]["DEFAULT_VALUE"]
                print(general.info("All parameters reseted to their default values."))
            else:
                raise ValueError("ERROR: parameter not valid.")
        except Exception as e:
            print(gemeral.error("[!] ERROR: Not enough parameters provided. Usage: unset OPTION"))
            print(general.error("Traceback: " + str(e)))

    def complete_unset(self, text, line, begidx, endidx):
        # First, we will try to get the available parameters
        unsettingOptions = ["all"] + self.CONFIG.keys()

        if len(line.split(" ")) == 2:
            if not text:
                completions = unsettingOptions
            else:
                completions = [ f
                    for f in unsettingOptions
                    if f.startswith(text.upper())
                ]
        return completions

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        if self._checkIfRequiredAreSet():
            print(general.info("Launching the util..."))
        else:
            print(general.error("There are required parameters which have not been set."))
            self.do_show("options")

    def do_show(self, line):
        """
        Showing the information about the module

        The things to show are: 'options' and 'command'.
            - 'options' will show the current values of each and every
                parameter.
            - 'command' will show the command needed to launch the module as is
                using the cli applications.

        Args:
        -----
            line: the string of the line typed.
        """
        if line.lower() == "options":
            print(general.info("Defining the different options for util " + self.UNAME + "..."))
            for key in self.CONFIG.keys():
                print(general.info("\t- " + (key + (" (*)." if self.CONFIG[key]["REQUIRED"] else ".") ).ljust(14) + "" + self.CONFIG[key]["DESCRIPTION"]))

            print(general.info("Showing the current state of the options for util " + self.UNAME + "..."))
            for key in self.CONFIG.keys():
                print(general.info("\t- " + (key + (" (*)" if self.CONFIG[key]["REQUIRED"] else "") + ": ").ljust(14) + ("" if self.CONFIG[key]["CURRENT_VALUE"] == None else str(self.CONFIG[key]["CURRENT_VALUE"]))))
        elif line.lower() == "command":
            print(general.info("Equivalent command to be launched to imitate the current configuration:\n\t$ ") + general.title(self.createCommandLine()) + "\n")

    def complete_show(self, text, line, begidx, endidx):
        # First, we will try to get the available parameters
        showOptions = ["options", "command"]

        if len(line.split(" ")) == 2:
            if not text:
                completions = showOptions
            else:
                completions = [ f
                    for f in showOptions
                    if f.startswith(text.lower())
                ]
        return completions

    def createCommandLine(self):
        """
        Method to build the command line command

        This method will build the command to run the same actions defined in
        using this tool.

        Returns:
        --------
            String: the string to type in the terminal
        """
        if self._checkIfRequiredAreSet():
            command = self.UNAME
            # Getting the params
            params = self._getParams()
            for p in params:
                command += " " +p
            # Returning the command
            return command
        else:
            return self.UNAME + " -h  # NOTE: all the required parameters are not set. Option '-h' is being shown."

    def do_info(self, line):
        """
        Shows all the information available about the module.

        Args:
        -----
            line: the string of the line typed.
        """
        print(general.info("Displaying module information."))
        self.do_show("options")
        self.do_show("command")

    def do_back(self, line):
        """
        Command to unload the current util and goes back to the main console

        Args:
        -----
            line: the string of the line typed.
        """
        return True

    def do_exit(self, line):
        """
        This command will exit the osrfconsole normally

        Args:
        -----
            line: the string of the line typed.
        """
        print(general.info("Exiting the program..."))
        sys.exit()

"""
     _                       _        __
  __| | ___  _ __ ___   __ _(_)_ __  / _|_   _
 / _` |/ _ \| '_ ` _ \ / _` | | '_ \| |_| | | |
| (_| | (_) | | | | | | (_| | | | | |  _| |_| |
 \__,_|\___/|_| |_| |_|\__,_|_|_| |_|_|  \__, |
                                         |___/
"""


################################################################################
# Defining the class that will create the calls to the domainfy util.          #
################################################################################

class OSRFConsoleDomainfy(OSRFConsoleUtil):
    """
    Class that controls an interactive domainfy program
    """
    # Setting up the name of the module
    UNAME = "domainfy.py"

    intro = ""
    # Defining the prompt
    prompt = general.emphasis('osrf (' + UNAME.split('.')[0] + ') > ')
    # Defining the character to create hyphens
    ruler = '-'

    DEFAULT_VALUES = configuration.returnListOfConfigurationValues("domainfy")

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["NICK"] = {
        "DESCRIPTION" : "Nick to be verified.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : True,
        "OPTIONS" : []
    }
    CONFIG["TLD"] = {
        "DESCRIPTION" : "Types of TLD to be verified",
        "CURRENT_VALUE" : DEFAULT_VALUES["tlds"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["tlds"],
        "REQUIRED" : False,
        "OPTIONS" : domainfy.TLD.keys(),
    }
    CONFIG["THREADS"] = {
        "DESCRIPTION" : "Number of threads to use.",
        "CURRENT_VALUE" : DEFAULT_VALUES["threads"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["threads"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : DEFAULT_VALUES["output_folder"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["output_folder"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : DEFAULT_VALUES["extension"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["extension"],
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }
    CONFIG["USER_DEFINED"] = {
        "DESCRIPTION" : "Other TLD to be verified. Note that it should start with a '.'.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : False,
        "OPTIONS" : [],
    }

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = [
            "-n" ] + self.CONFIG["NICK"]["CURRENT_VALUE"].split() + [
            "-t" ] + self.CONFIG["TLD"]["CURRENT_VALUE"].split() + [
            "-T", str(self.CONFIG["THREADS"]["CURRENT_VALUE"]),
            "-o", self.CONFIG["OUTPUT"]["CURRENT_VALUE"],
            "-e" ] + self.CONFIG["EXTENSION"]["CURRENT_VALUE"].split()

        # Appending new tlds if provided
        if self.CONFIG["USER_DEFINED"]["CURRENT_VALUE"] != None:
            params += [ "-u", self.CONFIG["USER_DEFINED"]["CURRENT_VALUE"] ]
        return params

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        # Checking if all the required parameters have been set
        if self._checkIfRequiredAreSet():
            print(general.info("Collecting the options set by the user..."))
            # Getting the parser...
            parser = domainfy.getParser()

            # Generating the parameters
            params = self._getParams()

            args = parser.parse_args(params)

            print(general.info("Launching " + self.UNAME + " with the following parameters: ") + general.emphashis(str(params)))

            try:
                usufy.main(args)
            except Exception as e:
                print(gemeral.error("[!] ERROR. Something happenned when launching the utility. Type 'show options' to check the parameters. "))
                print(general.error("Traceback: " + str(e)))
        else:
            print(general.error("[!] ERROR. There are required parameters which have not been set."))
            self.do_show("options")
        print(general.success("Execution ended successfully."))

"""
================================================================================
            _   _  __
  ___ _ __ | |_(_)/ _|_   _
 / _ \ '_ \| __| | |_| | | |
|  __/ | | | |_| |  _| |_| |
 \___|_| |_|\__|_|_|  \__, |
                      |___/
================================================================================
"""

################################################################################
# Defining the class that will create the calls to the entify util.            #
################################################################################

class OSRFConsoleEntify(OSRFConsoleUtil):
    """Class that controls an interactive entify program."""
    # Setting up the name of the module
    UNAME = "entify.py"

    intro = ""
    # Defining the prompt
    prompt = 'osrf (' + UNAME.split('.')[0] + ') > '
    # Defining the character to create hyphens
    ruler = '-'

    DEFAULT_VALUES = configuration.returnListOfConfigurationValues("entify")

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["URL"] = {
        "DESCRIPTION" : "The URL to be checked.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : True,
        "OPTIONS" : []
    }
    CONFIG["REGEXP"] = {
        "DESCRIPTION" : "The regular expressions to be checked.",
        "CURRENT_VALUE" : "all",
        "DEFAULT_VALUE" : "all",
        "REQUIRED" : False,
        "OPTIONS" : regexp_selection.getAllRegexpNames(),
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : DEFAULT_VALUES["output_folder"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["output_folder"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : DEFAULT_VALUES["extension"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["extension"],
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = [
            "-u", self.CONFIG["URL"]["CURRENT_VALUE"],
            "-r" ] + self.CONFIG["REGEXP"]["CURRENT_VALUE"].split() + [
            "-o", self.CONFIG["OUTPUT"]["CURRENT_VALUE"],
            "-e" ] + self.CONFIG["EXTENSION"]["CURRENT_VALUE"].split()

        return params

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        # Checking if all the required parameters have been set
        if self._checkIfRequiredAreSet():
            print(general.info("Collecting the options set by the user..."))
            # Getting the parser...
            parser = entify.getParser()

            # Generating the parameters
            params = self._getParams()

            args = parser.parse_args(params)

            print(general.info("Launching " + self.UNAME + " with the following parameters: ") + general.emphashis(str(params)))

            try:
                usufy.main(args)
            except Exception as e:
                print(gemeral.error("[!] ERROR. Something happened when launching the utility. Type 'show options' to check the parameters. "))
                print(general.error("Traceback: " + str(e)))
        else:
            print(general.error("[!] ERROR. There are required parameters which have not been set."))
            self.do_show("options")
        print(general.success("Execution ended successfully."))

"""
================================================================================
                 _ _  __
 _ __ ___   __ _(_) |/ _|_   _
| '_ ` _ \ / _` | | | |_| | | |
| | | | | | (_| | | |  _| |_| |
|_| |_| |_|\__,_|_|_|_|  \__, |
                         |___/
================================================================================
"""

################################################################################
# Defining the class that will create the calls to the mailfy util.             #
################################################################################

class OSRFConsoleMailfy(OSRFConsoleUtil):
    """Class that controls an interactive mailfy program."""
    # Setting up the name of the module
    UNAME = "mailfy.py"

    intro = ""
    # Defining the prompt
    prompt = 'osrf (' + UNAME.split('.')[0] + ') > '
    # Defining the character to create hyphens
    ruler = '-'

    DEFAULT_VALUES = configuration.returnListOfConfigurationValues("mailfy")

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["NICK"] = {
        "DESCRIPTION" : "Alias to be verified.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : True,
        "OPTIONS" : []
    }
    CONFIG["PLATFORMS"] = {
        "DESCRIPTION" : "Platforms to be checked.",
        "CURRENT_VALUE" : DEFAULT_VALUES["domains"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["domains"],
        "REQUIRED" : False,
        "OPTIONS" : mailfy.EMAIL_DOMAINS,
    }
    CONFIG["THREADS"] = {
        "DESCRIPTION" : "Number of threads to use.",
        "CURRENT_VALUE" : DEFAULT_VALUES["threads"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["threads"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : DEFAULT_VALUES["output_folder"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["output_folder"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : DEFAULT_VALUES["extension"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["extension"],
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = [
            "-n" ] + self.CONFIG["NICK"]["CURRENT_VALUE"].split() + [
            "-p" ] + self.CONFIG["PLATFORMS"]["CURRENT_VALUE"].split() + [
            "-T", str(self.CONFIG["THREADS"]["CURRENT_VALUE"]),
            "-o", self.CONFIG["OUTPUT"]["CURRENT_VALUE"],
            "-e" ] + self.CONFIG["EXTENSION"]["CURRENT_VALUE"].split()

        return params

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        # Checking if all the required parameters have been set
        if self._checkIfRequiredAreSet():
            print(general.info("Collecting the options set by the user..."))
            # Getting the parser...
            parser = mailfy.getParser()

            # Generating the parameters
            params = self._getParams()

            args = parser.parse_args(params)

            print(general.info("Launching " + self.UNAME + " with the following parameters: ") + general.emphashis(str(params)))

            try:
                usufy.main(args)
            except Exception as e:
                print(gemeral.error("[!] ERROR. Something happenned when launching the utility. Type 'show options' to check the parameters. "))
                print(general.error("Traceback: " + str(e)))
        else:
            print(general.error("[!] ERROR. There are required parameters which have not been set."))
            self.do_show("options")
        print(general.success("Execution ended successfully."))

"""
================================================================================
       _                       __
 _ __ | |__   ___  _ __   ___ / _|_   _
| '_ \| '_ \ / _ \| '_ \ / _ \ |_| | | |
| |_) | | | | (_) | | | |  __/  _| |_| |
| .__/|_| |_|\___/|_| |_|\___|_|  \__, |
|_|                               |___/
================================================================================
"""

################################################################################
# Defining the class that will create the calls to the phonefy util.          #
################################################################################

class OSRFConsolePhonefy(OSRFConsoleUtil):
    """Class that controls an interactive phonefy program."""
    # Setting up the name of the module
    UNAME = "phonefy.py"

    intro = ""
    # Defining the prompt
    prompt = 'osrf (' + UNAME.split('.')[0] + ') > '
    # Defining the character to create hyphens
    ruler = '-'

    DEFAULT_VALUES = configuration.returnListOfConfigurationValues("phonefy")

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["NUMBER"] = {
        "DESCRIPTION" : "Numbers to be verified.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : True,
        "OPTIONS" : []
    }
    CONFIG["PLATFORMS"] = {
        "DESCRIPTION" : "Platforms to be checked.",
        "CURRENT_VALUE" : DEFAULT_VALUES["platforms"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["platforms"],
        "REQUIRED" : False,
        "OPTIONS" : platform_selection.getAllPlatformNames("phonefy"),
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : DEFAULT_VALUES["output_folder"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["output_folder"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : DEFAULT_VALUES["extension"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["extension"],
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = [
            "-n" ] + self.CONFIG["NICK"]["CURRENT_VALUE"].split() + [
            "-p" ] + self.CONFIG["PLATFORMS"]["CURRENT_VALUE"].split() + [
            "-o", self.CONFIG["OUTPUT"]["CURRENT_VALUE"],
            "-e" ] + self.CONFIG["EXTENSION"]["CURRENT_VALUE"].split()

        return params

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        print
        # Checking if all the required parameters have been set
        if self._checkIfRequiredAreSet():
            print(general.info("Collecting the options set by the user..."))
            # Getting the parser...
            parser = phonefy.getParser()

            # Generating the parameters
            params = self._getParams()

            args = parser.parse_args(params)

            print(general.info("Launching " + self.UNAME + " with the following parameters: ") + general.emphashis(str(params)))

            try:
                usufy.main(args)
            except Exception as e:
                print(gemeral.error("[!] ERROR. Something happenned when launching the utility. Type 'show options' to check the parameters. "))
                print(general.error("Traceback: " + str(e)))
        else:
            print(general.error("[!] ERROR. There are required parameters which have not been set."))
            self.do_show("options")
        print(general.success("Execution ended successfully."))

"""
================================================================================
                         _      __
 ___  ___  __ _ _ __ ___| |__  / _|_   _
/ __|/ _ \/ _` | '__/ __| '_ \| |_| | | |
\__ \  __/ (_| | | | (__| | | |  _| |_| |
|___/\___|\__,_|_|  \___|_| |_|_|  \__, |
                                   |___/
================================================================================
"""

################################################################################
# Defining the class that will create the calls to the searchfy util.          #
################################################################################

class OSRFConsoleSearchfy(OSRFConsoleUtil):
    """Class that controls an interactive searchfy program"""
    # Setting up the name of the module
    UNAME = "searchfy.py"

    intro = ""
    # Defining the prompt
    prompt = 'osrf (' + UNAME.split('.')[0] + ') > '
    # Defining the character to create hyphens
    ruler = '-'

    DEFAULT_VALUES = configuration.returnListOfConfigurationValues("searchfy")

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["QUERY"] = {
        "DESCRIPTION" : "Query to be verified. Escape \" and \'.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : True,
        "OPTIONS" : []
    }
    CONFIG["PLATFORMS"] = {
        "DESCRIPTION" : "Platforms to be checked.",
        "CURRENT_VALUE" : DEFAULT_VALUES["platforms"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["platforms"],
        "REQUIRED" : False,
        "OPTIONS" : platform_selection.getAllPlatformNames("searchfy"),
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : DEFAULT_VALUES["output_folder"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["output_folder"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : DEFAULT_VALUES["extension"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["extension"],
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = [
            "-q" ] + self.CONFIG["QUERY"]["CURRENT_VALUE"].split() + [
            "-p" ] + self.CONFIG["PLATFORMS"]["CURRENT_VALUE"].split() + [
            "-o", self.CONFIG["OUTPUT"]["CURRENT_VALUE"],
            "-e" ] + self.CONFIG["EXTENSION"]["CURRENT_VALUE"].split()

        return params

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        # Checking if all the required parameters have been set
        if self._checkIfRequiredAreSet():
            print(general.info("Collecting the options set by the user..."))
            # Getting the parser...
            parser = searchfy.getParser()

            # Generating the parameters
            params = self._getParams()

            args = parser.parse_args(params)

            print(general.info("Launching " + self.UNAME + " with the following parameters: ") + general.emphashis(str(params)))

            try:
                usufy.main(args)
            except Exception as e:
                print(gemeral.error("[!] ERROR. Something happenned when launching the utility. Type 'show options' to check the parameters. "))
                print(general.error("Traceback: " + str(e)))
        else:
            print(general.error("[!] ERROR. There are required parameters which have not been set."))
            self.do_show("options")
        print(general.success("Execution ended successfully."))

"""
================================================================================
                      __
     _   _ ___ _   _ / _|_   _
    | | | / __| | | | |_| | | |
    | |_| \__ \ |_| |  _| |_| |
     \__,_|___/\__,_|_|  \__, |
                         |___/
================================================================================
"""

################################################################################
# Defining the class that will create the calls to the usufy util.             #
################################################################################

class OSRFConsoleUsufy(OSRFConsoleUtil):
    """Class that controls an interactive usufy program"""
    # Setting up the name of the module
    UNAME = "usufy.py"

    intro = ""
    # Defining the prompt
    prompt = general.emphasis('osrf (' + UNAME.split('.')[0] + ') > ')
    # Defining the character to create hyphens
    ruler = '-'

    DEFAULT_VALUES = configuration.returnListOfConfigurationValues("usufy")

    # Defining the configuration for this module
    CONFIG = {}
    CONFIG["NICK"] = {
        "DESCRIPTION" : "Alias to be verified.",
        "CURRENT_VALUE" : None,
        "DEFAULT_VALUE" : None,
        "REQUIRED" : True,
        "OPTIONS" : []
    }
    CONFIG["PLATFORMS"] = {
        "DESCRIPTION" : "Platforms to be checked.",
        "CURRENT_VALUE" : DEFAULT_VALUES["platforms"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["platforms"],
        "REQUIRED" : False,
        "OPTIONS" : platform_selection.getAllPlatformNames("usufy"),
    }
    CONFIG["THREADS"] = {
        "DESCRIPTION" : "Number of threads to use.",
        "CURRENT_VALUE" : DEFAULT_VALUES["threads"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["threads"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["OUTPUT"] = {
        "DESCRIPTION" : "The path to the output folder where the files will be created.",
        "CURRENT_VALUE" : DEFAULT_VALUES["output_folder"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["output_folder"],
        "REQUIRED" : False,
        "OPTIONS" : []
    }
    CONFIG["EXTENSION"] = {
        "DESCRIPTION" : "The default extension of the files to be written.",
        "CURRENT_VALUE" : DEFAULT_VALUES["extension"],
        "DEFAULT_VALUE" : DEFAULT_VALUES["extension"],
        "REQUIRED" : False,
        "OPTIONS" : ['csv', 'xls', 'xlsx', 'json', 'gml']
    }

    def _getParams(self):
        """
        Function that creates the array with the params of this function

        Returns:
        --------
            list: a list of the params that can be used
        """
        # Creating the parameters as if they were created using the command line
        params = [
            "-n" ] + self.CONFIG["NICK"]["CURRENT_VALUE"].split() + [
            "-p" ]  +  self.CONFIG["PLATFORMS"]["CURRENT_VALUE"].split() + [
            "-T", str(self.CONFIG["THREADS"]["CURRENT_VALUE"]),
            "-o", self.CONFIG["OUTPUT"]["CURRENT_VALUE"],
            "-e" ] + self.CONFIG["EXTENSION"]["CURRENT_VALUE"].split()

        return params

    def do_run(self, line):
        """
        Command that send the order to the framework to launch this util

        Args:
        -----
            line: the string of the line typed.
        """
        # Checking if all the required parameters have been set
        if self._checkIfRequiredAreSet():
            print(general.info("Collecting the options set by the user..."))
            # Getting the parser...
            parser = usufy.getParser()

            # Generating the parameters
            params = self._getParams()

            args = parser.parse_args(params)

            print(general.info("Launching " + self.UNAME + " with the following parameters: ") + general.emphashis(str(params)))

            try:
                usufy.main(args)
            except Exception as e:
                print(gemeral.error("[!] ERROR. Something happenned when launching the utility. Type 'show options' to check the parameters. "))
                print(general.error("Traceback: " + str(e)))
        else:
            print(general.error("[!] ERROR. There are required parameters which have not been set."))
            self.do_show("options")
        print(general.success("Execution ended successfully."))


"""
================================================================================
                     __                           _
      ___  ___ _ __ / _| ___ ___  _ __  ___  ___ | | ___
     / _ \/ __| '__| |_ / __/ _ \| '_ \/ __|/ _ \| |/ _ \
    | (_) \__ \ |  |  _| (_| (_) | | | \__ \ (_) | |  __/
     \___/|___/_|  |_|  \___\___/|_| |_|___/\___/|_|\___|

================================================================================
"""
################################################################################
# Main osrfconsole wrapper. It will control the rest of the utils.             #
################################################################################

class OSRFConsoleMain(cmd.Cmd):
    """
    OSRFramework console application to control the different framework utils

    The user can type 'help' at any time to find the available commands included
    in the framework.
    """

    DISCLAIMER = """\tOSRFConsole """ + __version__ + """ - Copyright (C) F. Brezo and Y. Rubio (i3visio) 2016-2017

    This program comes with ABSOLUTELY NO WARRANTY. This software is free software,
    and you are really welcome to redistribute it under certain conditions. For
    additional information about the terms and conditions of the AGPLv3+ license,
    visit <http://www.gnu.org/licenses/agpl-3.0.txt>."""

    intro = banner.text + "\n" + DISCLAIMER + "\n\n"

    info  = """    General information
    ===================

    OSRFramework stands for Open Sources Research Framework. It includes a set
    of tools that help the analyst in the task of user profiling making use of
    different OSINT tools.

    To get additional information about the available commands type 'help'.

    Modules available:
    ------------------

        - usufy --> the Jewel of the Chrown. A tool that verifies if a
            username exists in """ + str(len(platform_selection.getAllPlatformNames("usufy")))  + """ platforms.
        - mailfy --> a tool to check if a username has been registered in up to
            """ + str(len(mailfy.EMAIL_DOMAINS )) + """ email providers.
        - searchfy --> a tool to look for profiles using full names and other
            info in """ + str(len(platform_selection.getAllPlatformNames("searchfy")))  + """ platforms.
        - domainfy --> a tool to check the existence of a given domain in up to
            """ + str(domainfy.getNumberTLD()) + """ different TLDs.
        - phonefy --> a tool that checks if a phone number has been linked to
            spam practices in """ + str(len(platform_selection.getAllPlatformNames("phonefy")))  + """ platforms.
        - entify --> a util to look for regular expressions using """ + str(len(regexp_selection.getAllRegexpNames())) + """ patterns.
    """

    # Appending the self.info data to the headers...
    intro += info

    # Defining the prompt
    prompt = general.emphasis('osrf > ')

    ruler = '='

    def do_info(self, line):
        """
        Command that shows again the general information about the application

        Args:
        -----
            line: the string of the line typed.
        """
        configInfo =  """
    Additional configuration files:
    -------------------------------

    You will be able to find more configuration options in the following files
    in your system. The relevant paths are the ones that follow:"""
        # Get the configuration folders in each system
        paths = configuration.getConfigPath()

        configInfo += """
        - Configuration details about the login credentials in OSRFramework:
            """  + os.path.join(paths["appPath"], "accounts.cfg") + """
        - Configuration details about the API credentials already configured:
            """  + os.path.join(paths["appPath"], "api_keys.cfg") + """
        - Connection configuration about how the browsers will be connected:
            """  + os.path.join(paths["appPath"], "browser.cfg") + """
        - General default configuration of the the utils:
            """  + os.path.join(paths["appPath"], "general.cfg") + """
        - Directory containing default files as a backup:
            """  + paths["appPathDefaults"] + """
        - Directory containing the user-defined patterns for entify.py:
            """  + paths["appPathPatterns"] + """
        - Directory containing the user-defined wrappers for usufy platforms:
            """  + paths["appPathWrappers"]
        print(general.info(self.info) + general.info(configInfo))

    def do_use(self, line):
        """
        This command will define which of the framework's utilities will be loaded.

        The available options are the following:
            - domainfy
            - entify
            - mailfy
            - phonefy
            - searchfy
            - usufy
        For example, type 'use usufy' to load the usufy util. You can always use
        the <TAB> to be helped using the autocomplete options.

        Args:
        -----
            line: the string of the line typed.
        """
        if line not in UTILS:
            print(general.warning("[!] Util is not correct. Try 'help use' to check the available options."))
            return False
        elif line == "domainfy":
            OSRFConsoleDomainfy().cmdloop()
        elif line == "entify":
            OSRFConsoleEntify().cmdloop()
        elif line == "mailfy":
            OSRFConsoleMailfy().cmdloop()
        elif line == "phonefy":
            OSRFConsolePhonefy().cmdloop()
        elif line == "searchfy":
            OSRFConsoleSearchfy().cmdloop()
        elif line == "usufy":
            OSRFConsoleUsufy().cmdloop()
        else:
            print(general.warning("[!] Not implemented yet. Try 'help use' to check the available options."))

    def complete_use(self, text, line, begidx, endidx):
        if not text:
            completions = UTILS
        else:
            completions = [ f
                for f in UTILS
                if f.startswith(text.lower())
            ]
        return completions

    def do_exit(self, line):
        """
        This command will exit the osrfconsole normally

        Args:
        -----
            line: the string of the line typed.
        """
        print(general.info("Exiting..."))
        sys.exit()


if __name__ == '__main__':
    OSRFConsoleMain().cmdloop()
