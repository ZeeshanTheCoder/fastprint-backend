from django.core.management.base import BaseCommand
from printbookcalculator.models import *

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # --- Trim Sizes (matching exact names from pricing data) ---
        trim_sizes = {
            "Pocket Book (4.25 x 6.875 in / 108 x 175 mm)": {},
            "Novella (5 x 8 in / 127 x 203 mm)": {},
            "Digest (5.5 x 8.5 in / 140 x 216 mm)": {},
            "A5 (5.83 x 8.27 in / 148 x 210 mm)": {},
            "US Trade (6 x 9 in / 152 x 229 mm)": {},
            "Royal (6.14 x 9.21 in / 156 x 234 mm)": {},
            "Executive (7 x 10 in / 178 x 254 mm)": {},
            "Crown Quarto (7.44 x 9.68 in / 189 x 246 mm)": {},
            "Small Square (7.5 x 7.5 in / 190 x 190 mm)": {},
            "A4 (8.27 x 11.69 in / 210 x 297 mm)": {},
            "Square (8.5 x 8.5 in / 216 x 216 mm)": {},
            "US Letter (8.5 x 11 in / 216 x 279 mm)": {},
            "Small Landscape (9 x 7 in / 229 x 178 mm)": {},
            "US Letter Landscape (11 x 8.5 in / 279 x 216 mm)": {},
            "A4 Landscape (11.69 x 8.27 in / 297 x 210 mm)": {},
        }
        
        # Create and store TrimSize objects
        for trim_name in trim_sizes:
            trim_sizes[trim_name]['obj'] = TrimSize.objects.get_or_create(name=trim_name)[0]

        # --- Interior Colors (matching exact pricing from data) ---
        InteriorColor.objects.get_or_create(name="Standard Black & white", price_per_page=0.01)
        InteriorColor.objects.get_or_create(name="Premium Black & white", price_per_page=0.02)
        InteriorColor.objects.get_or_create(name="Standard Color", price_per_page=0.03)
        InteriorColor.objects.get_or_create(name="Premium Color", price_per_page=0.10)

        # --- Paper Types (matching exact pricing from data) ---
        PaperType.objects.get_or_create(name="60# Cream-Uncoated", price_per_page=0.01)
        PaperType.objects.get_or_create(name="60# White-uncoated", price_per_page=0.01)
        PaperType.objects.get_or_create(name="80# White-Coated", price_per_page=0.02)

        # --- Cover Finishes (matching exact pricing from data) ---
        CoverFinish.objects.get_or_create(name="Gloss", price=0.10)
        CoverFinish.objects.get_or_create(name="Matte", price=0.10)

        # --- Binding Types for each Trim Size (exact prices from pricing data) ---
        binding_data = {
            "Pocket Book (4.25 x 6.875 in / 108 x 175 mm)": [
                ("Perfect bond", 1.91, 32, 470),
                ("Saddle Stitch", 3.59, 4, 48),
                ("Case Wrap", 9.86, 24, 470),
                ("Coil bond", 5.90, 3, 470),
                ("Linen Wrap", 6.00, 32, 470),
            ],
            "Novella (5 x 8 in / 127 x 203 mm)": [
                ("Perfect bond", 1.97, 32, 470),
                ("Saddle Stitch", 3.50, 4, 48),
                ("Case Wrap", 9.80, 24, 470),
                ("Coil bond", 5.76, 3, 470),
                # Linen Wrap shows $- in data, treating as unavailable
            ],
            "Digest (5.5 x 8.5 in / 140 x 216 mm)": [
                ("Perfect bond", 1.90, 32, 470),
                ("Saddle Stitch", 3.50, 4, 48),
                ("Case Wrap", 9.80, 24, 470),
                ("Coil bond", 5.95, 3, 470),
                ("Linen Wrap", 13.75, 32, 470),
            ],
            "A5 (5.83 x 8.27 in / 148 x 210 mm)": [
                ("Perfect bond", 1.90, 32, 470),
                ("Saddle Stitch", 3.46, 4, 48),
                ("Case Wrap", 9.80, 24, 470),
                ("Coil bond", 5.80, 3, 470),
                ("Linen Wrap", 13.75, 32, 470),
            ],
            "US Trade (6 x 9 in / 152 x 229 mm)": [
                ("Perfect bond", 1.71, 32, 470),
                ("Saddle Stitch", 3.46, 4, 48),
                ("Case Wrap", 9.96, 24, 470),
                ("Coil bond", 5.96, 3, 470),
                ("Linen Wrap", 13.50, 32, 470),
            ],
            "Royal (6.14 x 9.21 in / 156 x 234 mm)": [
                ("Perfect bond", 1.71, 32, 470),
                ("Saddle Stitch", 3.46, 4, 48),
                ("Case Wrap", 9.96, 24, 470),
                ("Coil bond", 5.96, 3, 470),
                ("Linen Wrap", 13.50, 32, 470),
            ],
            "Executive (7 x 10 in / 178 x 254 mm)": [
                ("Perfect bond", 2.00, 32, 470),
                ("Saddle Stitch", 4.10, 4, 48),
                ("Case Wrap", 10.00, 24, 470),
                ("Coil bond", 6.40, 3, 470),
                ("Linen Wrap", 13.95, 32, 470),
            ],
            "Crown Quarto (7.44 x 9.68 in / 189 x 246 mm)": [
                ("Perfect bond", 2.00, 32, 470),
                ("Saddle Stitch", 4.10, 4, 48),
                ("Case Wrap", 10.00, 24, 470),
                ("Coil bond", 6.40, 3, 470),
                ("Linen Wrap", 13.95, 32, 470),
            ],
            "Small Square (7.5 x 7.5 in / 190 x 190 mm)": [
                ("Perfect bond", 2.00, 32, 470),
                ("Saddle Stitch", 4.10, 4, 48),
                ("Case Wrap", 10.00, 24, 470),
                ("Coil bond", 6.40, 3, 470),
                ("Linen Wrap", 13.50, 32, 470),
            ],
            "A4 (8.27 x 11.69 in / 210 x 297 mm)": [
                ("Perfect bond", 2.10, 32, 470),
                ("Saddle Stitch", 3.82, 4, 48),
                ("Case Wrap", 9.75, 24, 470),
                ("coil bond", 6.18, 3, 470),
                ("Linen Wrap", 13.80, 32, 470),
            ],
            "Square (8.5 x 8.5 in / 216 x 216 mm)": [
                ("Perfect bond", 2.00, 32, 470),
                ("Saddle Stitch", 3.82, 4, 48),
                ("Case Wrap", 9.75, 24, 470),
                ("coil bond", 6.18, 3, 470),
                ("Linen Wrap", 13.80, 32, 470),
            ],
            "US Letter (8.5 x 11 in / 216 x 279 mm)": [
                ("Perfect bond", 2.00, 32, 470),
                ("Saddle Stitch", 3.82, 4, 48),
                ("Case Wrap", 9.75, 24, 470),
                ("coil bond", 6.18, 3, 470),
                ("Linen Wrap", 13.80, 32, 470),
            ],
            "Small Landscape (9 x 7 in / 229 x 178 mm)": [
                ("Perfect bond", 2.00, 32, 470),
                ("Saddle Stitch", 3.82, 4, 48),
                ("Case Wrap", 9.75, 24, 470),
                ("coil bond", 6.18, 3, 470),
                ("Linen Wrap", 13.80, 32, 470),
            ],
            "US Letter Landscape (11 x 8.5 in / 279 x 216 mm)": [
                ("Perfect bond", 2.00, 32, 250),  # Perfect bound disappears after 250 pages
                ("Saddle Stitch", 3.82, 4, 48),
                ("Case Wrap", 9.75, 24, 470),
                ("coil bond", 6.22, 3, 470),
                ("Linen Wrap", 18.00, 32, 470),
            ],
            "A4 Landscape (11.69 x 8.27 in / 297 x 210 mm)": [
                ("Perfect bond", 2.00, 32, 250),  # Perfect bound disappears after 250 pages
                ("Saddle Stitch", 5.00, 4, 48),
                ("Case Wrap", 9.75, 24, 470),
                ("coil bond", 6.18, 3, 470),
                ("Linen Wrap", 13.80, 32, 470),
            ],
        }

        for trim_name, bindings in binding_data.items():
            trim_obj = trim_sizes[trim_name]['obj']
            for name, price, min_pages, max_pages in bindings:
                BindingType.objects.get_or_create(
                    name=name,
                    price=price,
                    trim_size=trim_obj,
                    min_pages=min_pages,
                    max_pages=max_pages
                )

        self.stdout.write(self.style.SUCCESS("✅ All trim sizes and binding types seeded as per calculation table!"))