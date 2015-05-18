import bpy, random

# ************************************************************************************************
# Define a pattern
pattern = 'teacher student student student teacher student school street'

# Pace of the music (in frames)
global pace
pace = 24

# Acceptable number of pace for one clip
global step
step = [1,2,4]

# Approximate length of the new sequence (sec)
Total_length = 60

# *************************************************************************************************
bpy.types.Object.tags = bpy.props.StringProperty()    
bpy.types.Object.inpoint = bpy.props.IntProperty()   
bpy.types.Object.outpoint = bpy.props.IntProperty() 

# some definitions
Total_length = Total_length * bpy.context.scene.render.fps
cont = bpy.context.scene
seq = bpy.ops.sequencer
cur = cont.frame_current
sce = bpy.data.scenes
Clips = []
Tags = []
dict = {}
global main_scene
   

def new_data(obj):
    inpoint = obj.inpoint
    outpoint = obj.outpoint
    
    clip_length = random.choice(step)*pace
    middle = ((outpoint-inpoint)/2)+inpoint
    
    inpoint = int(middle-(clip_length/2))
    outpoint = int(middle+(clip_length/2))
    
    return [inpoint,outpoint]
    
# define the actual scene as the working scene
main_scene = bpy.context.screen.scene

# iterate through all the clips and populate our clip collection
for obj in main_scene.objects:
    if obj.type == 'EMPTY':
        if len(obj.keys()) > 1:
            if obj.parent:
                Clips.append(obj)
                
# Create the list of tags
for obj in main_scene.objects:
    if obj.type =='EMPTY':
        if len(obj.keys()) > 1:
            if obj.parent:
                temp=(obj.tags).split()
                for i in temp:
                    if i not in Tags:
                        Tags.append(i)
                     
# make sure all tags exist                     
for p in pattern.split():
    for t in temp:
        if t not in Tags:
            print ("A tag doesn't exist in your scene, check the spelling, maybe ?")
            break
        
# Built the dictionnary (tags : obj)
for t in Tags:
    dict[t]=[]
    for obj in Clips:
        if t in (obj.tags).split():
            dict[t].append(obj)

 

# populate the sequence
start = bpy.context.scene.frame_current
begin_at = start
original_type = bpy.context.area.type
bpy.context.area.type = "SEQUENCE_EDITOR"

# Here loop until frame > total_length
while True:

    # create a list of obj following the pattern
    list = []
    for t in pattern.split():
        list.append( random.choice(dict[t]) )

    for obj in list:
        
        path = obj.parent.name
        clip = obj.name
        
        inpoint = (new_data(obj)[0])
        outpoint = (new_data(obj)[1])
        
        # the lego job
        bpy.ops.sequencer.select_all(action = "DESELECT")
        bpy.ops.sequencer.movie_strip_add(frame_start=start, filepath=path+clip, sound=False, channel=1)
        strip = bpy.context.scene.sequence_editor.active_strip
        strip.frame_final_end=start+outpoint
        strip.frame_final_start=start+inpoint
        bpy.ops.transform.seq_slide(value=(-(strip.frame_final_start-start), 0))
        start = strip.frame_final_end
        bpy.context.scene.frame_current = start
        
        if start > (Total_length + begin_at):
            break
        
    if start > (Total_length + begin_at):
        break
bpy.context.scene.frame_end = start
bpy.ops.sequencer.view_all()  
bpy.context.area.type = original_type
