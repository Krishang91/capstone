"""
Code verification script - checks for common issues
Run this before starting the API to catch potential problems
"""

def check_imports():
    """Check if all required imports are available"""
    print("Checking imports...")
    errors = []
    
    try:
        import torch
        print(f"✓ torch {torch.__version__}")
        print(f"  CUDA available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  CUDA version: {torch.version.cuda}")
            print(f"  Device: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        errors.append(f"✗ torch not found: {e}")
    
    try:
        import numpy as np
        print(f"✓ numpy {np.__version__}")
    except ImportError as e:
        errors.append(f"✗ numpy not found: {e}")
    
    try:
        import soundfile as sf
        print(f"✓ soundfile {sf.__version__}")
    except ImportError as e:
        errors.append(f"✗ soundfile not found: {e}")
    
    try:
        import fastapi
        print(f"✓ fastapi {fastapi.__version__}")
    except ImportError as e:
        errors.append(f"✗ fastapi not found: {e}")
    
    try:
        import uvicorn
        print(f"✓ uvicorn {uvicorn.__version__}")
    except ImportError as e:
        errors.append(f"✗ uvicorn not found: {e}")
    
    try:
        from torch.optim.swa_utils import AveragedModel, SWALR
        print(f"✓ torch.optim.swa_utils available")
    except ImportError as e:
        errors.append(f"✗ torch.optim.swa_utils not found: {e}")
    
    return errors


def check_files():
    """Check if required files exist"""
    print("\nChecking required files...")
    import os
    errors = []
    
    files_to_check = [
        "config/AASIST-L.conf",
        "models/weights/AASIST-L.pth",
        "api.py",
        "main.py",
        "data_utils.py",
        "utils.py",
        "models/AASIST.py"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            errors.append(f"✗ {file} - NOT FOUND")
    
    return errors


def check_model_import():
    """Check if model can be imported"""
    print("\nChecking model imports...")
    try:
        from models.AASIST import Model
        print("✓ AASIST model can be imported")
        return []
    except Exception as e:
        return [f"✗ Cannot import AASIST model: {e}"]


def check_data_utils():
    """Check if data_utils functions exist"""
    print("\nChecking data_utils...")
    try:
        from data_utils import pad, genSpoof_list
        print("✓ data_utils.pad available")
        print("✓ data_utils.genSpoof_list available")
        return []
    except Exception as e:
        return [f"✗ data_utils import error: {e}"]


def main():
    print("="*60)
    print("AASIST Code Verification")
    print("="*60)
    print()
    
    all_errors = []
    
    # Check imports
    all_errors.extend(check_imports())
    
    # Check files
    all_errors.extend(check_files())
    
    # Check model import
    all_errors.extend(check_model_import())
    
    # Check data utils
    all_errors.extend(check_data_utils())
    
    print()
    print("="*60)
    if all_errors:
        print("ERRORS FOUND:")
        print("="*60)
        for error in all_errors:
            print(error)
        print()
        print("Please fix these errors before running the API.")
        return False
    else:
        print("✓ ALL CHECKS PASSED!")
        print("="*60)
        print()
        print("Your code is ready to run!")
        print()
        print("Next steps:")
        print("1. Start the API: uvicorn api:app --reload")
        print("2. Test it: python test_api.py health")
        print("3. Open browser: http://localhost:8000/docs")
        return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
