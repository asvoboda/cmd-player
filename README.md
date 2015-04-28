cmd-player
==========

A windows only (for now), python based cli for navigating a music directory. Supports a variety of commands to seek/skip through songs, and features a simple queuing system.

Supports Python 3.4

Install with `python setup.py install` and then `python -m player` to start!

You will be prompted to give cmdplayer the location of the topmost music directory. This can be changed on startup, if necessary.

###Dumb Python Player
 - `cd [dir]` to change directories
 - `ls` to list directories
 - `play [song]` to play the specified song

###Playlist Operations
 - `addall` adds all songs in the current directory to your playlist
 - `showall` prints the songs in your playlist
 - `clear` clears the playlist
 - `add [song]` adds the specified song to your playlist
 - `repeat` toggles re-adding any song that finishes playing to the end of the playlist

###Song Operations
 - `pause` to pause the current song
 - `resume` resumes a paused song
 - `skip` to skip to the next song in the playlist
 - `stop` stops execution and clears the playlist
 - `show` displays information about the current playing song

 - `exit` to exit