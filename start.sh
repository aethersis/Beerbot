#!/bin/bash

# Start mediamtx in a detached screen session
screen -dmS mediamtx bash -c "./mediamtx mediamtx.yml; exec bash"

# Start the Python server in a new detached screen session
screen -dmS robot_server bash -c "
    source .venv/bin/activate;
    python3 server.py;
    exec bash
"

echo "Both services are now running in detached screen sessions."
echo "Use 'screen -ls' to see running sessions."
echo "Attach to a session using 'screen -r <session_name>' (e.g., mediamtx or robot_server)."
