import subprocess
import sys
import pkg_resources

# Function to install or update packages
def install_or_update_packages():
    try:
        # Read the requirements.txt file
        with open("../requirements.txt", "r") as f:
            packages = f.readlines()

        for package in packages:
            # Remove any trailing whitespace/newlines
            package = package.strip()

            # Skip comments and empty lines
            if not package or package.startswith('#'):
                continue

            # If package is not pinned, install or update it
            if '==' not in package:
                print(f"Installing/updating {package}...")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package])
            else:
                # Check if the package is already installed
                pkg_name = package.split("==")[0]
                installed_packages = [pkg.key for pkg in pkg_resources.working_set]

                if pkg_name not in installed_packages:
                    print(f"Installing {pkg_name} as it is not found...")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

    except Exception as e:
        print(f"Error processing requirements: {e}")
        sys.exit(1)


# Install or update unpinned libraries
install_or_update_packages()