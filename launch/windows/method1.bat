@echo off
REM Method 1 - Dedicated GPU-only EEVEE Next worker
REM Edit the variables below, then run from Command Prompt (or double-click).
set "BLENDER_EXE=C:\Program Files\Blender Foundation\Blender 4.4\blender.exe"
set "SCENE=C:\Path\To\Your_Scene.blend"
set /a START_FRAME=1
set /a END_FRAME=4440
set /a SECOND_START=START_FRAME+1

set "SCRIPT1=%~dp0..\..\scripts\method1_gpu_worker.py"

"%BLENDER_EXE%" -b --factory-startup "%SCENE%" -P "%SCRIPT1%" -t 2 -s %START_FRAME% -e %END_FRAME% -j 1 -a
pause
