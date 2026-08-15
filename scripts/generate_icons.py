import json
import os
from PIL import Image

# Source asset paths
SRC_SQUARE = "assets/icons/icon-512x512-square.png"
SRC_BG = "assets/icons/icon-512x512-background.png"
SRC_FG = "assets/icons/icon-512x512-foreground.png"
SRC_WIN = "assets/icons/icon-512x512.png"

# High-quality resampling filter
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS

def resize_save(img, size, dest_path):
    # Resizes an image and saves it to the target destination path.
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    img.resize((size, size), LANCZOS).save(dest_path, "PNG")

def resize_with_padding(img, target_size, safe_scale=0.666):
    # Resizes the image to fit the Android Safe Zone (~66.6% of the canvas)
    # and centers it on a transparent canvas to prevent the zoomed/cropped effect.
    inner_size = int(target_size * safe_scale)
    resized_inner = img.resize((inner_size, inner_size), LANCZOS)

    # Create a transparent target_size x target_size canvas
    canvas = Image.new("RGBA", (target_size, target_size), (0, 0, 0, 0))
    offset = (target_size - inner_size) // 2
    canvas.paste(resized_inner, (offset, offset), resized_inner)
    return canvas

def generate_android():
    res = "android/app/src/main/res"

    # Official Android icon specifications:
    # - Legacy (mipmap): 48, 72, 96, 144, 192 dp
    # - Adaptive (drawable): 108, 162, 216, 324, 432 dp
    densities = {
        "mdpi": (48, 108),
        "hdpi": (72, 162),
        "xhdpi": (96, 216),
        "xxhdpi": (144, 324),
        "xxxhdpi": (192, 432),
    }

    base = Image.open(SRC_SQUARE).convert("RGBA")
    fg = Image.open(SRC_FG).convert("RGBA") if os.path.exists(SRC_FG) else None
    bg = Image.open(SRC_BG).convert("RGBA") if os.path.exists(SRC_BG) else None

    for density, (legacy_size, adaptive_size) in densities.items():
        mipmap_dir = f"{res}/mipmap-{density}"
        drawable_dir = f"{res}/drawable-{density}"

        # 1. Legacy launcher icons (Android < API 26)
        resize_save(base, legacy_size, f"{mipmap_dir}/ic_launcher.png")

        # 2. Adaptive layers (Android API 26+)
        if fg:
            # Apply safe-zone padding to fix excessive zoom
            fg_padded = resize_with_padding(fg, adaptive_size, safe_scale=0.666)
            os.makedirs(drawable_dir, exist_ok=True)
            fg_padded.save(f"{drawable_dir}/ic_launcher_foreground.png", "PNG")
            fg_padded.save(f"{drawable_dir}/ic_launcher_monochrome.png", "PNG")

        if bg:
            # Background fills the full 108dp canvas
            resize_save(bg, adaptive_size, f"{drawable_dir}/ic_launcher_background.png")

    # 3. Adaptive icon XML configuration (in mipmap-anydpi-v26)
    xml_dir = f"{res}/mipmap-anydpi-v26"
    os.makedirs(xml_dir, exist_ok=True)
    with open(f"{xml_dir}/ic_launcher.xml", "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">\n'
            '    <background android:drawable="@drawable/ic_launcher_background"/>\n'
            '    <foreground android:drawable="@drawable/ic_launcher_foreground"/>\n'
            '    <monochrome android:drawable="@drawable/ic_launcher_monochrome"/>\n'
            "</adaptive-icon>\n"
        )
    print("✓ Android (Mipmap Legacy + Drawable Adaptive Safe-Zone)")

