def get_available_bindings(page_count, book_size_name=None):
    """
    Get available binding options based on page count and book size.
    Updated to match exact pricing data from calculation table.
    
    Args:
        page_count (int): Number of pages in the book
        book_size_name (str): Name of the book size (exact match from pricing data)
        
    Returns:
        list: List of available binding options with exact names from pricing data
    """
    bindings = []
    
    if page_count < 2:
        return bindings
    
    # Check if it's a landscape format
    is_landscape = book_size_name and (
        'Landscape' in book_size_name
    )
    
    # Base rules for all formats
    if page_count >= 3:
        # Use exact naming from pricing data - some use "Coil bond", others "coil bond"
        if book_size_name in [
            "A4 (8.27 x 11.69 in / 210 x 297 mm)",
            "Square (8.5 x 8.5 in / 216 x 216 mm)", 
            "US Letter (8.5 x 11 in / 216 x 279 mm)",
            "Small Landscape (9 x 7 in / 229 x 178 mm)",
            "US Letter Landscape (11 x 8.5 in / 279 x 216 mm)",
            "A4 Landscape (11.69 x 8.27 in / 297 x 210 mm)"
        ]:
            bindings.append("coil bond")
        else:
            bindings.append("Coil bond")
    
    if page_count >= 4:
        bindings.append("Saddle Stitch")
    
    if page_count >= 24:
        bindings.append("Case Wrap")
    
    if page_count >= 32:
        # Perfect Bound availability rules
        if is_landscape:
            # Special rules for landscape formats
            if book_size_name in [
                'US Letter Landscape (11 x 8.5 in / 279 x 216 mm)', 
                'A4 Landscape (11.69 x 8.27 in / 297 x 210 mm)'
            ] and page_count <= 250:
                bindings.append("Perfect bond")
            elif book_size_name == 'Small Landscape (9 x 7 in / 229 x 178 mm)':
                bindings.append("Perfect bond")
        else:
            bindings.append("Perfect bond")
        
        # Linen Wrap availability - check for formats that don't have it
        if book_size_name != "Novella (5 x 8 in / 127 x 203 mm)":  # Novella shows $- for Linen Wrap
            bindings.append("Linen Wrap")
    
    # Remove bindings based on page count limits
    if page_count > 48:
        bindings = [b for b in bindings if b != "Saddle Stitch"]
    
    if page_count > 470:
        bindings = [b for b in bindings if b not in ["Coil bond", "coil bond"]]
    
    # Special rule for landscape formats - Perfect Bound disappears after 250 pages
    if is_landscape and book_size_name in [
        'US Letter Landscape (11 x 8.5 in / 279 x 216 mm)', 
        'A4 Landscape (11.69 x 8.27 in / 297 x 210 mm)'
    ] and page_count > 250:
        bindings = [b for b in bindings if b != "Perfect bond"]
    
    return list(set(bindings))

# Test cases based on pricing data:

# Example 1: Standard format (32+ pages gets all bindings)
print("US Trade 50 pages:", get_available_bindings(50, "US Trade (6 x 9 in / 152 x 229 mm)"))
# Expected: ['Coil bond', 'Case Wrap', 'Perfect bond', 'Linen Wrap']

# Example 2: Landscape format with 250+ page Perfect Bound limit
print("US Letter Landscape 300 pages:", get_available_bindings(300, "US Letter Landscape (11 x 8.5 in / 279 x 216 mm)"))
# Expected: ['coil bond', 'Case Wrap', 'Linen Wrap'] (no Perfect bond after 250 pages)

# Example 3: Novella format (no Linen Wrap available)
print("Novella 50 pages:", get_available_bindings(50, "Novella (5 x 8 in / 127 x 203 mm)"))
# Expected: ['Coil bond', 'Case Wrap', 'Perfect bond'] (no Linen Wrap)

# Example 4: Small page count (only basic bindings)
print("Pocket Book 10 pages:", get_available_bindings(10, "Pocket Book (4.25 x 6.875 in / 108 x 175 mm)"))
# Expected: ['Coil bond', 'Saddle Stitch']

# Example 5: High page count (loses Saddle Stitch after 48 pages)
print("A4 100 pages:", get_available_bindings(100, "A4 (8.27 x 11.69 in / 210 x 297 mm)"))
# Expected: ['coil bond', 'Case Wrap', 'Perfect bond', 'Linen Wrap']