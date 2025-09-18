def get_allowed_binding_names(page_count):
    """
    Returns allowed binding types based on page count according to the conditions:
    - if there is a minimum of 3 pages: Only Coil Bound option will be available
    - if there is a minimum of 4 pages: the Coil Bound and Saddle Stitch both options will be available
    - if there is a minimum of 24 pages: the Coil Bound, Saddle Stitch and Case Wrap options will be available
    - if there is a minimum of 32 pages: the Perfect Bound, Coil Bound, Saddle Stitch and Case Wrap and Linen Wrap options will be available
    """
    bindings = []
    
    if page_count >= 32:
        # All binding options available
        bindings = ["Perfect Bound", "Coil Bound", "Saddle Stitch", "Case Wrap", "Linen Wrap"]
    elif page_count >= 24:
        # Coil Bound, Saddle Stitch and Case Wrap options available
        bindings = ["Coil Bound", "Saddle Stitch", "Case Wrap"]
    elif page_count >= 4:
        # Coil Bound and Saddle Stitch options available
        bindings = ["Coil Bound", "Saddle Stitch"]
    elif page_count >= 3:
        # Only Coil Bound option available
        bindings = ["Coil Bound"]
    
    return bindings