#!/bin/bash
SHORT_SHA=$(git rev-parse HEAD)
mkdir -p src/packages
cd src/ && pip install -r poe_ladder_exporter/requirements.txt --target ./packages
cd packages && zip -r9 $OLDPWD/function-$SHORT_SHA.zip .
cd $OLDPWD && zip -ur function-$SHORT_SHA.zip poe_ladder_exporter
rm -rf packages
