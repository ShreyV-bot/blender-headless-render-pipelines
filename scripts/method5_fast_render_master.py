# Method 5 - Universal Master Optimization Script (Customizable)   [scripts/method5_fast_render_master.py]
# Works in Blender's Scripting tab or via the command line with -P. Tested on Blender 4.4.3.
# Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 2 -s 1 -e 4440 -j 1 -a
# --- PART A: HARDWARE & QUALITY CONFIGURATION BLOCK ---
import bpy
import os
import platform

# 1. CPU THREAD LIMIT (Set 8 to cap at 8 threads; 0 for 100% of all threads)
#    - Set 2 when using GPU-only EEVEE on U-series laptops to prevent power throttling.
CPU_THREADS = 8

# 2. RENDER ENGINE ('EEVEE' for GPU speed, 'CYCLES' for CPU/GPU raytracing)
ENGINE_CHOICE = 'EEVEE'

# 3. PERSISTENT DATA (True = keeps scene in RAM, eliminates the ~9s reload gap!)
#    Set False ONLY on 4GB-8GB RAM PCs if Blender crashes with Out of Memory.
KEEP_SCENE_IN_RAM = True

# 4. EEVEE SHADOWS (False = fixes "Error: Shadow buffer full" on Intel Iris Xe)
ENABLE_EEVEE_SHADOWS = False

# 5. QUALITY & FRAME STEP (FRAME_STEP = 1 for all frames, 2 for 30fps half-frames)
RENDER_SAMPLES = 4       # 4-8 for fast animation, 16-64 for final quality
RESOLUTION_SCALE = 50    # 50 = 960x540 (4x faster), 75 = 1440x810, 100 = 1080p
FRAME_STEP = 1           # 1 = Every frame (1,2,3..), 2 = Odd frames (1,3,5..)

# 6. AUTOMATIC CROSS-PLATFORM FAST SSD OUTPUT PATH (Outside OneDrive/Cloud)
if platform.system() == "Windows":
    OUTPUT_DIR = "C:/Temp_Render/"
else:
    OUTPUT_DIR = os.path.expanduser("~/Temp_Render/")

# --- PART B: ENGINE, MEMORY & NVMe SSD EXECUTION BLOCK (keep directly below Part A) ---
scene = bpy.context.scene
render = scene.render
eevee = scene.eevee
cycles = scene.cycles

# A. Apply CPU Thread Locking & Disable Post-Processing Overhead
render.threads_mode = 'FIXED' if CPU_THREADS > 0 else 'AUTO'
if CPU_THREADS > 0:
    render.threads = CPU_THREADS
render.use_compositing = False
render.use_sequencer = False
render.use_motion_blur = False   # Unified location in Blender 4.2+
render.use_persistent_data = KEEP_SCENE_IN_RAM

# B. Geometry Simplification (Reduces RAM & CPU Prep Time)
render.use_simplify = True
render.simplify_subdivision_render = 0   # Set 1 or 2 if curved models look boxy
render.simplify_child_particles_render = 0.0

# C. Configure Selected Render Engine (Blender 4.2 / 4.3 / 4.4+)
if ENGINE_CHOICE.upper() == 'EEVEE':
    # EEVEE engine id: 'BLENDER_EEVEE_NEXT' on Blender 4.2-4.5, 'BLENDER_EEVEE' on Blender 5.x
    try:
        render.engine = 'BLENDER_EEVEE_NEXT'
    except TypeError:
        render.engine = 'BLENDER_EEVEE'
    eevee.taa_render_samples = RENDER_SAMPLES
    eevee.use_raytracing = False
    eevee.use_shadows = ENABLE_EEVEE_SHADOWS
    eevee.shadow_step_count = 2
    eevee.use_volumetric_shadows = False
elif ENGINE_CHOICE.upper() == 'CYCLES':
    render.engine = 'CYCLES'
    cycles.device = 'CPU'            # Change to 'GPU' for CUDA/OptiX/HIP/OneAPI
    cycles.samples = RENDER_SAMPLES
    cycles.use_adaptive_sampling = True
    cycles.adaptive_threshold = 0.1
    cycles.use_denoising = True
    cycles.denoiser = 'OPENIMAGEDENOISE'
    cycles.denoising_prefilter = 'FAST'
    cycles.max_bounces = 2
    cycles.diffuse_bounces = 1
    cycles.glossy_bounces = 1
    cycles.transmission_bounces = 1
    cycles.volume_bounces = 0
    cycles.use_auto_tile = True
    cycles.tile_size = 256
else:
    raise ValueError("ENGINE_CHOICE must be 'EEVEE' or 'CYCLES', got: " + repr(ENGINE_CHOICE))

# D. Resolution, Frame Step & Zero-Compression NVMe SSD Output
render.resolution_x = 1920
render.resolution_y = 1080
render.resolution_percentage = RESOLUTION_SCALE
scene.frame_step = FRAME_STEP
os.makedirs(OUTPUT_DIR, exist_ok=True)
render.filepath = os.path.join(OUTPUT_DIR, "frame_")
render.use_overwrite = False     # Skips existing frames on disk
render.use_placeholder = True    # Creates 0-byte lock file for multi-worker
render.image_settings.file_format = 'PNG'
render.image_settings.color_mode = 'RGB'
render.image_settings.color_depth = '8'
render.image_settings.compression = 0   # 0% CPU compression = instant SSD write

print(f">>> METHOD 5 (UNIVERSAL MASTER: {ENGINE_CHOICE.upper()}, THREADS={CPU_THREADS}) ACTIVE <<<")
