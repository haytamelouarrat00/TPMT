#!/bin/bash

cleanup() {
    echo "Terminating all processes..."
    pkill -P $$
    exit 0
}

trap cleanup SIGINT

echo "Compiling low_level.cpp..."
cd cplusplus/
cmake -B build -S .
cmake --build build
cd ..

sleep 2

echo "Starting queueManager.py..."
python3 src/queueManager.py &
sleep 5
echo "Starting proxy.py..."
python3 src/proxy.py &
sleep 5
echo "Launching the compiled C++ low_level executable..."
OMP_NUM_THREADS=8 ./cplusplus/build/low_level &
sleep 5
echo "Starting boss.py..."
python3 src/boss.py &
sleep 5

echo "All processes are running. Press Ctrl+C to terminate."
wait
