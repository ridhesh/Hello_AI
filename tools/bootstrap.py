import os
import sys
import glob

def bootstrap_venv():
    """Dynamically locates and injects the venv/lib/python*/site-packages folder into sys.path

    to ensure the application and all tooling work perfectly even when run under
    the system python interpreter.
    """
    # Start searching from the folder where this script resides
    base_dir = os.path.abspath(os.path.dirname(__file__))
    
    # Climb up to find the folder containing 'venv'
    while base_dir:
        if os.path.exists(os.path.join(base_dir, "venv")):
            break
        parent = os.path.dirname(base_dir)
        if parent == base_dir:
            base_dir = None
            break
        base_dir = parent
        
    if base_dir and os.path.exists(os.path.join(base_dir, "venv")):
        # Find site-packages dynamically across any Python version installed in venv
        site_packages_pattern = os.path.join(base_dir, "venv", "lib", "python*", "site-packages")
        paths = glob.glob(site_packages_pattern)
        for path in paths:
            if path not in sys.path:
                sys.path.insert(0, path)
                
# Automatically run the bootstrap logic upon module import
bootstrap_venv()
