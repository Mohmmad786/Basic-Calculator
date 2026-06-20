import tkinter
import math

button_values = [
    ["AC", "+/-", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["0", ".", "√", "="]
]

right_symbols = ["÷", "×", "-", "+", "="]
top_symbols = ["AC", "+/-", "%"]

row_count = len(button_values)
column_count = len(button_values[0])

color_light_gray = "#D4D4D2"
color_black = "#1C1C1C"
color_dark_gray = "#505050"
color_orange = "#FF9500"
color_white = "white"

# 1. Enable Windows High-DPI awareness to prevent a blurry UI
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    pass

# ----------------------------
# Window setup
# ----------------------------
window = tkinter.Tk()
window.title("Calculator")
window.resizable(False, False)
window.configure(background=color_black)

# Add standard external padding
window.config(padx=10, pady=10)

frame = tkinter.Frame(window, background=color_black)
frame.pack()

# Clean right-aligned Display configuration
label = tkinter.Label(frame, text="0", font=("Arial", 42), background=color_black,
                      foreground=color_white, anchor="e", width=column_count * 3, 
                      padx=10, pady=15)
label.grid(row=0, column=0, columnspan=column_count, sticky="we")

# ----------------------------
# Calculation state
# ----------------------------
A = "0"          # first operand as string
operator = None
B = None         # second operand as string
reset_on_next_digit = False  # Tells digit handler to replace display with new input

def clear_all():
    global A, operator, B, reset_on_next_digit
    A = "0"
    operator = None
    B = None
    reset_on_next_digit = False

def remove_zero_decimal(num):
    """Convert a number to string, removing trailing .0 if present."""
    if num % 1 == 0:
        return str(int(num))
    return str(num)

def compute_pending():
    """Perform the pending operation (A operator B) and return the result."""
    global A, operator, B
    if operator is None or B is None:
        return None
    try:
        numA = float(A)
        numB = float(B)
        if operator == "+":
            res = numA + numB
        elif operator == "-":
            res = numA - numB
        elif operator == "×":
            res = numA * numB
        elif operator == "÷":
            if numB == 0:
                return "Error"
            res = numA / numB
        else:
            return None
        return remove_zero_decimal(res)
    except Exception:
        return "Error"

def button_clicked(value):
    global A, operator, B, label, reset_on_next_digit

    # ----- Operators and Equals -----
    if value in right_symbols:
        if value == "=":
            if operator is not None:
                # FIX: Dynamically capture current display text as Operand B prior to evaluation
                B = label["text"]
                result = compute_pending()
                if result is not None:
                    label["text"] = result
                    if result == "Error":
                        clear_all()
                    else:
                        A = result
                        operator = None
                        B = None
                        reset_on_next_digit = True

        elif value in "+-×÷":
            if operator is not None:
                # Handle chained calculations (e.g., 5 + 3 - computes 8, then presets minus)
                B = label["text"]
                result = compute_pending()
                if result is not None and result != "Error":
                    label["text"] = result
                    A = result
                    B = None
                elif result == "Error":
                    label["text"] = "Error"
                    clear_all()
                    return
            
            A = label["text"]
            operator = value
            reset_on_next_digit = True

    # ----- Top row modifier buttons -----
    elif value in top_symbols:
        if value == "AC":
            clear_all()
            label["text"] = "0"
        elif value == "+/-":
            try:
                result = float(label["text"]) * -1
                label["text"] = remove_zero_decimal(result)
                if operator is None:
                    A = label["text"]
            except Exception:
                label["text"] = "Error"
        elif value == "%":
            try:
                result = float(label["text"]) / 100
                label["text"] = remove_zero_decimal(result)
                if operator is None:
                    A = label["text"]
            except Exception:
                label["text"] = "Error"

    # ----- Square root (√) -----
    elif value == "√":
        try:
            num = float(label["text"])
            if num < 0:
                label["text"] = "Error"
                clear_all()
            else:
                result = math.sqrt(num)
                label["text"] = remove_zero_decimal(result)
                if operator is None:
                    A = label["text"]
                reset_on_next_digit = True
        except Exception:
            label["text"] = "Error"
            clear_all()

    # ----- Digits and decimal point -----
    else:   
        if reset_on_next_digit:
            label["text"] = "0"
            reset_on_next_digit = False

        if value == ".":
            if "." not in label["text"]:
                label["text"] += value
        elif value in "0123456789":
            if label["text"] == "0":
                label["text"] = value
            else:
                label["text"] += value

# ----------------------------
# Create and Grid Buttons
# ----------------------------
for row in range(row_count):
    for column in range(column_count):
        value = button_values[row][column]
        button = tkinter.Button(frame, text=value, font=("Arial", 18, "bold"),
                                width=5, height=2, bd=0, highlightthickness=0,
                                activebackground="#606060",
                                command=lambda v=value: button_clicked(v))
        
        # Color coding mapped configuration
        if value in top_symbols:
            button.config(foreground=color_black, background=color_light_gray, activeforeground=color_black)
        elif value in right_symbols:
            button.config(foreground=color_white, background=color_orange, activeforeground=color_white)
        else:
            button.config(foreground=color_white, background=color_dark_gray, activeforeground=color_white)
            
        button.grid(row=row+1, column=column, padx=2, pady=2, sticky="nsew")

# Configure weights to enable proportional button layout boundaries
for i in range(column_count):
    frame.columnconfigure(i, weight=1)
for i in range(row_count + 1):
    frame.rowconfigure(i, weight=1)

# ----------------------------
# Center and Safe Scale Window
# ----------------------------
# Force layout calculations sequentially and without blocking interactions
window.update_idletasks()

window_width = window.winfo_reqwidth()
window_height = window.winfo_reqheight()

# Request display parameters
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Standard resolution safe bounds (limits clipping on small hardware screens)
max_allowed_height = int(screen_height * 0.85)
max_allowed_width = int(screen_width * 0.85)

# Scaledown fallback rules for extremely tiny screens or high system magnification
if window_height > max_allowed_height or window_width > max_allowed_width:
    smaller_font = ("Arial", 14, "bold")
    label.config(font=("Arial", 30))
    for widget in frame.winfo_children():
        if isinstance(widget, tkinter.Button):
            widget.config(font=smaller_font, width=4, height=1)
    
    # Refresh safe size specifications
    window.update_idletasks()
    window_width = window.winfo_reqwidth()
    window_height = window.winfo_reqheight()

# Math for exact screen centering coordinates
window_x = int((screen_width - window_width) / 2)
window_y = int((screen_height - window_height) / 2)

# Prevent negative coords (stops titlebars rendering off-screen)
window_x = max(0, window_x)
window_y = max(0, window_y)

# Set non-blocking screen geometry and display
window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

window.mainloop()