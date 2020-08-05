#!/bin/bash

sbtscript=./sbt
echo $0
full_path=$(realpath $0)
echo "full path:" $full_path

work_dir=$(dirname $full_path)
echo "dirname:" $work_dir

echo $work_dir/get-sbt.sh

if [ ! -f $sbtscript ]; then
  echo "downloading sbt" 1>&2
  bash $work_dir/get-sbt.sh
else 
    echo "scripts already downloaded"
fi