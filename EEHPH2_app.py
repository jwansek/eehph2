import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk, ImageOps
import screeninfo
import webbrowser
import threading
import win32file
import win32api
import shutil
import sys
import os

IMPORT_FILES = ['.png', '.jpg', '.jfif', '.jpg_large', '.gif']

class App(tk.Tk):

    def __init__(self, path = None, *args, **kwargs):
        """Main class
        
        Keyword Arguments:
            path {str} -- path to the image to open on (default: {None})
        """

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

        if path is not None:
            if os.path.splitext(path)[1] not in IMPORT_FILES:
                messagebox.showerror('Error', 'Invalid file type. EEHPH2 accepts only %s.' % (' ').join(IMPORT_FILES))
            else:
                self.img_viewer.open_image(path)

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
        editMenu.add_separator()
        self.__icon_edit = ImageTk.PhotoImage(Image.open(os.path.join("Assets", "edit.png")).resize((16, 16), Image.ANTIALIAS))
        editMenu.add_command(label = 'Edit image', accelerator = "Ctrl+E", command = self.img_viewer.edit_image, image = self.__icon_edit, compound = tk.LEFT)
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
        menu.add_command(label = "Source", underline = 0, command = lambda: webbrowser.open_new("https://github.com/jwansek/eehph2"))

        self.new_state = "normal"

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
        self.bind('<Control-e>', self.img_viewer.edit_image)
        self.bind('<F5>', self.refresh)
        self.bind('<Configure>', self.__on_config)

    def __on_config(self, event = None):
        """Event for when the app is resized.
        
        Keyword Arguments:
            event {event} -- Done to make the app work with events (default: {None})
        """

        self.old_state = self.new_state # assign the old state value
        self.new_state = self.state() # get the new state value

        if self.new_state == 'zoomed':
            #maximise event
            self.refresh()
        elif self.new_state == 'normal' and self.old_state == 'zoomed':
            #restore event
            self.refresh()


    def refresh(self, event = None):
        """Reloads the current image.
        Done so the image is resized when the app is resized.
        
        Keyword Arguments:
            event {event} -- Used to make the method work with events. (default: {None})
        """

        if self.img_viewer.large_img is not None:
            self.img_viewer.open_image(self.img_viewer.large_img)


    def __open(self, event=None):
        """Private. Used to open an image asking the user where
        they want to open an image from. Then calls the img_viewer
        class.
        
        Keyword Arguments:
            event {event} -- Unused. Used to make the method
            work with events (default: {None})
        """

        filetypes = get_filetypes()
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path != '' or path == None:
            self.img_viewer.open_image(path)

    def __open_folder(self, event=None):
        """Opens a folder from disk by opening a file from it.
        Checks allowed files are present first
        
        Keyword Arguments:
            event {event} -- Unused. Used to make the method
            work with events (default: {None})
        """

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
        """Widget made up of a ttk.Notebook to the user can see
        which drives they want.
        
        Arguments:
            parent {object} -- parent class
        """

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
        """Private. Retutns the letters of all the drives
        attatched to the system.
        
        Returns:
            List -- List of drives e.g. ["C:\", "D:\"]
        """ 

        return win32api.GetLogicalDriveStrings().split('\x00')[:-1]

