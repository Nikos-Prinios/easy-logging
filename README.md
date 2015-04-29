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
- <b>import clip :</b> import the clip directly from the file browser to your sequence. If the clip has already been logged, it is imported already trimmed.
- <b>edit clip :</b> import the clip from the file browser to the editing table.
- <b>Local edit :</b> uncheck if you use a dual-screen system. One for the normal sequence, one for the editing table

FROM THE EDITING TABLE
- <b>edit clip :</b> import the clip from the file browser to the editing table.
- <b>in :</b> define the starting point of your clip
- <b>out :</b> define the end point of your clip
- <b>set in&out :</b> define both in and out accordingly to the length of the active strip
- <b>add tag :</b> add a tag strip to the clip
- <b>place :</b> place the logged clip back to your main sequence
- <b>as meta :</b> ask for the clip to be packed as a metastrip (in case you added some other element in the editing table)
- <b>back to sequence :</b> save the log and get back to your main sequence
