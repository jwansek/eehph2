import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import screeninfo
import threading
import win32file
import win32api
import shutil
import sys
import os

IMPORT_FILES = ['.png', '.jpg', '.jfif', '.jpg_large', '.gif']

class App(tk.Tk):

    def __init__(self, path = None, *args, **kwargs):
        tk.Tk.__init__(self)

        self.title("EEHPH Photo Viewer v2")
        self.iconbitmap(os.path.join("Assets", "icon.ico"))
        self.geometry("%ix%i" % (max_width(), max_height()))
        print(max_height(), max_width())

        paned = ttk.Panedwindow(self, orient = tk.HORIZONTAL)
        paned.pack(fill = tk.BOTH, expand = True)

        self.drive_viewer = DriveViewer(self)
        paned.add(self.drive_viewer)

        self.img_viewer = ImageViewer(self)
        paned.add(self.img_viewer)

        if start is not None:
            if os.path.splitext(path)[1] not in IMPORT_FILES:
                messagebox.showerror('Error', 'Invalid file type. EEHPH2 accepts only %s.' % (' ').join(IMPORT_FILES))
            else:
                self.img_viewer.open_image(start)

        #draw menubar
        menu = tk.Menu(self)
        self.config(menu=menu)
        fileMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='File', menu=fileMenu, underline=0)
        self.__icon_img = tk.PhotoImage(file=os.path.join('Assets', 'image.png'))
        fileMenu.add_command(label='Open image...', accelerator = "Ctrl+O", image=self.__icon_img, compound=tk.LEFT, command=self.__open)
        self.__icon_folder = tk.PhotoImage(file=os.path.join('Assets', 'folder.png'))
        fileMenu.add_command(label='Open folder...', accelerator = "Ctrl+Shift+O", image=self.__icon_folder, compound=tk.LEFT, command=self.__open_folder)
        fileMenu.add_separator()
        fileMenu.add_command(label='Close', command=self.destroy)
        editMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Edit', menu=editMenu, underline=0)
        self.__icon_clipboard = tk.PhotoImage(file=os.path.join('Assets', 'clipboard_small.png'))
        editMenu.add_command(label='Copy path to clipboard', accelerator = "Ctrl+C", image=self.__icon_clipboard, compound=tk.LEFT, command=self.img_viewer.buttons.clipboard)
        self.__icon_save = tk.PhotoImage(file=os.path.join('Assets', 'save_small.png'))
        editMenu.add_command(label='Save image to another location', accelerator = "Ctrl+S", image=self.__icon_save, compound=tk.LEFT, command=self.img_viewer.buttons.save)
        viewMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='View', menu=viewMenu, underline=0)
        self.__icon_fullscreen = tk.PhotoImage(file=os.path.join('Assets', 'images.png'))
        viewMenu.add_command(label='Fullscreen', accelerator = "<Space> / F11", image=self.__icon_fullscreen, compound=tk.LEFT, command=self.img_viewer.buttons.fullscreen)
        self.__icon_left = ImageTk.PhotoImage(Image.open(os.path.join("Assets", "arrow_left.png")).resize((16, 16), Image.ANTIALIAS))
        viewMenu.add_command(label='Previous image', accelerator = "←", image = self.__icon_left, compound = tk.LEFT, command=self.img_viewer.buttons.backwards)
        self.__icon_right = ImageTk.PhotoImage(Image.open(os.path.join("Assets", "arrow_left.png")).resize((16, 16), Image.ANTIALIAS).rotate(180))
        viewMenu.add_command(label='Next image', accelerator = "→", image = self.__icon_right, compound = tk.LEFT, command=self.img_viewer.buttons.forwards)
        imageMenu = tk.Menu(menu, tearoff = 0)
        menu.add_cascade(label = "Image", menu = imageMenu, underline = 0)
        self.__icon_clockwise = ImageTk.PhotoImage(ImageOps.mirror(Image.open(os.path.join("Assets", "rotate_right.png")).resize((16, 16), Image.ANTIALIAS)))
        imageMenu.add_command(label='Rotate 90° clockwise', accelerator = "R", image = self.__icon_clockwise, compound = tk.LEFT, command=self.img_viewer.buttons.clockwise)
        self.__icon_anticlockwise = ImageTk.PhotoImage(Image.open(os.path.join("Assets", "rotate_right.png")).resize((16, 16), Image.ANTIALIAS))
        imageMenu.add_command(label='Rotate 90° anticlockwise', accelerator = "Shift+R", image = self.__icon_anticlockwise, compound = tk.LEFT, command=self.img_viewer.buttons.anticlockwise)
        self.__icon_flip = ImageTk.PhotoImage(Image.open(os.path.join("Assets", "flip.png")).resize((16, 16), Image.ANTIALIAS))
        imageMenu.add_command(label='Flip image', accelerator = "F", image = self.__icon_flip, compound = tk.LEFT, command=self.img_viewer.buttons.flip)

        self.bind('<Left>', self.img_viewer.buttons.backwards)
        self.bind('<Right>', self.img_viewer.buttons.forwards)
        self.bind('<space>', self.img_viewer.buttons.fullscreen)
        self.bind('<F11>', self.img_viewer.buttons.fullscreen)
        self.bind('<Control-c>', self.img_viewer.buttons.clipboard)
        self.bind('<Control-s>', self.img_viewer.buttons.save)
        self.bind('<Control-o>', self.__open)
        self.bind('<Control-O>', self.__open_folder)
        self.bind('<r>', self.img_viewer.buttons.clockwise)
        self.bind('<R>', self.img_viewer.buttons.anticlockwise)
        self.bind('<f>', self.img_viewer.buttons.flip)

    def __open(self, event=None):
        filetypes = get_filetypes()
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path != '' or path == None:
            self.img_viewer.open_image(path)

    def __open_folder(self, event=None):
        path = filedialog.askdirectory()
        files = []
        if path != '' or path == None:
            for file in os.listdir(path):
                if os.path.splitext(file)[1].lower() in IMPORT_FILES:
                    files.append(file)

            if files != []:
                self.img_viewer.open_image(os.path.join(path, files[0]))
            else:
                messagebox.showwarning('', 'There are no avaliable file types in the folder. Accepts %s.' % (' ').join(IMPORT_FILES))

