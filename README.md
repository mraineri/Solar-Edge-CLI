# Solar-Edge-CLI

Copyright 2022 Mike Raineri.  All rights reserved.

## About

Solar-Edge-CLI is a Python3 tool to collect and display data from SolarEdge.

## Requirements

External modules:

* requests

## Usage

```
usage: solar-edge-cli.py [-h] [--config CONFIG] {inventory,energy} ...

A tool collect and display data from SolarEdge

positional arguments:
  {inventory,energy}
    inventory           Displays the inventory of the site equipment
    energy              Displays the energy production of the site over a
                        period of time

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG, -c CONFIG
                        Filepath to the config file containing site ID and API
                        key; defaults to 'config.json'
```

### Inventory

Displays the inventory of the site equipment.

```
usage: solar-edge-cli.py inventory [-h]

optional arguments:
  -h, --help  show this help message and exit
```

### Energy

Displays the energy production of the site over a period of time

```
usage: solar-edge-cli.py energy [-h] [--start START] [--end END]

optional arguments:
  -h, --help            show this help message and exit
  --start START, -start START
                        The start date for reporting energy production; one
                        month ago if not specified
  --end END, -end END   The end date for reporting energy production; today if
                        not specified
```

## Configuration File

The configuration file specified by the `config` argument contains a JSON object with two properties:

* `SiteId`: Your SolarEdge site identifier as a string
* `APIKey`: Your SolarEdge API key as a string

Both of these properties are obtained from the administrator tab of your SolarEdge dashboard.

Example configuration file:

```json
{
    "SiteId": "1",
    "APIKey": "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
}
```
