import os
from subprocess import getoutput
from tkinter import Tk, Label, Button, messagebox, filedialog, Entry

def transformation(input_file, output_file):
    if not os.path.exists(input_file):
        messagebox.showerror("File Error", f"The file {input_file} does not exist.")
        return False
    output = getoutput(f'ffmpeg -i "{input_file}" -ar 48000 -ac 1 -acodec pcm_u8 "{output_file}.wav"')
    if 'size' in output.lower():
        return True
    return False 
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Audio Files", "*.mp3")])
    if file_path:
        entry.delete(0, 'end')
        entry.insert(0, file_path)
def convert_file():
    input_file = entry.get().strip()
    if not input_file:
        messagebox.showwarning("Input Error", "Please enter the name of the file.")
        return
    output_name = os.path.splitext(input_file)[0]
    if transformation(input_file, output_name): messagebox.showinfo("Success", f"The transformation of the file {input_file} into {output_name}.wav was completed successfully.")
    else: messagebox.showerror("Error", "Unknown error. Please ensure that you have entered the correct name.")

root = Tk()
root.title("Audio File Converter")
root.configure(background="#2E2E2E")
label = Label(root, text="Select an .mp3 file:", bg="#2E2E2E", fg="#FFFFFF").pack(pady=10)
entry = Entry(root, width=50, bg="#4B4B4B", fg="#FFFFFF", insertbackground='white')
entry.pack(pady=5)
select_button = Button(root, text="Browse", command=select_file, bg="#5A5A5A", fg="#FFFFFF").pack(pady=5)
convert_button = Button(root, text="Convert to .wav", command=convert_file, bg="#5A5A5A", fg="#FFFFFF").pack(pady=20)
root.mainloop()
