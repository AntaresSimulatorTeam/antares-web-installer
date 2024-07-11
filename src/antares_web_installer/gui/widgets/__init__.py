def convert_in_du(window, size: int):
    """
    @param window:
    @param size:
    @return:
    """
    pixels = window.winfo_fpixels("9p")
    converted = int((pixels / 4) * size)
    return converted
