#!/bin/bash

# Function for error check
function error_check {
    if [ $? -eq 0 ]; then
        echo "No errors found."
    else
        echo "Errors found."
        exit 1
    fi
}

flake8 fastapi_rest_jsonapi tests --count --select=E9,F63,F7,F82 --show-source --statistics
error_check

flake8 fastapi_rest_jsonapi tests --count --max-complexity=10 --max-line-length=127 --statistics
error_check

pytest
error_check

echo "🚀 All checks passed."