class FileTree(tk.Frame):
    columns = ('path', 'filetype', 'size')

    def __init__(self, parent, start = os.path.expanduser('~')):
        """Filetree widget to the user can navigate through files.
        Made of ttk.Treeview. Only dirs and allowed images show up.
        For speed, child dirs don't show up until they are clicked on.
        
        Arguments:
            parent {object} -- class that calls this widget
        
        Keyword Arguments:
            start {str} -- Drive to make tree of. Defaults to user's home folder. (default: {os.path.expanduser('~')})
        """

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
        """Private. Gets child files and dirs that are in IMPORT_FILES.
        Only allowed filetypes show up.
        
        Arguments:
            start {str} -- Path of parent directory
        
        Returns:
            List -- List of all allowed dirs and files.
        """

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
        """Private. Works out the file type of an item
        
        Arguments:
            dir_ {str} -- item of file to check
        
        Returns:
            str -- returns 'hidden' or 'directory', else the file extenstion
        """

        extension = os.path.splitext(dir_)[-1:][0]
        if dir_.startswith('.'):
            return 'hidden'
        elif extension == '':
            return 'directory'
        else:
            return extension.lower()

    def __on_click(self, event):
        """Private. Event holder for when the user clicks on a node to expand
        Works out child folders and dirs. Adds a 'dummy' child to each
        item so that the + icon is there. This is removed if the folder has
        usable items in it.
        
        Arguments:
            event {event} -- so the method works with events
        """

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
        """Private. Populates a parent node. For more infomation, see
        __on_click().
        
        Arguments:
            path {str} -- path of parent node
        
        Keyword Arguments:
            root {bool} -- Is the node a root? (probably not) (default: {False})
        """

        if os.path.splitext(path)[-1:][0] == '':
            if root:
                parent = ''
            else:
                parent = os.path.normpath(os.path.split(path)[:-1][0])
            
            name = [i for i in os.path.split(path)][-1]
            if name == 'Music':
                image = self.music_icon
            elif name == 'Desktop':
                image = self.desktop_icon
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
        """Private. Returns the size of a file. From:
        https://pyinmyeye.blogspot.co.uk/2012/07/tkinter-multi-column-list-demo.html
        
        Arguments:
            path {str} -- Path to file
        
        Returns:
            str -- file size in bytes/KB/MB/GB
        """

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
        """Class to show images on screen. Resizes images
        appropopriately so it fits on the screen.
        
        Arguments:
            parent {object} -- class that called this
        """

        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.focus_set()

        self.lbl_img = tk.Label(self, text = "No image selected")
        self.lbl_img.pack(fill = tk.BOTH, expand = True)

        self.buttons = Buttons(self)
        self.buttons.pack()

    def open_image(self, path):
        """Changes the label to show 'loading' and starts a loading thread.
        
        Arguments:
            path {str} -- path of image to open
        """

        self.lbl_img.config(image = "", text = "Loading...")
        print(path)
        threading.Thread(target = self.__open, args = (path, None)).start() #for some reason it requires at least two args or weird stuff starts happening
    
    def __open(self, arg, _):
        """Private. Actually open an image. Work out an appropriate size and show on screen.
        
        Arguments:
            arg {str/Image} -- str of path to open or Image object to show
            _ {N/A} -- Unused. Required for some reason since apparently threading.Thread() requires at least two
            args or weird stuff starts happenning.
        """

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


        #image is too big in both directions
        #https://stackoverflow.com/questions/6565703/math-algorithm-fit-image-to-screen-retain-aspect-ratio
        if imgwidth > maxwidth and imgheight > maxheight:
            if (maxwidth/maxheight) > (imgwidth/imgheight):
                img = img.resize((int(imgwidth * maxheight / imgheight) - 5, maxheight - 5), Image.ANTIALIAS)
            else:
                img = img.resize((maxwidth, int(imgheight * maxwidth / imgwidth)), Image.ANTIALIAS)

        #image is too wide
        if img.size[0] > maxwidth:
            img = self.resize(img, width = maxwidth)
        #image is too taall
        if img.size[1] > maxheight:
            img = self.resize(img, height = maxheight)

        #display
        dims = img.size
        tkimg = ImageTk.PhotoImage(image = img)
        self.lbl_img.config(image = tkimg)
        self.lbl_img.image = tkimg

        #update label
        text = "%-56s %s (%ix%i)" % (os.path.split(self.path)[-1:][0], str(int((img.size[0] / self.orig_dims[0]) * 100)) + "%", self.orig_dims[0], self.orig_dims[1])
        self.buttons.lbl_text.config(text = text)

    #unused
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

    def edit_image(self, event = None):
        """Event placeholder to edit an image. Calls the EditWindow()
        class.
        
        Keyword Arguments:
            event {event} -- Used to make the method work with events.
             (default: {None})
        """

        if self.large_img is not None:
            EditWindow(self, self.large_img)

