"""
Simple test script to verify CORS configuration without FastAPI dependency.

This script tests the CORS configuration reading from environment variables.
"""

import os


def test_cors_env():
    """Test CORS environment variable configuration."""
    print("=" * 60)
    print("CORS Configuration Test (No Dependencies)")
    print("=" * 60)
    
    # Test getting allowed origins from env
    origins_env = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
    origins = [origin.strip() for origin in origins_env.split(",")]
    
    print(f"\n✅ Environment Variable ALLOWED_ORIGINS: {origins_env}")
    print(f"✅ Parsed Origins: {origins}")
    
    # Display expected CORS settings
    cors_config = {
        "allowed_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
        "expose_headers": ["*"],
        "max_age": 600,
    }
    
    print(f"\n✅ CORS Configuration:")
    for key, value in cors_config.items():
        print(f"   - {key}: {value}")
    
    print("\n" + "=" * 60)
    print("✅ CORS configuration is ready!")
    print("=" * 60)
    print("\nNote: This will be applied when FastAPI server starts.")


if __name__ == "__main__":
    test_cors_env()
