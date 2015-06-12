# UbuntuDJ

An unobtrusive music player for linux, developed in Ubuntu. Very useful for micspam in games too.

Dependencies:
* mplayer (*sudo apt-get install mplayer2*)
* python-xlib (*sudo apt-get install python-xlib*)
* mplayer.py
* (optional) pavucontrol (*sudo apt-get install pavucontrol*)

To install mplayer.py, run *sudo pip install mplayer.py*.

However, there is a possible bug, which will throw a KeyError on install. To get around this, download mplayer.py from [here](https://pypi.python.org/pypi/mplayer.py/), extract, and modify core.py inside the mplayer folder.

Around line 252, change this:
```python
t = mtypes.type_map[arg]
sig.append('{0}{1}{2}'.format(t.name, i, optional))
types.append('mtypes.{0},'.format(t.__name__))
```

to this:
```python
if(arg in mtypes.type_map):
    t = mtypes.type_map[arg]
    sig.append('{0}{1}{2}'.format(t.name, i, optional))
    types.append('mtypes.{0},'.format(t.__name__))
```

Then run *sudo python setup.py install* from the main folder. [Credit](https://code.google.com/p/python-mplayer/issues/detail?id=14)


Once everything is installed, you'll need to modify the config file, ```config.cfg```, by providing it with at least one directory to find your music files in. It doesn't really matter what key you give the paths (1 and 2 in the example), but numbers allow you to order the music's appearance in the player: so in the example, all the music from the Micspam directory will come before all the music in the OtherMicspam directory. In each separate directory, the music will be displayed in standard alphabetical order.


The other settings have defaults, and are used as follows:
* mplayerloc: the location of the mplayer executable. You can change this if you installed mplayer elsewhere.
* minimiseonplay: the window will hide when you start playing a song.
* horsize and versize: horizontal and vertical size of the player respectively.
* horoffset and veroffset: offset in pixels from the top left of the screen. The defaults are good for a 1080p display.
* fixedonscreen: if this is ```true```, you will not be able to move the player once the program starts. Experiment with the offsets to find a comfortable location on screen. You will need this option active if you want the player to appear over fullscreen applications, such as games.

If you want to modify a setting, simply delete the semicolon from in front of the ```[Settings]``` header and the setting you want to change.


The default controls provide what I find to be easy to use defaults on the numpad, which work even with num lock off. If however you don't have a numpad, you can of course change the keys. Common key codes can be found in the file 'Common Xlib Keys', while if you have a weird keyboard you can find all (literally, **all**) key codes accepted by Xlib in the file 'Complete Xlib Keys'. Warning, it's a big file. Feel free to delete these files once you've found a configuration that you like.

To change a key, delete the semicolon from in front of the ```[Controls]``` header and the control you want to change.

## Micspam

You may want this to micspam in your favourite game - there's some additional steps to go through however. Here's where you'll need pavucontrol.
These instructions are for Steam TF2, though I'm sure you can extend them to other games if you wish.

1. Open up a terminal, and type *load-module module-null-sink sink_name=UbuntuDJ*
2. Start up UbuntuDJ and play something. While it's playing, open up pavucontrol.
3. On the playback tab, make select 'Show: All Streams' at the bottom. Change the mplayer output from the default to 'Null Output'. This will mute the music.
4. Now go to Steam > Settings > Voice and change the microphone device to 'Monitor of Null Output'. If you click 'Test Microphone' and UbuntuDJ is still playing, you should hear music coming through.
5. Finally, for each game you want to be able to micspam in, you need to paste the following to the game's autoexec.cfg file:

```
// Micspam toggle
alias micspamEnable "voice_loopback 1; +voicerecord; alias micspamToggle micspamDisable"
alias micspamDisable "-voicerecord; voice_loopback 0; alias micspamToggle micspamEnable"
alias micspamToggle micspamEnable
bind KP_5 micspamToggle
```
(Credit to TF2DJ)

6. To make this permanent, run *sudo cp /etc/pulse/default.pa ~/.pulse/default.pa* to make a local copy of your Pulseaudio config file. Open it up and type *load-module module-null-sink sink_name=UbuntuDJ* at the bottom of the file.
7. The audio sink will persist through reboots now. Steam will remember your mic input, but annoyingly pavucontrol may forget that mplayer is supposed to output to the null sink. Just re-run steps 2-3 after a reboot to be able to micspam again.

```KP_5``` in the autoexec.cfg file must be the same key you've selected for ```playstop``` in the config file. Note that the names may be different! For the key names that Steam will accept, refer [here](http://tf2wiki.net/wiki/Bindable_keys).

Unlike other programs on Windows, such as TF2DJ, this runs completely independently. Simply launch it at some point, and you'll be ready to micspam.
To launch this without a terminal window, you'll need to make UbuntuDJ.py executable (Right click > Properties > Permissions > Allow executing file as program).
