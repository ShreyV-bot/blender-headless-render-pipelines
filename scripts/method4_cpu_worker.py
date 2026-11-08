# Method 4 - Hybrid Dual-Engine, WORKER 2: ultra-fast Cycles on 8 CPU threads (75-85% CPU)
# [scripts/method4_cpu_worker.py]   Tested on Blender 4.4.3.
# Run: blender -b --factory-startup SCENE.blend -P THIS_FILE -t 8 -s 2 -e 4440 -j 1 -a
import bpy, os, platform

s = bpy.context.scene
r = s.render
c = s.cycles

r.engine = 'CYCLES'
c.device = 'CPU'
s.frame_step = 1                       # 1 = Every frame sequentially
r.threads_mode = 'FIXED'
r.threads = 8                          # Customise: set 6, 8, or 12 for your CPU!
r.use_persistent_data = True
r.use_compositing = False
r.use_sequencer = False
r.use_motion_blur = False

c.samples = 4                          # Ultra-fast 4 samples + AI denoiser
c.use_adaptive_sampling = True
c.adaptive_threshold = 0.1
c.max_bounces = 1
c.diffuse_bounces = 1
c.glossy_bounces = 0
c.transmission_bounces = 0
c.volume_bounces = 0
c.use_denoising = True
c.denoiser = 'OPENIMAGEDENOISE'
c.denoising_prefilter = 'FAST'
c.use_auto_tile = True
c.tile_size = 256

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

print(">>> METHOD 4 / WORKER 2 (CPU CYCLES) ACTIVE <<<")
