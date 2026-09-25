#!/bin/sh

echo "Enter your name:"
read NAME

export REACT_APP_TITLE=$NAME

npm start
