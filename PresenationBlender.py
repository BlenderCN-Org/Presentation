
bl_info = {
    "name": "Presentation Maker",
    "category": "Animation",
}

import math
import mathutils
import bpy
import os.path
import json
import bpy.types
import inspect
from types import *

debugmode = True
def debugPrint(val=None):
    if debugmode and val:
        print(val)
    
validmembers = ["node_tree","alpha","specular_alpha","raytrace_transparency","specular_shader","specular_intensity","specular_hardness","transparency_method","use_transparency","translucency","ambient","emit","use_specular_map","specular_color","diffuse_color", "halo","volume", "diffuse_shader", "tonemap_type","f_stop","source","bokeh","contrast","adaptation","correction","index","use_antialiasing","offset","size",  "use_min", "use_max", "max","min", "threshold_neighbor","use_zbuffer", "master_lift","intensity","blur_max", "highlights_lift","midtones_lift","use_variable_size","use_bokeh","shadows_lift","midtones_end","midtones_start","blue","green","red", "shadows_gain", "midtones_gain", "highlights_gain","use_curved", "master_gain","speed_min","speed_max", "factor", "samples", "master_gamma", "highlights_gamma", "midtones_gamma", "shadows_gamma","hue_interpolation","interpolation","use_gamma_correction","use_relative", "shadows_contrast","operation", "use_antialias_z", "midtones_contrast", "master_saturation", "highlights_saturation", "midtones_saturation", "shadows_saturation", "master_contrast","highlights_contrast", "gain", "gamma","lift", "mapping", "height", "width", "premul", "use_premultiply","fade","angle_offset","streaks", "threshold", "mix","color_ramp", "color_modulation", "iterations","quality", "glare_type","filter_type", "ray_length", "use_projector","sigma_color","sigma_space", "use_jitter", "use_fit", "x", "y","rotation", "mask_type", "filter_type", "use_relative", "size_x","color_mode", "size_y", "use_clamp", "color_hue", "color_saturation", "color_value", "use_alpha", "name", "layer","zoom","spin", "angle", "distance", "center_y", "center_x","use_wrap"]
RENDERSETTINGS = [
        "use_compositing",
        "use_sequencer"]
CYCLESRENDERSETTINGS = ["use_animated_seed",
        "sample_clamp_direct",
        "sample_clamp_indirect",
        "aa_samples",
        "progressive",
        "diffuse_samples",
        "glossy_samples",
        "transmission_samples",
        "ao_samples",
        "mesh_light_samples",
        "subsurface_samples",
        "volume_samples",
        "sampling_pattern",
        "transparent_max_bounces",
        "transparent_min_bounces",
        "use_transparent_shadows",
        "caustics_reflective",
        "caustics_refractive",
        "blur_glossy",
        "max_bounces",
        "min_bounces" ,
        "diffuse_bounces",
        "glossy_bounces",
        "transmission_bounces",
        "volume_bounces"]
               
class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class PresentationBlenderGUI(bpy.types.Panel):
    """Presentation GUI"""
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_context = "objectmode"
    bl_category = "Movie"
    bl_label = "Generate Presentation"
 
    def draw(self, context):
        TheCol = self.layout.column(align=True)
        TheCol.prop(context.scene, "presentation_settings")
        TheCol.operator("object.presentation_blender_maker", text="Update")
        TheCol.operator("object.presentation_blender_mat_comp_reader", text="Read Mat/Comp")


class PresentationBlenderMatCompReader(bpy.types.Operator):
    """Presentation Blender Material Composition"""
    bl_idname = "object.presentation_blender_mat_comp_reader"
    bl_label = "Presentation Material Reader"
    bl_options = {'REGISTER', 'UNDO'}
    
    # total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        # settings = context.scene.presentation_settings
        debugPrint(context.scene.presentation_settings)
        
        try:
            debugPrint("start")
            materials = self.readMats(bpy.data.materials)
            comp = self.readComp(self.context.scene)
            res = { "materials" : materials, "composite": comp }
            text = json.dumps(res, sort_keys=True, indent=4, separators=(',', ': '))
            bpy.context.window_manager.clipboard = text  # now the clipboard content will be string "abc"
            debugPrint("complete")
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")
        #for i in range(self.total):
        #    obj_new = obj.copy()
        #    scene.objects.link(obj_new)

        #    factor = i / self.total
        #    obj_new.location = (obj.location * factor) + (cursor * (1.0 -
        #    factor))

        return {'FINISHED'}
    def readMats(self, _materials):
        materials = []
        node_count = 0
        for material in _materials:
            mat_value = {}
            mat = { "name" : material.name, "value": mat_value }
            materials.append(mat)
            
            if material.node_tree == None:
                mat["blender_render"] = True
            # if material.node_tree != None:
            self.readMaterialsToDictionary(material, mat, mat_value)
            t = [f for f in materials if f["name"] == material.name]
            if len(t) == 0:
                materials.append(mat)
        return materials
    def readComp(self, material):
        mat_value = {}
        mat = { "name" : material.name, "value": mat_value }
        # materials.append(mat)
        
        if material.node_tree == None:
            mat["blender_render"] = True
        self.readMaterialsToDictionary(material, mat, mat_value)
        return mat_value
    def packProperties(self, obj):
        debugPrint("packing properties")
        members = inspect.getmembers(obj)
        result = {}
        for member in members:
            try:
                if isinstance(member[1], int) or isinstance(member[1], float) or isinstance(member[1], bool):
                    result[member[0]] = result[member[1]]
                elif isinstance(member[1], mathutils.Color):
                    result[member[0]] = [f for f in member[1]]
            except Exception as e:
                debugPrint(e)
        return result
        
    def readMaterialsToDictionary(self, material, mat, mat_value):
        node_count = 0
        if material.node_tree == None:
            mat["blender_render"] = True
            members = inspect.getmembers(material)
            for member in members:
                mval = member[1]
                if isinstance(member[1], int) or isinstance(member[1], float) or isinstance(member[1], bool):
                    mat_value[member[0]] = member[1]
                elif isinstance(member[1], mathutils.Color):
                    mat_value[member[0]] = [f for f in member[1]]
                else: # isinstance(mval, bpy.types.MaterialHalo):
                    mat_value[member[0]] = self.packProperties(member[1])
        if material.node_tree != None:
            nodes = []
            nodes_ref = []
            links = []
            mat_value["nodes"] = nodes
            mat_value["links"] = links
            for _node in material.node_tree.nodes:
                inputs = []
                node_name = "node_{}".format(node_count)
                node = {"_type" : _node.bl_idname, "inputs": inputs, "_name" : node_name, "location": [f for f in _node.location] }
                nodes_ref.append({"node": _node, "name": node_name })
                node_count =  node_count + 1
                nodes.append(node)
                members = inspect.getmembers(_node)
                for member in members:
                    if any(member[0] in s for s in validmembers):
                        try:
                            try:
                                mval = member[1]
                                if isinstance(mval, bpy.types.ShaderNodeTree):
                                    debugPrint(member[1].name )
                                    node[member[0]] = member[1].name
                                elif isinstance(mval, bpy.types.CurveMapping):
                                    curvemap = { "data" : [] }
                                    node[member[0]] = curvemap
                                    curves = [curve for curve in mval.curves]
                                    k = 0 
                                    for curve in curves:
                                        curve_data = {"data" :  [] , "index": k}
                                        k = k + 1
                                        points = [f for f in curve.points]
                                        i = 0
                                        for point in points:
                                            point_data = {"index": i}
                                            i = i + 1
                                            point_data["location"] = [point.location[0], point.location[1]]
                                            point_data["handle_type"] = point.handle_type
                                            curve_data["data"].append(point_data)
                                        curvemap["data"].append(curve_data)
                                elif isinstance(mval, bpy.types.ColorRamp):
                                    color_ramp = {"data": [] }
                                    node[member[0]] = color_ramp
                                    elements = [element for element in mval.elements]
                                    for element in elements:
                                        element_data = { "alpha": element.alpha, "position": element.position, "color": [c for c in element.color] }
                                        color_ramp["data"].append(element_data) 
                                elif isinstance(mval, bool) or isinstance(mval,  float) or isinstance(mval,  int) or isinstance(mval, str):
                                    node[member[0]] = member[1]
                                else:
                                    node[member[0]] = [f for f in member[1]]
                            except  Exception as e:
                                debugPrint(e)
                                mval = member[1]
                                if isinstance(mval, bool) or isinstance(mval,  float) or isinstance(mval,  int) or isinstance(mval, list):
                                    node[member[0]] = member[1]
                        except:
                            debugPrint(member)
                for i in range(len(_node.inputs)):
                    input = _node.inputs[i]
                    if hasattr(input, "default_value"):
                        # if hasattr(input.default_value, "data") and input.default_value.data.type == "RGBA":
                        try:
                            try:
                                inputs.append({"index": i, "value": [f for f in input.default_value] })
                            # elif isinstance(input.default_value, float) or isinstance(input.default_value, int) or isinstance(input.default_value, str) or isinstance(input.default_value, bool ):
                            except:
                                inputs.append({"index": i, "value": input.default_value })
                        except:
                            debugPrint("didnt set anything")
            for _link in material.node_tree.links:
                from_ = self.selectNodeName(_link.from_node, nodes_ref)
                to_ = self.selectNodeName(_link.to_node, nodes_ref)
                links.append( { "from": {"port": _link.from_socket.name , "name": from_ }, "to": {"port": _link.to_socket.name , "name": to_ } })
                    
    def selectNodeName(self, target, refs):
        for ndata in refs:
            if ndata["node"] == target:
                return ndata["name"]       
        return None             
                    
        
