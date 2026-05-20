import json
import os
import glob


def validate_json_files():
    # define the folder
    folder = "json_db"

    print(f"🔍 Scanning {folder} for syntax errors...\n")

    # Get all .json files
    files = glob.glob(os.path.join(folder, "*.json"))

    if not files:
        print(f"❌ No JSON files found in {folder}. Check your directory structure.")
        return

    error_count = 0

    for file_path in files:
        file_name = os.path.basename(file_path)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                json.load(f)
            # If we get here, it is valid
            print(f"✅ {file_name}: OK")

        except json.JSONDecodeError as e:
            error_count += 1
            print(f"❌ {file_name}: ERROR")
            print(f"   Line {e.lineno}, Column {e.colno}")
            print(f"   Issue: {e.msg}")
            print("-" * 30)
        except Exception as e:
            error_count += 1
            print(f"❌ {file_name}: CRITICAL ERROR - {e}")

    print("\n" + "=" * 30)
    if error_count == 0:
        print("🎉 ALL FILES ARE VALID. You are ready to run the engine.")
    else:
        print(f"⚠️ FOUND {error_count} BROKEN FILES. Fix them before running.")


if __name__ == "__main__":
    validate_json_files()