#!/bin/bash
SHORT_SHA=$(git rev-parse HEAD)
mkdir -p src/packages
cd src/ && pip install -r $1/requirements.txt --target ./packages
cd packages && zip -r9 $OLDPWD/$1-$SHORT_SHA.zip .
cd $OLDPWD && zip -ur $1-$SHORT_SHA.zip $1
rm -rf packages
