#!/usr/bin/env python3
"""
Secure configuration management for SynBi
This module handles API keys and sensitive configuration using environment variables.
"""

import os
from typing import Optional

# Default configuration values (non-sensitive)
DEFAULT_CONFIG = {
    "weather_units": "metric",
    "spotify_redirect_uri": "http://127.0.0.1:5000/callback/",
    "spotify_scope": "user-read-playback-state user-modify-playbook-state user-read-currently-playing"
}

def get_env_var(key: str, default: Optional[str] = None, required: bool = False) -> Optional[str]:
    """
    Get environment variable with optional default and required validation.
    
    Args:
        key: Environment variable name
        default: Default value if env var not found
        required: If True, raise error if env var not found and no default
    
    Returns:
        Environment variable value or default
    
    Raises:
        ValueError: If required=True and no value found
    """
    value = os.getenv(key, default)
    
    if required and not value:
        raise ValueError(f"Required environment variable '{key}' not found. Please set it or add to .env file.")
    
    return value

def get_weather_config():
    """Get weather API configuration."""
    return {
        "api_key": get_env_var("WEATHER_API_KEY", required=True),
        "base_url": "http://api.openweathermap.org/data/2.5/weather?",
        "units": get_env_var("WEATHER_UNITS", DEFAULT_CONFIG["weather_units"])
    }

def get_spotify_config():
    """Get Spotify API configuration."""
    return {
        "client_id": get_env_var("SPOTIFY_CLIENT_ID", required=True),
        "client_secret": get_env_var("SPOTIFY_CLIENT_SECRET", required=True),
        "redirect_uri": get_env_var("SPOTIFY_REDIRECT_URI", DEFAULT_CONFIG["spotify_redirect_uri"]),
        "scope": get_env_var("SPOTIFY_SCOPE", DEFAULT_CONFIG["spotify_scope"])
    }


def get_user_config():
    """Get user-specific configuration."""
    return {
        "password": get_env_var("USER_PASSWORD", required=True),
        "gemini_api_key": get_env_var("GEMINI_API_KEY", required=True)
    }

def validate_all_configs():
    """
    Validate all required configurations are available.
    
    Returns:
        dict: Validation results with missing keys
    """
    missing_configs = []
    
    try:
        get_weather_config()
    except ValueError as e:
        missing_configs.append("Weather: " + str(e))
    
    try:
        get_spotify_config()
    except ValueError as e:
        missing_configs.append("Spotify: " + str(e))
    
    
    try:
        get_user_config()
    except ValueError as e:
        missing_configs.append("User: " + str(e))
    
    return {
        "valid": len(missing_configs) == 0,
        "missing": missing_configs
    }

def create_env_template():
    """Create a template .env file with required variables."""
    env_template = '''# SynBi Environment Configuration
# Copy this to .env and fill in your actual API keys and credentials

# Weather API (OpenWeatherMap)
WEATHER_API_KEY=your_openweather_api_key_here

# Spotify API
SPOTIFY_CLIENT_ID=your_spotify_client_id_here
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret_here


# User Configuration
USER_PASSWORD=your_secure_password_here
GEMINI_API_KEY=your_gemini_api_key_here

# Optional Configuration (uncomment to override defaults)
# WEATHER_UNITS=metric
# SPOTIFY_REDIRECT_URI=http://127.0.0.1:5000/callback/
'''
    
    template_path = ".env.template"
    with open(template_path, "w", encoding="utf-8") as f:
        f.write(env_template)
    
    print(f"Environment template created at: {template_path}")
    print("Please copy this to '.env' and fill in your actual API keys.")
    
    return template_path

def load_env_file(env_path: str = ".env"):
    """
    Load environment variables from a .env file.
    
    Args:
        env_path: Path to .env file
    """
    if not os.path.exists(env_path):
        print(f"No .env file found at {env_path}")
        return False
    
    try:
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Only set if not already in environment
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()
        
        print(f"Environment variables loaded from {env_path}")
        return True
    except Exception as e:
        print(f"Error loading .env file: {e}")
        return False

# Auto-load .env file on import
if __name__ != "__main__":
    load_env_file()

if __name__ == "__main__":
    # CLI for configuration management
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "validate":
            validation = validate_all_configs()
            if validation["valid"]:
                print("✅ All configurations are valid!")
            else:
                print("❌ Missing configurations:")
                for missing in validation["missing"]:
                    print(f"  - {missing}")
                
        elif sys.argv[1] == "template":
            create_env_template()
            
        elif sys.argv[1] == "test":
            # Test all configurations
            try:
                weather = get_weather_config()
                print(f"✅ Weather config loaded (API key: {weather['api_key'][:10]}...)")
            except Exception as e:
                print(f"❌ Weather config error: {e}")
            
            try:
                spotify = get_spotify_config()
                print(f"✅ Spotify config loaded (Client ID: {spotify['client_id'][:10]}...)")
            except Exception as e:
                print(f"❌ Spotify config error: {e}")
                
    else:
        print("SynBi Secure Configuration Manager")
        print("Usage:")
        print("  python config_secure.py validate  - Validate all configurations")
        print("  python config_secure.py template  - Create .env template")
        print("  python config_secure.py test      - Test configuration loading")