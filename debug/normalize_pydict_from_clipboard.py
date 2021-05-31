#import tkinter as tk
import pprint
import yaml
import pyperclip

if __name__ == '__main__':
    # root = tk.Tk()
    # root.withdraw()  # keep the window from showing

    try:
        # data = root.clipboard_get()
        data = pyperclip.paste()
        data = eval(data)
        # result = pprint.pformat(data, indent=2)
        result = yaml.safe_dump(data, indent=2)
        # root.clipboard_clear()
        # root.clipboard_append(result)
        # root.update()
        # root.destroy()
        pyperclip.copy(result)
    except:
        pass
