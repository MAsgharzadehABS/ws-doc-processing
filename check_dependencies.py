#!/usr/bin/env python3
"""
Dependency checker for Marine Fuel Document Processing System
Verifies that all required dependencies are installed and configured properly.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.7 or higher."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 7:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (Good)")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.7+)")
        return False

def check_tesseract():
    """Check if Tesseract OCR is installed and accessible."""
    print("\n🔍 Checking Tesseract OCR...")
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            return True
        else:
            print(f"   ❌ Tesseract command failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("   ❌ Tesseract not found in PATH")
        print("   💡 Install from: https://github.com/UB-Mannheim/tesseract/wiki")
        return False
    except subprocess.TimeoutExpired:
        print("   ❌ Tesseract command timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error checking Tesseract: {e}")
        return False

def check_python_packages():
    """Check if required Python packages are installed."""
    print("\n📦 Checking Python packages...")
    
    # Package mapping: pip_name -> import_name
    required_packages = {
        'pytesseract': 'pytesseract',
        'pdf2image': 'pdf2image', 
        'Pillow': 'PIL',  # Pillow package imports as PIL
        'openai': 'openai',
        'python-dotenv': 'dotenv'  # python-dotenv package imports as dotenv
    }
    
    missing_packages = []
    
    for pip_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✅ {pip_name}")
        except ImportError:
            print(f"   ❌ {pip_name} (missing)")
            missing_packages.append(pip_name)
    
    if missing_packages:
        print(f"\n   💡 Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    return True

def check_test_directory():
    """Check if test directory exists and contains PDF files."""
    print("\n📁 Checking test directory...")
    test_dir = Path("test")
    
    if not test_dir.exists():
        print("   ❌ 'test' directory not found")
        print("   💡 Create 'test' directory and place your PDF files there")
        return False
    
    pdf_files = list(test_dir.glob("*.pdf")) + list(test_dir.glob("*.PDF"))
    if not pdf_files:
        print("   ⚠️  'test' directory exists but contains no PDF files")
        print("   💡 Place your PDF files in the 'test' directory")
        return False
    
    print(f"   ✅ Found {len(pdf_files)} PDF file(s):")
    for pdf_file in pdf_files:
        print(f"      - {pdf_file.name}")
    
    return True

def check_env_file():
    """Check if .env file exists and contains required Azure OpenAI configuration."""
    print("\n🔧 Checking configuration...")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("   ❌ .env file not found")
        print("   💡 Create .env file with your Azure OpenAI configuration")
        return False
    
    env_content = env_file.read_text()
    required_vars = ['OPENAI_ENDPOINT', 'OPENAI_KEY']
    missing_vars = []
    
    for var in required_vars:
        if var not in env_content or f"{var}=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Missing required variables: {', '.join(missing_vars)}")
        print("   💡 Add to .env file:")
        for var in missing_vars:
            print(f"      {var}=your_value_here")
        return False
    
    print("   ✅ .env file configured")
    return True

def test_tesseract_functionality():
    """Test Tesseract OCR functionality with a simple test."""
    print("\n🧪 Testing Tesseract functionality...")
    try:
        import pytesseract
        from PIL import Image
        import io
        
        # Create a simple test image with text
        from PIL import ImageDraw, ImageFont
        
        # Create a simple white image with black text
        img = Image.new('RGB', (200, 50), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "TEST", fill='black')
        
        # Test OCR
        text = pytesseract.image_to_string(img).strip()
        if 'TEST' in text.upper():
            print("   ✅ Tesseract OCR functionality working")
            return True
        else:
            print(f"   ⚠️  Tesseract OCR may have issues (got: '{text}')")
            return False
            
    except Exception as e:
        print(f"   ❌ Tesseract functionality test failed: {e}")
        return False

def main():
    """Run all dependency checks."""
    print("🔍 Marine Fuel Document Processing System - Dependency Check")
    print("=" * 65)
    
    checks = [
        ("Python Version", check_python_version),
        ("Tesseract OCR", check_tesseract),
        ("Python Packages", check_python_packages),
        ("Test Directory", check_test_directory),
        ("Configuration", check_env_file),
        ("OCR Functionality", test_tesseract_functionality)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Error during {name} check: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 65)
    print("📊 DEPENDENCY CHECK SUMMARY")
    print("=" * 65)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All dependencies are ready!")
        print("You can now run: python main.py")
    else:
        print(f"\n⚠️  {total - passed} issue(s) need to be resolved before processing PDFs")
        print("\nNext steps:")
        if not any(name == "Tesseract OCR" and result for name, result in results):
            print("1. Install Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki")
        if not any(name == "Python Packages" and result for name, result in results):
            print("2. Install Python packages: pip install -r requirements.txt")
        if not any(name == "Configuration" and result for name, result in results):
            print("3. Create .env file with Azure OpenAI configuration")
        if not any(name == "Test Directory" and result for name, result in results):
            print("4. Create 'test' directory and add your PDF files")

if __name__ == "__main__":
    main() 