# !/usr/bin/python
# -*- coding: cp1252 -*-
#
##################################################################################
#
#    Copyright 2015 Félix Brezo and Yaiza Rubio (i3visio, contacto@i3visio.com)
#
#    This program is part of OSRFramework. You can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##################################################################################


import sys
import json
from osrframework.transforms.lib.maltego import *
import osrframework.thirdparties.skype.checkInSkype as skype

def aliasToSkypeAccounts(query=None):
    ''' 
        Method that checks if a given alias appears in Skype.

        :param query:    query to verify.

    '''
    me = MaltegoTransform()

    jsonData = skype.checkInSkype(query=query)

    # This returns a dictionary like:
    # [{}]
    newEntities = []

    #print json.dumps(entities, indent=2)
    for user in jsonData:
	    # Defining the main entity
        aux ={}
        aux["type"] = "i3visio.profile"
        aux["value"] =  "Skype - " + str(user["i3visio.alias"])
        aux["attributes"] = []    

        # Defining the attributes recovered
        att ={}
        att["type"] = "i3visio.platform"
        att["value"] =  str("Skype")
        att["attributes"] = []
        aux["attributes"].append(att)

        for field in user.keys():
            # [TO-DO] Appending all the information from the json:
            if user[field] != None:
                try:
                    att ={}
                    att["type"] = field
                    att["value"] =  str(user[field]).encode('utf-8')
                    att["attributes"] = []
                    aux["attributes"].append(att)                
                except:
                    # Something passed...
                    pass
        # Appending the entity
        newEntities.append(aux)

    me.addListOfEntities(newEntities)
        
    # Returning the output text...
    me.returnOutput()


if __name__ == "__main__":
    aliasToSkypeAccounts(query=sys.argv[1])


