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
SE_ENERGY_API = "https://monitoringapi.solaredge.com/site/{}/energyDetails?timeUnit=DAY&endTime={}&startTime={}&api_key={}"

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
    response = requests.get( SE_ENERGY_API.format( config["SiteId"], end + " 23:59:59", start + " 00:00:00", config["APIKey"] ) )
    check_response( response )
    payload = response.json()

    # Display the energy produced as a table
    print()
    date_format = "{:>10s}"
    value_format = " {:>13s}"
    unit = payload["energyDetails"]["unit"]
    header_str = date_format.format( "" )
    meter_values = []
    meter_totals = []
    for item in payload["energyDetails"]["meters"]:
        meter_values.append( item["values"] )
        meter_totals.append( 0 )
        header_str = header_str + value_format.format( item["type"] )
    print( header_str )
    for data_point in list( zip( *meter_values ) ):
        out_str = date_format.format( data_point[0]["date"].split( " " )[0] )
        for i, item in enumerate( data_point ):
            value = ""
            if "value" in item:
                value = "{}{}".format( item["value"], unit )
                meter_totals[i] = meter_totals[i] + item["value"]
            out_str = out_str + value_format.format( value )
        print( out_str )
    footer_str = date_format.format( "Totals" )
    for item in meter_totals:
        value = "{}{}".format( item, unit )
        footer_str = footer_str + value_format.format( value )
    print()
    print( footer_str )
    print()

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
