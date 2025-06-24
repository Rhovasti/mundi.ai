#!/usr/bin/env python3
"""
Restore original files from backups and re-run transformation with correct bounds.
"""

import shutil
from pathlib import Path
import subprocess
import sys

def restore_from_backups():
    """Restore original files from .backup versions."""
    print("🔄 Restoring original files from backups...")
    
    # Find all backup files
    eno_base = Path("/app/Eno")
    backup_files = list(eno_base.glob("**/*.backup"))
    
    restored_count = 0
    for backup_file in backup_files:
        original_file = backup_file.with_suffix('')  # Remove .backup extension
        
        if backup_file.exists():
            shutil.copy2(backup_file, original_file)
            print(f"  ✅ Restored: {original_file.relative_to(eno_base)}")
            restored_count += 1
    
    print(f"Restored {restored_count} files from backups")
    return restored_count

def run_transformation():
    """Run the coordinate transformation script."""
    print("\n🗺️  Running coordinate transformation...")
    
    try:
        # Run the transformation script
        result = subprocess.run([
            sys.executable, "/app/transform_eno_coordinates.py"
        ], capture_output=True, text=True, timeout=300)  # 5 minute timeout
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Transformation completed successfully!")
            return True
        else:
            print(f"❌ Transformation failed with return code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Transformation timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"❌ Error running transformation: {e}")
        return False

def main():
    """Main restoration and transformation function."""
    print("🔧 Eno Coordinate Restoration and Re-transformation")
    print("=" * 60)
    
    # Step 1: Restore from backups
    restored_count = restore_from_backups()
    
    if restored_count == 0:
        print("⚠️  No backup files found. Proceeding with existing files...")
    
    # Step 2: Run transformation with corrected bounds
    success = run_transformation()
    
    if success:
        print("\n🎉 Process completed successfully!")
    else:
        print("\n❌ Process failed. Check the logs above.")

if __name__ == "__main__":
    main()