#! /usr/bin/python
# Copyright Notice:
# Copyright 2022 Mike Raineri.  All rights reserved.
# License: BSD 3-Clause License.  For full text see link: https://github.com/mraineri/Solar-Edge-CLI/blob/master/LICENSE.md

import argparse
import json
import requests

SE_INVENTORY_API = "https://monitoringapi.solaredge.com/site/{}/inventory?api_key={}"

def check_response( response ):
    """
    Verifies the response is OK for a caller

    Args:
        response: The response to inspect
    """

    if response.status_code >= 400:
        raise ValueError( "Operation failed: HTTP {}\n{}".format( response.status_code, response.text ) )

    return

def get_inventory( config ):
    """
    Gets and prints the site inventory

    Args:
        config: The configuration containing the site info
    """

    # Get the site inventory
    response = requests.get( SE_INVENTORY_API.format( config["SiteId"], config["APIKey"] ) )
    check_response( response )
    payload = response.json()
    
    # Tabulate the info
    print()
    inventory_groups = [ "Meters", "Sensors", "Gateways", "Batteries", "Inverters" ]
    for group in inventory_groups:
        print( group )
        group = group.lower()
        if len( payload["Inventory"][group] ) == 0:
            print( "No {} registered".format( group ) )
        else:
            for item in payload["Inventory"][group]:
                print( "- {}".format( item.get( "name", item.get( "id", "Unknown Name" ) ) ) )
                print( "    Manufacturer: {}".format( item.get( "manufacturer", "N/A" ) ) )
                print( "    Model: {}".format( item.get( "model", "N/A" ) ) )
                print( "    Serial Number: {}".format( item.get( "SN", "N/A" ) ) )
                print( "    Firmware Version: {}".format( item.get( "firmwareVersion", "N/A" ) ) )
                if "nameplateCapacity" in item:
                    print( "    Nameplate Capacity: {}".format( item["nameplateCapacity"] ) )
                if "connectedOptimizers" in item:
                    print( "    Connected Optimizers: {}".format( item["connectedOptimizers"] ) )
                if "connectedTo" in item:
                    connected_sn = item.get( "connectedSolaredgeDeviceSN", item.get( "connectedInverterSn", "" ) )
                    print( "    Connected To: {} ({})".format( item["connectedTo"], connected_sn ) )
                if "type" in item:
                    print( "    Type: {}".format( item["type"] ) )
                if "form" in item:
                    print( "    Form: {}".format( item["form"] ) )
                if "category" in item:
                    print( "    Category: {}".format( item["category"] ) )
        print()

    return


# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool collect and display data from SolarEdge" )
argget.add_argument( "--config", "-c", type = str, help = "Filepath to the config file containing site ID and API key; defaults to 'config.json'", default = "config.json" )
args = argget.parse_args()

# Load the config file
with open( args.config ) as f:
    config = json.load( f )

# Show the site inventory
get_inventory( config )
