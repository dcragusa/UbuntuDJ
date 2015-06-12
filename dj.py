#!/usr/bin/env python

from collections import OrderedDict
from Tkinter import *
import ConfigParser
import threading
import tkFont
import os


class MessageBox(object):

    def __init__(self, msg):
        root = self.root = Tk()
        root.title('UbuntuDJ')
        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(size=14)
        root.option_add("*Font", default_font)
        # main frame
        frame = Frame(root)
        frame.pack(ipadx=2, ipady=2)
        # message
        message = Label(frame, text=msg)
        message.pack(padx=16, pady=6)
        # buttons
        ok = Button(frame, width=8, text='OK', command=self.dismiss)
        ok.pack(side=TOP)
        ok.focus_set()
        ok.bind('<KeyPress-Return>', func=self.dismiss)
        root.update_idletasks()
        # centre screen
        xp = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        yp = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        geom = (root.winfo_width(), root.winfo_height(), xp, yp)
        root.geometry('{0}x{1}+{2}+{3}'.format(*geom))

    def dismiss(self):
        self.root.quit()


def errorbox(msg):
    msgbox = MessageBox(msg)
    msgbox.root.mainloop()
    msgbox.root.destroy()
    # exit after error
    quit()


try:
    from Xlib import X, XK, display
    from Xlib.ext import record
    from Xlib.protocol import rq
    # both import and test
except ImportError:
    errorbox('The Xlib library is not installed.\nRun sudo apt-get install python-xlib.')

try:
    from mplayer import Player, Step
except ImportError:
    errorbox('The mplayer library is not installed. Run sudo pip install mplayer.py')


if not os.path.isfile('config.cfg'):
    errorbox('Missing configuration file.\nconfig.cfg should be in this folder.')

config = ConfigParser.RawConfigParser()
config.read('config.cfg')

if not config.has_section('Directories'):
    errorbox('Incorrect configuration file.\nMake sure there is a [Directories] section.')
else:
    directories = config.items('Directories')

if not directories:
    errorbox('You must have at least one directory!')

### SETTINGS CHANGE
if config.has_option('Settings', 'mplayerloc'):
    mplayerloc = config.get('Settings', 'mplayerloc')
else:
    mplayerloc = '/usr/bin/mplayer'
if config.has_option('Settings', 'hideonplay'):
    option = config.get('Settings', 'hideonplay')
    if option.lower() == 'true':
        hideonplay = True
    elif option.lower() == 'false':
        hideonplay = False
    else:
        errorbox('Invalid option for hideonplay:\n%s' % option)
else:
    hideonplay = True
if config.has_option('Settings', 'showonstop'):
    option = config.get('Settings', 'showonstop')
    if option.lower() == 'true':
        showonstop = True
    elif option.lower() == 'false':
        showonstop = False
    else:
        errorbox('Invalid option for showonstop:\n%s' % option)
else:
    showonstop = True
if config.has_option('Settings', 'fixedonscreen'):
    option = config.get('Settings', 'fixedonscreen')
    if option.lower() == 'true':
        fixed = True
    elif option.lower() == 'false':
        fixed = False
    else:
        errorbox('Invalid option for fixedonscreen:\n%s' % option)
else:
    fixed = False
if config.has_option('Settings', 'horsize'):
    option = config.get('Settings', 'horsize')
    try:
        horsize = int(option)
    except ValueError:
        errorbox('Invalid number for horsize:\n%s' % option)
else:
    horsize = 200
if config.has_option('Settings', 'versize'):
    option = config.get('Settings', 'versize')
    try:
        versize = int(option)
    except ValueError:
        errorbox('Invalid number for versize:\n%s' % option)
else:
    versize = 600
if config.has_option('Settings', 'horoffset'):
    option = config.get('Settings', 'horoffset')
    try:
        horoffset = int(option)
    except ValueError:
        errorbox('Invalid number for horoffset:\n%s' % option)
