#!/bin/bash

sbtscript=./sbt

if [ ! -f $sbtscript ]; then
  echo "downloading sbt" 1>&2
  ./get-sbt.sh
else 
    echo "scripts already downloaded"
fi