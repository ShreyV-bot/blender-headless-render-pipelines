# Method 2 - Low-RAM CPU-Capped Cycles Rendering   [scripts/method2_cycles_low_ram.py]
# Tested on Blender 4.4.3. Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 8 -s 1 -e 4440 -j 1 -a
# --- PART A: USER CUSTOMIZATION SETTINGS ---
import bpy, os, platform

# 1. STRICT CPU CORE / THREAD LIMIT:
# - Set 8 to use exactly 8 CPU threads (e.g., ~70% on a 12-thread i7-1255U).
# - Adjust to 4 on quad-core laptops, or 12-16 on desktop workstations.
CPU_THREADS = 8

# 2. ULTRA-LOW RAM vs. FAST SCENE PERSISTENCE:
# - Set True if your scene uses < 4 GB RAM (saves ~9s reload time per frame!).
# - Set False on 4GB-8GB RAM PCs so Blender frees 100% of RAM after every frame.
KEEP_SCENE_IN_RAM = True

# 3. CYCLES SPEED & QUALITY TUNING:
SAMPLES = 8          # 4-8 for fast animation with AI Denoiser; 32-64 for final stills
MAX_BOUNCES = 2      # 1-2 for fast interior/object renders; 4 for complex glass
TILE_SIZE = 256      # 128 or 256 keeps RAM usage tiny; 2048 for high-RAM PCs
RES_PERCENT = 50     # 50 = 960x540; 75 = 1440x810; 100 = full 1920x1080
FRAME_STEP = 1       # 1 = Render EVERY frame (1, 2, 3...); 2 = Odd frames only

# --- PART B: CYCLES LOW-RAM ENGINE BLOCK (keep directly below Part A) ---
s = bpy.context.scene
r = s.render
c = s.cycles

# Lock Engine & CPU Threads
r.engine = 'CYCLES'
c.device = 'CPU'     # Change to 'GPU' if using NVIDIA OptiX / AMD HIP
s.frame_step = FRAME_STEP
r.threads_mode = 'FIXED'
r.threads = CPU_THREADS
r.use_persistent_data = KEEP_SCENE_IN_RAM
r.use_compositing = False
r.use_sequencer = False
r.use_motion_blur = False

# High-Speed Cycles Sampling & Fast AI Denoising
c.samples = SAMPLES
c.use_adaptive_sampling = True
c.adaptive_threshold = 0.1
c.use_denoising = True
c.denoiser = 'OPENIMAGEDENOISE'      # Runs on CPU via Intel OIDN
c.denoising_prefilter = 'FAST'

# Minimal Light Bounces (Huge CPU Speedup)
c.max_bounces = MAX_BOUNCES
c.diffuse_bounces = 1
c.glossy_bounces = 1
c.transmission_bounces = 1
c.volume_bounces = 0
c.transparent_max_bounces = 2
c.caustics_reflective = False
c.caustics_refractive = False

# Low-RAM Memory Protection (Small Tiles + Subdivision Cap)
c.use_auto_tile = True
c.tile_size = TILE_SIZE
c.debug_use_spatial_splits = False   # Saves hundreds of MB of BVH RAM
r.use_simplify = True
r.simplify_subdivision_render = 1    # Prevents subdivision modifiers from eating RAM
r.simplify_child_particles_render = 0.1

# Resolution & Fast SSD Uncompressed PNG Output
r.resolution_x = 1920
r.resolution_y = 1080
r.resolution_percentage = RES_PERCENT
out = "C:/Temp_Render/" if platform.system() == "Windows" else os.path.expanduser("~/Temp_Render/")
os.makedirs(out, exist_ok=True)
r.filepath = os.path.join(out, "frame_")
r.use_overwrite = False
r.use_placeholder = True
r.image_settings.file_format = 'PNG'
r.image_settings.color_mode = 'RGB'
r.image_settings.color_depth = '8'
r.image_settings.compression = 0

print(f">>> METHOD 2 (CYCLES {CPU_THREADS}-THREAD LOW-RAM MODE) ACTIVE <<<")
