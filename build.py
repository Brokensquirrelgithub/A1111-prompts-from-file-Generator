import os
import sys
import shutil
import PyInstaller.__main__
import platform
from pathlib import Path

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def build():
    # Clean up previous builds
    for item in ['build', 'dist']:
        if os.path.exists(item):
            shutil.rmtree(item, ignore_errors=True)
    
    # Ensure required directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('profiles', exist_ok=True)
    
    # PyInstaller configuration
    app_name = 'A1111-Prompt-Generator'
    script_path = 'launch.py'  # Use the launcher as entry point
    icon_path = 'icon.ico' if os.path.exists('icon.ico') else None
    
    # Get absolute paths for data files
    current_dir = Path('.').resolve()
    data_dir = str(current_dir / 'data')
    profiles_dir = str(current_dir / 'profiles')
    
    # Base command
    cmd = [
        script_path,
        '--name', app_name,
        '--onefile',
        '--windowed',  # For GUI apps
        '--add-data', f'{profiles_dir}{os.pathsep}profiles',
        '--noconfirm',  # Overwrite output directory without confirmation
        '--clean',  # Clean PyInstaller cache and remove temporary files
    ]
    
    # Handle icon based on platform
    if icon_path and os.path.exists(icon_path):
        if platform.system() == 'Darwin':  # macOS
            try:
                from PIL import Image
                # Convert ICO to ICNS for macOS
                icns_path = os.path.splitext(icon_path)[0] + '.icns'
                if not os.path.exists(icns_path):
                    img = Image.open(icon_path)
                    img.save(icns_path, format='ICNS')
                cmd.extend(['--icon', icns_path])
            except ImportError:
                print("Warning: Pillow not available, skipping icon conversion")
                # On macOS, we can proceed without an icon
        else:
            cmd.extend(['--icon', str(Path(icon_path).resolve())])
    
    # Platform specific options
    if platform.system() == 'Darwin':  # macOS
        cmd.extend([
            '--osx-bundle-identifier', 'com.example.promptgenerator',
        ])
        # Create entitlements file if it doesn't exist
        if not os.path.exists('entitlements.plist'):
            with open('entitlements.plist', 'w') as f:
                f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.cs.allow-jit</key>
    <true/>
    <key>com.apple.security.cs.allow-unsigned-executable-memory</key>
    <true/>
</dict>
</plist>''')
    elif platform.system() == 'Windows':
        cmd.extend(['--version-file', 'version.txt'])
    
    # Add hidden imports for any packages that might be missing
    hidden_imports = [
        'tkinter',
        'json',
        'os',
        'pathlib',
        'shutil',
        'subprocess',
        'platform',
        'random',
        'sys',
        'python-dotenv',
    ]
    
    for imp in hidden_imports:
        cmd.extend(['--hidden-import', imp])
    
    print("Starting build with command:", ' '.join(cmd))
    
    # Run PyInstaller
    try:
        PyInstaller.__main__.run(cmd)
        print("\n✅ Build completed successfully!")
        print(f"📁 Executable is in: {os.path.abspath('dist')}")
        
        # On macOS, print additional instructions
        if platform.system() == 'Darwin':
            print("\nOn macOS, you may need to run the following command to allow the app to run:")
            print(f"xattr -d com.apple.quarantine dist/{app_name}.app")
            
    except Exception as e:
        print(f"\n❌ Build failed with error: {str(e)}")
        print("\nTroubleshooting tips:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Try running with administrator/root privileges")
        print("3. Check if there are any error messages above")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(build())
