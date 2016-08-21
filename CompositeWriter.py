import bpy
import bpy.types
import inspect
import json
import math
import mathutils
import os.path
from types import *

image_properties = ["name", "filepath", "filepath_raw", "source", "alpha_mode",  "use_fake_user"]
composite_image_node_properties = [ "frame_duration", "frame_start","use_cyclic","use_auto_refresh", "frame_offset"]
validmembers = ["image","frame_duration", "frame_start","use_cyclic","use_auto_refresh", "frame_offset", "node_tree","alpha","specular_alpha","raytrace_transparency","specular_shader","specular_intensity","specular_hardness","transparency_method","use_transparency","translucency","ambient","emit","use_specular_map","specular_color","diffuse_color", "halo","volume", "diffuse_shader", "tonemap_type","f_stop","source","bokeh","contrast","adaptation","correction","index","use_antialiasing","offset","size",  "use_min", "use_max", "max","min", "threshold_neighbor","use_zbuffer", "master_lift","intensity","blur_max", "highlights_lift","midtones_lift","use_variable_size","use_bokeh","shadows_lift","midtones_end","midtones_start","blue","green","red", "shadows_gain", "midtones_gain", "highlights_gain","use_curved", "master_gain","speed_min","speed_max", "factor", "samples", "master_gamma", "highlights_gamma", "midtones_gamma", "shadows_gamma","hue_interpolation","interpolation","use_gamma_correction","use_relative", "shadows_contrast","operation", "use_antialias_z", "midtones_contrast", "master_saturation", "highlights_saturation", "midtones_saturation", "shadows_saturation", "master_contrast","highlights_contrast", "gain", "gamma","lift", "mapping", "height", "width", "premul", "use_premultiply","fade","angle_offset","streaks", "threshold", "mix","color_ramp", "color_modulation", "iterations","quality", "glare_type","filter_type", "ray_length", "use_projector","sigma_color","sigma_space", "use_jitter", "use_fit", "x", "y","rotation", "mask_type", "filter_type", "use_relative", "size_x","color_mode", "size_y", "use_clamp", "color_hue", "color_saturation", "color_value", "use_alpha", "name", "layer","zoom","spin", "angle", "distance", "center_y", "center_x","use_wrap"]

debugmode = True
def debugPrint(val=None):
    if debugmode and val:
        print(val)

class CompositeWriter():
    def readComp(self, scene):
        mat_value = {}
        mat = { "name" : scene.name, "value": mat_value }
        # materials.append(mat)
        
        if scene.node_tree == None:
            mat["blender_render"] = True
        self.readObjectToDictionary(scene, mat, mat_value)
        return mat_value
    
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
            self.readObjectToDictionary(material, mat, mat_value)
            t = [f for f in materials if f["name"] == material.name]
            if len(t) == 0:
                materials.append(mat)
        return materials

    def readObjectToDictionary(self, material, mat, mat_value):
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
                                debugPrint("found " + member[0])
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
                                elif isinstance(mval, bpy.types.Image):
                                    debugPrint("found an image")
                                    image_data = { }
                                    node[member[0]] = image_data
                                    for imageprop in image_properties:
                                        image_data[imageprop] = getattr(mval, imageprop)
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

    def doesMaterialExistAlready(self, name):
        for item in bpy.data.materials:
            if item.name == name:
                debugPrint("found material")
                return True
        debugPrint("no material found")
        return False

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

    def setupComposite(self, scene, context, presentation_material_animation_points):
        if "composite" in scene:
            composite_settings = scene["composite"]
            if "file" in composite_settings:
                f = open(composite_settings["file"], 'r')
                filecontents = f.read()
                composite_settings = json.loads(filecontents)
            custom_mat = { "name":"composite", "value": composite_settings["composite"] }
            # switch on nodes and get reference
            context.scene.use_nodes = True
            tree = bpy.context.scene.node_tree

            # clear default nodes
            for node in tree.nodes:
                tree.nodes.remove(node)
            self.defineNodeTree(tree, custom_mat, presentation_material_animation_points)

    def hasImage(self, imageName):
        for key in bpy.data.images.keys():
            if key == imageName:
                return True
        return False

    def defineNodeTree(self, node_tree, custom_mat, presentation_material_animation_points):
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
                        if isinstance(newnode, bpy.types.CompositorNodeImage):
                            image_name = node["image"]["name"]
                            _image_properties = node["image"]
                            if self.hasImage(image_name) == False:
                                debugPrint("does not have image " + image_name)
                                bpy.data.images.load(filepath=_image_properties["filepath"])
                            else:
                                debugPrint("has image " + image_name)
                            
                            newnode.image = bpy.data.images[node["image"]["name"]]
                            image_node = newnode.image

                            image_data = node["image"]
                            debugPrint("image properties")
                            for image_prop in image_properties:
                                setattr(image_node, image_prop, image_data[image_prop])

                            debugPrint("composite image node properties")
                            for node_prop in composite_image_node_properties:
                                setattr(newnode, node_prop, node[node_prop])
                        else:
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
                                presentation_material_animation_points.append(point)
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

if __name__ == "__main__":
    ob = CompositeWriter()
    print(ob, "created")