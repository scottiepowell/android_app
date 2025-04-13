import oci
import os


class OKEDeployer:
    def __init__(self, config_path: str = "~/.oci/config", profile: str = "DEFAULT"):
        self.config_path = os.path.expanduser(config_path)
        self.profile = profile
        self.config = None
        self.container_client = None

    def validate_config(self) -> bool:
        """
        Validates that the OCI config file exists and contains required fields.
        """
        print(f"Validating OCI config at {self.config_path} with profile '{self.profile}'...")

        if not os.path.isfile(self.config_path):
            print("❌ Config file not found.")
            return False

        try:
            self.config = oci.config.from_file(self.config_path, self.profile)
            required_keys = {"user", "fingerprint", "key_file", "tenancy", "region"}
            if not required_keys.issubset(self.config.keys()):
                print(f"❌ Missing keys in config: {required_keys - self.config.keys()}")
                return False

            print("✅ OCI config validated.")
            return True
        except Exception as e:
            print(f"❌ Failed to parse config: {e}")
            return False

    def init_clients(self):
        """
        Initializes OCI SDK clients (e.g., ContainerEngineClient).
        """
        if not self.config:
            raise RuntimeError("OCI config is not loaded. Run validate_config() first.")

        self.container_client = oci.container_engine.ContainerEngineClient(self.config)
        print("✅ ContainerEngineClient initialized.")