def generate_ios():
    dest = "ios/Runner/Assets.xcassets/AppIcon.appiconset"
    
    # 1. Load image and ensure NO alpha channel (App Store requirement)
    raw_base = Image.open(SRC_SQUARE)
    if raw_base.mode in ("RGBA", "LA") or (raw_base.mode == "P" and "transparency" in raw_base.info):
        # Create a solid white background (or change (255, 255, 255) to your brand color)
        base = Image.new("RGB", raw_base.size, (255, 255, 255))
        base.paste(raw_base, mask=raw_base.split()[-1])
    else:
        base = raw_base.convert("RGB")

    # Complete iOS size configuration (iPhone + iPad + App Store Marketing)
    sizes = [
        # iPhone
        ("20x20", "2x", 40, "iphone"),
        ("20x20", "3x", 60, "iphone"),
        ("29x29", "1x", 29, "iphone"),
        ("29x29", "2x", 58, "iphone"),
        ("29x29", "3x", 87, "iphone"),
        ("40x40", "2x", 80, "iphone"),
        ("40x40", "3x", 120, "iphone"),
        ("60x60", "2x", 120, "iphone"),
        ("60x60", "3x", 180, "iphone"),
        # iPad
        ("20x20", "1x", 20, "ipad"),
        ("20x20", "2x", 40, "ipad"),
        ("29x29", "1x", 29, "ipad"),
        ("29x29", "2x", 58, "ipad"),
        ("40x40", "1x", 40, "ipad"),
        ("40x40", "2x", 80, "ipad"),
        ("76x76", "1x", 76, "ipad"),
        ("76x76", "2x", 152, "ipad"),
        ("83.5x83.5", "2x", 167, "ipad"),
        # App Store Marketing
        ("1024x1024", "1x", 1024, "ios-marketing"),
    ]

    images = []
    for size, scale, px, idiom in sizes:
        filename = f"Icon-App-{size}@{scale}.png"
        resize_save(base, px, f"{dest}/{filename}")
        images.append(
            {
                "size": size,
                "idiom": idiom,
                "filename": filename,
                "scale": scale,
            }
        )

    with open(f"{dest}/Contents.json", "w", encoding="utf-8") as f:
        json.dump(
            {"images": images, "info": {"version": 1, "author": "xcode"}},
            f,
            indent=2,
        )
    print("✓ iOS (AppIcon.appiconset with iPad + No Alpha)")

def generate_windows():
    src = SRC_WIN if os.path.exists(SRC_WIN) else SRC_SQUARE
    os.makedirs("windows/runner/resources", exist_ok=True)
    sizes = [
        (16, 16),
        (24, 24),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256),
    ]
    Image.open(src).convert("RGBA").save("windows/runner/resources/app_icon.ico", format="ICO", sizes=sizes)
    print("✓ Windows (.ico multi-resolution)")

def generate_macos():
    dest = "macos/Runner/Assets.xcassets/AppIcon.appiconset"
    base = Image.open(SRC_SQUARE).convert("RGBA")
    sizes = [
        ("16x16", "1x", 16),
        ("16x16", "2x", 32),
        ("32x32", "1x", 32),
        ("32x32", "2x", 64),
        ("128x128", "1x", 128),
        ("128x128", "2x", 256),
        ("256x256", "1x", 256),
        ("256x256", "2x", 512),
        ("512x512", "1x", 512),
        ("512x512", "2x", 1024),
    ]

    images = []
    for size, scale, px in sizes:
        filename = f"app_icon_{px}.png"
        resize_save(base, px, f"{dest}/{filename}")
        images.append(
            {
                "size": size,
                "idiom": "mac",
                "filename": filename,
                "scale": scale,
            }
        )

    with open(f"{dest}/Contents.json", "w", encoding="utf-8") as f:
        json.dump(
            {"images": images, "info": {"version": 1, "author": "xcode"}},
            f,
            indent=2,
        )
    print("✓ macOS (AppIcon.appiconset)")

def generate_linux():
    """Generates standard FreeDesktop Linux icon sizes and Flutter window icon."""
    base = Image.open(SRC_SQUARE).convert("RGBA")

    # 1. Main GTK window icon (used directly by the Flutter Linux runner)
    resize_save(base, 512, "linux/assets/app_icon.png")

    # 2. Standard FreeDesktop icon resolutions (for .desktop files, snap, flatpak, deb)
    freedesktop_sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    for size in freedesktop_sizes:
        resize_save(base, size, f"linux/icons/{size}x{size}.png")

    print("✓ Linux (GTK runner asset + FreeDesktop resolutions)")

if __name__ == "__main__":
    if not os.path.exists(SRC_SQUARE):
        print(f"Error: Source image '{SRC_SQUARE}' not found.")
        exit(1)

    print("Generating launcher icons...")
    generate_windows()
    generate_android()
    generate_ios()
    generate_macos()
    generate_linux()
    print("Done! Clean and rebuild your project (flutter clean && flutter build apk).")