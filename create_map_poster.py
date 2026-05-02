from __future__ import annotations

import argparse
import sys

from maptoposter import MapPosterApp


def print_examples() -> None:
    """Print usage examples."""
    print("""
Poster Generator
================

Usage:
  python create_map_poster.py --city <city> --country <country> [options]
  python create_map_poster.py --face-image <path> [options]

Examples:
  # Iconic grid patterns
  python create_map_poster.py -c "New York" -C "USA" -t noir -d 12000
  python create_map_poster.py -c "Barcelona" -C "Spain" -t warm_beige -d 8000

  # Waterfront & canals
  python create_map_poster.py -c "Venice" -C "Italy" -t blueprint -d 4000
  python create_map_poster.py -c "Amsterdam" -C "Netherlands" -t ocean -d 6000
  python create_map_poster.py -c "Dubai" -C "UAE" -t midnight_blue -d 15000

  # Radial patterns
  python create_map_poster.py -c "Paris" -C "France" -t pastel_dream -d 10000
  python create_map_poster.py -c "Moscow" -C "Russia" -t noir -d 12000

  # Organic old cities
  python create_map_poster.py -c "Tokyo" -C "Japan" -t japanese_ink -d 15000
  python create_map_poster.py -c "Marrakech" -C "Morocco" -t terracotta -d 5000
  python create_map_poster.py -c "Rome" -C "Italy" -t warm_beige -d 8000

  # Coastal cities
  python create_map_poster.py -c "San Francisco" -C "USA" -t sunset -d 10000
  python create_map_poster.py -c "Sydney" -C "Australia" -t ocean -d 12000
  python create_map_poster.py -c "Mumbai" -C "India" -t contrast_zones -d 18000

  # River cities
  python create_map_poster.py -c "London" -C "UK" -t noir -d 15000
  python create_map_poster.py -c "Budapest" -C "Hungary" -t copper_patina -d 8000

  # List themes
  python create_map_poster.py --list-themes

  # Face poster
  python create_map_poster.py --face-image images/a.png -t noir --face-title "A" --face-subtitle "PORTRAIT"

Options:
  --city, -c        City name (required)
  --country, -C     Country name (required)
  --theme, -t       Theme name (default: feature_based)
  --distance, -d    Map radius in meters (default: 29000)
  --face-image      Local image path for a face poster
  --face-title      Main title for a face poster
  --face-subtitle   Subtitle for a face poster
  --list-themes     List all available themes
""")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate themed map posters and face posters",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python create_map_poster.py --city "New York" --country "USA"
  python create_map_poster.py --city Tokyo --country Japan --theme midnight_blue
  python create_map_poster.py --city Paris --country France --theme noir --distance 15000
  python create_map_poster.py --face-image images/a.png --theme noir --face-title "A"
  python create_map_poster.py --list-themes
        """,
    )
    parser.add_argument("--city", "-c", type=str, help="City name")
    parser.add_argument("--country", "-C", type=str, help="Country name")
    parser.add_argument("--theme", "-t", type=str, default="feature_based", help="Theme name (default: feature_based)")
    parser.add_argument("--distance", "-d", type=int, default=29000, help="Map radius in meters (default: 29000)")
    parser.add_argument("--face-image", type=str, help="Local image path for a face poster")
    parser.add_argument("--face-title", type=str, help="Main title for a face poster")
    parser.add_argument("--face-subtitle", type=str, default="Portrait", help="Subtitle for a face poster")
    parser.add_argument("--list-themes", action="store_true", help="List all available themes")
    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)
    app = MapPosterApp()

    if len(argv) == 0:
        print_examples()
        return 0

    if args.list_themes:
        app.list_themes()
        return 0

    if not app.has_theme(args.theme):
        print(f"Error: Theme '{args.theme}' not found.")
        print(f"Available themes: {', '.join(app.get_available_themes())}")
        return 1

    if args.face_image:
        face_title = args.face_title or "Portrait"
        print("=" * 50)
        print("Face Poster Generator")
        print("=" * 50)

        try:
            app.create_face_poster(args.face_image, args.theme, face_title, args.face_subtitle)
        except Exception as error:
            print(f"\nError: {error}")
            import traceback

            traceback.print_exc()
            return 1

        print("\n" + "=" * 50)
        print("Face poster generation complete.")
        print("=" * 50)
        return 0

    if not args.city or not args.country:
        print("Error: --city and --country are required for map posters.\n")
        print_examples()
        return 1

    print("=" * 50)
    print("City Map Poster Generator")
    print("=" * 50)

    try:
        app.create_city_poster(args.city, args.country, args.theme, args.distance)
    except Exception as error:
        print(f"\nError: {error}")
        import traceback

        traceback.print_exc()
        return 1

    print("\n" + "=" * 50)
    print("Poster generation complete.")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