class Buttons(tk.Frame):

    def __init__(self, parent):
        """Class widget for the buttons at the bottom of the screen
        
        Arguments:
            parent {object} -- class that called this
        """

        tk.Frame.__init__(self, parent)
        self.parent = parent

        arrow_left = Image.open(os.path.join("Assets", "arrow_left.png"))
        rotate_right = Image.open(os.path.join("Assets", "rotate_right.png"))

        self.img_backwards = ImageTk.PhotoImage(arrow_left)
        self.img_forwards = ImageTk.PhotoImage(arrow_left.rotate(180))
        self.img_rotate_anticlockwise = ImageTk.PhotoImage(ImageOps.mirror(rotate_right))
        self.img_rotate_clockwise = ImageTk.PhotoImage(rotate_right)
        self.img_clipboard = tk.PhotoImage(file = os.path.join("Assets", "clipboard.png"))
        self.img_fullscreen = tk.PhotoImage(file = os.path.join("Assets", "fullscreen.png"))
        self.img_save = tk.PhotoImage(file = os.path.join("Assets", "save.png"))
        self.img_flip = tk.PhotoImage(file = os.path.join("Assets", "flip.png"))
        self.img_edit = tk.PhotoImage(file = os.path.join("Assets", "edit.png"))

        self.lbl_text = tk.Label(self)
        self.lbl_text.grid(row = 0, column = 0, columnspan = 11)

        ttk.Button(self, image = self.img_backwards, command = self.backwards).grid(row = 1, column = 0)
        ttk.Button(self, image = self.img_rotate_anticlockwise, command = self.anticlockwise).grid(row = 1, column = 1)
        ttk.Separator(self, orient=tk.VERTICAL).grid(row = 1, column = 2, sticky = 'ns', padx = 3)
        ttk.Button(self, image = self.img_edit, command = self.parent.edit_image).grid(row = 1, column = 3)
        ttk.Button(self, image = self.img_clipboard, command = self.clipboard).grid(row = 1, column = 4)
        ttk.Button(self, image = self.img_fullscreen, command = self.fullscreen).grid(row = 1, column = 5)
        ttk.Button(self, image = self.img_save, command = self.save).grid(row = 1, column = 6)
        ttk.Button(self, image = self.img_flip, command = self.flip).grid(row = 1, column = 7)
        ttk.Separator(self, orient=tk.VERTICAL).grid(row = 1, column = 8, sticky = 'ns', padx = 3)
        ttk.Button(self, image = self.img_rotate_clockwise, command = self.clockwise).grid(row = 1, column = 9)
        ttk.Button(self, image = self.img_forwards, command = self.forwards).grid(row = 1, column = 10)

    def __get_images(self):
        """Private. Returns all avaliable files
        
        Returns:
            list -- List of files that the app can open
        """

        return [file for file in os.listdir(os.path.split(self.parent.parent.img_viewer.path)[:-1][0]) if os.path.splitext(file)[1].lower() in IMPORT_FILES]

    def backwards(self, event = None):
        """Event placeholder for when someone wants to go back an image.
        Wraps around if required.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """

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
        """Event placeholder for when someone wants to go forwards an image.
        Wraps around if nessisary.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """

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
        """Adds the path to the current image to the clipboard.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """

        if self.parent.parent.img_viewer.path is not None:
            print(self.parent.parent.img_viewer.path)
            self.parent.parent.clipboard_clear()
            self.parent.parent.clipboard_append(self.parent.parent.img_viewer.path)
            self.parent.parent.update()

    def save(self, event = None):
        """Allows the user to copy this file to another directory
        
        Keyword Arguments:
            event {event} --  Makes this method work with events (default: {None})
        """
        if self.parent.parent.img_viewer.path is not None:
            orig = self.parent.parent.img_viewer.path
            if orig is not None:
                path = filedialog.askdirectory()
                if path != '':
                    shutil.copy2(orig, path)
                    messagebox.showinfo('Operation complete', 'Copied file %s to %s.' % (os.path.normpath(orig), os.path.normpath(path)))

    def fullscreen(self, event = None):
        """Opens a Toplevel window with the current image shown in full on it.
        Calls the FullscreenWindow() class.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """
        if self.parent.parent.img_viewer.path is not None:
            FullscreenWindow(self, Image.open(self.parent.parent.img_viewer.path))

    def anticlockwise(self, event = None):
        """Rotates the current image 90 degress anticlockwise.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """

        if self.parent.parent.img_viewer.path is not None:
            self.parent.open_image(self.parent.large_img.rotate(-90, expand = 1))

    def clockwise(self, event = None):
        """Rotates the current image 90 degrees clockwise.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """

        if self.parent.parent.img_viewer.path is not None:
            self.parent.open_image(self.parent.large_img.rotate(90, expand = 1))

    def flip(self, event = None):
        """Flips the image.
        
        Keyword Arguments:
            event {event} -- Makes this method work with events (default: {None})
        """

        if self.parent.parent.img_viewer.path is not None:
            self.parent.open_image(ImageOps.mirror(self.parent.large_img))

