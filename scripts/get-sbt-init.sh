#!/bin/bash

sbtscript=./sbt
echo $0
full_path=$(realpath $0)
echo $full_path

if [ ! -f $sbtscript ]; then
  echo "downloading sbt" 1>&2
  bash get-sbt.sh
else 
    echo "scripts already downloaded"
fi