#!/bin/bash
# Run direct test without going through bash cd
cd "$(dirname "$0")" && python3 direct_test_glgroup.py
