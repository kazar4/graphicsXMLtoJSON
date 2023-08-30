import xml.etree.ElementTree as ET
import json
import sys
from os import listdir


def parse_vector(element, *attributes):
    return [float(element.get(attr)) for attr in attributes]

def parse_globaldata(element):
    return {
        "ambientCoeff": float(element.find('ambientcoeff').get('v')),
        "diffuseCoeff": float(element.find('diffusecoeff').get('v')),
        "specularCoeff": float(element.find('specularcoeff').get('v')),
        "transparentCoeff": 1
    }

def parse_cameradata(element):
    return {
        "position": parse_vector(element.find('pos'), 'x', 'y', 'z'),
        "up": parse_vector(element.find('up'), 'x', 'y', 'z'),
        "look": parse_vector(element.find('look'), 'x', 'y', 'z') if element.find('look') is not None else [0, 0, 0],
        "heightAngle": float(element.find('heightangle').get('v'))
    }

def parse_lightdata(element):
    data = {
        "type": element.find('type').get('v') if element.find('type') is not None else "point",
        "color": parse_vector(element.find('color'), 'r', 'g', 'b')
    }
    
    if data["type"] == "directional":
        data["direction"] = parse_vector(element.find('direction'), 'x', 'y', 'z')
    elif data["type"] == "point":
        data["attenuationCoeff"] = [0, 0, 0]
    return data

def parse_object(element):
    groups = []
    if element.get('type') == "tree":
        for child in element:
            if child.tag == 'transblock':
                groups.append(parse_transblock(child))
        return {"groups": groups}
    else:  # primitive
        primitive = {"type": element.get('name')}
        
        optional_fields = [
            ('ambient', 'ambient', ['r', 'g', 'b'], parse_vector),
            ('diffuse', 'diffuse', ['r', 'g', 'b'] , parse_vector),
            ('specular', 'specular', ['r', 'g', 'b'] , parse_vector),
            ('shininess', 'shininess', 'v', float),
            ('reflective', 'reflective', ['r', 'g', 'b'] , parse_vector),
            ('transparent', 'transparent', ['r', 'g', 'b' ] , parse_vector),
            ('blend', 'blend', 'v', float),
            ('textureFile', 'texture', 'file', str),
            ('textureU', 'texture', 'u', float),
            ('textureV', 'texture', 'v', float),
            ('bumpMapFile', 'bumpmap', 'file', str),
            ('bumpMapU', 'bumpmap', 'u', float),
            ('bumpMapV', 'bumpmap', 'v', float),
        ]
        
        for field_name, tag_name, attributes, conversion_func in optional_fields:
            tag_element = element.find(tag_name)
            if tag_element is not None:
                if isinstance(attributes, list):  # Multiple attributes like 'r', 'g', 'b'
                    primitive[field_name] = parse_vector(tag_element, *attributes)
                else:  # Single attribute
                    primitive[field_name] = conversion_func(tag_element.get(attributes))

        return {"primitives": [primitive]}


def parse_transblock(element):
    data = {}
    for child in element:
        if child.tag == "translate":
            data["translate"] = parse_vector(child, 'x', 'y', 'z')
        elif child.tag == "scale":
            data["scale"] = parse_vector(child, 'x', 'y', 'z')
        elif child.tag == "rotate":
            # multiple the x y and z you get by 3.14
            x = float(child.get('x')) * 3.14
            y = float(child.get('y')) * 3.14
            z = float(child.get('z')) * 3.14
            data["rotate"] = [x, y, z]
        elif child.tag == "object":
            data.update(parse_object(child))
    
    return data

def xml_to_json(xml_str):
    root = ET.fromstring(xml_str)
    
    scene = {
        "name": "root",
        "globalData": parse_globaldata(root.find('globaldata')),
        "cameraData": parse_cameradata(root.find('cameradata')),
        "groups": []
    }
    
    # Extract lights first, as they're separate in the JSON structure
    for light in root.findall('lightdata'):
        scene["groups"].append({
            "lights": [parse_lightdata(light)]
        })
    
    scene["groups"].append(parse_object(root.find('object')))

    
    return json.dumps(scene, indent=2)


for file in listdir(sys.argv[1]):
    if file.endswith(".xml"):
        xml_str = open(sys.argv[1] + "/" + file).read()
        with open(sys.argv[2] + "/" + file[:-4] + ".json", "w") as json_file:
            json_file.write(xml_to_json(xml_str))