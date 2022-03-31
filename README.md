# Solar-Edge-CLI

Copyright 2022 Mike Raineri.  All rights reserved.

## About

Solar-Edge-CLI is a Python3 tool to collect and display data from SolarEdge.

## Requirements

External modules:

* requests

## Usage

```
usage: solar-edge-cli.py [-h] [--config CONFIG]

A tool collect and display data from SolarEdge

required arguments:
  --config CONFIG, -c CONFIG
                        Filepath to the config file containing site ID and API
                        key; defaults to 'config.json'

optional arguments:
  -h, --help            show this help message and exit
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