class DriveViewer(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)

        self.home_icon = tk.PhotoImage(file = os.path.join('Assets', 'home.png'))
        self.disc_icon = tk.PhotoImage(file = os.path.join('Assets', 'disc.png'))
        self.disk_drive = tk.PhotoImage(file = os.path.join('Assets', 'disk_drive.png'))
        self.network_drive = tk.PhotoImage(file = os.path.join('Assets', 'network_drive.png'))
        self.removable_disc = tk.PhotoImage(file = os.path.join('Assets', 'removable_drive.png'))
        self.cdrive = tk.PhotoImage(file = os.path.join('Assets', 'cdrive.png'))

        self.book = ttk.Notebook(self)
        self.book.pack(fill = tk.BOTH, expand = True)
        
        self.book.add(FileTree(parent), text = 'Home', image = self.home_icon, compound = tk.LEFT)
        for drive in self.__get_drives():
            type_ = win32file.GetDriveType(drive)
            if type_ == win32file.DRIVE_REMOVABLE:
                image = self.removable_disc
            elif type_ == win32file.DRIVE_CDROM:
                image = self.disk_drive
            elif type_ == win32file.DRIVE_FIXED:
                if drive == "C:\\":
                    image = self.cdrive
                else:
                    image = self.disc_icon
            else:
                image = self.network_drive
            try:
                self.book.add(FileTree(parent, start = drive), text = drive.replace('\\', ''), image = image, compound = tk.LEFT)
            except PermissionError:
                pass

    def __get_drives(self):
        return win32api.GetLogicalDriveStrings().split('\x00')[:-1]

