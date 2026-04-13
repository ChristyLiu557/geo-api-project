#!/bin/bash

export FLASK_ENV=development
export PROJ_DIR=$PWD
#  MongoDB connection mode (local vs cloud) is controlled via environment variables:
# - CLOUD_MONGO=0 → local MongoDB
# - CLOUD_MONGO=1 → MongoDB Atlas (cloud) 
export DEBUG=1
export CLOUD_MONGO=1


# run our server locally:
PYTHONPATH=$(pwd):$PYTHONPATH
FLASK_APP=server.endpoints flask run --debug --host=127.0.0.1 --port=8000
