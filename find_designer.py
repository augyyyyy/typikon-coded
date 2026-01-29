import os
import sys
import subprocess
import PySide6

# Find where PySide6 is installed
location = os.path.dirname(PySide6.__file__)

# The designer is always here in PySide6
designer_path = os.path.join(location, "designer.exe")

if os.path.exists(designer_path):
    print(f"\n✅ FOUND OFFICIAL DESIGNER:\n{designer_path}")
    print("Launching...")
    subprocess.Popen(designer_path)
else:
    print(f"❌ Could not find designer at: {designer_path}")