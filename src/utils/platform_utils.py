# src/utils/platform_utils.py

import os
import logging
from src.config import DATABASE_PATH
Logger = logging.getLogger(__name__)

def get_database_path():
    try:
        from kivy.utils import platform
    except ImportError:
        platform = 'other'

    if platform == 'android':
        try:
            # For Android, use the app's user data directory
            from android.storage import app_storage_path
            app_dir = app_storage_path()
            database_file = os.path.join(app_dir, 'whats_in_the_box.db')
        except ImportError:
            Logger.error("platform_utils.py: Failed to import android.storage. Is 'android' in your requirements?")
            raise RuntimeError("Running on a non-Android platform but tried to use Android-specific storage.")
    else:
        # For desktop platforms, use the centralized DATABASE_PATH from config.py
        database_file = DATABASE_PATH
    Logger.debug(f"platform_utils.py: Using database file at {database_file}")
    return database_file