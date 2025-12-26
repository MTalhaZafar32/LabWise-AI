import subprocess
import sys

# Required packages from requirements.txt
required_packages = {
    'fastapi': '0.109.0',
    'uvicorn': '0.27.0',
    'python-multipart': '0.0.6',
    'pydantic': '2.5.3',
    'pydantic-settings': '2.1.0',
    'sqlalchemy': '2.0.25',
    'paddlepaddle': '2.6.2',
    'opencv-python': '4.6.0.66',
    'pdf2image': '1.17.0',
    'Pillow': '10.2.0',
    'requests': '2.31.0',
    'httpx': '0.26.0',
    'pandas': '2.1.4',
    'numpy': '1.26.3',
    'python-dotenv': '1.0.0',
    'aiofiles': '23.2.1',
}

# Get installed packages
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                       capture_output=True, text=True)
installed = {}
for line in result.stdout.split('\n')[2:]:  # Skip header
    if line.strip():
        parts = line.split()
        if len(parts) >= 2:
            installed[parts[0].lower()] = parts[1]

print("=== PACKAGE VERIFICATION ===\n")
missing = []
version_mismatch = []
installed_ok = []

for package, required_version in required_packages.items():
    package_key = package.lower().replace('-', '_')
    alt_package_key = package.lower().replace('_', '-')
    
    if package_key in installed:
        installed_version = installed[package_key]
        if installed_version == required_version:
            installed_ok.append(f"✓ {package} == {required_version}")
        else:
            version_mismatch.append(f"⚠ {package}: installed {installed_version}, required {required_version}")
    elif alt_package_key in installed:
        installed_version = installed[alt_package_key]
        if installed_version == required_version:
            installed_ok.append(f"✓ {package} == {required_version}")
        else:
            version_mismatch.append(f"⚠ {package}: installed {installed_version}, required {required_version}")
    else:
        missing.append(f"✗ {package} == {required_version} - NOT INSTALLED")

print(f"Installed correctly: {len(installed_ok)}")
for pkg in installed_ok:
    print(f"  {pkg}")

if version_mismatch:
    print(f"\nVersion mismatches: {len(version_mismatch)}")
    for pkg in version_mismatch:
        print(f"  {pkg}")

if missing:
    print(f"\nMissing packages: {len(missing)}")
    for pkg in missing:
        print(f"  {pkg}")
else:
    print("\n✓ All required packages are installed!")

print(f"\nTotal packages in environment: {len(installed)}")
