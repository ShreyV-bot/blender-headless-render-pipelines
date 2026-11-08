# OS Power & Hardware Preparation

Before any long render, stop the operating system from throttling the CPU below its base frequency. On thin laptops the CPU and GPU share one power limit, so this matters most when both are working (Methods 3, 4, 5).

## Unlock full CPU clock speed

**Windows (Command Prompt as Administrator):**

```text
:: Activate the built-in High Performance power plan:
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

:: Optional: unlock the Ultimate Performance plan on Windows 10/11:
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61
```

**Linux (Bash):**

```bash
# Check the current CPU scaling governor:
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# Force all cores into 'performance' mode (prevents 1.1 GHz throttling):
sudo cpupower frequency-set -g performance
# Or on Ubuntu 22.04+ / Fedora:
powerprofilesctl set performance
```

**macOS (prevent sleep during a headless render):**

```bash
caffeinate -i &
```

## Laptop checklist

- Keep the AC charger plugged in.
- Raise the back of the laptop for airflow when running Methods 3 or 4.
- Create the output folder (`C:\Temp_Render` or `~/Temp_Render`) **outside** OneDrive, Dropbox, iCloud, or any synced folder.
- Close the Blender GUI and other heavy apps before starting a headless run (the GUI alone can use 2–3 GB of RAM).
