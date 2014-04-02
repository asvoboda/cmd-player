cmd-player
==========

A windows only, python based cli for navigating a music directory. Supports a variety of commands to seek/skip through songs, and features a  simple queuing system.

Just type `python player.py` to start!

###Dumb Python Player
 - `cd [dir]` to change directories
 - `ls` to list directories
 - `play [song]` to play the specified song

###Playlist Operations
 - `queue all` adds all songs in the current directory to your playlist
 - `queue show` prints the songs in your playlist
 - `queue clear` clears the playlist
 - `queue [song]` adds the specified song to your playlist

###Song Operations
 - `song pause` to pause the current song
 - `song resume` resumes a paused song
 - `song skip` to skip to the next song in the playlist
 - `song stop` stops execution and clears the playlist

 - `exit` to exit