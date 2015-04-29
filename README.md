# easy-logging
A footage logging system for Blender VSE
# What can it do ?
Derushing tons of footage, adding tags, 3-point editing.
# Principle
When you pick a clip to log from a folder, easy logging brings it to an editing table where you can choose its IN and OUT point and define some tags.
# Where is it ?
In the video sequencer
# List of functions
FROM A NORMAL SEQUENCE
- import clip : import the clip directly from the file browser to your sequence. If the clip has already been logged, it is imported already trimmed.
- edit clip : import the clip from the file browser to the editing table.
- Local edit : uncheck if you use a dual-screen system. One for the normal sequence, one for the editing table

FROM THE EDITING TABLE
- edit clip : import the clip from the file browser to the editing table.
- in : define the starting point of your clip
- out : define the end point of your clip
- set in&out : define both in and out accordingly to the length of the active strip
- add tag : add a tag strip to the clip
- place : place the logged clip back to your main sequence
- as meta : ask for the clip to be packed as a metastrip (in case you added some other element in the editing table)
- back to sequence : save the log and get back to your main sequence
