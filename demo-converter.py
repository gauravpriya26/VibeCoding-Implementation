#!/usr/bin/env python3
"""
Jenkins to GitHub Actions Converter - Demo Script
=================================================

This script demonstrates how to use the Jenkins to GHA converter
and provides an easy way to convert your Jenkins repositories.

Usage:
    python demo-converter.py
"""

import os
import sys
from pathlib import Path

def main():
    print("=" * 60)
    print("   Jenkins to GitHub Actions Converter - Demo")
    print("=" * 60)
    print()
    
    # Check if the main converter script exists
    converter_script = Path("jenkins-to-gha-converter.py")
    if not converter_script.exists():
        print("❌ Error: jenkins-to-gha-converter.py not found!")
        print("   Please ensure the converter script is in the same directory.")
        return 1
    
    # Get input directory
    print("📁 Enter the path to your Jenkins repository:")
    print("   (Example: ./simple-java-maven-app)")
    input_path = input("Input path: ").strip()
    
    if not input_path:
        input_path = "./simple-java-maven-app"
        print(f"   Using default: {input_path}")
    
    # Validate input path
    if not Path(input_path).exists():
        print(f"❌ Error: Input path '{input_path}' does not exist!")
        return 1
    
    # Get output directory
    print()
    print("📁 Enter the output path for GitHub Actions repository:")
    print("   (Example: ./converted-project)")
    output_path = input("Output path: ").strip()
    
    if not output_path:
        output_path = "./converted-project"
        print(f"   Using default: {output_path}")
    
    # Java versions
    print()
    print("☕ Java versions to test against (space-separated):")
    print("   (Example: 17 21)")
    java_versions_input = input("Java versions: ").strip()
    
    if java_versions_input:
        java_versions = java_versions_input.split()
    else:
        java_versions = ["17", "21"]
        print(f"   Using default: {' '.join(java_versions)}")
    
    # Build the command
    command_parts = [
        "python",
        "jenkins-to-gha-converter.py",
        "--input", f'"{input_path}"',
        "--output", f'"{output_path}"',
        "--java-versions"
    ]
    command_parts.extend(java_versions)
    command_parts.append("--verbose")
    
    command = " ".join(command_parts)
    
    print()
    print("🚀 Running conversion with the following command:")
    print(f"   {command}")
    print()
    
    # Confirm before running
    confirm = input("Proceed with conversion? (y/N): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Conversion cancelled.")
        return 0
    
    print()
    print("=" * 60)
    print("Starting conversion...")
    print("=" * 60)
    
    # Run the conversion
    exit_code = os.system(command)
    
    print()
    print("=" * 60)
    if exit_code == 0:
        print("✅ CONVERSION COMPLETED SUCCESSFULLY!")
        print()
        print(f"Your Jenkins repository has been converted to GitHub Actions!")
        print(f"📁 Output directory: {output_path}")
        print(f"🔄 Workflows: {output_path}/.github/workflows/")
        print()
        print("Next steps:")
        print("1. Review the generated workflows")
        print("2. Copy to your GitHub repository")
        print("3. Commit and push to test the workflows")
    else:
        print("❌ CONVERSION FAILED!")
        print("Please check the error messages above.")
    print("=" * 60)
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        input("\nPress Enter to exit...")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nConversion cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
        sys.exit(1)
