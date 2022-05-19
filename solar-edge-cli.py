#! /usr/bin/python
# Copyright Notice:
# Copyright 2022 Mike Raineri.  All rights reserved.
# License: BSD 3-Clause License.  For full text see link: https://github.com/mraineri/Solar-Edge-CLI/blob/master/LICENSE.md

import argparse
import datetime
import json
import re
import requests

SE_INVENTORY_API = "https://monitoringapi.solaredge.com/site/{}/inventory?api_key={}"
SE_ENERGY_API = "https://monitoringapi.solaredge.com/site/{}/energy?timeUnit=DAY&endDate={}&startDate={}&api_key={}"

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

def get_energy( config, start, end ):
    """
    Gets and prints the energy production of the site over a period of time

    Args:
        config: The configuration containing the site info
        start: The start date in the form YYYY-MM-DD; None indicates one month ago
        end: The end date in the form YYYY-MM-DD; None indicates today
    """

    # Generate default dates if needed
    today = datetime.date.today()
    if start is None:
        first = today.replace( day = 1 )
        last_month = first - datetime.timedelta( days = 1 )
        start = last_month.strftime( "%Y-%m" ) + "-" + today.strftime( "%d" )
    if end is None:
        end = today.strftime( "%Y-%m-%d" )

    # Verify the date format
    if not re.match( r"^\d{4}-\d{2}-\d{2}$", start ):
        raise ValueError( "Start date needs to be in the form YYYY-MM-DD" )
    if not re.match( r"^\d{4}-\d{2}-\d{2}$", end ):
        raise ValueError( "End date needs to be in the form YYYY-MM-DD" )

    # Get the site energy production
    response = requests.get( SE_ENERGY_API.format( config["SiteId"], end, start, config["APIKey"] ) )
    check_response( response )
    payload = response.json()

    # Display the energy produced
    unit = payload["energy"]["unit"]
    total_energy = 0
    for item in payload["energy"]["values"]:
        if item["value"] is not None:
            print( "{}: {}{}".format( item["date"].split( " " )[0], item["value"], unit ) )
            total_energy = total_energy + item["value"]
        else:
            print( "{}: No energy reported".format( item["date"].split( " " )[0] ) )
    print()
    print( "Total energy produced over the period: {}{}".format( total_energy, unit ) )

# Get the input arguments
argget = argparse.ArgumentParser( description = "A tool collect and display data from SolarEdge" )
argget.add_argument( "--config", "-c", type = str, help = "Filepath to the config file containing site ID and API key; defaults to 'config.json'", default = "config.json" )
subparsers = argget.add_subparsers( dest = "command" )
inventory_argget = subparsers.add_parser( "inventory", help = "Displays the inventory of the site equipment" )
energy_argget = subparsers.add_parser( "energy", help = "Displays the energy production of the site over a period of time" )
energy_argget.add_argument( "--start", "-start", type = str, help = "The start date for reporting energy production; defaults to one month ago" )
energy_argget.add_argument( "--end", "-end", type = str, help = "The end date for reporting energy production; defaults to today" )
args = argget.parse_args()

# Load the config file
with open( args.config ) as f:
    config = json.load( f )

# Perform the request
if args.command == "energy":
    get_energy( config, args.start, args.end )
else:
    get_inventory( config )