else:
    horoffset = 1700
if config.has_option('Settings', 'veroffset'):
    option = config.get('Settings', 'veroffset')
    try:
        veroffset = int(option)
    except ValueError:
        errorbox('Invalid number for veroffset:\n%s' % option)
else:
    veroffset = 250

### CONTROLS CHANGE
controls = {}
controls['reset'] = ('KP_Home' if not config.has_option('Controls', 'reset') else config.get('Controls', 'reset'))
controls['showhide'] = ('KP_Insert' if not config.has_option('Controls', 'showhide') else config.get('Controls', 'showhide'))
controls['quit'] = ('KP_Delete' if not config.has_option('Controls', 'quit') else config.get('Controls', 'quit'))
controls['playstop'] = ('KP_Begin' if not config.has_option('Controls', 'playstop') else config.get('Controls', 'playstop'))
controls['volup'] = ('KP_Right' if not config.has_option('Controls', 'volup') else config.get('Controls', 'volup'))
controls['voldown'] = ('KP_Left' if not config.has_option('Controls', 'voldown') else config.get('Controls', 'voldown'))
controls['navup'] = ('KP_Up' if not config.has_option('Controls', 'navup') else config.get('Controls', 'navup'))
controls['navdown'] = ('KP_Down' if not config.has_option('Controls', 'navdown') else config.get('Controls', 'navdown'))


directorymap = OrderedDict()
for directory in directories:
    value, path = directory
    try:
        songs = sorted(os.listdir(path))
    except OSError:
        errorbox('You have specified an invalid directory:\n%s' % path)
    for song in songs:
        directorymap[song] = path

if not directorymap:
    errorbox('There are no files in the directories selected.')

if not os.path.isfile(mplayerloc):
    errorbox('Invalid mplayer location.\nCheck if mplayer is installed.\nIf not, run sudo apt-get install mplayer2.')


