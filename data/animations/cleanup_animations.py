#!/usr/bin/env python3
"""
Animation Cleanup Script
========================
Deletes all animation JSON files from output_html/data/animations that aren't
used by the hitbox viewer. Reduces the ~46 GB animations folder to only the
files actually referenced by the viewer.

Usage:
    python cleanup_animations.py                 # Dry run (shows what would be deleted)
    python cleanup_animations.py --delete        # Actually delete files
    python cleanup_animations.py --delete --remove-empty  # Delete files AND empty folders
"""

import os
import sys
from pathlib import Path

# ============================================================================
# CONFIGURATION - Update this path to match your setup
# ============================================================================

ANIMATIONS_DIR = r"C:\Users\Alex\Desktop\output_html\data\animations"

# ============================================================================
# DEFINITIVE LIST OF NEEDED ANIMATION FILENAMES
# Built from viewer.html ANIM_FILENAMES, CHARACTER_ANIM_OVERRIDES,
# getAnimFilenames(), and hitbox_extractor.py MOVE_ANIM_FILENAMES.
# ============================================================================

# --- Global animations (any character may use these) ---
GLOBAL_ANIMS = {
    # Jabs
    'c00attack11',          # jab1
    'c00attack12',          # jab2
    'c00attack13',          # jab3 (also used as jab3 fallback)
    'c00attack100',         # rapid_jab
    'c00attackend',         # rapid_jab_finisher (standard)
    'c00attack100end',      # rapid_jab_finisher (alt) / jab3 (alt)

    # Kazuya 10-hit combo
    'c00attack1combo3',
    'c00attack1combo4',
    'c00attack1combo5',
    'c00attack1combo6',
    'c00attack1combo7',
    'c00attack1combo8',
    'c00attack1combo9',
    'c00attack1combo10',

    # Tilts
    'c01attacks3s',         # ftilt
    'c01attacks3s2',        # ftilt2 (Snake second hit / ftilt2 fallback)
    'c02attackhi3',         # utilt
    'c02attacklw3',         # dtilt

    # Smashes
    'c03attacks4s',         # fsmash
    'c03attacks4s2',        # fsmash2 (Link/Snake fsmash hit 2, Prickly lunge)
    'c03attacks4s3',        # fsmash3 (Snake fsmash hit 3)
    'c04attackhi4',         # usmash
    'c04attacklw4',         # dsmash

    # Aerials
    'c05attackairn',        # nair
    'c05attackairf',        # fair
    'c05attackairb',        # bair
    'c05attackairhi',       # uair
    'c05attackairlw',       # dair

    # Dash attack
    'c00attackdash',        # dash_attack

    # Grabs
    'e00catch',             # grab
    'e00catchdash',         # dash_grab
    'e00catchturn',         # pivot_grab
    'e00catchattack',       # pummel

    # Throws
    'e01throwf',            # fthrow
    'e01throwb',            # bthrow
    'e01throwhi',           # uthrow
    'e01throwlw',           # dthrow

    # DK cargo throw variants
    'e01throwff',           # fthrow_forward
    'e01throwfb',           # fthrow_back
    'e01throwfhi',          # fthrow_high
    'e01throwflw',          # fthrow_low
}

# --- Character-specific animations ---
# Only these characters need these additional files.
# Key = character folder name (as it appears in the animations directory)
# Value = set of additional animation basenames needed
CHARACTER_SPECIFIC_ANIMS = {
    # Ryu: weak/strong variants for jabs and tilts
    'ryu': {
        'c00attack11w',     # jab1 weak
        'c00attack11s',     # jab1 strong
        'c00attack12s',     # jab2 strong
        'c01attacks3sw',    # ftilt weak
        'c01attacks3ss',    # ftilt strong
        'c02attackhi3w',    # utilt weak
        'c02attackhi3s',    # utilt strong
        'c02attacklw3w',    # dtilt weak
        'c02attacklw3s',    # dtilt strong
    },
    # Ken: same weak/strong variants as Ryu
    'ken': {
        'c00attack11w',
        'c00attack11s',
        'c00attack12s',
        'c01attacks3sw',
        'c01attacks3ss',
        'c02attackhi3w',
        'c02attackhi3s',
        'c02attacklw3w',
        'c02attacklw3s',
    },
    # Piranha Plant: stance-specific animations
    'packun': {
        'c01attacks3sa',    # Regular ftilt (fire breath)
        'c05attackairbs',   # Prickly bair (spike)
    },
}

# --- Folder aliases ---
# Some characters share animation folders or use alternate folder names.
# Maps: viewer's animFolder name -> actual folder name in the filesystem.
# The cleanup script needs to know which folders to look in.
ANIM_FOLDER_ALIASES = {
    # Ice Climbers: popo and nana both use popo's animations,
    # but data may be in 'popo' or 'iceclimber' folder
    'popo': 'popo',
    'nana': 'popo',
    'iceclimber': 'popo',
    # Mii characters use miienemy* folders for animations
    'miifighter': 'miienemyf',
    'miiswordsman': 'miienemys',
    'miigunner': 'miienemyg',
}


def get_needed_anims_for_folder(folder_name):
    """Return the set of animation basenames needed for a given character folder."""
    needed = set(GLOBAL_ANIMS)

    # Add character-specific anims
    if folder_name in CHARACTER_SPECIFIC_ANIMS:
        needed |= CHARACTER_SPECIFIC_ANIMS[folder_name]

    # Also check if this folder is an alias target for any character with specific anims
    for char, alias in ANIM_FOLDER_ALIASES.items():
        if alias == folder_name and char in CHARACTER_SPECIFIC_ANIMS:
            needed |= CHARACTER_SPECIFIC_ANIMS[char]

    return needed


