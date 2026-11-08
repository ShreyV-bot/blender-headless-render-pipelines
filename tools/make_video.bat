@echo off
REM Assemble frame_0001.png ... into an H.264 MP4 with FFmpeg (Windows).
REM Usage: make_video.bat [FRAMES_DIR] [FPS] [OUTPUT.mp4]
set "DIR=%~1"
if "%DIR%"=="" set "DIR=C:\Temp_Render"
set "FPS=%~2"
if "%FPS%"=="" set "FPS=60"
set "OUT=%~3"
if "%OUT%"=="" set "OUT=%DIR%\Final_Output.mp4"
ffmpeg -framerate %FPS% -i "%DIR%\frame_%%04d.png" -c:v libx264 -pix_fmt yuv420p -crf 18 "%OUT%"
