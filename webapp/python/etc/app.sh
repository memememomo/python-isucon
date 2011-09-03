#!/bin/bash

APPDIR=$(dirname $0)/..

cd $APPDIR
exec python isucon.py
