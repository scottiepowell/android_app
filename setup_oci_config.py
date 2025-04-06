import os
from pathlib import Path
from dotenv import load_dotenv

OCI_CONFIG_PATH = Path.home() / ".oci" / "config"


def load_env():
    load_dotenv()
    user = os.getenv("OCI_USER")
    fingerprint = os.getenv("OCI_FINGERPRINT")
    tenancy = os.getenv("OCI_TENANCY")
    region = os.getenv("OCI_REGION")
    key_file = os.path.expanduser(os.getenv("OCI_KEY_FILE", ""))

    missing = [k for k in ["OCI_USER", "OCI_FINGERPRINT", "OCI_TENANCY", "OCI_REGION", "OCI_KEY_FILE"] if os.getenv(k) is None]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return user, fingerprint, tenancy, region, key_file


def validate_key_file(path):
    if not os.path.isfile(path):
        raise FileNotFoundError(f"❌ Private key file not found: {path}")
    return True


def write_config(user, fingerprint, tenancy, region, key_file):
    oci_dir = OCI_CONFIG_PATH.parent
    oci_dir.mkdir(parents=True, exist_ok=True)

    with open(OCI_CONFIG_PATH, "w") as f:
        f.write("[DEFAULT]\n")
        f.write(f"user={user}\n")
        f.write(f"fingerprint={fingerprint}\n")
        f.write(f"key_file={key_file}\n")
        f.write(f"tenancy={tenancy}\n")
        f.write(f"region={region}\n")

    os.chmod(OCI_CONFIG_PATH, 0o600)
    print(f"✅ OCI config written to {OCI_CONFIG_PATH}")


if __name__ == "__main__":
    try:
        user, fingerprint, tenancy, region, key_file = load_env()
        validate_key_file(key_file)
        write_config(user, fingerprint, tenancy, region, key_file)
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
