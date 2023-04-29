"""
A short script that lines up several Windows programs uniformly on a monitor. 
"""

import win32con
import win32gui
import win32api
import psutil
import argparse

target_names = []

taskbar_size = 48  # options: 72, 48, 32

# TODO mathematically assign these numbers
windows_per_row = 3
windows_per_col = 3


def isRealWindow(hWnd):
    """Return True iff given window is a real Windows application window."""
    if not win32gui.IsWindowVisible(hWnd):
        return False
    if win32gui.GetParent(hWnd) != 0:
        return False
    hasNoOwner = win32gui.GetWindow(hWnd, win32con.GW_OWNER) == 0
    lExStyle = win32gui.GetWindowLong(hWnd, win32con.GWL_EXSTYLE)
    if ((lExStyle & win32con.WS_EX_TOOLWINDOW) == 0 and hasNoOwner) or (
        (lExStyle & win32con.WS_EX_APPWINDOW != 0) and not hasNoOwner
    ):
        if win32gui.GetWindowText(hWnd):
            return True
    return False


def getWindowSizes(targets: list = None):
    """
    Return a list of tuples (handler, (width, height)) for each real window.
    """

    def callback(hWnd, windows):
        process_name = win32gui.GetWindowText(hWnd)
        if not isRealWindow(hWnd):
            return
        rect = win32gui.GetWindowRect(hWnd)
        windows.append((process_name, hWnd, (rect[2] - rect[0], rect[3] - rect[1])))

    windows = []
    win32gui.EnumWindows(callback, windows)

    if targets is not None:
        windows = [
            (displayed_title, handler_id, dimensions)
            for displayed_title, handler_id, dimensions in windows
            if displayed_title in targets
        ]
        windows_ordered = []
        for target in targets:
            for displayed_title, handler_id, dimensions in windows:
                if displayed_title == target:
                    windows_ordered.append((displayed_title, handler_id, dimensions))
                    break

    return windows_ordered


def getScreenSize():
    """
    from screeninfo import get_monitors

    for m in get_monitors():
        print(str(m))
    """
    import ctypes

    user32 = ctypes.windll.user32
    screensize = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    return screensize


def new_windows_size(
    screen_size: tuple,
    windows_per_row: int,
    windows_per_col: int,
    windows_dimensions: list,
):
    total_width = [width for width, height in windows_dimensions]
    total_width = sum(total_width)

    total_height = [height for width, height in windows_dimensions]
    total_height = sum(total_height)

    windows_width_height_proportion = total_width / total_height
    repositioned_total_width_height_proportion = (
        windows_width_height_proportion * windows_per_row / windows_per_col
    )

    screen_width, screen_height = screen_size[0], screen_size[1]
    screen_width_height_proportion = screen_width / screen_height

    resize_by_width = (
        repositioned_total_width_height_proportion > screen_width_height_proportion
    )

    if resize_by_width:
        new_window_width = int(screen_width / windows_per_row)
        new_window_height = int(new_window_width / windows_width_height_proportion)

    else:
        new_window_height = int(screen_height / windows_per_col)
        new_window_width = int(new_window_height * windows_width_height_proportion)

    return new_window_width, new_window_height


def get_new_windows_positions(
    screen_size, windows_per_row, windows_per_col, new_window_size
):
    # theoretical_total_windows_width, theoretical_total_window_height =

    screen_width, screen_height = screen_size[0], screen_size[1]
    windows_width_total, windows_height_total = (
        windows_per_row * new_window_size[0],
        windows_per_col * new_window_size[1],
    )
    default_x_movement_needed = (screen_width - windows_width_total) / 2
    default_x_movement_needed = max(0, default_x_movement_needed)
    default_y_movement_needed = (screen_height - windows_height_total) / 2
    default_y_movement_needed = max(0, default_y_movement_needed)

    positions = [
        (
            int(default_x_movement_needed + i * (new_window_size[0] - 1)),
            int(default_y_movement_needed + j * (new_window_size[1] - 1)),
        )
        for j in range(windows_per_col)
        for i in range(windows_per_row)
    ]
    return positions


def place_windows(windows, new_positions, new_window_size):
    names = [name for name, hWnd, orig_size in windows]
    hWnds = [hWnd for name, hWnd, orig_size in windows]
    Xs = [X for X, Y in new_positions]
    Ys = [Y for X, Y in new_positions]
    cxs = [new_window_size[0] for win in windows]
    cys = [new_window_size[1] for win in windows]
    Flagses = [0x0040 for win in windows]

    for name, hWnd, X, Y, cx, cy, Flags in zip(names, hWnds, Xs, Ys, cxs, cys, Flagses):
        win32gui.SetWindowPos(hWnd, None, X, Y, cx, cy, Flags)
        print(f"Updated {name} successfully")


def find_best_arrangements(screen_size, windows):
    screen_width = screen_size[0]
    screen_height = screen_size[1]
    screen_width_height_ratio = screen_width / screen_height

    window_widths = [width for name, hWnd, (width, height) in windows]
    width_per_window = int(sum(window_widths) / len(windows))
    window_heights = [height for name, hWnd, (width, height) in windows]
    height_per_window = int(sum(window_heights) / len(windows))
    window_width_height_ratio = width_per_window / height_per_window


def main():
    windows = getWindowSizes(targets=target_names)
    print("windows:")
    for win in windows:
        print(win)

    screen_size = getScreenSize()
    screen_size = (screen_size[0], screen_size[1] - taskbar_size)
    print("screen_size:")
    print(screen_size)

    windows_dimensions = [
        dimensions for displayed_title, handler_id, dimensions in windows
    ]
    new_window_size = new_windows_size(
        screen_size, windows_per_row, windows_per_col, windows_dimensions
    )
    print("new_window_size:")
    print(new_window_size)

    new_positions = get_new_windows_positions(
        screen_size, windows_per_row, windows_per_col, new_window_size
    )
    print("new_positions:")
    print(new_positions)

    place_windows(windows, new_positions, new_window_size)


if __name__ == "__main__":
    for i in range(3):
        main()
