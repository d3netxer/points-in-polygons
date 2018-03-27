#!/bin/sh

#echo command below will not create file unless the permissions of the directory allows it to
#echo "testing writing to log file" >> /opt/points-in-polygons/data/test5.log

cd /opt/points-in-polygons && docker run -d -e "HOME=/home" -v $HOME/.aws:/home/.aws -v "$PWD/data:/opt/data" points-in-polygons-image


