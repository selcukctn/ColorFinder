import tkinter as tk
import pyautogui
import pyperclip
import json
import os

CONFIG_FILE = "config.json"
ICON_FILE = "app_icon.ico"
current_rgb = (0, 0, 0)
display_mode = "HEX"  # HEX or RGB

def get_text_color(bg_rgb):
    r, g, b = bg_rgb
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    return "black" if brightness > 186 else "white"

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

def update_color():
    global current_rgb
    x, y = pyautogui.position()
    pixel_color = pyautogui.screenshot().getpixel((x, y))
    current_rgb = pixel_color
    hex_color = rgb_to_hex(pixel_color)
    text_color = get_text_color(pixel_color)

    color_label.config(bg=hex_color, fg=text_color, text=hex_color if display_mode == "HEX" else f'rgb{pixel_color}')
    top_frame.config(bg=hex_color)

    # Buton arka planları sabit, çerçeve rengi değişiyor
    close_button.config(highlightbackground=hex_color)
    info_button.config(highlightbackground=hex_color)
    rgb_button.config(highlightbackground=hex_color)

    root.after(100, update_color)

def show_copied_box(message="Copied!"):
    copied_label.config(text=message)
    copied_box.deiconify()
    update_copied_box_position()
    copied_box.after(3000, copied_box.withdraw)

def show_info():
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    info = tk.Toplevel(root)
    info.title("Info")
    info.geometry(f"300x120+{root_x}+{root_y + root.winfo_height()}")
    info.attributes("-topmost", True)
    try:
        info.iconbitmap(ICON_FILE)
    except:
        pass
    tk.Label(
        info,
        text="• Ctrl + 3 : Copy HEX\n• Ctrl + 4 : Copy RGB\n• RGB/HEX button: Toggle view",
        font=("Arial", 10),
        justify="left",
        wraplength=280
    ).pack(pady=20)
    tk.Button(info, text="Close", command=info.destroy).pack()

def toggle_display_mode():
    global display_mode
    display_mode = "RGB" if display_mode == "HEX" else "HEX"
    rgb_button.config(text="HEX" if display_mode == "RGB" else "RGB")

def on_key_press(event):
    if event.state & 0x4 and event.keysym == '3':
        pyperclip.copy(rgb_to_hex(current_rgb))
        show_copied_box("HEX copied!")
    elif event.state & 0x4 and event.keysym == '4':
        rgb_str = f'rgb({current_rgb[0]}, {current_rgb[1]}, {current_rgb[2]})'
        pyperclip.copy(rgb_str)
        show_copied_box("RGB copied!")

def start_move(event):
    root.x = event.x
    root.y = event.y

def stop_move(event):
    root.x = None
    root.y = None
    save_position()

def do_move(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f'+{x}+{y}')
    update_copied_box_position()

def save_position():
    x = root.winfo_x()
    y = root.winfo_y()
    config = {"x": x, "y": y}
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)

def load_position():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            try:
                config = json.load(f)
                return config.get("x", 100), config.get("y", 100)
            except:
                return 100, 100
    return 100, 100

def update_copied_box_position():
    root.update_idletasks()
    x = root.winfo_x()
    y = root.winfo_y() + root.winfo_height()
    copied_box.geometry(f"150x40+{x}+{y}")

# Launch
x, y = load_position()
root = tk.Tk()
root.overrideredirect(True)
root.attributes('-topmost', True)
root.geometry(f"150x70+{x}+{y}")
try:
    root.iconbitmap(ICON_FILE)
except:
    pass

# Top frame (buttons area)
top_frame = tk.Frame(root, height=25, bg="gray")
top_frame.pack(fill=tk.X)

# Close button
close_button = tk.Button(top_frame, text="X", command=root.destroy, font=('Arial', 8), fg="white",
                         bg="#800000", bd=0, relief="flat", highlightthickness=2)
close_button.place(x=130, y=2, width=18, height=18)

# Info button
info_button = tk.Button(top_frame, text="i", command=show_info, font=('Arial', 8), fg="white",
                        bg="blue", bd=0, relief="flat", highlightthickness=2)
info_button.place(x=110, y=2, width=18, height=18)

# RGB/HEX toggle button
rgb_button = tk.Button(top_frame, text="RGB", command=toggle_display_mode, font=('Arial', 8), fg="white",
                       bg="green", bd=0, relief="flat", highlightthickness=2)
rgb_button.place(x=80, y=2, width=28, height=18)

# Color label (below buttons)
color_label = tk.Label(root, text="", font=('Arial', 11), width=12)
color_label.pack(fill=tk.BOTH, expand=True)

# Copied popup box
copied_box = tk.Toplevel(root)
copied_box.withdraw()
copied_box.overrideredirect(True)
copied_box.attributes("-topmost", True)
copied_box.geometry("150x40+100+150")
copied_label = tk.Label(copied_box, text="Copied!", font=("Arial", 11), bg="#dff0d8", fg="green", bd=1, relief="solid")
copied_label.pack(fill=tk.BOTH, expand=True)

# Dragging functionality
color_label.bind("<ButtonPress-1>", start_move)
color_label.bind("<ButtonRelease-1>", stop_move)
color_label.bind("<B1-Motion>", do_move)

# Keyboard listener
root.bind_all("<KeyPress>", on_key_press)

update_color()
root.mainloop()
