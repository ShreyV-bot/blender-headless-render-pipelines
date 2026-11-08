# Method 4 - Hybrid Dual-Engine, WORKER 1: EEVEE Next on 100% GPU + 2 CPU helper threads
# [scripts/method4_gpu_worker.py]   Tested on Blender 4.4.3.
# Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 2 -s 1 -e 4440 -j 1 -a
import bpy, os, platform

s = bpy.context.scene
r = s.render
eevee = s.eevee

# EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
try:
    r.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    r.engine = 'BLENDER_EEVEE'
s.frame_step = 1                       # 1 = Every frame sequentially
r.threads_mode = 'FIXED'
r.threads = 2                          # 2 CPU helper threads
r.use_persistent_data = True
r.use_compositing = False
r.use_sequencer = False
r.use_motion_blur = False

eevee.taa_render_samples = 4
eevee.use_raytracing = False
eevee.use_shadows = False              # Prevents "Error: Shadow buffer full"
eevee.use_volumetric_shadows = False

r.use_simplify = True
r.simplify_subdivision_render = 0
r.resolution_x = 1920
r.resolution_y = 1080
r.resolution_percentage = 50

out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
r.filepath = os.path.join(out, "frame_")
r.use_overwrite = False
r.use_placeholder = True
r.image_settings.file_format = 'PNG'
r.image_settings.compression = 0

print(">>> METHOD 4 / WORKER 1 (GPU EEVEE) ACTIVE <<<")
