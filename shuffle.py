import pickle, os, random, bpy

# ************************************************************************************************
# Define a pattern
pattern = 'arnaud fireworks arnaud guitare remi tanguy remi guitare fireworks'

# Pace of the music (in frames)
global pace
pace = 24

# Acceptable number of pace for one clip
global step
step = [.5,1,2]

# Approximate length of the new sequence (sec)
Total_length = 60

# *************************************************************************************************


dict = {}
pattern = pattern.split()

# find the path of a clip
def find_path(clip):
	for s in path_list:
		filepath = s + clip
		if os.path.isfile(filepath):
			return filepath
# Define new in and out point regarding the pace			
def new_data(inpoint,outpoint):
	while True:
		clip_length = random.choice(step)*pace
		length = outpoint - inpoint
		if length >= clip_length:
			middle = ((outpoint-inpoint)/2)+inpoint
			inpoint = int(middle-(clip_length/2))
			outpoint = int(middle+(clip_length/2))
			return [inpoint,outpoint]
			break

		
log_file = os.path.expanduser('~/%s.ez' % 'Easy-Logging-log-file')
if os.path.exists(log_file):
	path_list, user,log = pickle.load( open( log_file, "rb" ) )
	print('Metadata created by : ' + user)
	
	# La list des tags
	tag_list = set()
	for t in pattern:
		tag_list.add(t)
	print ('tag list: ' + str(tag_list))
	
	# construction du dictionnaire des tags
	for t in tag_list:	
		dict[t]=[]
		print(t)
		for clip_file in log:
			if len(clip_file) > 1 :
				clip = clip_file[0]
				for tag_obj in clip_file[1:]:
					tag = tag_obj[0].split('.', 1)[0]
					inpoint = tag_obj[1]
					outpoint = tag_obj[2]
					length = outpoint-inpoint
					if tag == t:
						dict[t].append( [clip[0].split('#')[0],inpoint,outpoint,length] )
						print(clip[0], inpoint, outpoint)
						
# create the list of clips to import on the timeline	
list = []
for t in pattern:
	try:
		list.append( random.choice(dict[t]) )
	except:
		pass
	
# populating....
start = bpy.context.scene.frame_current
begin_at = start

original_type = bpy.context.area.type
bpy.context.area.type = "SEQUENCE_EDITOR"

for c in list:
	clip = c[0]
	inout = new_data(c[1],c[2])
	inpoint = inout[0]
	outpoint = inout[1]
	path = find_path(clip)
	
 	# the lego job
	bpy.ops.sequencer.select_all(action = "DESELECT")
	bpy.ops.sequencer.movie_strip_add(frame_start=start, filepath=path, sound=False, channel=1)
	strip = bpy.context.scene.sequence_editor.active_strip
	strip.frame_final_end=start+outpoint
	strip.frame_final_start=start+inpoint
	bpy.ops.transform.seq_slide(value=(-(strip.frame_final_start-start), 0))
	start = strip.frame_final_end
	bpy.context.scene.frame_current = start
	
bpy.context.scene.frame_end = start
bpy.ops.sequencer.view_all()  
bpy.context.area.type = original_type
