#!/bin/bash


./replays_json.sh

python replays_csv.py

python replays_analyze.py
