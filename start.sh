#!/usr/bin/env bash

if [ -z "$PPCMD" ]; then
  python3 bpproxypool.py launch
else
  python3 bpproxypool.py $PPCMD
fi
