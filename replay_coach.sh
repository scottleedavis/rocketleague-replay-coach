#!/bin/bash

json_dir="$(pwd)/json"   # Directory where the JSON files will be saved

mkdir -p "$json_dir"

for replay_file in "$RL_REPLAY_DIR"/*.replay; do

    if [ ! -f "$replay_file" ]; then
        echo "No .replay files found in $RL_REPLAY_DIR."
        break
    fi


    filename=$(basename "$replay_file" .replay)
    rattletrap -i "$replay_file" -c -o "$json_dir/$filename.replay.json" 

    if [ $? -ne 0 ]; then
        echo "Error processing $replay_file."
    else
        echo "Processed $replay_file"
    fi
    
done

python rocketleague_replay_coach/replays_csv.py
python rocketleague_replay_coach/replays_analyze.py
