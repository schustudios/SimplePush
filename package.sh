#!/usr/bin/env sh

# Install packages
python3 -m pip install --target ./package -r requirements.txt

# Compress the Packages
cd package
zip -r9 ${OLDPWD}/function.zip .

cd $OLDPWD
zip -gr function.zip lambda_function.py cert  -x ./cert/artifacts/*

