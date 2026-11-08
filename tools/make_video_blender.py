# Assemble frame_*.png into an MP4 using Blender only (no FFmpeg install needed).
# Run: blender -b --factory-startup -P tools/make_video_blender.py
# Frames are added in sorted filename order, so keep the zero-padded frame_0001.png naming.
import bpy, os, glob, platform, struct

FRAMES_DIR = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
FPS = 60
OUTPUT = os.path.join(FRAMES_DIR, "Final_Video.mp4")

files = sorted(glob.glob(os.path.join(FRAMES_DIR, "frame_*.png")))
if not files:
    raise SystemExit("No frame_*.png files found in " + FRAMES_DIR)

def png_size(path):
    """Read width/height from the PNG header so the video matches the rendered frames."""
    with open(path, "rb") as f:
        head = f.read(24)
    return struct.unpack(">II", head[16:24])

width, height = png_size(files[0])
scene = bpy.context.scene
scene.render.fps = FPS
scene.render.resolution_x = width
scene.render.resolution_y = height
scene.render.resolution_percentage = 100

seq_editor = scene.sequence_editor_create()
# Newer Blender versions rename `sequences` to `strips`; support both.
strips = seq_editor.strips if hasattr(seq_editor, "strips") else seq_editor.sequences
strip = strips.new_image("frames", files[0], 1, 1)
for f in files[1:]:
    strip.elements.append(os.path.basename(f))

scene.frame_start = 1
scene.frame_end = len(files)
scene.render.image_settings.file_format = 'FFMPEG'
scene.render.ffmpeg.format = 'MPEG4'
scene.render.ffmpeg.codec = 'H264'
scene.render.filepath = OUTPUT
bpy.ops.render.render(animation=True)
print(">>> VIDEO WRITTEN:", OUTPUT, "<<<")