class FileTree(tk.Frame):
    columns = ('path', 'filetype', 'size')

    def __init__(self, parent, start = os.path.expanduser('~')):
        tk.Frame.__init__(self)
        self.parent = parent
        self.starting_dir = start

        self.desktop_icon = tk.PhotoImage(file = os.path.join('Assets', 'desktop.png'))
        self.download_icon = tk.PhotoImage(file = os.path.join('Assets', 'downloads.png'))
        self.documents_icon = tk.PhotoImage(file = os.path.join('Assets', 'documents.png'))
        self.images_icon = tk.PhotoImage(file = os.path.join('Assets', 'images.png'))
        self.image_icon = tk.PhotoImage(file = os.path.join('Assets', 'image.png'))
        self.music_icon = tk.PhotoImage(file = os.path.join('Assets', 'music.png'))
        self.videos_icon = tk.PhotoImage(file = os.path.join('Assets', 'videos.png'))
        self.threedee_icon = tk.PhotoImage(file = os.path.join('Assets', '3d_objs.png'))
        self.warning_icon = tk.PhotoImage(file = os.path.join('Assets', 'warning.png'))
        self.folder_icon = tk.PhotoImage(file = os.path.join('Assets', 'folder.png'))

        self.tree = ttk.Treeview(self, height = 20, columns = self.columns, displaycolumns = 'size')
        self.tree.heading('#0', text = 'Directory', anchor = tk.W)
        self.tree.heading('size', text = 'Size', anchor = tk.W)
        self.tree.column('path', width = 180)
        self.tree.column('size', stretch = 1, width = 48)
        self.tree.grid(row = 0, column = 0, sticky = 'nsew')

        sbr_y = ttk.Scrollbar(self, orient = tk.VERTICAL, command = self.tree.yview)
        sbr_x = ttk.Scrollbar(self, orient = tk.HORIZONTAL, command = self.tree.xview)
        self.tree['yscroll'] = sbr_y.set
        self.tree['xscroll'] = sbr_x.set
        sbr_y.grid(row = 0, column = 1, sticky = 'ns')
        sbr_x.grid(row = 1, column = 0, sticky = 'ew')
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)

        #add all the root nodes
        for dir_ in self.__get_dirs(self.starting_dir):
            self.__populate_node(os.path.join(self.starting_dir, dir_), root = True)

        self.tree.bind('<<TreeviewOpen>>', self.__on_click)

    def __get_dirs(self, start):
        dirs = []
        files = []
        try:
            for dir_ in os.listdir(start):
                type_ = self.__dir_type(dir_)
                if type_ == 'directory':
                    dirs.append(dir_)
                elif type_ in IMPORT_FILES:
                    files.append(dir_)

            return dirs + files
        except PermissionError:
            messagebox.showerror('', 'Access Denied')
        except NotADirectoryError:
            messagebox.showerror('', 'Access Denied')

    def __dir_type(self, dir_):
        extension = os.path.splitext(dir_)[-1:][0]
        if dir_.startswith('.'):
            return 'hidden'
        elif extension == '':
            return 'directory'
        else:
            return extension.lower()

    def __on_click(self, event):
        items = []
        id = os.path.normpath(self.tree.focus())
        if not os.path.exists(id):
            messagebox.showwarning('', 'There are no folders or files that can be opened in this directory.')
        else:
            if self.__dir_type(id) == 'directory':
                try:
                    for dir_ in self.__get_dirs(id):
                        items.append(dir_)
                        self.__populate_node(os.path.join(id, dir_))
                except TypeError:
                    #is None since access denied
                    return

                if items != []:
                    self.tree.delete(self.tree.get_children(id)[0])
            else:
                self.parent.img_viewer.open_image(path=id)

    def __populate_node(self, path, root=False):
        if os.path.splitext(path)[-1:][0] == '':
            if root:
                parent = ''
            else:
                parent = os.path.normpath(os.path.split(path)[:-1][0])
            
            name = [i for i in os.path.split(path)][-1]
            if name == 'Music':
                image = self.music_icon
            elif name == 'Desktop':
                image = self.music_icon
            elif name == 'Documents':
                image = self.documents_icon
            elif name == 'Downloads':
                image = self.download_icon
            elif name == 'Pictures':
                image = self.images_icon
            elif name == '3D Objects':
                image = self.threedee_icon
            elif name == 'Videos':
                image = self.videos_icon
            else:
                image = self.folder_icon
            
            try:
                id = self.tree.insert(parent, tk.END, path, text=name, image=image, values=[path, '', ''])
                self.tree.insert(id, tk.END, text='<*No avaliable files*>', image=self.warning_icon)
            except tk.TclError:
                pass

        else:
            if root:
                parent = ''
            else:
                parent = os.path.normpath(os.path.split(path)[:-1][0])
            name = [i for i in os.path.split(path)][-1]
        try:
            #set the id to the full path so we can't have multiple of the same id
            id = self.tree.insert(parent, tk.END, path, text=name, image=self.image_icon, values=[path, '', self._FileTree__get_size(path)])
        except tk.TclError:
            pass

    def __get_size(self, path):
        size = os.path.getsize(path)
        KB = 1024.0
        MB = KB * KB
        GB = MB * KB
        if size >= GB:
            return ('{:,.1f} GB').format(size / GB)
        elif size >= MB:
            return ('{:,.1f} MB').format(size / MB)
        elif size >= KB:
            return ('{:,.1f} KB').format(size / KB)
        else:
            return ('{} bytes').format(size)

