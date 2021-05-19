#!/bin/bash

sbtscript=./scripts/sbt

if [ ! -f $sbtscript ]; then
  echo "downloading sbt"
  ./scripts/get-sbt
fi

$sbtscript "project core" "runMain tps.Main $*"