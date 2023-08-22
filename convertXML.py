# Program to convert an xml
# file to json file
 
# import json module and xmltodict
# module provided by python
import json
import untangle

# open the input xml file and read
# data in form of python dictionary
# using xmltodict module
with open("test.xml") as xml_file:

    globaldata = None
    cameradata = None
    lightdata = []
    rootObject = None
     
    data_dict = untangle.parse(xml_file).children[0]

    #print(data_dict)

    # takes in an xml element (from the untangle library)
    # and removes the inner "v" keys    
    def fixXMLStructure(c):
        temp = c
        for attribs in temp.children:
            if "v" in attribs._attributes.keys():
                temp._attributes[attribs._name] = attribs._attributes["v"]
            else:
                temp._attributes[attribs._name] = attribs._attributes

        temp = temp._attributes
        return temp

    # takes in an xml element (from the untangle library)
    def createPrimitive(c):
        attribs = c._attributes
        primitive = {"type": attribs["name"]}
        for child in c.children:
            if child._name in ["ambient", "diffuse", "specular", "reflective", "transparent"]:
                primitive[child._name] = [child["r"], child["g"], child["b"]]
            else:
                primitive[child._name] = child["v"]
        return primitive

    # takes in an xml element (from the untangle library)     
    def createTransblockGroup(c):
        attribs = c._attributes
        group = {}
        for child in c.children:
            if child._name in ["translate", "rotate", "scale"]:
                group[child._name] = [child["x"], child["y"], child["z"]]
        return group
    
    # this takes in a dict rather than a xml element
    def createCameraData(c):
        camera = c.copy()
        for keyName in camera.keys():
            print(keyName)
            if keyName in ["look", "focus", "up", "position"]:
                subElement = camera[keyName]
                c[keyName] = [subElement["x"], subElement["y"], subElement["z"]]
        return c
    
    # this takes in a dict rather than a xml element
    def fixLightValues(c):
        light = c.copy()
        for keyName in light.keys():
            print(keyName)
            if keyName in ["position", "direction", "up", "function"]:
                subElement = light[keyName]
                c[keyName] = [subElement["x"], subElement["y"], subElement["z"]]
            elif keyName == "color":
                subElement = light[keyName]
                c[keyName] = [subElement["r"], subElement["g"], subElement["b"]]
        return c

    # recurseively goes through each group and child to convert into a dict
    def fixTransblockStructure(c, start):
        temp = c
        for child in temp.children:
            attribs = child._attributes
            #print("child", child)

            if child._name == "transblock":
                start["groups"] = start.get("group", []) + [createTransblockGroup(child)]
                fixTransblockStructure(child, start["groups"][len(start["groups"]) - 1])
            elif "type" not in attribs.keys():
                continue
            elif attribs["type"] == "tree":
                start["groups"] = start.get("group", []) + [{}]
                fixTransblockStructure(child, start["groups"][len(start["groups"]) - 1])
            elif attribs["type"] == "primitive":
                start["primitves"] = start.get("primitve", []) + [createPrimitive(child)]
            
        return start
    
    # Goes through the scenefile and gets data for each part
    # Essentially what happens is we use untangle to get an XML object
    # Then we use the following functions to convert that object to a Dict
    for c in data_dict.children:
        element_name = (c._name).strip()
        fixed_element = fixXMLStructure(c)
        if c._name == "globaldata":
            globaldata = fixed_element
        elif c._name == "cameradata":
            cameradata = fixed_element
            cameradata = createCameraData(cameradata)
        elif c._name == "lightdata":
            lightdata.append(fixed_element)
        elif c._name == "object":
            rootObject = c
            #traverseObjects(rootObject)
            #rootObject = {"group" : rootObject["transblock"]}
            rootObject = fixTransblockStructure(rootObject, {})
    
    print("globaldata", globaldata)
    print("cameradata", cameradata)
    print("~~~~~LIGHTS~~~~~")
    for l in lightdata:
        l = fixLightValues(l)
    lightGroup = {"lights": lightdata}
    print("rootObject", rootObject)


    # final dict of everything together
    scenefile = {"globaldata": globaldata,
                  "cameradata": cameradata, 
                  "groups": [lightGroup] + rootObject["groups"]}
    
    json_data = json.dumps(scenefile)
     
    # Write the json data to output json file
    with open("data2.json", "w") as json_file:
        json_file.write(json_data)
        json_file.close()


    # def traverseObjects(node):
    #     #print(node)
    #     for objs in node.children:
    #         traverseObjects(objs)
    #     node = fixXMLStructure(node)

    # # xml_file.close()
     
    # # generate the object using json.dumps()
    # # corresponding to json data
     
    # json_data = json.dumps(data_dict)
     
    # # Write the json data to output
    # # json file
    # with open("data.json", "w") as json_file:
    #     json_file.write(json_data)
    #     # json_file.close()