class FullscreenWindow(tk.Toplevel):

    def __init__(self, parent, img):
        """Opens a tk.Toplevel window which shows the image as large as possible on
        it. Closed by Esc key.
        
        Arguments:
            parent {object} -- class that called this class.
            img {Image} -- image to display.
        """

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

class EditWindow(tk.Toplevel):

    def __init__(self, parent, img):
        """tk.Toplevel widget where the user can preform various manupulations
        on an image and saves the new one to disc.
        
        Arguments:
            parent {object} -- class that called this class
            img {Image} -- image to be operated on.
        """

        tk.Toplevel.__init__(self, parent)
        self.parent = parent
        self.img = img
        self.iconbitmap(os.path.join("Assets", "icon.ico"))
        self.resizable(0, 0)
        self.orig_dims = img.size

        lbf_resize = tk.LabelFrame(self, text = "Resize image")
        lbf_resize.grid(row = 0, column = 0, columnspan = 2, padx = 5, pady = 5)

        self.maintainratio = tk.BooleanVar()
        ttk.Label(lbf_resize, text = "Width:").grid(row = 0, column = 0, padx = 6, pady = 6)
        ttk.Label(lbf_resize, text = "Height:").grid(row = 1, column = 0, padx = 6, pady = 6)
        self.ent_x = ttk.Entry(lbf_resize, width = 5)
        self.ent_x.grid(row = 0, column = 1, padx = 3, pady = 6)
        self.ent_y = ttk.Entry(lbf_resize, width = 5)
        self.ent_y.grid(row = 1, column = 1, padx = 3, pady = 6)
        self.__icon_chain = tk.PhotoImage(file = os.path.join("Assets", "chain.png"))
        ttk.Button(lbf_resize, image = self.__icon_chain, command = lambda: self.__fix_ratio("x")).grid(row = 0, column = 2, padx = 3, pady = 6)
        ttk.Button(lbf_resize, image = self.__icon_chain, command = lambda: self.__fix_ratio("y")).grid(row = 1, column = 2, padx = 3, pady = 6)

        self.ent_x.insert(0, self.orig_dims[0])
        self.ent_y.insert(0, self.orig_dims[1])

        lbf_transformation = tk.LabelFrame(self, text = "Image transformation")
        lbf_transformation.grid(row = 1, column = 0, columnspan = 2, padx = 5, pady = 5)

        self.flip = tk.BooleanVar()
        ttk.Checkbutton(lbf_transformation, text = "Flip image", variable = self.flip, onvalue = True, offvalue = False).grid(row = 0, column = 0, columnspan = 2, padx = 6, pady = 6)
        tk.Label(lbf_transformation, text = "Rotation:").grid(row = 1, column = 0, padx = 6, pady = 6)
        self.ent_rotate = ttk.Entry(lbf_transformation, width = 5)
        self.ent_rotate.grid(row = 1, column = 1, padx = 3, pady = 3)

        ttk.Separator(self).grid(row = 2, column = 0, columnspan = 2, sticky = "ew")

        self.__icon_tick = tk.PhotoImage(file = os.path.join("Assets", "tick.png"))
        self.__icon_cross = tk.PhotoImage(file = os.path.join("Assets", "cross.png"))

        ttk.Button(self, text = "Save", image = self.__icon_tick, compound = tk.LEFT, command = self.__go).grid(row = 3, column = 0, padx = 5, pady = 5, sticky = tk.W)
        ttk.Button(self, text = "Cancel", image = self.__icon_cross, compound = tk.LEFT, command = lambda: self.destroy()).grid(row = 3, column = 1, padx = 5, pady = 5, sticky = tk.E)

    def __fix_ratio(self, hw):
        """Private. Works out the other dimention so that the aspect ratio is mantained.
        
        Arguments:
            hw {str} -- char indicating if the calculations should be preformed on the height
            or the width.
        """

        try:
            if hw == "x":
                self.ent_y.delete(0, tk.END)
                self.ent_y.insert(0, self.__calc(self.img, width = int(self.ent_x.get())))
            elif hw == "y":
                self.ent_x.delete(0, tk.END)
                self.ent_x.insert(0, self.__calc(self.img, height = int(self.ent_y.get())))
        except ValueError:
            messagebox.showwarning("", "Please only input integers")
            self.focus_set()

    def __calc(self, img, **kwargs):
        """Private. Calculates the other dimention so that aspect ratio is mantained.
        
        Arguments:
            img {Image} -- image that's going to be resized. Needed for the calculation
        
        Raises:
            TypeError -- Thrown if neither 'height' nor 'width' args are found.
        
        Returns:
            int -- size of the other dim.
        """

        if list(kwargs.keys())[0] == 'height':
            baseheight = kwargs['height']
            hpercent = baseheight / float(img.size[1])
            wsize = int(float(img.size[0]) * float(hpercent))
            return wsize
        elif list(kwargs.keys())[0] == 'width':
            basewidth = kwargs['width']
            wpercent = basewidth / float(img.size[0])
            hsize = int(float(img.size[1]) * float(wpercent))
            return hsize
        raise TypeError("Missing argument: must have 'height' or 'width'.")

    def __go(self):
        """Private. Does transformations and saves to disc.
        
        Returns:
            None -- If user cancelled.
        """

        if self.ent_x.get().isdigit() and self.ent_y.get().isdigit():
            self.img = self.img.resize((int(self.ent_x.get()), int(self.ent_y.get())), Image.ANTIALIAS)
            if self.flip.get():
                self.img = ImageOps.mirror(self.img)
            if self.ent_rotate.get() != '':
                if self.ent_rotate.get().isdigit():
                    self.img = self.img.rotate(int(self.ent_rotate.get()), expand = 1)
                else:
                    messagebox.showwarning("", "Please only input integers")
                    self.focus_set()
                    return
            path = filedialog.asksaveasfile(filetypes = (("PNG images", "*.png"), ("JPEG images", "*.jpg")))
            if path == '' or path is None:
                return  #user cancelled
            else:
                path = path.name
                if os.path.splitext(path)[1] == "":
                    messagebox.showinfo("", "No file extension specified. Saving as .png.")
                    os.remove(path)
                    path += ".png"
                self.img.save(path)
                messagebox.showinfo("Done", "Image saved at %s" % path)
        else:
            messagebox.showwarning("", "Please only input integers")
            self.focus_set()

def max_height():
    """Returns an appropriate height for the app so that it fits on the screen.
    
    Returns:
        {int} -- height of app (pixels)
    """

    return int(min([i.height for i in screeninfo.get_monitors()]) * 2/3)

def max_width():
    """Returns an appropriate width for the app so that it fits on the screen.

    Returns:
        {int} -- the width of the app (pixels)
    """

    return int(min([i.width for i in screeninfo.get_monitors()]) * 2/3)

def get_filetypes():
    """Returns tuples of the avaliable filetpyes for use in a filedialog
    
    Returns:
        tuple -- avaliable filetypes
    """

    return (('%s images' % type[1:].upper(), type) for type in IMPORT_FILES)

#for testing purposes only
if __name__ == "__main__":
    try:
        start = sys.argv[1]
    except:
        start = None
    
    root = App(path = start)
    root.mainloop()