# main gui box
class UbuntuDJ:
    def __init__(self, parent, mplayerloc, hideonplay, showonstop, controls):

        self.parent = parent
        self.hideonplay = hideonplay
        self.showonstop = showonstop
        self.controls = controls
        self.parent.title('UbuntuDJ')

        # initially visible and not playing
        self.visible = True
        self.playing = False
        self.selected = 0

        # get mplayer info
        Player.exec_path = mplayerloc
        Player.introspect()
        self.p = Player()

        # bottom labels
        self.songname = StringVar()
        self.label1 = Label(parent, textvariable=self.songname, anchor=W)
        self.label1.pack(side=BOTTOM)
        self.status = StringVar()
        self.label2 = Label(parent, textvariable=self.status)
        self.label2.pack(side=BOTTOM)

        # scrollbar and listbox
        self.scrollbar = Scrollbar(parent)
        self.scrollbar.pack(side=LEFT, fill=Y)

        self.listbox = Listbox(parent, yscrollcommand=self.scrollbar.set, selectmode=BROWSE)
        for i in directorymap:
            self.listbox.insert(END, i)
        self.listbox.pack(side=LEFT, fill=BOTH, expand=1)

        self.scrollbar.config(command=self.listbox.yview)

        # select first item
        self.listbox.focus_set()
        self.listbox.selection_set(0)

        # bind to click too
        self.listbox.bind('<<ListboxSelect>>', self.OnClick)

        # topmost window
        self.parent.wm_attributes("-topmost", 1)

        # set up labels
        self.UpdateLabels()

    def ButtonPress(self, button):
        if button == self.controls['playstop']:     # play/stop
            self.PlayStop()
        elif button == self.controls['navup']:      # nav up
            if self.selected != 0:
                self.listbox.selection_clear(self.selected)
                self.selected -= 1
                self.listbox.selection_set(self.selected)
                self.listbox.activate(self.selected)
                self.listbox.see(self.selected)
        elif button == self.controls['navdown']:    # nav down
            if self.selected != self.listbox.size()-1:
                self.listbox.selection_clear(self.selected)
                self.selected += 1
                self.listbox.selection_set(self.selected)
                self.listbox.activate(self.selected)
                self.listbox.see(self.selected)
        elif button == self.controls['volup']:      # vol inc
            self.p.volume = Step(1)
            self.UpdateLabels()
        elif button == self.controls['voldown']:    # vol dec
            self.p.volume = Step(-1)
            self.UpdateLabels()
        elif button == self.controls['showhide']:   # show/hide
            self.ShowHide()
        elif button == self.controls['reset']:      # reset
            self.Reset()
        elif button == self.controls['quit']:       # exit
            self.Reset()
            self.parent.quit()

    def PlayStop(self):

        self.listbox.focus_set()
        if self.playing:
            self.playing = False
            self.p.quit()           # quit and get new player
            self.p = Player()
            if self.showonstop:
                self.parent.update()
                self.parent.deiconify()
                self.visible = True
            self.UpdateLabels()
        else:
            self.playing = True
            song = self.listbox.get(ACTIVE)
            prefix = directorymap[song]
            self.p.loadfile(prefix+'/'+song)
            if self.hideonplay:
                self.parent.withdraw()
                self.visible = False
            self.UpdateLabels()

    def ShowHide(self):
        if self.visible:
            self.parent.withdraw()
            self.visible = False
        else:
            self.parent.update()
            self.parent.deiconify()
            self.visible = True

    def OnClick(self, event):
        w = event.widget
        index = int(w.curselection()[0])
        self.selected = index
        self.listbox.activate(index)

    def UpdateLabels(self):
        playing = ('Playing' if self.playing else 'Stopped')
        volume = ('None' if self.p.volume is None else str(self.p.volume))
        self.status.set(playing + ' | Volume: ' + volume)
        songname = (self.listbox.get(ACTIVE) if self.playing else '-')
        self.songname.set(songname)

    def Reset(self):
        self.p.quit()
        self.p = Player()
        self.playing = False
        self.UpdateLabels()


root = Tk()
root.resizable(width=False, height=False)
root.geometry('%sx%s+%s+%s' % (horsize, versize, horoffset, veroffset))
if fixed:
    root.overrideredirect(True)
UbuntuDJ = UbuntuDJ(root, mplayerloc, hideonplay, showonstop, controls)

# keypress detection section
local_dpy = display.Display()
record_dpy = display.Display()

def lookup_keysym(keysym):
    for name in dir(XK):
        if name[:3] == "XK_" and getattr(XK, name) == keysym:
            return name[3:]
    return "[%d]" % keysym

def record_callback(reply):
    if reply.category != record.FromServer:
        return
    if reply.client_swapped:
        return
    if not len(reply.data) or ord(reply.data[0]) < 2:
        # not an event
        return

    data = reply.data
    while len(data):
        event, data = rq.EventField(None).parse_binary_value(data, record_dpy.display, None, None)

        if event.type == X.KeyPress:
            keysym = local_dpy.keycode_to_keysym(event.detail, 0)
            if keysym:
                UbuntuDJ.ButtonPress(lookup_keysym(keysym))

ctx = record_dpy.record_create_context(
        0,
        [record.AllClients],
        [{
            'core_requests': (0, 0),
            'core_replies': (0, 0),
            'ext_requests': (0, 0, 0, 0),
            'ext_replies': (0, 0, 0, 0),
            'delivered_events': (0, 0),
            'device_events': (X.KeyPress, X.KeyPress),
            'errors': (0, 0),
            'client_started': False,
            'client_died': False,
        }])

# need this to run at the same time
logger = threading.Thread(target=record_dpy.record_enable_context, args=(ctx, record_callback))
# quits on main program exit
logger.daemon = True
logger.start()

# main gui loop
root.mainloop()
record_dpy.record_free_context(ctx)
