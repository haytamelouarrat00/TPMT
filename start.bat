@echo off
REM Clean the build directory
echo Cleaning build directory...
if exist build rd /s /q build
mkdir build

REM Configure CMake with MSYS Makefiles generator
echo Configuring CMake...
cd build
cmake -G "MSYS Makefiles" -S .. -B .
if errorlevel 1 (
    echo CMake configuration failed. Exiting.
    cd ..
    exit /B 1
)
cd ..

REM Build the project
echo Building the project...
cd build
cmake --build . --config Release
if errorlevel 1 (
    echo Compilation failed. Exiting.
    cd ..
    exit /B 1
)
cd ..

REM Start the Python scripts and C++ executable
echo Starting Python scripts and C++ executable...
start /B python src\queueManager.py
start /B python src\proxy.py
start /B ./cplusplus/build\low_level.exe
start /B python src\boss.py

echo All processes are running. Press Ctrl+C to terminate.
pause