class PresentationBlenderAnimation(bpy.types.Operator):
    """Presentation Blender Animation"""
    bl_idname = "object.presentation_blender_maker"
    bl_label = "Presentation Maker"
    bl_options = {'REGISTER', 'UNDO'}
    
    presentation_armatures = []
    presentation_objects = []
    presentation_target_bones = []
    presentation_material_animation_points = []
    # total = bpy.props.IntProperty(name="Steps", default=2, min=1, max=100)

    def execute(self, context):
        scene = context.scene
        cursor = scene.cursor_location
        obj = scene.objects.active
        self.context = context
        settings = context.scene.presentation_settings
        self.relativeDirePath = self.fixPath(os.path.dirname(settings))
        debugPrint(context.scene.presentation_settings)
        try:
            self.clearObjects()
        except Exception as e:
            debugPrint(e)
        try:
            f = open(settings, 'r')
            filecontents = f.read()
            
            obj = json.loads(filecontents)
            debugPrint("loaded config json")
            self.processAnimation(obj)
            bpy.ops.file.pack_all()
            bpy.ops.file.unpack_all(method='USE_LOCAL')
        except Exception as e:
            debugPrint("didnt work out") 
            debugPrint(e)
        debugPrint("Executing")
        #for i in range(self.total):
        #    obj_new = obj.copy()
        #    scene.objects.link(obj_new)

        #    factor = i / self.total
        #    obj_new.location = (obj.location * factor) + (cursor * (1.0 -
        #    factor))

        return {'FINISHED'}
    def processAnimation(self, config):
        debugPrint("processing animation")
        self.settings = self.loadSettings(config)
        debugPrint("set settings")
        self.scenes = self.loadSceneConfig(config)
        debugPrint("set scenes config")
        self.createScenes(self.scenes)
        debugPrint("created scenes")
        for scene in self.scenes:
            debugPrint("switching scenes")
            self.switchToScene(scene["name"])
            debugPrint("processing setings")
            self.processSettings(scene)
            self.processWorld(scene)
            self.prolightingProcess(scene)
            debugPrint("start proskies processing")
            self.proskiesProcess(scene)
            self.armatures = self.loadArmaturesConfig(scene)
            newobjects = self.createObjectsUsed(scene)
            self.createStage(scene)
            self.attachGroups(scene)
            for i in range(len(newobjects)):
                newobjects[i]["scene"] = self.scene
                self.presentation_objects.append(newobjects[i])
            self.parentCreatedObjects(scene)
            
            debugPrint("configur armatures")
            self.configureArmature(scene)
            self.processArmatures(scene)
            self.processKeyFrames(scene)
            self.processArmatureFrames(scene)
            self.processMaterialKeyFrames(scene)
        for scene in self.scenes:
            self.switchToScene(scene["name"])
            self.setupComposite(scene)
        
    def parseValue(self, value):
        if isinstance(value, bool) or isinstance(value, float) or isinstance(value, int) or isinstance(value, str):
            try:
                return float(value)
            except:
                try:
                    return int(value)
                except:
                    return value
        return value
    def proskiesProcess(self, scene):
        debugPrint("Pro skies processing")
        if "proskies" in scene:
            if scene["proskies"] == False:
                return
            else:
                debugPrint("Found : Pro skies processing")
                proskies_config = scene["proskies"]
                if "skies" in proskies_config:
                    skies_config = proskies_config["skies"]
                    if "use_pl_skies" in skies_config and skies_config["use_pl_skies"]:
                        debugPrint("Using pl_skies")
                        setattr(bpy.context.scene.world.pl_skies_settings, 'use_pl_skies', True);
                        if "evn_previews" in skies_config:
                            try:
                                setattr(bpy.context.scene.world, "env_previews", skies_config["evn_previews"])
                                debugPrint("set environment preview")
                            except:
                                pass
                        for key in skies_config:
                            val = self.parseValue(skies_config[key])
                            if hasattr(bpy.context.scene.world.pl_skies_settings, key):
                                setattr(bpy.context.scene.world.pl_skies_settings, key , val)   
    def prolightingProcess(self, scene):
        if "prolighting" in scene:
            firefixes = False
            if scene["prolighting"] == False:
                return
            else:
                debugPrint("setup pro lighting ")
                prolighting_config = scene["prolighting"]
                if "light" in prolighting_config:
                    light_config = prolighting_config["light"]
                    debugPrint(light_config)
                    light_key_list = ["use_pl_studio_lights"]
                    if "use_pl_studio_lights" in light_config  and light_config["use_pl_studio_lights"]:
                        firefixes = True
                        for key in light_config:
                            light_key_list.append(key)
                        for key in light_key_list:
                            debugPrint(key)
                            val = self.parseValue(light_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                if "background" in prolighting_config:
                    background_config = prolighting_config["background"]
                    debugPrint(background_config)
                    background_key_list = ["use_pl_studio_background"]
                    if "use_pl_studio_background" in background_config and background_config["use_pl_studio_background"]:
                        firefixes = True
                        for key in background_config:
                            background_key_list.append(key)
                        for key in background_key_list:
                            debugPrint(key)
                            val = self.parseValue(background_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                if "reflections" in prolighting_config:
                    reflections_config = prolighting_config["reflections"]
                    debugPrint(reflections_config)
                    reflections_key_list = ["use_pl_studio_reflections"]
                    if "use_pl_studio_reflections" in reflections_config and reflections_config["use_pl_studio_reflections"]:
                        firefixes = True
                        for key in reflections_config:
                            reflections_key_list.append(key)
                        for key in reflections_key_list:
                            debugPrint(key)
                            val = self.parseValue(reflections_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                if "floor" in prolighting_config :
                    floor_config = prolighting_config["floor"]
                    debugPrint(floor_config)
                    floor_key_list = ["use_pl_studio_floors"]
                    if "use_pl_studio_floors" in floor_config and floor_config["use_pl_studio_floors"]:
                        firefixes = True
                        for key in floor_config:
                            floor_key_list.append(key)
                        for key in floor_key_list:
                            debugPrint(key)
                            val = self.parseValue(floor_config[key])
                            setattr(bpy.context.scene.pl_studio_props, key, val)
                         
                        bpy.ops.scene.pl_studio_floor_apply()
                if firefixes :
                    bpy.ops.scene.pl_studio_fix_warnings(warning_type='background_color')
                    bpy.ops.scene.pl_studio_make_real()


                    
    def setupComposite(self, scene):
        if "composite" in scene:
            composite_settings = scene["composite"]
            if "file" in composite_settings:
                f = open(composite_settings["file"], 'r')
                filecontents = f.read()
                composite_settings = json.loads(filecontents)
            custom_mat = { "name":"composite", "value": composite_settings["composite"] }
            # switch on nodes and get reference
            self.context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree

            # clear default nodes
            for node in tree.nodes:
                tree.nodes.remove(node)
            self.defineNodeTree(tree, custom_mat)
    def createScenes(self, scenes):
        running = True
        while len(bpy.data.scenes) > 1:
            running = False
            debugPrint("deleting scene")
            res = bpy.ops.scene.delete()
            debugPrint("deleted scene")
            if res.pop() != "CANCELLED":
                running = True
        for scene in scenes:
            bpy.ops.scene.new(type='NEW')
            cloneScene = bpy.context.scene
            cloneScene.name = scene["name"]
    def switchToScene(self, name):
        bpy.data.screens['Default'].scene = bpy.data.scenes[name]
        bpy.context.screen.scene=bpy.data.scenes[name]
        self.scene = bpy.context.screen.scene
    def processWorld(self, scene):
        if "world" in scene:
            debugPrint("set the world ")
            worldName = scene["world"]
            if self.hasWorldsByName(worldName):
                world = self.getWorldByName(worldName)
                self.context.scene.world = world

    def processSettings(self, scene):
        debugPrint("Process settings")
        if "RenderEngine" in scene:
            self.context.scene.render.engine = scene["RenderEngine"]
        elif "RenderEngine" in self.settings:
            debugPrint("set render engine")
            self.context.scene.render.engine = self.settings["RenderEngine"]
        
        if "Device" in self.settings:
            debugPrint("device in settings")
            self.context.scene.cycles.device = self.settings["Device"]
        if "resolution_x" in self.settings:
            bpy.context.scene.render.resolution_x = float(self.settings["resolution_x"])
        else:
            bpy.context.scene.render.resolution_x = 1280
        
        if "resolution_y" in self.settings:
            bpy.context.scene.render.resolution_y = float(self.settings["resolution_y"])
        else:
            bpy.context.scene.render.resolution_y = 720
        if "filepath" in self.settings and self.settings["filepath"]:
            bpy.context.scene.render.filepath = os.path.relpath(self.settings["filepath"]);
            
        bpy.context.scene.render.tile_y = 256
        bpy.context.scene.render.tile_x = 256
        
        if "fps" in self.settings:
            debugPrint("fps in settings")
            bpy.context.scene.render.fps = float(self.settings["fps"])
            bpy.context.scene.render.fps_base = 1


        bpy.context.scene.render.resolution_percentage = 100
        if "samples" in self.settings:
            debugPrint("samples in settings")
            bpy.context.scene.cycles.samples = float(self.settings["samples"])
        else :
            bpy.context.scene.cycles.samples = 200
        bpy.context.scene.cycles.preview_samples = 0

        for _setting in RENDERSETTINGS:
            if _setting in self.settings and hasattr(bpy.context.scene.render, _setting):
                setattr(bpy.context.scene.render, _setting, self.settings[_setting])
        for _setting in CYCLESRENDERSETTINGS:
            if _setting in self.settings and hasattr(bpy.context.scene.cycles, _setting):
                setattr(bpy.context.scene.cycles, _setting, self.settings[_setting])
        
        if "FrameEnd" in self.settings:
            debugPrint("frameend in settings")
            bpy.context.scene.frame_end = self.settings["FrameEnd"]
        
        if "FrameStart" in self.settings:
            debugPrint("framestart in settings")
            bpy.context.scene.frame_start = self.settings["FrameStart"]
        if "Objects" in self.settings:
            debugPrint("objects in settings")
            objectssettings = self.settings["Objects"]
            
            if "File" in objectssettings:
                obj_location = self.fixPath(os.path.join(self.relativeDirePath, objectssettings["File"])) 
                with bpy.data.libraries.load(obj_location) as (data_from, data_to):
                    data_to.groups = [name for name in data_from.groups if not self.hasGroupByName(name)]
            
            if "Files" in objectssettings:
                for i in range(len(objectssettings["Files"])):
                    objlocation = self.fixPath(os.path.join(self.relativeDirePath, objectssettings["Files"][i]))
                    debugPrint(objlocation);
                    with bpy.data.libraries.load(objlocation) as (data_from, data_to):
                        data_to.groups = [name for name in data_from.groups if not self.hasGroupByName(name)]
                        

        if "Materials" in self.settings:
            debugPrint("setup materials")
            matsettings = self.settings["Materials"]
            mat_location = matsettings["File"]
             
            for i in range(len(matsettings["Names"])):
                matname = matsettings["Names"][i]
                opath = self.fixPath(os.path.join(self.relativeDirePath,  mat_location))
                debugPrint(opath)
                with bpy.data.libraries.load(opath) as (data_from, data_to):
                    data_to.materials = [name for name in data_from.materials if not self.hasMaterialByName(name)]
                    data_to.worlds = [name for name in data_from.worlds if not self.hasWorldsByName(name)]
            
            if "Materials" in matsettings:
                custom_materials = matsettings["Materials"]
                debugPrint("creating custom materials")
                for custom_mat in custom_materials:
                    debugPrint("create material")
                    if "name" in custom_mat:
                        self.defineMaterial(custom_mat)
                    elif "file" in custom_mat:
                        f = open(custom_mat["file"], 'r')
                        filecontents = f.read()
                        composite_settings = json.loads(filecontents)
                        if "materials" in composite_settings:
                            for material in composite_settings["materials"]:
                                self.defineMaterial(material)
                            
    def defineMaterial(self,  custom_mat):
        if "name" in custom_mat:
            mat_name = custom_mat["name"]
            if self.doesMaterialExistAlready(mat_name):
                return
            debugPrint("create material called {}".format(mat_name))
            mat = bpy.data.materials.new(name=mat_name)
            if mat == None:
                raise ValueError("no material created")
            if "blender_render" in custom_mat:
                self.defineBlenderRenderMaterial(mat, custom_mat["value"])
            else:
                mat.use_nodes = True
                # clear all nodes to start clean
                for node in mat.node_tree.nodes:
                    mat.node_tree.nodes.remove(node)
                self.defineNodeTree(mat.node_tree, custom_mat)
    def defineBlenderRenderMaterial(self, material, custom_mat_value):
        debugPrint("define blender render material")
        for property in custom_mat_value.keys():
            debugPrint("property {}".format(property))
            try:
                if isinstance(custom_mat_value[property], bool) or isinstance(custom_mat_value[property], float) or isinstance(custom_mat_value[property], int) or isinstance(custom_mat_value[property], str):
                    setattr(material, property, custom_mat_value[property])
                elif isinstance(custom_mat_value[property], list):
                    setattr(material, property,  [f for f in custom_mat_value[property]])
                else:
                    mat_prop = getattr(material, property)
                    for p in custom_mat_value[property]:
                        if hasattr(mat_prop, p):
                            setattr(mat_prop, p, mat_prop[p])
            except Exception as e:
                debugPrint(e)
    def doesMaterialExistAlready(self, name):
        for item in bpy.data.materials:
            if item.name == name:
                debugPrint("found material")
                return True
        debugPrint("no material found")
        return False
        
    def defineNodeTree(self, node_tree, custom_mat):
        debugPrint("create material")
        if "name" in custom_mat:
            debugPrint("created new material")
            if "value" in custom_mat:
                material_definition = custom_mat["value"]
                debugPrint("material definition found")
                node_tree_dict = {}
                if "nodes" in material_definition:
                    debugPrint("creating nodes in material")
                    node_definitions = material_definition["nodes"]
                    for node in node_definitions:
                        debugPrint("creating {}".format(node["_type"]))
                        newnode = node_tree.nodes.new(type=node["_type"])
                        if "location" in node:
                            newnode.location = node["location"]
                        debugPrint("created type")
                        
                        node_tree_dict[node["_name"]] = newnode
                        members = inspect.getmembers(newnode)
                        
                        for member in members:
                            if any(member[0] in s for s in validmembers):
                                debugPrint("found {}".format(member[0]))
                                if member[0] in node:
                                    try:
                                        if member[0] == "node_tree":
                                            debugPrint("setting shader node tree " + node[member[0]])
                                            #setattr(newnode, member[0], bpy.data.node_groups[node[member[0]]])
                                            newnode.node_tree = bpy.data.node_groups[node[member[0]]]
                                            debugPrint("set node groups")
                                        elif isinstance(member[1], bpy.types.CurveMapping) and member[1] != None:
                                            debugPrint(member)
                                            debugPrint("curve mapping {} ".format(member[0]))
                                            curvemap = getattr(newnode, member[0])
                                            curves =  node[member[0]]["data"]
                                            i = -1
                                            for curve in curves:
                                                i = i + 1
                                                debugPrint("curves")
                                                debugPrint(curve)
                                                j = -1 
                                                for point in curve["data"]:
                                                    j = j + 1
                                                    debugPrint("points {}".format( len (curvemap.curves[i].points)))
                                                    if len (curvemap.curves[i].points) <= j :
                                                        debugPrint("adding new curve")
                                                        res = curvemap.curves[i].points.new(point["location"][0], point["location"][1])
                                                        res.handle_type = point["handle_type"]
                                                        debugPrint("added new curve")
                                                    else:
                                                        debugPrint("update existing curve")
                                                        curvemap.curves[i].points[j].location = point["location"]
                                                        curvemap.curves[i].points[j].handle_type = point["handle_type"]
                                        elif isinstance(member[1], bpy.types.ColorRamp):
                                            color_ramp_node = getattr(newnode, member[0])
                                            elements =  node[member[0]]["data"]
                                            j = -1
                                            for element in elements:
                                                j = j + 1
                                                if len(color_ramp_node.elements) <= j:
                                                    res = color_ramp_node.elements.new(element["position"])
                                                    res.alpha = element["alpha"]
                                                    res.color = element["color"]
                                                else:
                                                    res = color_ramp_node.elements[j]
                                                    res.alpha = element["alpha"]
                                                    res.color = element["color"]
                                                    res.position = element["position"]
                                                # element_data = { "alpha": element.alpha, "position": element.position, "color": [c for c in element.color] }
                                                # color_ramp["data"].append(element_data)
                                        else:
                                            setattr(newnode, member[0], node[member[0]])
                                    except Exception as e:
                                        debugPrint(e)
                                        debugPrint("couldnt set propertY")
                        if "inputs" in node:
                            debugPrint("input defintions in node")
                            for inputs in node["inputs"]:
                                debugPrint("setting node's input")
                                newnode.inputs[inputs["index"]].default_value = inputs["value"]
                        if "_animation" in node:
                            _animationPoints = node["_animation"]
                            for _animationPoint in _animationPoints:
                                point = { 
                                            "material": custom_mat["name"], 
                                            "name" : _animationPoint["name"], 
                                            "index": _animationPoint["index"], 
                                            "node" : newnode 
                                            }
                                self.presentation_material_animation_points.append(point)
                if "links" in material_definition:
                    debugPrint("links in material definition found")
                    link_definitions = material_definition["links"]
                    debugPrint("link definitions")
                    links = node_tree.links
                    for link in link_definitions:
                        debugPrint("link defintions ")
                        from_node = link["from"]["name"]
                        from_port = link["from"]["port"]
                        to_node = link["to"]["name"]
                        to_port = link["to"]["port"]
                        debugPrint("from_node : {}".format(from_node))
                        debugPrint("from_port : {}".format(from_port))
                        debugPrint("to_node : {}".format(to_node))
                        debugPrint("to_port : {}".format(to_port))
                        output = node_tree_dict[from_node].outputs[from_port]
                        input = node_tree_dict[to_node].inputs[to_port]
                        links.new(output, input)
                        print
                        
            else : 
                debugPrint("no material definition found")
                raise ValueError("no material definition found")
        else:
            raise ValueError("no material name found")
    def hasGroupByName(self, name):
        debugPrint("has group by name")
        for i in range(len(bpy.data.groups)):
            group = bpy.data.groups[i]
            if group.name == name:
                debugPrint("found group")
                return True
        debugPrint("group not found")
        return False
    def getGroupByName(self, name):
        for i in range(len(bpy.data.groups)):
            group = bpy.data.groups[i]
            if group.name == name:
                return group
        return False

    def duplicateGroup(self, group):
        debugPrint("duplicating group")
        root = self.getObject(group)
        print ("looked for root " + group.name)
        bpy.ops.object.empty_add(type="PLAIN_AXES")
        empty = self.context.active_object
        if root is None: 
            raise ValueError("There was no group found.")
            return empty
        else:
            debugPrint("has root")
            for i in range(len(root.children)):
                # root.children[i].name
                if root.children[i].name.startswith("Root"):
                    debugPrint("__")
                else :
                    bpy.ops.object.select_all(action="DESELECT")
                    debugPrint("deselected all")
                    root.children[i].select = True
                    debugPrint("select child root")
                    debugPrint(root.children[i].name)
                    # bpy.ops.object.duplicate_move()
                    temp = self.duplicateObject(self.context.scene,root.children[i].name, root.children[i], root)
                    root.children[i].select = False
                    debugPrint(temp.name)
                    debugPrint("duplicated the object")
                    temp.parent = empty
                    debugPrint("empty parent then temp")
                    bpy.ops.object.select_all(action="DESELECT")
                    debugPrint("last deselect")
        return empty
        
    def duplicateObject(self, scene, name, copyobj, root_parent):
 
        # Create new mesh
        debugPrint("create new mesh")
        if copyobj.type == 'LAMP':
            mesh = bpy.data.lamps.new(name, 'AREA')
        else: 
            mesh = bpy.data.meshes.new(name)
 
        # Create new object associated with the mesh
        debugPrint("create new object associated with the mesh")
        ob_new = bpy.data.objects.new(name, mesh)
 
        # Copy data block from the old object into the new object
        debugPrint("copy data block from the old object into the new object")
        if copyobj.data != None:
            ob_new.data = copyobj.data.copy() 
        # ob_new.scale = copyobj.scale.copy()
        debugPrint(root_parent.matrix_world.translation);
        # ob_new.rotation_euler = copyobj.rotation_euler.copy()
        # ob_new.location = copyobj.location.copy() - root_parent.location.copy()
        ob_new.matrix_world = copyobj.matrix_world.copy();
 
        # Link new object to the given scene and select it
        debugPrint("link new object to the given scene and select it")
        scene.objects.link(ob_new)
        ob_new.select = True
        self.context.scene.update();
        if len(copyobj.children) > 0:
            for i in range(len(copyobj.children)):
                obj_ject = self.duplicateObject(scene, copyobj.children[i].name , copyobj.children[i], copyobj)
                obj_ject.parent = ob_new
                # obj_ject.location = obj_ject.location - ob_new.location
 
        return ob_new
    def getObject(self, group):
        return self.selectObject(group.objects,"Root")

    def selectObject(self, array, name):
        for i in range(len(array)):
            temp = array[i]
            debugPrint(temp.name)
            if temp.name.startswith(name):
                return temp
        for i in range(len(array)):
            temp = array[i]
            if len(temp.children) > 0:
                res = self.selectObject(temp.children, name)
                if res != None:
                    return res
        return None

    def hasMaterialByName(self, name):
        for i in range(len(bpy.data.materials)):
            material = bpy.data.materials[i]
            if material.name == name:
                return True
        return False
    def hasWorldsByName(self, name):
        for i in range(len(bpy.data.worlds)):
            environment = bpy.data.worlds[i]
            if environment.name == name:
                return True
        return False

    def getWorldByName(self,name):
        for i in range(len(bpy.data.worlds)):
            world = bpy.data.worlds[i]
            if world.name == name:
                return world
        return None
    def getBlenderObjectByName(self, name):
        for i in range(len(bpy.data.objects)):
            material = bpy.data.objects[i]
            if material.name == name:
                return material
        return None
        
    def getMaterialByName(self,name):
        for i in range(len(bpy.data.materials)):
            material = bpy.data.materials[i]
            if material.name == name:
                return material
        return None

    def processArmatures(self, scene):
        debugPrint("process armatures")
        #self.presentation_armatures.append({"bone_chains":bone_chains,"armature"
        #: armature, "rig":rig})
        debugPrint("setting object mode");
        # bpy.ops.object.mode_set(mode='OBJECT')
        debugPrint("set object mode");
        if len(self.presentation_armatures) > 0 :
            bpy.ops.object.mode_set(mode='POSE')
            debugPrint(len(self.presentation_armatures))
            for i in range(len(self.presentation_armatures)):
                bone_chains = self.presentation_armatures[i]["bone_chains"]
                armature = self.presentation_armatures[i]["armature"]
                config = self.presentation_armatures[i]["configuration"]
                debugPrint("armature chains")
                debugPrint("len(self.presentation_armatures)")
                chains = self.armatures[i]["chain"]
                debugPrint("has armature chains")
                rig = self.presentation_armatures[i]["rig"]
                scn = self.context.scene
                debugPrint("setting active to rig")
                scn.objects.active = rig
                self.arrangeArmature(bone_chains, config, chains)
            bpy.ops.object.mode_set(mode='OBJECT')
           

    def arrangeArmature(self, bone_chains,  config, chains):
        debugPrint("setting to POSE mode")
        debugPrint("arrange armature") 
        arrange = "spiral"
        if "arrange" in config:
            arrange = config["arrange"]

        count = 0
        thresh = 0
        debugPrint("for each bone in chain")
        if arrange == "spiral":
            for j in range(len(bone_chains)):
                bone_chain = bone_chains[j]
                chain = chains[j]
                if count == thresh:
                    rig.pose.bones["bone.chain." + chain].rotation_quaternion[3] = 1
                    count = 0
                    thresh = thresh + 1
                count = count + 1

    def configureArmature(self, scene):
        debugPrint("armatures")
        
        if self.armatures:
            debugPrint("foreach armature config")
            for i in range(len(self.armatures)):
                armatureConfig = self.armatures[i]
                debugPrint("new armature()")
                armature = bpy.data.armatures.new(armatureConfig["name"])
                debugPrint("new rig()")
                rig = bpy.data.objects.new(armatureConfig["name"], armature) # "Rig$" + 
                if "origin" in armatureConfig:
                    rig.location = [armatureConfig["origin"]["x"],armatureConfig["origin"]["y"],armatureConfig["origin"]["z"]]
                else :
                    rig.location = [0,0,0]
                if "rotation" in armatureConfig:
                    rig.rotation_euler.x = armatureConfig["rotation"]["x"]
                    rig.rotation_euler.y = armatureConfig["rotation"]["y"]
                    rig.rotation_euler.z = armatureConfig["rotation"]["z"]
                    
                if "parent"  in armatureConfig:
                    a_parent = self.getObjectByName(armatureConfig["parent"])
                    if a_parent == 0:
                        raise ValueError("Cant find the armatures parent " + armatureConfig["parent"])
                    else :
                         rig.parent = a_parent["object"];
                    
                rig.show_x_ray = True
                self.presentation_objects.append({"scene": self.scene,  "name" : armatureConfig["name"], "type" : "rig",  "rig" : rig, "mesh": rig.data, "object": rig });
                armature.draw_type = "STICK"
                armature.show_names = True
                scn = self.context.scene
                scn.objects.link(rig)
                scn.objects.active = rig
                debugPrint("update scene")
                scn.update()
                
                bpy.ops.object.mode_set(mode='EDIT')
                chains = armatureConfig["chain"]
                bone_chains = []
                grid = {"x":1,"y":1,"z":1}
                if "grid" in armatureConfig:
                    grid = armatureConfig["grid"]
                x_grid = grid["x"]
                chain_positions = []
                if "chain_positions" in armatureConfig:
                    chain_positions = armatureConfig["chain_positions"] 
                last_bone = False
                info_chains = [];
                for j  in range(len(chains)):
                    chain = chains[j]
                    bone_chain = armature.edit_bones.new("bone.chain." + chain)
                    bone_chains.append(bone_chain)
                    chain_position = self.getBoneChain(chain_positions, chain)
                    if chain_position == None :
                        bone_chain.head = (j * x_grid,0,0)
                        bone_chain.tail = ((j + 1) * x_grid,0,0)
                    else:
                        bone_chain.head = (chain_position["head"]["x"], chain_position["head"]["y"], chain_position["head"]["z"])
                        bone_chain.tail = (chain_position["tail"]["x"], chain_position["tail"]["y"], chain_position["tail"]["z"])
                    info_chains.append({ "name" : chain, "chain" : bone_chain})
                    if last_bone:
                        bone_chain.parent = last_bone
                        bone_chain.use_connect = True
                    last_bone = bone_chain
                if "ik_bones" in armatureConfig:
                    debugPrint("has ik_bones");
                    ik_bones = armatureConfig["ik_bones"]
                    debugPrint(len(ik_bones))
                    for y in range(len(ik_bones)):
                        ik_bone = ik_bones[y]
                        bone = self.getBoneChain(info_chains, ik_bone["connectTo"]);
                        the_bone = bone["chain"]
                        new_ik_bone = armature.edit_bones.new(ik_bone["id"])
                        if "head" in ik_bone:
                            new_ik_bone.head = mathutils.Vector(((ik_bone["head"]["x"], ik_bone["head"]["y"], ik_bone["head"]["z"])))
                        else:
                            new_ik_bone.head = the_bone.tail;
                            
                        if "tail" in ik_bone:
                            new_ik_bone.tail = mathutils.Vector(((ik_bone["tail"]["x"], ik_bone["tail"]["y"], ik_bone["tail"]["z"])))
                        else:
                            new_ik_bone.tail = the_bone.tail + mathutils.Vector((0,0,0.6));
                        bpy.ops.object.mode_set(mode='OBJECT')
                        bpy.ops.object.select_all(action='DESELECT') 
                        bpy.ops.object.mode_set(mode='POSE')       
                        the_bone.select = True
                        the_bone = rig.pose.bones["bone.chain." + ik_bone["connectTo"]].bone;
                        armature.bones.active = the_bone
                        bpy.ops.pose.constraint_add(type='IK')
                        self.context.selected_pose_bones[0].constraints["IK"].target = rig
                        self.context.selected_pose_bones[0].constraints["IK"].subtarget = ik_bone["id"]
                        if "chain_length" in ik_bone:
                            self.context.selected_pose_bones[0].constraints["IK"].chain_count = ik_bone["chain_length"]
                        bpy.ops.object.mode_set(mode='OBJECT')
                        self.presentation_target_bones.append({"pose_bone": rig.pose.bones[ik_bone["id"]], "armature":armature, "rig" : rig, "name": ik_bone["id"] })       

                #connect bones to targets
                bpy.ops.object.mode_set(mode='OBJECT')
                bpy.ops.object.select_all(action='DESELECT')
                debugPrint("Object mode")
                for j in range(len(chains)):
                    chain = chains[j]
                    mdObj = self.getObjectByName(chain)
                    debugPrint("Deselect all objects")
                    bpy.ops.object.select_all(action='DESELECT')
                    debugPrint("Deselected all objects")
                    mdObj["object"].select = True
                    mdObj["object"].location = bone_chains[j].head + rig.location
                    debugPrint("Pose mode")
                    if "forceFit" in armatureConfig and armatureConfig["forceFit"] == "True":
                        debugPrint("Force fit")
                        mdObj["object"].dimensions[0] = grid["x"]
                    bpy.ops.object.mode_set(mode='POSE')
                    armature.bones.active = rig.pose.bones["bone.chain." + chain].bone
                    debugPrint("setting parent to bone")
                    bpy.ops.object.parent_set(type='BONE')
                    debugPrint("deselecting")
                    
                    bpy.ops.object.mode_set(mode='OBJECT')
                    mdObj["object"].select = False
                self.presentation_armatures.append({"bone_chains":bone_chains,"armature" : armature, "rig":rig, "configuration": armatureConfig})
                bpy.ops.object.mode_set(mode='OBJECT')
                
        
    def getBoneChain(self, bones, name):
        for k in range(len(bones)):
            bone  = bones[k]
            if bone["name"] == name:
                return bone
        return None

    def processKeyFrames(self, scene):
        debugPrint("process key frames")
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        keyframes = scene["keyframes"]
        for k in range(len(keyframes)):
            keyframe = keyframes[k]
            #self.setFrame(keyframe)
            self.setObjectsProperty(keyframe)
            debugPrint("finished setting properties")
    def processArmatureFrames(self, scene):
        debugPrint("process armature frames")
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        if "armatureframes" in scene:
            keyframes = scene["armatureframes"]
            for k in range(len(keyframes)):
                keyframe = keyframes[k]
                self.setArmatureObjectsProperties(keyframe)
    def processMaterialKeyFrames(self, scene):
        if "materialframes" in scene:
            materialframes = scene["materialframes"]
            for keyframe in materialframes:
                self.setMaterialObjectProperties(keyframe)
    def setObjectsProperty(self, keyframe):
        debugPrint("set objects property")
        objects = keyframe["objects"]
        for i in range(len(objects)):
            obj = self.getObjectByName(objects[i]["name"])
            if obj == 0:
                debugPrint("object not found, thats not good!")
            else :
                if ("frame" in keyframe):
                    debugPrint()
                else:
                    debugPrint("no frame in key frame ")
                    debugPrint(keyframe)
                self.setObjectProperty(obj, objects[i], keyframe["frame"])
                debugPrint("set object  properties")
    def setArmatureObjectsProperties(self, keyframe):
        debugPrint("set armature objects frames")
        objects = keyframe["objects"]
        
        for i in range(len(objects)):
            debugPrint("getting " + objects[i]["name"]);
            obj = self.getBoneByName(objects[i]["name"])
            
            if obj == 0:
                debugPrint("bone not found, thats not good! " +  objects[i]["name"])
                # setArmatureObjectProperties
                debugPrint("get object by name : " + objects[i]["name"])
                obj = self.getObjectByName(objects[i]["name"])
                if obj == 0:
                    debugPrint("still cant find " + objects[i]["name"])
                else:
                    self.setObjectProperty(obj, objects[i], keyframe["frame"])
            else:
                debugPrint("found : " + objects[i]["name"]);
                bpy.ops.object.mode_set(mode='OBJECT')
                debugPrint("set mode to object")
                bpy.ops.object.select_all(action='DESELECT')
                debugPrint("deselected")
                rig = obj["rig"]
                debugPrint("got rig")
                armature = obj["armature"]
                rig.select = True;
                bpy.ops.object.mode_set(mode='POSE')       
                the_bone = rig.pose.bones[obj["name"]].bone;
                armature.bones.active = the_bone
                self.setArmatureObjectProperties({"object": rig.pose.bones[obj["name"]]}, objects[i], keyframe["frame"])
                debugPrint("set armature properties")
                bpy.ops.object.mode_set(mode='OBJECT')
    def getMaterialObject(self, name, material):
        debugPrint(self.presentation_material_animation_points)
        for mat_Target in self.presentation_material_animation_points:
            if mat_Target["name"] == name and mat_Target["material"] == material:
                return mat_Target
        return None
    def setMaterialObjectProperties(self, keyframe):
        objects = keyframe["objects"] 
        for _obj in objects:
            obj = self.getMaterialObject(_obj["name"], _obj["material"])
            if obj == None:
                raise ValueError("material not found")
            mat_node = obj["node"]
            mat_node_input = mat_node.inputs[obj["index"]]
            setattr(mat_node_input, "default_value", _obj["value"])
            mat_node_input.keyframe_insert(data_path="default_value",frame=keyframe["frame"])
                    
    def parentCreatedObjects(self, scene):
        debugPrint("Parent created objects")
        # for i in range(len(self.scenes)):
        debugPrint("scene parent ")
        #       objs = self.scenes[i]["objects"]
        objs = scene["objects"]
        for j in range(len(objs)):
            obj = objs[j]
            debugPrint("scene parent  > OBJECTS")
            debugPrint("here")
            debugPrint(obj)
            createdObject = self.getObjectByName(obj["name"])
            debugPrint("got created object")
            if "parent" in obj:
                debugPrint("has a parent : " + obj["parent"])
            if createdObject and "parent" in obj:
                parentObj = self.getObjectByName(obj["parent"])
                if parentObj:
                    self.parentObject(parentObj, createdObject)

    def parentObject(self, b, a):
        debugPrint("Parent object a to b")
        a["object"].parent = b["object"]
        #bpy.ops.object.select_all(action='DESELECT')
        #a["object"].select = True
        #b["object"].select = True
        #bpy.context.scene.objects.active = a["object"]
        #bpy.ops.object.parent_set()
    def deselectAll(self):
        debugPrint("object mode")
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active = None
    def setArmatureObjectProperties(self, obj, config, frame):
        debugPrint("setting armature object properties")
        if "position" in config and config["position"]:
            position = config["position"]
            debugPrint("setting armture object position")
            self.translation(obj, position, True, frame)
        if "scale" in config and config["scale"]:
            scale = config["scale"]
            debugPrint("setting armture object scale")
            self.scale(obj, scale, True, frame)
        if "rotation" in config and config["rotation"]:
            rotation = config["rotation"]
            debugPrint("setting armture object rotation")
            self.rotation(obj, rotation , True, frame);
        
    def setObjectProperty(self, obj, config, frame):
        debugPrint(obj);
        debugPrint("obj type : " + obj["type"])
        debugPrint(type(obj["object"]))
        if "position" in config:
            pos = config["position"]
            if "x" in pos:
                obj["object"].location.x = float(pos["x"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=0)
            if "y" in pos:
                obj["object"].location.y = float(pos["y"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=1)
            if "z" in pos:
                obj["object"].location.z = float(pos["z"])
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=2)
   
        if "scale" in config and config["scale"]: 
            scale = config["scale"] 
            if "x" in scale:
                obj["object"].scale.x = scale["x"]
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                
            if "y" in scale:
                obj["object"].scale.y = float(scale["y"])
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                
            if "z" in scale:
                obj["object"].scale.z = float(scale["z"])
                obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)
        if "position_rel" in config and config["position_rel"]:
            debugPrint("position relative to ")
            target = config["position_rel"]["target"]
            target_obj = self.getObjectByName(target)
            distance = 7
            if "distance" in config["position_rel"]:
                distance = config["position_rel"]["distance"]
            if "offset" in config["position_rel"]:
                offset = config["position_rel"]["offset"]
            else :
                offset = {"x":0,"y":0,"z":0}
            if config["position_rel"]["position"] == "front":
                debugPrint("matrix world to euler")
                direction = target_obj["object"].matrix_world.to_euler()
                direction = mathutils.Vector(direction)
                direction.normalize()
                debugPrint("direction normalized")
                debugPrint(direction)
                
                location = target_obj["object"].matrix_world * mathutils.Vector((0,-distance ,0)) #target_obj["object"].matrix_world.translation
                
                t = location #+ (7 * direction)
                obj["object"].location.x = t[0] + offset["x"]
                obj["object"].location.y = t[1] + offset["y"]
                obj["object"].location.z = t[2] + offset["z"]
                debugPrint("Set location")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
                debugPrint("set keyframe ")
            elif config["position_rel"]["position"] == "top":
                debugPrint("location + dimension")
                l = target_obj["object"].matrix_world * mathutils.Vector((0,0,distance)) 
                obj["object"].location.x = l[0] + offset["x"]
                obj["object"].location.y = l[1] + offset["y"]
                obj["object"].location.z = l[2] + offset["z"]
                debugPrint("insert key frame")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
            elif config["position_rel"]["position"] == "center":
                debugPrint("location + dimension")
                l = target_obj["object"].matrix_world.translation
                obj["object"].location.x = l[0] 
                obj["object"].location.y = l[1] 
                obj["object"].location.z = l[2]
                debugPrint("insert key frame")
                obj["object"].keyframe_insert(data_path="location", frame=frame)
            
        if "children" in config :
            debugPrint("children")        
            for childConfig in config["children"]:
                debugPrint("Value : %s" % obj.keys())
                if "name" in childConfig:
                    name = childConfig["name"]
                    selectedObj = self.selectObject(obj["object"].children, name)
                    debugPrint("attempted object")
                    if selectedObj != None:
                        tempObject = {}
                        tempObject["object"] = selectedObj
                        debugPrint("got an object")
                        self.applyConfig(tempObject, childConfig, frame)

        if "target" in config and config["target"]: 
            debugPrint("track target")
            target = config["target"]
            target_obj = self.getObjectByName(target)
            bpy.ops.object.select_all(action='DESELECT')
            obj["object"].select = True
            constraint = obj["object"].constraints.new(type='TRACK_TO')
            constraint.target = target_obj["object"]
            constraint.track_axis = "TRACK_NEGATIVE_Z"
            constraint.up_axis = "UP_Y"

        if "rotation" in config and config["rotation"]: 
            rotation = config["rotation"] 
            self.rotation(obj, rotation, True, frame)

        if "scale" in config and config["scale"]:
            scale = config["scale"]
            self.scale(obj, scale, True, frame)
        if config:
            self.applyConfig(obj, config, frame)
            
    def applyConfig(self, tempObject, childConfig, frame):
        debugPrint("-----------------------")
        debugPrint("apply config")
        debugPrint("------------rotation-----------")
        if "rotation" in childConfig:
            self.rotation(tempObject , childConfig["rotation"],True,frame)
        
        debugPrint("------------scale-----------")
        if "scale" in childConfig:
            self.scale(tempObject , childConfig["scale"],True,frame)
        debugPrint("----------translate-------------")
        if "translate" in childConfig:
            self.translation(tempObject , childConfig["translate"],True,frame)
        
        debugPrint("----------particles-------------")
        if "particles" in childConfig:
            self.particles(tempObject, childConfig["particles"], True, frame)
            
        debugPrint("----------dynamic paint-------------")
        if "dynamic_paint" in childConfig:
            self.dynamic_paint(tempObject, childConfig["dynamic_paint"], True, frame)
        debugPrint("----------dynamic brush-------------")
        if "dynamic_brush" in childConfig:
            self.dynamic_brush(tempObject, childConfig["dynamic_brush"], True, frame)
        debugPrint("----------collision-------------")
        if "collision" in childConfig:
            self.collision(tempObject, childConfig["collision"], True, frame)
        debugPrint("----------follow path-------------")
        if "follow_path" in childConfig:
            self.follow_path(tempObject, childConfig["follow_path"], True , frame)
        debugPrint("----------track to-------------")
        if "track_to" in childConfig:
            self.track_to(tempObject, childConfig["track_to"], True, frame)
        debugPrint("----------limit rotation-------------")
        if "limit_rotation" in childConfig:
            self.limit_rotation(tempObject, childConfig["limit_rotation"], True, frame)
        if "lens" in childConfig:
            tempObject["object"].data.lens  = float(childConfig["lens"])
            tempObject["object"].data.keyframe_insert(data_path="lens", frame=frame)
        if "sensor_width" in childConfig:
            tempObject["object"].data.sensor_width  = float(childConfig["sensor_width"])
            tempObject["object"].data.keyframe_insert(data_path="sensor_width", frame=frame)
        if "dof_object" in childConfig:
            target = self.getObjectByName(childConfig["dof_object"])
            if target != None:
                tempObject["object"].data.dof_object = target["object"]
        if "gpu_dof" in childConfig:
            gpu_dof = childConfig["gpu_dof"]
            if "fstop" in gpu_dof:
                tempObject["object"].data.gpu_dof.fstop = gpu_dof["fstop"]
            if "fstop_anim" in gpu_dof:
                tempObject["object"].data.gpu_dof.keyframe_insert(data_path="fstop", frame=frame)
            if "use_high_quality" in gpu_dof:
                tempObject["object"].data.gpu_dof.use_high_quality = gpu_dof["use_high_quality"]
        if "cycles" in childConfig:
            cycles = childConfig["cycles"]
            if "aperture_type" in cycles:
                tempObject["object"].data.cycles.aperture_type = cycles["aperture_type"]
            if "aperture_size" in cycles:
                tempObject["object"].data.cycles.aperture_size = cycles["aperture_size"]
            if "aperture_size_anim" in cycles:
                tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_size", frame=frame)
            if "aperture_fstop" in cycles:
                tempObject["object"].data.cycles.aperture_fstop = cycles["aperture_fstop"]
            if "aperture_fstop_anim" in cycles:
                tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_fstop", frame=frame)
            if "aperture_blades" in cycles:
                tempObject["object"].data.cycles.aperture_blades = cycles["aperture_blades"]
            if "aperture_blades_anim" in cycles:
                tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_blades", frame=frame)
            if "aperture_rotation" in cycles:
                tempObject["object"].data.cycles.aperture_rotation = cycles["aperture_rotation"]
            if "aperture_rotation_anim" in cycles:
                tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_rotation", frame=frame)
            if "aperture_ratio" in cycles:
                tempObject["object"].data.cycles.aperture_ratio = cycles["aperture_ratio"]
            if "aperture_ratio_anim" in cycles:
                tempObject["object"].data.cycles.keyframe_insert(data_path="aperture_ratio", frame=frame)
        debugPrint("-======completed applying config====-")

    def limit_rotation(self, obj, config, keyframe, frame):
        debugPrint("limit rotation")
        meshobject = obj["object"]
        cns = meshobject.constraints.new('LIMIT_ROTATION') 
        if "use_limit_x" in config:
            cns.use_limit_x = self.str2bool(config["use_limit_x"])
        if "use_limit_y" in config:
            cns.use_limit_y = self.str2bool(config["use_limit_y"])
        if "use_limit_z" in config:
            cns.use_limit_z = self.str2bool(config["use_limit_z"])
        if "owner_space" in config:
            cns.owner_space = config["owner_space"]
    def track_to(self, obj, config, keyframe, frame):
        debugPrint("track to")
        meshobject = obj["object"]
        if "target" in config:
            debugPrint("getting track to target" + (config["target"]))
            targetObj = self.getBlenderObjectByName(config["target"])
            debugPrint("got track to target")
            if targetObj != None:
                debugPrint("found track to target")
                cns = meshobject.constraints.new("TRACK_TO")
                cns.target = targetObj
                if "track_axis" in config:
                    cns.track_axis = config["track_axis"]
                if "up_axis" in config:
                    cns.up_axis = config["up_axis"]
            else: 
                raise ValueError("Cant find the target " + config["target"])
                
                
    def follow_path(self, obj, config, keyframe, frame):
        debugPrint("follow path")
        meshobject = obj["object"]
        if "target" in config:
            targetObj = self.getBlenderObjectByName(config["target"])
            if targetObj != None:
                cns = meshobject .constraints.new('FOLLOW_PATH')
                cns.target = targetObj
                cns.use_curve_follow = True
                if "use_curve_follow" in config:
                    cns.use_curve_follow = self.str2bool(config["use_curve_follow"])
                cns.use_curve_radius = True
                if "use_curve_radius" in config:
                    cns.use_curve_radius = self.str2bool(config["use_curve_radius"])
                
                cns.use_fixed_location = False    
                if "use_curve_radius" in config:
                    cns.use_fixed_location = self.str2bool(config["use_fixed_location"])
                
                cns.forward_axis = 'FORWARD_Y'
                if "forward_axis" in config:
                    cns.forward_axis = config["forward_axis"]
                    
                cns.up_axis = 'UP_Z'
                if "up_axis" in config:
                    cns.up_axis = config["up_axis"]
    def collision(self, obj, config, keyframe , frame):
        debugPrint("adding collision")
        bpy.context.scene.objects.active = obj["object"]
        paintlayer = bpy.context.scene.objects.active
        bpy.ops.object.modifier_add(type="COLLISION")
        settings = paintlayer.modifiers["Collision"].settings
        if "use_particle_kill" in config:
            settings.use_particle_kill = self.str2bool(config["use_particle_kill"])
    def dynamic_brush(self, obj , configs , keyframe ,  frame):
        debugPrint("creating dynamic paint brush")
        bpy.context.scene.objects.active = obj["object"]
        paintlayer = bpy.context.scene.objects.active
        bpy.ops.object.modifier_add(type="DYNAMIC_PAINT")
        config = configs[0]
        bpy.ops.dpaint.type_toggle(type="BRUSH")
        settings = paintlayer.modifiers["Dynamic Paint"].brush_settings
        if "paint_source" in config:
            settings.paint_source = config["paint_source"]
        if "particle_system" in config:
            system = obj["particle_systems"][config["particle_system"]]
            settings.particle_system = system
        if "solid_radius" in config:
            settings.solid_radius = config["solid_radius"]
        if "smooth_radius" in config:
            settings.smooth_radius = config["smooth_radius"]
        if "use_particle_radius" in config:
            settings.use_particle_radius = self.str2bool(config["use_particle_radius"])
    def str2bool(self, v):
        if isinstance(v, bool):
            return v
        return v.lower() in ("yes", "true", "t", "1")    
    def dynamic_paint(self, obj , config, keyframe , frame):
        debugPrint("creating dynamic paint")
        bpy.context.scene.objects.active = obj["object"]
        paintlayer = bpy.context.scene.objects.active
        bpy.ops.object.modifier_add(type="DYNAMIC_PAINT")
        
        bpy.ops.dpaint.type_toggle(type="CANVAS")
        settings = paintlayer.modifiers["Dynamic Paint"].canvas_settings
        debugPrint(settings.canvas_surfaces)
        canvas_surface = settings.canvas_surfaces[-1]
        if "surface_type" in config:
            canvas_surface.surface_type = config["surface_type"]
        if "use_dissolve" in config:
            canvas_surface.use_dissolve = bool(config["use_dissolve"])
        if "dissolve_speed" in config and canvas_surface.use_dissolve:
            canvas_surface.dissolve_speed = int(config["dissolve_speed"])
        if "frame_end" in config:
            canvas_surface.frame_end = int(config["frame_end"])
        if "frame_start" in config:
            canvas_surface.frame_start = int(config["frame_start"])
            
            

    def particles( self, obj , configs, keframe , frame):
        debugPrint("creating particles")
        bpy.context.scene.objects.active = obj["object"]
        emitter = bpy.context.scene.objects.active
        for i in range(len(configs)):
            config = configs[i]
            bpy.ops.object.particle_system_add()    
            psys1 = emitter.particle_systems[-1]
            pset1 = psys1.settings
            if "particle_systems" in obj:
                obj["particle_systems"].append(psys1)
            else:
                obj["particle_systems"] = [psys1]
            # Emission
            if "system" in config:
                pset1.name = config["system"]
            else:
                pset1.name = 'ParticleSettings_Gen'
            if "frame_end" in config:
                pset1.frame_end = int(config["frame_end"])
            if "frame_start" in config:
                pset1.frame_start = int(config["frame_start"])
            if "lifetime" in config:
                pset1.lifetime = int(config["lifetime"])
            else:
                pset1.lifetime = 50
            if "lifetime_random" in config:    
                pset1.lifetime_random = float(config["lifetime_random"])
            if "emit_from" in config:  
                pset1.emit_from = config["emit_from"]
            if "emit_from" in config:
                pset1.emit_from = bool(config["use_render_emitter"])
            if "count" in config:
                pset1.count = int(config["count"])
            # Velocity
            if "normal_factor" in config:
                pset1.normal_factor = float(config["normal_factor"])
            # Physics
            pset1.physics_type = 'NEWTON'
            if "mass" in config:
                pset1.mass = float(config["mass"])
            if "particle_size" in config:
                pset1.particle_size = float(config["particle_size"])
            if "use_multiply_size_mass" in config:
                pset1.use_multiply_size_mass = bool(config["use_multiply_size_mass"])
                # Effector weights
                ew = pset1.effector_weights
            if "gravity" in config:
                ew.gravity = float(config["gravity"])
            if "wind" in config:
                ew.wind = float(config["wind"])
            
                # Children
            if "child_nbr" in config:
                pset1.child_nbr = int(config["child_nbr"])
            if "rendered_child_count" in config:            
                pset1.rendered_child_count = int(config["rendered_child_count"])
            if "child_type" in config:
                pset1.child_type = config["child_type"]
            
                # Display and render
            if "draw_percentage" in config:
                pset1.draw_percentage = int(config["draw_percentage"])
            if "draw_method" in config:            
                pset1.draw_method = config["draw_method"]
            if "material" in config:
                pset1.material = int(config["material"])
            if "particle_size" in config:
                pset1.particle_size = float(config["particle_size"])    
            if "render_type" in config:
                pset1.render_type = config["render_type"]
            if "dupli_object" in config:
                ot_targ = self.getObjectByName(config["dupli_object"])
                if ot_targ != None:
                    pset1.dupli_object = ot_targ["object"]
            if "dupli_group" in config:
                #group = self.getGroupByName(config["dupli_group"])
                pset1.dupli_group = bpy.data.groups[config["dupli_group"]]
                
            if "render_step" in config:    
                pset1.render_step = config["render_step"]
                  
    def translation(self, obj, pos, keyframe, frame):
        if pos == None:
                return
        if "x" in pos:
            obj["object"].location.x = float(pos["x"])
            if keyframe:
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=0)
        if "y" in pos:
            obj["object"].location.y = float(pos["y"])
            if keyframe:
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=1)
        if "z" in pos:
            obj["object"].location.z = float(pos["z"])
            if keyframe:
                obj["object"].keyframe_insert(data_path="location", frame=frame, index=2)

    def scale(self, obj, scale, keyframe, frame):
            if scale == None:
                return
            if "x" in scale:
                debugPrint(scale["x"])
                obj["object"].scale.x = (scale["x"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=0)
                
            if "y" in scale:
                obj["object"].scale.y = (scale["y"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=1)
                
            if "z" in scale:
                obj["object"].scale.z = (scale["z"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="scale", frame=frame, index=2)

    def rotation(self, obj, rotation, keyframe, frame):
            debugPrint("rotation")
            if rotation == None:
                return
            if "x" in rotation:
                debugPrint(rotation["x"])
                obj["object"].rotation_euler.x = math.radians(rotation["x"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=0)
                
            if "y" in rotation:
                obj["object"].rotation_euler.y = math.radians(rotation["y"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=1)
                
            if "z" in rotation:
                obj["object"].rotation_euler.z = math.radians(rotation["z"])
                if keyframe:
                    obj["object"].keyframe_insert(data_path="rotation_euler", frame=frame, index=2)
                           
    def getObjectByName(self, name):
        for i in range(len(self.presentation_objects)):
            obj = self.presentation_objects[i]
            if "name" in obj:
                if obj["name"] == name and obj["scene"] == self.scene:
                    return obj
        for obj in bpy.data.objects:
            if obj.name == name:
                newobject = { "name" : name, "object" : obj }
                self.presentation_objects.append(newobject)
                return newobject
        return 0
    def getBoneByName(self, name):
        for i in range(len(self.presentation_target_bones)):
            obj = self.presentation_target_bones[i]
            if "name" in obj:
                if obj["name"] == name:
                    return obj
        return 0
    
    def searchForObject(self, name, root):
        if root == None:
            objects = self.context.scene.obects
        if name.find("#") == -1:
            obj_name = name.split("#")[0]
            if root.name == obj_name:
                v = "#";
                v.join(name.split("#")[1:])
                return self.searchForObject(v, root)
            
        elif name == root.name:
            return root
                     
        for i in range(len(root.children)):
            res = self.searchForObject(name, root.children[i])
            if res != None:
                return res
        return None

    def setFrame(self, keyframe):
        self.context.scene.frame_current = keyframe["frame"]    
    def createStage(self, scene):
        debugPrint("create stage")
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        #     if "name" in scene:
        #         if scene["name"] in bpy.data.scenes:
        #             bpy.data.screens['Default'].scene = bpy.data.scenes[scene["name"]]
        #             bpy.context.screen.scene=bpy.data.scenes[scene["name"]]
        #         else: 
        #             raise("no scene named {}".format(scene["name"]))
        #     else:
        #         raise("name not attached to scene")
        if "stage" in scene:
            stageConfig = scene["stage"]
            if "File" in stageConfig:
                opath = stageConfig["File"]
                if "Group" in stageConfig:
                    if not self.hasGroupByName(stageConfig["Group"]):
                        with bpy.data.libraries.load(opath) as (data_from, data_to):
                            data_to.groups = [stageConfig["Group"]]
                    group = bpy.data.groups[stageConfig["Group"]]
                    for j in range(len(group.objects)):
                        obj = group.objects[j]
                        debugPrint("stage: add object")
                        o = bpy.ops.object.add_named(name=obj.name)
                        self.context.active_object.location.x = 0
                        self.context.active_object.location.y = 0
                        self.context.active_object.location.z = 0
        debugPrint("created stage")

    def attachGroups(self, scene):
        if "groups" in scene:
            groups = scene["groups"]
            if groups != None:
                for groupData in groups:
                    file = groupData["file"]
                    name = groupData["name"]
                    with bpy.data.libraries.load(file) as (df, dt):
                        dt.groups = [name]
                    group = bpy.data.groups[name]
                    instance = bpy.data.objects.new("dupli_group", None)
                    instance.dupli_type = "GROUP"
                    instance.dupli_group = group
                    self.context.scene.objects.link(instance)
                    obj = { "object" : instance }
                    keyframe = True
                    frame = 1
                    if "position" in groupData:
                        pos = groupData["position"]
                        self.translation(obj, pos, keyframe, frame)
                    if "scale" in groupData:
                        pos = groupData["scale"]
                        self.scale(obj, pos, keyframe, frame)
                    if "rotation" in groupData:
                        pos = groupData["rotation"]
                        self.rotation(obj, pos, keyframe, frame)
                    
                    
    def createObjectsUsed(self, scene):
        objects = []
        objectnames = []
        # for i in range(len(self.scenes)):
        #     scene = self.scenes[i]
        keyframes = scene["keyframes"]
        for k in range(len(keyframes)):
            debugPrint("keyframe s" )
            debugPrint(len(keyframes));
            keyframe = keyframes[k]
            debugPrint("keyframe #" );
            keyframe_objects = keyframe["objects"]
            debugPrint("for each keyframe_obect")
            for j in range(len(keyframe_objects)):
                obj = keyframe_objects[j]
                debugPrint("get name keyframe_obect")
                count = objectnames.count(obj["name"])
                debugPrint("got name " + obj["name"])
                debugPrint("count : " + str(count))
                if count == 0:
                    debugPrint("appending object name")
                    objectnames.append(obj["name"])
                    debugPrint("create object")
                    newobj = self.createObject(obj, scene["objects"])
                    if newobj == None:
                        raise ValueError('new object has value of None')
                    debugPrint("created the object")
                    objects.append(newobj)
                    debugPrint("appended object to list")
        debugPrint("created objectes used array")
        return objects

    def createObject(self, obj, scene_objects):
        debugPrint("create object")
        for i in range(len(scene_objects)):
            so = scene_objects[i]
            if so["name"] == obj["name"]:
                res = self.createObjectWithConfig(so)
                res["name"] = obj["name"]
                return res

    def createObjectWithConfig(self, scene_object_config):
        debugPrint("Create object with configuration")
        result = {}
        if "type" in scene_object_config:
            debugPrint(scene_object_config["type"])
            result["type"] = scene_object_config["type"]
        if(scene_object_config["type"] == "cube"):
            bpy.ops.mesh.primitive_cube_add(radius=1, location=(0, 0, 0))
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
        elif scene_object_config["type"] == "custom":
            if "name" in scene_object_config:
                group = self.getGroupByName(scene_object_config["group"])
                if group:
                    res = self.duplicateGroup(group)
                    result["object"] = res
                    result["mesh"] = res.data
        elif scene_object_config["type"] == "path":
            pathobject = self.path(scene_object_config);
            result["object"] = pathobject["object"]
            result["mesh"] = pathobject["mesh"]                
        elif scene_object_config["type"] == "circle":
            bpy.ops.curve.primitive_bezier_circle_add()
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
        elif scene_object_config["type"] == "camera":
            bpy.ops.object.camera_add()
            result["object"] = self.context.active_object
            result["object"].data.clip_end = 10000
        elif scene_object_config["type"] == "plane":
            bpy.ops.mesh.primitive_plane_add(radius=1,location=(0,0,0))
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
        elif scene_object_config["type"] == "empty":
            bpy.ops.object.empty_add(type="PLAIN_AXES")
            result["object"] = self.context.active_object
        elif scene_object_config["type"] == "image":
            bpy.ops.import_image.to_plane(
                files=[{"name":scene_object_config["fileName"], "name":scene_object_config["fileName"]}], 
                directory= scene_object_config["directory"], 
                filter_image=True, 
                filter_movie=True,
                filter_glob="", 
                relative=False)
            result["object"] = self.context.active_object
            result["mesh"] = self.context.active_object.data
            if "fuzzy" in scene_object_config:
                result["fuzzy"] = scene_object_config["fuzzy"]
                result["config"] = scene_object_config
            if "dim_width" in scene_object_config:
                self.context.active_object.dimensions.x = scene_object_config["dim_width"]
                bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
            if "dim_height" in scene_object_config:
                self.context.active_object.dimensions.y = scene_object_config["dim_height"]
                bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
                
        elif scene_object_config["type"] == "lamp":
            light = "POINT"
            if "light" in scene_object_config:
                light = scene_object_config["light"]
            bpy.ops.object.lamp_add(type=light)
            result["object"] = self.context.active_object
            if "strength" in scene_object_config:
                strength = scene_object_config["strength"]
                debugPrint("setting strength")
                debugPrint(strength)
                if result["object"].data and result["object"].data.node_tree:
                    result["object"].data.node_tree.nodes["Emission"].inputs[1].default_value = strength
        elif scene_object_config["type"] == "text":
            bpy.ops.object.text_add()
            debugPrint("added a text object")
            result["text"] = True
            result["object"] = self.context.active_object
            if "value" in scene_object_config:
                result["object"].data.body = scene_object_config["value"]
            result["mesh"] = self.context.active_object.data
            
            if "extrude" in scene_object_config and scene_object_config["extrude"]:
                result["object"].data.extrude = scene_object_config["extrude"]
                
            if "align" in scene_object_config and scene_object_config["align"]:
                result["object"].data.align = scene_object_config["align"]
            if "size" in scene_object_config:
                result["object"].data.size = scene_object_config["size"]
            if "font" in scene_object_config:
                try:
                    loaded = self.ensureFontLoaded(scene_object_config["font"])
                    if loaded: 
                        font = self.getFont(scene_object_config["font"])
                        debugPrint("got font " + scene_object_config["font"])
                        if font != 0:
                            result["object"].data.font = font
                except:
                    debugPrint("couldnt find font")
            if "dim_width" in scene_object_config:
                result["object"].data.text_boxes[0].width = scene_object_config["dim_width"]
            if "dim_height" in scene_object_config:
                result["object"].data.text_boxes[0].height = scene_object_config["dim_height"]
            # bpy.ops.object.convert(target="MESH")
            # bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS')

        if "scale" in scene_object_config and scene_object_config["scale"] and not isinstance(scene_object_config["scale"], int) and not isinstance(scene_object_config["scale"], float):
            scale = scene_object_config["scale"]
            self.scale(result, scale, False, 0)
            bpy.ops.object.transform_apply(location=False, rotation=False, scale= True)

        if "rotation" in scene_object_config and not isinstance(scene_object_config["rotation"], int)and not isinstance(scene_object_config["rotation"], float):
            debugPrint("roation {}".format(scene_object_config["rotation"]))
            self.rotation(result, scene_object_config["rotation"], False, 0)
            bpy.ops.object.transform_apply(location=False, rotation=True, scale= False)
        
        
        if "material" in scene_object_config and scene_object_config["material"]:
            if self.hasMaterialByName(scene_object_config["material"]):
                material = self.getMaterialByName(scene_object_config["material"])
                debugPrint("append material " + scene_object_config["material"])
                result["object"].data.materials.append(material)
        
        if "object" in result:
            result["object"].name = scene_object_config["name"]

        return result

    def optimalFit(self, obj, h, w):
        debugPrint("optimal fit")
        obj.data.size = .01
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
        _h = obj.dimensions[0]
        _w = obj.dimensions[1]
        _size = obj.data.size
        _step = 3
        prev_high_score = w * h
        prev_low_score = 0
        prev_low_size = 0
        prev_high_size = 10
        newsize = 5
        down = False;
        lastdirection = -1
        for i in range(1, 5):
            obj.data.size = newsize
            score = self.calcScore(obj, h , w)
            
            obj.data.size = (prev_high_size + newsize) / 2
            high_score = self.calcScore(obj, h, w)
            
            obj.data.size = (newsize + prev_low_size) / 2
            low_score = self.calcScore(obj, h, w)
            
            if high_score < low_score: # closer to desired value
                prev_low_size = obj.data.size
            else:
                prev_high_size = obj.data.size
                
            newsize = (prev_high_size + prev_low_size) / 2
            print(newsize)
        obj.data.size = newsize      
        # print("size {}, score {}".format(prev_low_size, prev_low_score))  
    def calcScore(self, obj, h, w):
        bpy.ops.wm.redraw_timer(type='DRAW', iterations=1) 
        _h = obj.dimensions[0]
        _w = obj.dimensions[1]
        hh = _h-h
        hh = hh * hh
        ww = _w-w
        ww = ww * ww
        score = ww + hh
        return score
    def path(self, config):
        debugPrint("----path-----")
        x = 0
        y = 0
        z = 0
        if "position" in config:
            pconfig = config["position"]
            if "x" in pconfig:
                x = int(pconfig["x"])
            if "y" in pconfig:
                y = int(pconfig["y"])
            if "z" in pconfig:
                z = int(pconfig["z"])
        debugPrint("create new curve")    
        curvename = config["name"]
        debugPrint(curvename)    
        curvedata = bpy.data.curves.new(name=curvename, type='CURVE') 
        objectdata = bpy.data.objects.new(curvename, curvedata)  
        objectdata.location = (x,y,z) #object origin  
        bpy.context.scene.objects.link(objectdata)   
        
        # Set path data
        curvedata.dimensions = '3D'
        if "hooks" in config:
            for k in range(len(config["hooks"])):
                debugPrint("add hook")
                hookConfig = config["hooks"][k];
                debugPrint("hookConfig");
                #create modifiers & set Parent Object
                hookname = hookConfig["hook"]+"_"+str(hookConfig["index"])+"_"+config["name"]
                debugPrint("hook name : " + hookname);
                objectdata.modifiers.new(hookname, type='HOOK')
                debugPrint("added modifier")
                hookObj = bpy.data.objects[hookConfig["hook"]]; #self.getObjectByName(hookConfig["hook"]); 
                debugPrint(hookObj);
                objectdata.modifiers[hookname].object = hookObj
                debugPrint("modifier object set")

        curvedata.use_path = True
        if "use_path" in config:
            debugPrint("set use_path" + config["use_path"])
            temp = self.str2bool(config["use_path"])
            curvedata.use_path = temp
            debugPrint("use path set")
        
        debugPrint("use path follow")    
        curvedata.use_path_follow = True
        if "use_path_follow" in config:
            debugPrint("use_path_follow")
            curvedata.use_path_follow = self.str2bool(config["use_path_follow"])
        
        if "twist_mode" in config:
            debugPrint("twist_mode")
            curvedata.twist_mode = config["twist_mode"]
            
        debugPrint("use path_duration")  
        curvedata.path_duration = 100
        if "path_duration" in config:
            debugPrint("path_duration")
            curvedata.path_duration = int(config["path_duration"])
        
        debugPrint("use path_animation") 
        if "path_animation" in config:
            debugPrint("path_animation")
            for num in range(len(config["path_animation"])):
                path_anim_config = config["path_animation"][num]
                curvedata.eval_time = int(path_anim_config["eval_time"])
                path_anim_frame = int(path_anim_config["frame"])
                curvedata.keyframe_insert(data_path="eval_time", frame=path_anim_frame)  
        
    
        curvetype = "POLY"
        if "curvetype" in config:
            curvetype = config["curvetype"]
        polyline = curvedata.splines.new(curvetype)  
        polyline.use_cyclic_u = False
        if "use_cyclic_u" in config:
            debugPrint("use_cyclic_u")
            polyline.use_cyclic_u = self.str2bool(config["use_cyclic_u"])
            
        config["radius_interpolation"] = 'BSPLINE'
        if "radius_interpolation" in config:
            polyline.radius_interpolation = config[ "radius_interpolation"]
    
        polyline.use_endpoint_u = False
        if "use_endpoint_u" in config:
            debugPrint("use_endpoint_u")
            polyline.use_endpoint_u = self.str2bool(config["use_endpoint_u"])
            
        if "bevel_object" in config:
            bevel_object = bpy.data.objects[config["bevel_object"]]
            curvedata.bevel_object = bevel_object
            
        if "taper_object" in config:
            taper_object = bpy.data.objects[config["taper_object"]]
            curvedata.taper_object = taper_object
                
        debugPrint("creating points")
        if "points" in config:
            cList = config["points"]
            debugPrint(str(len(cList)))
            polyline.points.add(len(cList)-1)
            for num in range(len(cList)):  
                x, y, z, w = cList[num]
                polyline.order_u = 4
                if "order_u" in config:
                    polyline.points[num].order_u = int(config["order_u"])
                polyline.points[num].co = (x, y, z, w)
        if "hooks" in config:
            for k in range(len(config["hooks"])):
                debugPrint("hooking up hooks");
                hookConfig = config["hooks"][k]
                hookname = hookConfig["hook"]+"_"+str(hookConfig["index"])+"_"+config["name"]
                index =  int(hookConfig["index"])
                point = polyline.points[index];
                debugPrint("point ");
                debugPrint(point);
                self.deselectAll();
                hookObj = bpy.data.objects[hookConfig["hook"]]
                hookObj.select= True;
                objectdata.select = True;
                bpy.context.scene.objects.active = objectdata
                debugPrint("object data selected ");
                point.select = True;
                objectdata.select = True;
                bpy.ops.object.mode_set(mode='EDIT'); 
                                #select point
                debugPrint("assigning");
                bpy.ops.object.hook_assign(modifier=hookname);
                point.select = False;
                bpy.ops.object.mode_set(mode='OBJECT'); 
                debugPrint("assigning");
                
        return { "object": objectdata, "mesh": curvedata}

    def getFont(self, fontname):
        fonts = bpy.data.fonts
        for i in range(len(fonts)):
            font = fonts[i]
            debugPrint(font.name.lower())
            if font.filepath.lower() == self.getFontPath(fontname).lower():
                return font
        return 0
    def fixPath(self, _path):
        if os.path.sep == ("\\"):
            return _path
        return _path.replace("\\",  "/")
    
    def getFontPath(self, fontname):
        debugPrint("get font paths")
        fontlocation = "c:\\Windows\\Fonts\\"
        if "fonts" in self.settings:
            fontlocation = self.fixPath(os.path.join(self.relativeDirePath, self.settings["fonts"]))
        debugPrint("font location = " + fontlocation)
        fontpath = (os.path.join(fontlocation , fontname + ".ttf"))
        debugPrint(fontpath)
        if os.path.isfile(os.path.join(fontlocation , fontname + ".ttf")): 
            
            return fontpath
        return 0

    def ensureFontLoaded(self, fontname):
        fonts = bpy.data.fonts
        for i in range(len(fonts)):
            font = fonts[i]
            if font.name.lower() == fontname.lower():
                return True
        
        fontlocation = self.getFontPath(fontname)
        if os.path.isfile(fontlocation): 
            bpy.data.fonts.load(fontlocation)
            return True
        return False

    def loadSceneConfig(self, config):
        return config["scenes"]
    def loadArmaturesConfig(self,config):
        debugPrint("Load armatures config")
        if "armatures" in config:
            return config["armatures"]
        return None

    def loadSettings(self, config):
        return config["settings"]

    def clearObjects(self):
        del self.presentation_objects[:]
        del self.presentation_armatures[:]
        del self.presentation_target_bones[:]
        del self.presentation_material_animation_points[:]
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action = 'SELECT')
        bpy.ops.object.delete(use_global=False)
        for item in bpy.data.meshes:
            bpy.data.meshes.remove(item)
        for item in bpy.data.armatures:
            bpy.data.armatures.remove(item)
        for item in bpy.data.cameras:
            bpy.data.cameras.remove(item)
        for item in bpy.data.curves:
            bpy.data.curves.remove(item)
        


def menu_func(self, context):
    self.layout.operator(PresentationBlenderAnimation.bl_idname)
    self.layout.operator(PresentationBlenderMatCompReader.bl_idname)

# store keymaps here to access after registration
# addon_keymaps = []
def register():
    bpy.utils.register_class(PresentationBlenderAnimation)
    bpy.utils.register_class(PresentationBlenderMatCompReader)
    bpy.utils.register_class(PresentationBlenderGUI)
    bpy.types.Scene.presentation_settings = bpy.props.StringProperty \
      (name = "Movie settings",
        subtype = "FILE_PATH",
        description = "JSON description of the movie to generate")
    bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    #wm = bpy.context.window_manager
    #km = wm.keyconfigs.addon.keymaps.new(name='Object Mode',
    #space_type='EMPTY')
    #kmi = km.keymap_items.new(ObjectCursorArray.bl_idname, 'SPACE', 'PRESS',
    #ctrl=True, shift=True)
    #kmi.properties.total = 4
    #addon_keymaps.append((km, kmi))
def unregister():
    bpy.utils.unregister_class(PresentationBlenderAnimation)
    del bpy.types.Scene.presentation_settings
    bpy.utils.unregister_class(PresentationBlenderMatCompReader)
    bpy.utils.unregister_class(PresentationBlenderGUI)
    bpy.types.VIEW3D_MT_object.remove(menu_func)

    # handle the keymap
    #for km, kmi in addon_keymaps:
    #    km.keymap_items.remove(kmi)
    #addon_keymaps.clear()
if __name__ == "__main__":
    register()