def normalize_basename(filename):
    """Extract the animation basename from a filename.
    Handles: 'c00attack11.json', 'c00attack11.nuanmb.json', etc.
    Returns the basename without extension (e.g. 'c00attack11')."""
    name = filename
    # Strip .json
    if name.endswith('.json'):
        name = name[:-5]
    # Strip .nuanmb if present (some files are .nuanmb.json)
    if name.endswith('.nuanmb'):
        name = name[:-7]
    return name


def cleanup_animations(animations_dir, do_delete=False, remove_empty=False):
    """Walk the animations directory and identify/delete unneeded files."""
    animations_path = Path(animations_dir)

    if not animations_path.exists():
        print(f"ERROR: Animations directory not found: {animations_path}")
        print(f"Update ANIMATIONS_DIR in this script to point to your output_html/data/animations folder.")
        sys.exit(1)

    total_files = 0
    kept_files = 0
    deleted_files = 0
    deleted_bytes = 0
    kept_bytes = 0
    per_char_stats = {}

    # Walk each character folder
    for char_folder in sorted(animations_path.iterdir()):
        if not char_folder.is_dir():
            continue

        char_name = char_folder.name
        needed = get_needed_anims_for_folder(char_name)

        char_kept = 0
        char_deleted = 0
        char_deleted_bytes = 0

        # Walk all files recursively under this character folder
        for root, dirs, files in os.walk(char_folder):
            for filename in files:
                filepath = Path(root) / filename

                if not filename.endswith('.json'):
                    continue

                total_files += 1
                basename = normalize_basename(filename)
                file_size = filepath.stat().st_size

                if basename in needed:
                    kept_files += 1
                    kept_bytes += file_size
                    char_kept += 1
                else:
                    deleted_files += 1
                    deleted_bytes += file_size
                    char_deleted += 1
                    char_deleted_bytes += file_size

                    if do_delete:
                        filepath.unlink()

        if char_kept > 0 or char_deleted > 0:
            per_char_stats[char_name] = {
                'kept': char_kept,
                'deleted': char_deleted,
                'deleted_bytes': char_deleted_bytes,
            }

    # Remove empty directories if requested
    empty_dirs_removed = 0
    if do_delete and remove_empty:
        # Walk bottom-up to remove empty dirs
        for root, dirs, files in os.walk(animations_path, topdown=False):
            for d in dirs:
                dir_path = Path(root) / d
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        empty_dirs_removed += 1
                except OSError:
                    pass

    return {
        'total_files': total_files,
        'kept_files': kept_files,
        'deleted_files': deleted_files,
        'deleted_bytes': deleted_bytes,
        'kept_bytes': kept_bytes,
        'per_char': per_char_stats,
        'empty_dirs_removed': empty_dirs_removed,
    }


def format_size(bytes_val):
    """Format bytes as human-readable size."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024
    return f"{bytes_val:.1f} PB"


def main():
    do_delete = '--delete' in sys.argv
    remove_empty = '--remove-empty' in sys.argv

    mode = "DELETE MODE" if do_delete else "DRY RUN (use --delete to actually remove files)"

    print("=" * 70)
    print("ANIMATION CLEANUP SCRIPT")
    print(f"Mode: {mode}")
    print(f"Target: {ANIMATIONS_DIR}")
    print("=" * 70)
    print()

    # Show what we're keeping
    print(f"Global animations kept per character: {len(GLOBAL_ANIMS)}")
    for char, anims in sorted(CHARACTER_SPECIFIC_ANIMS.items()):
        print(f"  + {char}: {len(anims)} extra ({', '.join(sorted(anims))})")
    print()

    stats = cleanup_animations(ANIMATIONS_DIR, do_delete=do_delete, remove_empty=remove_empty)

    # Per-character summary (only show chars with deletions)
    chars_with_deletions = {k: v for k, v in stats['per_char'].items() if v['deleted'] > 0}
    if chars_with_deletions:
        print(f"Per-character breakdown ({len(chars_with_deletions)} characters with removals):")
        print(f"  {'Character':<25} {'Kept':>6} {'Removed':>8} {'Freed':>12}")
        print(f"  {'-'*25} {'-'*6} {'-'*8} {'-'*12}")
        for char, info in sorted(chars_with_deletions.items()):
            print(f"  {char:<25} {info['kept']:>6} {info['deleted']:>8} {format_size(info['deleted_bytes']):>12}")
        print()

    # Summary
    action = "Deleted" if do_delete else "Would delete"
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Total animation files scanned:  {stats['total_files']:>8}")
    print(f"  Files kept:                      {stats['kept_files']:>8}  ({format_size(stats['kept_bytes'])})")
    print(f"  Files {action.lower():<8}:                {stats['deleted_files']:>8}  ({format_size(stats['deleted_bytes'])})")
    if stats['kept_bytes'] + stats['deleted_bytes'] > 0:
        pct = stats['deleted_bytes'] / (stats['kept_bytes'] + stats['deleted_bytes']) * 100
        print(f"  Space freed:                     {pct:.1f}%")
    if do_delete and remove_empty:
        print(f"  Empty directories removed:       {stats['empty_dirs_removed']:>8}")
    print()

    if not do_delete:
        print("This was a DRY RUN. No files were deleted.")
        print("Run with --delete to actually remove files.")
        print("Run with --delete --remove-empty to also clean up empty folders.")
    else:
        print(f"Done! Freed {format_size(stats['deleted_bytes'])}.")


if __name__ == '__main__':
    main()
