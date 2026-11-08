@echo off
REM Method 4 - Hybrid: GPU EEVEE worker + 8-thread CPU Cycles worker
REM Edit the variables below, then run from Command Prompt (or double-click).
set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
set "SCENE=C:\Path\To\Your_Scene.blend"
set /a START_FRAME=1
set /a END_FRAME=4440
set /a SECOND_START=START_FRAME+1

set "SCRIPT1=%~dp0..\..\scripts\method4_gpu_worker.py"
set "SCRIPT2=%~dp0..\..\scripts\method4_cpu_worker.py"

start "Worker 1" "%BLENDER_EXE%" -b --factory-startup "%SCENE%" -P "%SCRIPT1%" -t 2 -s %START_FRAME% -e %END_FRAME% -j 1 -a
start "Worker 2" "%BLENDER_EXE%" -b --factory-startup "%SCENE%" -P "%SCRIPT2%" -t 8 -s %SECOND_START% -e %END_FRAME% -j 1 -a

echo Both workers were started in separate windows. Close them with Ctrl+C when finished.
echo If you stop early, run tools\cleanup_placeholders.ps1 AFTER all workers have stopped.
pause
