#!/usr/bin/env python3
"""Test script for Phase 3 implementation."""

import sys
import traceback

def test_interfaces():
    """Test interface imports."""
    try:
        from src.interfaces.base import AbstractScraperService
        print("✅ Interface imports successful")
        return True
    except Exception as e:
        print(f"❌ Interface import failed: {e}")
        traceback.print_exc()
        return False

def test_logging():
    """Test logging service."""
    try:
        from src.utils.logging_service import LoggingService
        logger = LoggingService('test')
        logger.info('Test message')
        print("✅ Logging service successful")
        return True
    except Exception as e:
        print(f"❌ Logging service failed: {e}")
        traceback.print_exc()
        return False

def test_container():
    """Test container with new services."""
    try:
        from src.container import container
        processor = container.get_processor()
        print("✅ Container successful")
        return True
    except Exception as e:
        print(f"❌ Container failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Phase 3 implementation...")
    
    results = []
    results.append(test_interfaces())
    results.append(test_logging())
    results.append(test_container())
    
    if all(results):
        print("🎉 All Phase 3 tests passed!")
    else:
        print("❌ Some Phase 3 tests failed!")
        sys.exit(1)
