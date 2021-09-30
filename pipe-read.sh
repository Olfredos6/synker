#!/bin/bash
# https://stackoverflow.com/a/3018124/5253580
# requires parallel
# localStorage.colorThemeData

(docker-compose up; while true; (do eval "$(cat ./pipes)";done) ) | parallel

(docker-compose up; while true; do eval "$(cat ./pipes)";done ) | echo 