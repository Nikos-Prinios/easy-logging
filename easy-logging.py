#  ***** GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#  All rights reserved.
#  ***** GPL LICENSE BLOCK *****

bl_info = {
    "name": "Easy Logging",
    "author": "Nicolas Priniotakis",
    "version": (0,2,0),
    "blender": (2, 7, 4, 0),
    "api": 44539,
    "category": "Sequencer",
    "location": "Sequencer > UI > Easy Logging",
    "description": "Logging system for the Video Sequence Editor",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",}

# -- IMPORT ------------------------------------------------------------
import bpy, random, time, os
import pickle


# -- Custom Properties & VARIABLES -------------------------------------
bpy.types.Object.tags = bpy.props.StringProperty()    
bpy.types.Object.inpoint = bpy.props.IntProperty()   
bpy.types.Object.outpoint = bpy.props.IntProperty() 
bpy.types.Scene.local_edit = bpy.props.BoolProperty(name="Local Edit",description="Edit in the opened sequencer",default = True)
bpy.types.Scene.meta = bpy.props.BoolProperty(name="As Meta",description="Send trimed clip(s) as a meta strip to the sequencer",default = False)

bad_obj_types = ['CAMERA','LAMP','MESH']
global clip, clip_object, main_scene, log, fps

# Initialization -----
# Load the log file
log_file = "Easy-Logging-log-file.txt"
if os.path.exists(log_file):
    log = pickle.load( open( log_file, "rb" ) )
else:
    log = []

print(log)
inpoint = 0
outpoint = 0
tags = 'none'


# -- FUNCTIONS - 2.0 ----------------------------------------------------
# clip = clip name
# clip_id = clip index in the log object
# tag is a tag name
# inpoint - for either a clip or a tag
# outpoint - for either a clip or a tag
# -----------------------------------------------------------------------

# Update the log file
def update_log_file():    
    pickle.dump( log, open( "Easy-Logging-log-file.txt", "wb" ) )
   
# Add a new clip
def add_clip(clip,inpoint,outpoint):
    log.append([[clip,inpoint,outpoint]])
    print(log)

# Add tag to a referenced clip
def add_tag(clip,name,inpoint,outpoint):
    tag = [name,inpoint,outpoint]
    if isinstance(clip,str):
        exists, id = clip_exists(clip)
    else:
        id = clip
    log[id].append(tag)
    print(log)
 
# Check if a clip is already referenced and return its id
def clip_exists(clip):
    for x in log:
        if clip in x[0]:
            return (True,log.index(x))
    return (False, -1)
    print(log)

# Update a clip in point
def update_inpoint(clip,inpoint):
    exists,id = clip_exists(clip)
    if exists:
        log[id][0][1] = inpoint
        print(log)
        
# Update a clip out point
def update_outpoint(clip,outpoint):
    exists,id = clip_exists(clip)
    if exists:
        log[id][0][2] = outpoint
        print(log)

# Update a clip in & out points
def update_clip(clip,inpoint,outpoint):
    update_inpoint(clip,inpoint)
    update_outpoint(clip,outpoint)
    print(log)

# Update a tag or create it
def update_tag(clip,tag,inpoint,outpoint):
    updated = False
    exists,id = clip_exists(clip)
    if exists:
        for x in log[id][1:]:
            if x[0] == tag :
                x[1] = inpoint
                x[2] = outpoint
                updated = True
    if not updated:
        add_tag(id,tag,inpoint,outpoint)
    print(log)

# Return the list of tags of a clip
def tag_list(clip):
    exists, id = clip_exists(clip)
    tags = []
    if exists:
        for y in log[id][1:]:
            tags.append([y[0],y[1],y[2]])
        return tags

# Return the clip_object [name,in,out]
def get_clip(clip):
    exists,id = clip_exists(clip)
    if exists:
        return [clip,log[id][0][1],log[id][0][2]]
    else:
        add_clip(clip,-1,-1)
    return [clip,-1,-1]

# Returns TRUE if the scene 'Editing table' already exists
def editing_table_exists():
    for i in bpy.data.scenes:
        if i.name == 'Editing table':
            return True
    return False

# Create the 'Editing table' scene
def reset_editing_table():
    global main_scene
    if editing_table_exists():
        bpy.context.screen.scene = bpy.data.scenes['Editing table']
        bpy.ops.scene.delete()                                    
    new_scene = bpy.data.scenes.new('Editing table')
    new_scene.render.fps = main_scene.render.fps
    new_scene.use_audio_scrub = True
    new_scene.use_audio_sync = True
    new_scene.use_frame_drop = True
    return True
      
# Define the main scene
def set_as_main_scene():
    global main_scene
    main_scene = bpy.context.screen.scene

# Set active scene to main
def goto_main_scene():
    global main_scene
    bpy.context.screen.scene = main_scene

# Create tag strip
def new_tag_strip(inpoint,outpoint,name):
    if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
        orginal_context = bpy.context.area.type
        bpy.context.area.type = "SEQUENCE_EDITOR"
        seq = bpy.ops.sequencer
        seq.effect_strip_add(frame_start=inpoint, frame_end=outpoint, type='COLOR', color=(random.uniform(0.5,1),random.uniform(0.5,1),1), overlap=False)
        new_strip = bpy.context.scene.sequence_editor.active_strip
        new_strip.name = name
        new_strip.blend_alpha = 0
        bpy.context.area.type = orginal_context

# Update clip and tags in the log
def update_log():
    global clip
    # tags
    for s in bpy.context.scene.sequence_editor.sequences_all:
        if s.type == 'COLOR':
            tag = s.name
            inpoint = s.frame_start
            outpoint = s.frame_final_end
            update_tag(clip,tag,inpoint,outpoint)
    # clip
    inpoint = bpy.data.scenes['Editing table'].frame_start
    outpoint = bpy.data.scenes['Editing table'].frame_end
    update_clip(clip,inpoint,outpoint)
    # Update the log file on disk
    update_log_file()

# Returns the type of the selected element in the browser          
# This nice function has been written by Björn Sonnenschein 
def detect_strip_type(filepath):
    print (filepath)

    imb_ext_movie = [
    ".avi",
    ".flc",
    ".mov",
    ".movie",
    ".mp4",
    ".m4v",
    ".m2v",
    ".m2t",
    ".m2ts",
    ".mts",
    ".mv",
    ".avs",
    ".wmv",
    ".ogv",
    ".dv",
    ".mpeg",
    ".mpg",
    ".mpg2",
    ".vob",
    ".mkv",
    ".flv",
    ".divx",
    ".xvid",
    ".mxf",
    ]

    imb_ext_audio = [
    ".wav",
    ".ogg",
    ".oga",
    ".mp3",
    ".mp2",
    ".ac3",
    ".aac",
    ".flac",
    ".wma",
    ".eac3",
    ".aif",
    ".aiff",
    ".m4a",
    ]

    extension = os.path.splitext(filepath)[1]
    extension = extension.lower()
    if extension in imb_ext_movie:
        type = 'MOVIE'
    elif extension in imb_ext_audio:
        type = 'SOUND'
    else:
        type = None
    print (type)
    return type

# --- CLASSES ---------------------------------------------------------------------

# Creating the IN/OUT PANEL    
class iop_panel(bpy.types.Header):     
    bl_space_type = "SEQUENCE_EDITOR"       
    bl_region_type = "UI"          
    bl_label = "Trim"
    global main_scene
    
    @classmethod
    def poll(self, context):
        return True
    
    def draw(self, context):
        layout = self.layout
        layout.separator()
        if editing_table_exists():
            if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
                row=layout.row()
                row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
                layout.separator()
                row.operator("sequencer.setin", icon="TRIA_RIGHT")
                row.operator("sequencer.setout", icon='TRIA_LEFT')
                row.operator("sequencer.addtag", icon='TRIA_LEFT')
                row.operator("sequencer.place", icon="PASTEFLIPDOWN")
                row.prop(context.scene,"meta")
                row.operator("sequencer.back", icon="LOOP_BACK")
            else:
                row=layout.row()
                row.operator("sequencer.import", icon="ZOOMIN")
                row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
                row.prop(context.scene,"local_edit")
        else:
                row=layout.row()
                row.operator("sequencer.import", icon="ZOOMIN")
                row.operator("sequencer.trim", icon="ARROW_LEFTRIGHT")
                row.prop(context.scene,"local_edit")

# Creating the Place button operator - 2.0
class OBJECT_OT_Place(bpy.types.Operator):  
    bl_label = "Place"
    bl_idname = "sequencer.place"
    bl_description = "Place the clip in the timeline"
        
    def invoke(self, context, event):
        global main_scene
        # Save clip meta in the log
        update_log()
        
        # Trim the area
        inpoint = bpy.data.scenes['Editing table'].frame_start
        outpoint = bpy.data.scenes['Editing table'].frame_end
        bpy.ops.sequencer.select_all(action = "SELECT")
        bpy.context.scene.frame_current = inpoint
        bpy.ops.sequencer.cut(frame=inpoint, type='SOFT', side='LEFT')
        bpy.ops.sequencer.delete()
        bpy.ops.sequencer.select_all(action = "SELECT")
        bpy.context.scene.frame_current = outpoint
        bpy.ops.sequencer.cut(frame=outpoint, type='SOFT', side='RIGHT')
        bpy.ops.sequencer.delete()  
        bpy.context.scene.frame_current = inpoint
        
        if bpy.data.scenes['Editing table'].meta == True:
            # make metastrip
            bpy.ops.sequencer.select_all(action = "SELECT")
            bpy.ops.sequencer.meta_make()
            bpy.ops.sequencer.select_all(action = "SELECT")
        else:
            # select everything except tag strips
            bpy.ops.sequencer.select_all(action = "DESELECT")
            for s in context.scene.sequence_editor.sequences_all:
                if s.type != 'COLOR':
                    s.select = True
        
        
        
        bpy.ops.sequencer.copy()
        #goto_main_scene()
        bpy.context.screen.scene = main_scene
        bpy.ops.sequencer.paste()
        bpy.context.scene.frame_current = bpy.context.scene.frame_current + (outpoint-inpoint)
        # clean up
        reset_editing_table()
        if main_scene.local_edit == False:
            bpy.context.screen.scene = bpy.data.scenes['Editing table']
        else:
            bpy.context.screen.scene = main_scene

        
        return {'FINISHED'}

# Creating the IMPORT button operator - 2.0
class OBJECT_OT_import(bpy.types.Operator): 
    bl_label = "Import clip"
    bl_idname = "sequencer.import"
    bl_description = "Import the selected clip in the browser"
    global main_scene  
    def invoke(self, context, event):

        for a in bpy.context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                the_path = params.directory
                the_file = params.filename
                clip = the_path + the_file
                break

        clip_object = get_clip(clip)
        start = clip_object[1]
        end = clip_object[2]

        if bpy.context.screen.scene.name != 'Editing table':
            set_as_main_scene()

        reset_editing_table()

        bpy.context.screen.scene = bpy.data.scenes['Editing table']
        if start != -1 and end != -1 :
            file_type = detect_strip_type(clip)
            
            original_type = bpy.context.area.type
            bpy.context.area.type = "SEQUENCE_EDITOR"
            if (file_type == "MOVIE"):
                bpy.ops.sequencer.movie_strip_add(frame_start=1, filepath=clip)
            if (file_type == "SOUND"):
                bpy.ops.sequencer.sound_strip_add(frame_start=1, filepath=clip)
            bpy.context.area.type = original_type

            bpy.data.scenes['Editing table'].frame_start = start if start > 0 else 1 
            bpy.data.scenes['Editing table'].frame_end = end if end >1 else bpy.context.scene.sequence_editor.active_strip.frame_final_duration +1
                
            bpy.context.scene.frame_current = start
            bpy.ops.sequencer.cut(frame=start, type='SOFT', side='LEFT')
            bpy.ops.sequencer.delete()

            bpy.ops.sequencer.select_all(action = "SELECT")
            
            bpy.context.scene.frame_current = end
            bpy.ops.sequencer.cut(frame=end, type='SOFT', side='RIGHT')
            bpy.ops.sequencer.delete()
            
            bpy.context.scene.frame_current = start
            bpy.ops.sequencer.select_all(action = "SELECT")
            bpy.ops.sequencer.copy()
            goto_main_scene()
            bpy.ops.sequencer.paste()
            bpy.context.scene.frame_current = bpy.context.scene.frame_current + (end-start)
        else:
            file_type = detect_strip_type(clip)
            if (file_type == "MOVIE"):
                    bpy.ops.sequencer.movie_strip_add(filepath=clip, frame_start=bpy.context.scene.frame_current)
            if (file_type == "SOUND"):
                    bpy.ops.sequencer.sound_strip_add(filepath=clip, frame_start=bpy.context.scene.frame_current)
            
        
        return {'FINISHED'}

# Creating the TRIM (EDIT) button operator - 2.0
class OBJECT_OT_Trim(bpy.types.Operator): 
    bl_label = "Edit clip"
    bl_idname = "sequencer.trim"
    bl_description = "Trim the selected clip in the browser"
    
    def invoke(self, context, event):
        global main_scene, clip, clip_object
        #get directory & name (path - clip)
        for a in bpy.context.window.screen.areas:
            if a.type == 'FILE_BROWSER':
                params = a.spaces[0].params
                the_path = params.directory
                the_file = params.filename
                clip = the_path + the_file
                break

        # set current scene as main scene
        if bpy.context.screen.scene.name != 'Editing table':
            set_as_main_scene()

        #create the log scene if it doesn't already exist
        reset_editing_table()
        
        # Go to log scene, import the file and set start/end if exists
        bpy.context.screen.scene = bpy.data.scenes['Editing table']

        #check the type of the file and add its strips accordingly
        file_type = detect_strip_type(clip)
        if (file_type == "MOVIE") or (file_type == "SOUND"):
            original_type = bpy.context.area.type
            bpy.context.area.type = "SEQUENCE_EDITOR"
            if (file_type == "MOVIE"):
                bpy.ops.sequencer.movie_strip_add(frame_start=1, filepath=clip)
            else:
                bpy.ops.sequencer.sound_strip_add(frame_start=1, filepath=clip)
            bpy.context.area.type = original_type

            # create clip entry in the log if not already registered
            # pick up the in and out point and the tags
            # initialize the object variables
            tags = []
            exists, id = clip_exists(clip)
            if exists:
                clip_object = get_clip(clip)
                tags = tag_list(clip)
                start = clip_object[1]
                end = clip_object[2]
            else:
                start = 1
                end = bpy.context.scene.sequence_editor.active_strip.frame_final_duration
                add_clip(clip,start,end)
            bpy.data.scenes['Editing table'].frame_start = start if start > 0 else 1
            bpy.data.scenes['Editing table'].frame_end = end if end > 1 else bpy.context.scene.sequence_editor.active_strip.frame_final_duration
            # add existing tags linked to the clip
            if len(tags) > 0:
                for x in tags:
                    new_tag_strip(x[1],x[2],x[0])

        bpy.ops.sequencer.select_all(action = "SELECT")
        bpy.ops.sequencer.view_selected()
        return {'FINISHED'}
  
# creating the ADD TAG button operator - 2.0
class OBJECT_OT_addTag(bpy.types.Operator): 
    bl_label = "Add Tag"
    bl_idname = "sequencer.addtag"
    bl_description = "Add a new tag to the clip"
        
    def invoke(self, context, event):
        inpoint = bpy.data.scenes['Editing table'].frame_current
        outpoint = inpoint + 50
        new_tag_strip(inpoint,outpoint,'new tag')
        return {'FINISHED'}
  
# creating the IN button operator - 2.0
class OBJECT_OT_Setin(bpy.types.Operator): 
    bl_label = "IN"
    bl_idname = "sequencer.setin"
    bl_description = "Set the IN point of the clip"
    
    def invoke(self, context, event):
        global clip
        if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
            inpoint = bpy.context.scene.frame_current
            bpy.data.scenes['Editing table'].frame_start = inpoint
            update_inpoint(clip,inpoint)
        return {'FINISHED'}
        
# creating the OUT button operator - 2.0  
class OBJECT_OT_Setout(bpy.types.Operator):  
    bl_label = "OUT"
    bl_idname = "sequencer.setout"
    bl_description = "Set the OUT point of the clip"
        
    def invoke(self, context, event):
        global clip
        clip_object = get_clip(clip)
        if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
            outpoint = bpy.context.scene.frame_current
            bpy.data.scenes['Editing table'].frame_end = outpoint + 1
            update_outpoint(clip,outpoint)           
            if clip_object[1] < 1:
                inpoint = 1
                update_inpoint(clip,inpoint)
        return {'FINISHED'}

# creating the back button operator - 2.0 
class OBJECT_OT_Back(bpy.types.Operator):  
    bl_label = "Back to Sequence"
    bl_idname = "sequencer.back"
    bl_description = "Go back to the main sequence"
        
    def invoke(self, context, event):
        global main_scene
        if bpy.context.screen.scene == bpy.data.scenes['Editing table']:
            goto_main_scene()
        return {'FINISHED'}

# creating the menu "create log file" operator   /disabled/    
class SEQUENCER_OT_createlog(bpy.types.Operator):
    bl_idname = "sequencer.createlog"
    bl_label = "Create the log file"
    def execute(self, context):
        #create_the_log_file()
        return {'FINISHED'}
        
class SEQUENCER_OT_makewagon(bpy.types.Operator):
    bl_idname = "sequencer.makewagon"
    bl_label = "Create the tag scenes"
    def execute(self, context):
        #make_wagon()
        return {'FINISHED'}

# -- MENU EASY LOGGING ----------------------------------------------------



# -- REGISTRATIONS -----------------------------------------------------

def register():
    #bpy.utils.register_class(EasyLog)
    #bpy.types.INFO_HT_header.append(draw_item)
    bpy.utils.register_class(iop_panel)
    bpy.utils.register_class(OBJECT_OT_Trim)
    bpy.utils.register_class(OBJECT_OT_Setin)
    bpy.utils.register_class(OBJECT_OT_addTag)
    bpy.utils.register_class(OBJECT_OT_Setout)
    bpy.utils.register_class(OBJECT_OT_Place)
    bpy.utils.register_class(OBJECT_OT_Back)
    #bpy.utils.register_class(SEQUENCER_OT_createlog)
    #bpy.types.OBJECT_MT_easy_log.append(log_func)
    #bpy.utils.register_class(tags_panel)
    #bpy.types.OBJECT_MT_easy_log.append(wagon_func)
    #bpy.utils.register_class(SEQUENCER_OT_makewagon)
    bpy.utils.register_class(OBJECT_OT_import)


def unregister():
    #bpy.utils.unregister_class(EasyLog)
    #bpy.types.INFO_HT_header.remove(draw_item)  
    bpy.utils.unregister_class(iop_panel)
    bpy.utils.unregister_class(OBJECT_OT_Trim)
    bpy.utils.unregister_class(OBJECT_OT_Setin)
    bpy.utils.register_class(OBJECT_OT_addTag)
    bpy.utils.unregister_class(OBJECT_OT_Setout)
    bpy.utils.unregister_class(OBJECT_OT_Place)
    bpy.utils.unregister_class(OBJECT_OT_Back)
    #bpy.utils.unregister_class(SEQUENCER_OT_createlog)
    #bpy.types.OBJECT_MT_easy_log.remove(log_func)
    #bpy.utils.unregister_class(tags_panel)
    #bpy.types.OBJECT_MT_easy_log.remove(wagon_func)
    #bpy.utils.unregister_class(SEQUENCER_OT_makewagon)
    bpy.utils.unregister_class(OBJECT_OT_import)


if __name__ == "__main__":
    register()

def updateStringParameter(self,context):
    print(self.my_string)
def updateIntParameter(self,context):
    print(self.my_int)
