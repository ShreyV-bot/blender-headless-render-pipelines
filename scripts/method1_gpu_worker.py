# Method 1 - Dedicated GPU-Only High-Speed Rendering (EEVEE Next)   [scripts/method1_gpu_worker.py]
# Tested on Blender 4.4.3. Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 2 -s 1 -e 4440 -j 1 -a
# --- PART A: USER CUSTOMIZATION SETTINGS ---
import bpy, os, platform

# 1. CPU HELPER THREADS:
# - Set 2 for laptops with integrated GPUs (prevents thermal/power throttling).
# - Set 4 for desktop PCs with dedicated NVIDIA/AMD graphics cards.
HELPER_THREADS = 2

# 2. SEQUENTIAL FRAME STEP:
# - Set 1 to render EVERY frame (1, 2, 3, 4... full 60fps/30fps timeline).
# - Set 2 ONLY if your timeline is 60fps and you want 30fps (halves render time).
FRAME_STEP = 1

# 3. RAM PERSISTENCE (True = saves ~9 seconds per frame by keeping meshes in RAM):
# - Set False ONLY on 4GB-8GB RAM PCs if Blender crashes with "Out of Memory".
KEEP_IN_RAM = True

# 4. GPU QUALITY & SHADOW BUFFER PROTECTION:
# - Set ENABLE_SHADOWS = False on Intel Iris Xe / integrated GPUs to prevent
#   "Error: Shadow buffer full". Set True on dedicated GPUs with 6GB+ VRAM.
ENABLE_SHADOWS = False
SAMPLES = 4          # 4-8 for fast speed; 16-32 for high quality
RES_PERCENT = 50     # 50 = 960x540 (4x faster); 100 = full 1920x1080

# --- PART B: ENGINE & SSD EXECUTION BLOCK (keep directly below Part A) ---
scene = bpy.context.scene
render = scene.render
eevee = scene.eevee

# Configure Engine & CPU Threads
# EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
try:
    render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    render.engine = 'BLENDER_EEVEE'
scene.frame_step = FRAME_STEP
render.threads_mode = 'FIXED'
render.threads = HELPER_THREADS
render.use_compositing = False
render.use_sequencer = False
render.use_persistent_data = KEEP_IN_RAM

# Apply GPU Speed & Shadow Settings (Blender 4.2 / 4.3 / 4.4+)
eevee.taa_render_samples = SAMPLES
eevee.use_raytracing = False
eevee.use_shadows = ENABLE_SHADOWS
eevee.shadow_step_count = 2
eevee.use_volumetric_shadows = False
render.use_motion_blur = False   # Moved to scene.render in Blender 4.2+

# Geometry Simplification & Resolution
render.use_simplify = True
render.simplify_subdivision_render = 0   # Increase to 1 if curved meshes look boxy
render.simplify_child_particles_render = 0.0
render.resolution_x = 1920
render.resolution_y = 1080
render.resolution_percentage = RES_PERCENT

# Cross-Platform Fast SSD Output & Smart Resume
out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
render.filepath = os.path.join(out, "frame_")
render.use_overwrite = False     # Skips frames already rendered on disk
render.use_placeholder = True
render.image_settings.file_format = 'PNG'
render.image_settings.color_mode = 'RGB'
render.image_settings.color_depth = '8'
render.image_settings.compression = 0   # 0% CPU compression = instant SSD write

print(">>> METHOD 1 (GPU-ONLY WORKER) ACTIVE <<<")
