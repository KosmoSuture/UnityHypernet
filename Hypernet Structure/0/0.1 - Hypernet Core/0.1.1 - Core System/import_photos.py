"""
Photo Import Script for Hypernet MVP
Imports photos from a directory, extracts EXIF metadata, and populates the database
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import hashlib
import json

# For EXIF extraction
try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    print("PIL/Pillow not installed. Run: pip install Pillow")
    exit(1)

from mvp_models import (
    HypernetObject, Photo, ObjectType, PrivacyLevel,
    HypernetAddress
)


class PhotoImporter:
    """Import photos into Hypernet database"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def get_next_photo_instance(self, owner_address: str = "1.1") -> int:
        """Get next available instance number for photos"""
        self.cursor.execute("""
            SELECT MAX(instance) as max_instance
            FROM ha_registry
            WHERE category = 1
              AND subcategory = (SELECT subcategory FROM ha_registry WHERE hypernet_address = ?)
              AND type = 8
              AND subtype = 0
        """, (owner_address,))

        result = self.cursor.fetchone()
        max_instance = result['max_instance'] if result['max_instance'] else 0
        return max_instance + 1

    def extract_exif(self, image_path: str) -> dict:
        """Extract EXIF metadata from image"""
        try:
            image = Image.open(image_path)
            exif_data = image._getexif()

            if not exif_data:
                return {}

            exif = {}

            for tag_id, value in exif_data.items():
                tag = TAGS.get(tag_id, tag_id)
                exif[tag] = value

            # Extract GPS info if available
            if 'GPSInfo' in exif:
                gps_info = {}
                for key in exif['GPSInfo'].keys():
                    decode = GPSTAGS.get(key, key)
                    gps_info[decode] = exif['GPSInfo'][key]
                exif['GPSInfo'] = gps_info

            return exif

        except Exception as e:
            print(f"Error extracting EXIF from {image_path}: {e}")
            return {}

    def convert_gps_to_degrees(self, gps_coord, gps_ref) -> float:
        """Convert GPS coordinates to degrees"""
        d, m, s = gps_coord
        degrees = float(d) + float(m) / 60.0 + float(s) / 3600.0

        if gps_ref in ['S', 'W']:
            degrees = -degrees

        return degrees

    def get_gps_coordinates(self, exif: dict) -> Tuple[Optional[float], Optional[float]]:
        """Extract GPS latitude and longitude from EXIF"""
        gps_info = exif.get('GPSInfo', {})

        if not gps_info:
            return None, None

        try:
            gps_latitude = gps_info.get('GPSLatitude')
            gps_latitude_ref = gps_info.get('GPSLatitudeRef')
            gps_longitude = gps_info.get('GPSLongitude')
            gps_longitude_ref = gps_info.get('GPSLongitudeRef')

            if gps_latitude and gps_longitude:
                lat = self.convert_gps_to_degrees(gps_latitude, gps_latitude_ref)
                lon = self.convert_gps_to_degrees(gps_longitude, gps_longitude_ref)
                return lat, lon

        except Exception as e:
            print(f"Error parsing GPS data: {e}")

        return None, None

    def get_date_taken(self, exif: dict, file_path: str) -> datetime:
        """Get the date the photo was taken"""
        # Try EXIF date first
        date_str = exif.get('DateTimeOriginal') or exif.get('DateTime')

        if date_str:
            try:
                return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except:
                pass

        # Fall back to file modification time
        return datetime.fromtimestamp(os.path.getmtime(file_path))

    def compute_perceptual_hash(self, image_path: str) -> str:
        """Compute perceptual hash for duplicate detection"""
        try:
            image = Image.open(image_path)
            # Resize to 8x8
            image = image.resize((8, 8), Image.Resampling.LANCZOS).convert('L')
            # Get pixels
            pixels = list(image.getdata())
            # Compute average
            avg = sum(pixels) / len(pixels)
            # Generate hash
            bits = ''.join('1' if pixel > avg else '0' for pixel in pixels)
            # Convert to hex
            return hex(int(bits, 2))[2:].zfill(16)
        except Exception as e:
            print(f"Error computing hash for {image_path}: {e}")
            return ""

    def import_photo(self, file_path: str, owner_address: str = "1.1",
                    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE) -> Optional[str]:
        """Import a single photo"""

        # Get file info
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        # Extract EXIF
        print(f"Importing: {file_name}")
        exif = self.extract_exif(file_path)

        # Get image dimensions
        try:
            image = Image.open(file_path)
            width, height = image.size
        except Exception as e:
            print(f"Error opening image {file_path}: {e}")
            return None

        # Extract metadata
        camera_make = exif.get('Make', '').strip()
        camera_model = exif.get('Model', '').strip()
        lens_model = exif.get('LensModel', '').strip()
        iso = exif.get('ISOSpeedRatings')
        aperture = exif.get('FNumber')
        focal_length = exif.get('FocalLength')
        flash = 1 if exif.get('Flash', 0) else 0

        # Get GPS coordinates
        latitude, longitude = self.get_gps_coordinates(exif)

        # Get date taken
        taken_at = self.get_date_taken(exif, file_path)

        # Compute perceptual hash
        perceptual_hash = self.compute_perceptual_hash(file_path)

        # Check for duplicates
        if perceptual_hash:
            self.cursor.execute("""
                SELECT hypernet_address FROM photos WHERE perceptual_hash = ?
            """, (perceptual_hash,))
            if self.cursor.fetchone():
                print(f"  Duplicate detected, skipping: {file_name}")
                return None

        # Generate Hypernet Address
        instance = self.get_next_photo_instance(owner_address)
        hypernet_address = HypernetAddress.generate(1, 1, 8, 0, instance)

        # Create object record
        self.cursor.execute("""
            INSERT INTO objects (
                hypernet_address, object_type, owner_address, title,
                created_at, updated_at, original_date,
                file_path, file_size, mime_type,
                privacy_level, status, search_text
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hypernet_address,
            ObjectType.PHOTO.value,
            owner_address,
            file_name,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            taken_at.isoformat(),
            file_path,
            file_size,
            'image/jpeg',  # Simplified, could detect from extension
            privacy_level.value,
            'active',
            file_name  # For full-text search
        ))

        object_id = self.cursor.lastrowid

        # Create photo record
        self.cursor.execute("""
            INSERT INTO photos (
                object_id, hypernet_address,
                width, height,
                camera_make, camera_model, lens_model,
                iso, aperture, focal_length, flash,
                latitude, longitude,
                taken_at, perceptual_hash
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            object_id,
            hypernet_address,
            width,
            height,
            camera_make,
            camera_model,
            lens_model,
            iso,
            aperture,
            focal_length,
            flash,
            latitude,
            longitude,
            taken_at.isoformat(),
            perceptual_hash
        ))

        # Register address
        self.cursor.execute("""
            INSERT INTO ha_registry (
                hypernet_address, category, subcategory, type, subtype, instance,
                object_type, object_id, status, allocated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            hypernet_address, 1, 1, 8, 0, instance,
            ObjectType.PHOTO.value, object_id, 'active',
            datetime.now().isoformat()
        ))

        self.conn.commit()

        print(f"  ✓ Imported as {hypernet_address}")
        return hypernet_address

    def import_directory(self, directory: str, owner_address: str = "1.1",
                        privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE,
                        recursive: bool = False):
        """Import all photos from a directory"""

        photo_extensions = {'.jpg', '.jpeg', '.png', '.heic', '.heif'}
        count = 0

        if recursive:
            # Walk through all subdirectories
            for root, dirs, files in os.walk(directory):
                for file in files:
                    ext = Path(file).suffix.lower()
                    if ext in photo_extensions:
                        file_path = os.path.join(root, file)
                        if self.import_photo(file_path, owner_address, privacy_level):
                            count += 1
        else:
            # Just process files in the directory
            for file in os.listdir(directory):
                ext = Path(file).suffix.lower()
                if ext in photo_extensions:
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path):
                        if self.import_photo(file_path, owner_address, privacy_level):
                            count += 1

        print(f"\nImported {count} photos")
        return count

    def generate_thumbnails(self, max_photos: int = None):
        """Generate thumbnails for photos that don't have them"""
        # TODO: Implement thumbnail generation
        # For MVP, could use PIL to create 256x256, 512x512, 1024x1024 versions
        pass


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main import script"""
    import argparse

    parser = argparse.ArgumentParser(description='Import photos into Hypernet')
    parser.add_argument('directory', help='Directory containing photos')
    parser.add_argument('--db', default='hypernet.db', help='Database file')
    parser.add_argument('--owner', default='1.1', help='Owner Hypernet Address')
    parser.add_argument('--privacy', default='private',
                       choices=['private', 'family', 'friends', 'professional', 'public'],
                       help='Privacy level')
    parser.add_argument('--recursive', action='store_true',
                       help='Recursively import from subdirectories')

    args = parser.parse_args()

    # Convert privacy string to enum
    privacy_map = {
        'private': PrivacyLevel.PRIVATE,
        'family': PrivacyLevel.FAMILY,
        'friends': PrivacyLevel.FRIENDS,
        'professional': PrivacyLevel.PROFESSIONAL,
        'public': PrivacyLevel.PUBLIC
    }
    privacy_level = privacy_map[args.privacy]

    print(f"Importing photos from: {args.directory}")
    print(f"Owner: {args.owner}")
    print(f"Privacy: {args.privacy}")
    print(f"Recursive: {args.recursive}")
    print()

    with PhotoImporter(args.db) as importer:
        importer.import_directory(
            args.directory,
            owner_address=args.owner,
            privacy_level=privacy_level,
            recursive=args.recursive
        )

    print("\nDone!")


if __name__ == "__main__":
    main()


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

"""
# Import photos from Google Photos export
python import_photos.py "/path/to/Google Photos Takeout/Photos" --recursive --privacy family

# Import just your iPhone photos from last month
python import_photos.py "/Users/matt/Pictures/2024-02" --privacy private

# Import photos for another family member
python import_photos.py "/path/to/sarah/photos" --owner 1.2 --privacy private
"""
