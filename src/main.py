# main.py
import logging
from install_or_update_packages import install_or_update_packages

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def main():
    # Call the function to install or update the packages
    print("Starting the package installation or update process...")
    install_or_update_packages()
    print("Package installation or update completed.")

if __name__ == "__main__":
    main()
