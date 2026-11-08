# Method 3 - Parallel Multi-Process EEVEE Pipelining   [scripts/method3_parallel_eevee.py]
# Tested on Blender 4.4.3. Launch TWO processes with this same file (-s 1 and -s 2), e.g.:
#   blender -b --factory-startup SCENE.blend -P THIS_FILE -t 4 -s 1 -e 4440 -j 1 -a
#   blender -b --factory-startup SCENE.blend -P THIS_FILE -t 4 -s 2 -e 4440 -j 1 -a
import bpy, os, platform

# ==============================================================================
# USER CUSTOMIZATION SETTINGS
# ==============================================================================
# Each worker uses 4 threads (2 workers x 4 threads = 8 CPU threads total!)
THREADS_PER_WORKER = 4
FRAME_STEP = 1         # 1 = Render EVERY frame sequentially (1, 2, 3, 4...)
KEEP_IN_RAM = True     # Set True on 16GB+ RAM PCs; False on 8GB RAM PCs
ENABLE_SHADOWS = False # False fixes "Shadow buffer full" on integrated GPUs
SAMPLES = 4            # 4-8 for fast animation; 16-32 for dedicated GPUs
RES_PERCENT = 50       # 50 = 960x540; 100 = full 1920x1080

# ==============================================================================
# ENGINE & SSD PLACEHOLDER LOCK CONFIGURATION
# ==============================================================================
scene = bpy.context.scene
render = scene.render
eevee = scene.eevee

# EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
try:
    render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    render.engine = 'BLENDER_EEVEE'
scene.frame_step = FRAME_STEP
render.threads_mode = 'FIXED'
render.threads = THREADS_PER_WORKER
render.use_compositing = False
render.use_sequencer = False
render.use_persistent_data = KEEP_IN_RAM

eevee.taa_render_samples = SAMPLES
eevee.use_raytracing = False
eevee.use_shadows = ENABLE_SHADOWS
eevee.shadow_step_count = 2
eevee.use_volumetric_shadows = False
render.use_motion_blur = False

render.use_simplify = True
render.simplify_subdivision_render = 0
render.simplify_child_particles_render = 0.0
render.resolution_x = 1920
render.resolution_y = 1080
render.resolution_percentage = RES_PERCENT

out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
render.filepath = os.path.join(out, "frame_")

# CRITICAL FOR MULTI-PROCESS: Prevents both workers from rendering the same frame!
render.use_overwrite = False
render.use_placeholder = True
render.image_settings.file_format = 'PNG'
render.image_settings.color_mode = 'RGB'
render.image_settings.color_depth = '8'
render.image_settings.compression = 0

print(">>> METHOD 3 (PARALLEL EEVEE WORKER) READY <<<")
