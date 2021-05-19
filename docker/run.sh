#!/bin/bash

sbtscript=./scripts/sbt

if [ ! -f $sbtscript ]; then
  echo "downloading sbt"
  bash ./scripts/get-sbt.sh
fi

$sbtscript "project core" "runMain tps.Main $*"