class ImageViewer(tk.Frame):

    orig_dims = None
    dims = None
    path = None
    large_img = None

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.focus_set()

        self.lbl_img = tk.Label(self, text = "No image selected")
        self.lbl_img.pack(fill = tk.BOTH, expand = True)

        self.buttons = Buttons(self)
        self.buttons.pack()

    def open_image(self, path):
        self.lbl_img.config(image = "", text = "Loading...")
        print(path)
        threading.Thread(target = self.__open, args = (path, None)).start() #for some reason it requires at least two args or weird stuff starts happening
    
    def __open(self, arg, _):
        if type(arg) is str:
            self.path = arg
            img = Image.open(self.path)
        else:
            img = arg

        self.orig_dims = img.size
        self.lbl_img.focus_set()    #focus this so using the arrow keys doesn't mess up the treeview
        self.large_img = img

        treewidth = self.parent.drive_viewer.winfo_width()
        appwidth = self.parent.winfo_width()
        appheight = self.parent.winfo_height()
        btnsheight = self.buttons.winfo_height()
        imgwidth = img.size[0]
        imgheight = img.size[1]

        maxwidth = appwidth - (treewidth + 10)
        maxheight = appheight - (btnsheight + 10)
        print(maxwidth, maxheight)

        if imgwidth > maxwidth and imgheight > maxheight:
            if (maxwidth/maxheight) > (imgwidth/imgheight):
                img = img.resize((int(imgwidth * maxheight / imgheight) - 5, maxheight - 5), Image.ANTIALIAS)
            else:
                img = img.resize((maxwidth, int(imgheight * maxwidth / imgwidth)), Image.ANTIALIAS)

        if img.size[0] > maxwidth:
            img = self.resize(img, width = maxwidth)
        if img.size[1] > maxheight:
            img = self.resize(img, height = maxheight)

        dims = img.size
        tkimg = ImageTk.PhotoImage(image = img)
        self.lbl_img.config(image = tkimg)
        self.lbl_img.image = tkimg

        text = "%-46s %s (%ix%i)" % (os.path.split(self.path)[-1:][0], str(int((img.size[0] / self.orig_dims[0]) * 100)) + "%", self.orig_dims[0], self.orig_dims[1])
        self.buttons.lbl_text.config(text = text)

    def resize(self, img, **kwargs):
        if list(kwargs.keys())[0] == 'height':
            baseheight = kwargs['height']
            hpercent = baseheight / float(img.size[1])
            wsize = int(float(img.size[0]) * float(hpercent))
            return img.resize((wsize, baseheight), Image.ANTIALIAS)
        elif list(kwargs.keys())[0] == 'width':
            basewidth = kwargs['width']
            wpercent = basewidth / float(img.size[0])
            hsize = int(float(img.size[1]) * float(wpercent))
            return img.resize((basewidth, hsize), Image.ANTIALIAS)
        raise TypeError("Missing argument: must have 'height' or 'width'.")

