#!/bin/bash

socat -u TCP-LISTEN:7777,reuseaddr,fork /dev/null