class Buttons(tk.Frame):

    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        arrow_left = Image.open(os.path.join("Assets", "arrow_left.png"))
        rotate_right = Image.open(os.path.join("Assets", "rotate_right.png")).resize((40, 40), Image.ANTIALIAS)

        self.img_backwards = ImageTk.PhotoImage(arrow_left)
        self.img_forwards = ImageTk.PhotoImage(arrow_left.rotate(180))
        self.img_rotate_anticlockwise = ImageTk.PhotoImage(ImageOps.mirror(rotate_right))
        self.img_rotate_clockwise = ImageTk.PhotoImage(rotate_right)
        self.img_clipboard = tk.PhotoImage(file = os.path.join("Assets", "clipboard.png"))
        self.img_fullscreen = tk.PhotoImage(file = os.path.join("Assets", "fullscreen.png"))
        self.img_save = tk.PhotoImage(file = os.path.join("Assets", "save.png"))
        self.img_flip = ImageTk.PhotoImage(Image.open(os.path.join("Assets", "flip.png")).resize((40, 40), Image.ANTIALIAS))

        self.lbl_text = tk.Label(self)
        self.lbl_text.grid(row = 0, column = 0, columnspan = 9)

        ttk.Button(self, image = self.img_backwards, command = self.backwards).grid(row = 1, column = 0)
        ttk.Button(self, image = self.img_rotate_anticlockwise, command = self.anticlockwise).grid(row = 1, column = 1)
        ttk.Separator(self, orient=tk.VERTICAL).grid(row = 1, column = 2, sticky = 'ns', padx = 3)
        ttk.Button(self, image = self.img_clipboard, command = self.clipboard).grid(row = 1, column = 3)
        ttk.Button(self, image = self.img_fullscreen, command = self.fullscreen).grid(row = 1, column = 4)
        ttk.Button(self, image = self.img_save, command = self.save).grid(row = 1, column = 5)
        ttk.Button(self, image = self.img_flip, command = self.flip).grid(row = 1, column = 6)
        ttk.Separator(self, orient=tk.VERTICAL).grid(row = 1, column = 7, sticky = 'ns', padx = 3)
        ttk.Button(self, image = self.img_rotate_clockwise, command = self.clockwise).grid(row = 1, column = 8)
        ttk.Button(self, image = self.img_forwards, command = self.forwards).grid(row = 1, column = 9)

    def __get_images(self):
        return [file for file in os.listdir(os.path.split(self.parent.parent.img_viewer.path)[:-1][0]) if os.path.splitext(file)[1].lower() in IMPORT_FILES]

    def backwards(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            path = self.parent.parent.img_viewer.path
            if path is not None:
                images = self._Buttons__get_images()
                index = images.index(os.path.split(self.parent.parent.img_viewer.path)[-1:][0])
                if index == 0:
                    self.parent.parent.img_viewer.open_image(os.path.join(os.path.split(path)[:-1][0], images[-1]))
                else:
                    self.parent.parent.img_viewer.open_image(os.path.join(os.path.split(path)[:-1][0], images[index - 1]))

    def forwards(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            path = self.parent.parent.img_viewer.path
            if path is not None:
                images = self._Buttons__get_images()
                index = images.index(os.path.split(self.parent.parent.img_viewer.path)[-1:][0])
            try:
                images.index(os.path.split(self.parent.parent.img_viewer.path)[-1:][0])
                self.parent.parent.img_viewer.open_image(os.path.join(os.path.split(path)[:-1][0], images[index + 1]))
            except IndexError:
                self.parent.parent.img_viewer.open_image(os.path.join(os.path.split(path)[:-1][0], images[0]))

    def clipboard(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            print(self.parent.parent.img_viewer.path)
            self.parent.parent.clipboard_clear()
            self.parent.parent.clipboard_append(self.parent.parent.img_viewer.path)
            self.parent.parent.update()

    def save(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            orig = self.parent.parent.img_viewer.path
            if orig is not None:
                path = filedialog.askdirectory()
                if path != '':
                    shutil.copy2(orig, path)
                    messagebox.showinfo('Operation complete', 'Copied file %s to %s.' % (os.path.normpath(orig), os.path.normpath(path)))

    def fullscreen(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            FullscreenWindow(self, Image.open(self.parent.parent.img_viewer.path))

    def anticlockwise(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            self.parent.open_image(self.parent.large_img.rotate(-90, expand = 1))

    def clockwise(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            self.parent.open_image(self.parent.large_img.rotate(90, expand = 1))

    def flip(self, event = None):
        if self.parent.parent.img_viewer.path is not None:
            self.parent.open_image(ImageOps.mirror(self.parent.large_img))

class FullscreenWindow(tk.Toplevel):

    def __init__(self, parent, img):
        tk.Toplevel.__init__(self, parent)
        self.iconbitmap(os.path.join('Assets', 'icon.ico'))
        self.attributes('-fullscreen', True)
        self.focus_set()
        self.update_idletasks()
        width = self.winfo_height()
        height = self.winfo_height()
        imgwidth = img.size[0]
        imgheight = img.size[1]
        img = img.resize((int(imgwidth * height / imgheight) - 5, height - 5), Image.ANTIALIAS)
        tkimg = ImageTk.PhotoImage(img)
        lbl_img = ttk.Label(self, image=tkimg)
        lbl_img.image = tkimg
        lbl_img.grid(row=0, column=0, sticky='nsew')
        self.bind('<Escape>', lambda a: self.destroy())

def max_height():
    return int(min([i.height for i in screeninfo.get_monitors()]) * 2/3)

def max_width():
    return int(min([i.width for i in screeninfo.get_monitors()]) * 2/3)

def get_filetypes():
    return (('%s images' % type[1:].upper(), type) for type in IMPORT_FILES)

if __name__ == "__main__":
    try:
        start = sys.argv[1]
    except IndexError:
        start = None
    root = App(start)
    root.mainloop()