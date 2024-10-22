import struct
import os
import json

START_OP = "01040400000000000000000000000000"
POLY_OP = "011580C8000000000000000000000000"
END_OP = "00000000"
MAT_CONST = "09400000001A"
ROM_POL_OFFSET = int("0x2000010", 0)

def float_to_hex(a_float):
    return hex(struct.unpack('>I', struct.pack('<f', float(a_float)))[0])

def open_obj(a_path):
    in_file = open(a_path)
    in_text = in_file.read()
    in_text = in_text.replace(f"\r", "")
    in_file.close()
    return in_text

def get_vertices(an_obj):
    lines = an_obj.split("\n")
    vertex_list = []
    for line in lines:
        if len(line) > 2:
            if line[0] == "v" and line[1] == " ":
                vtx_list = []
                floats = line.split(" ")
                counter = 0
                for float in floats:
                    counter += 1
                    if float != "v":
                        if counter != 3:
                            vtx_list.append(float)
                        else:
                            if "-" in float:
                                vtx_list.append(float.replace("-", ""))
                            else:
                                vtx_list.append("-" + float)
                vertex_list.append(vtx_list)
    return vertex_list

def verts_to_ascii(vtx_list):
    ascii_list = []
    for vtx in vtx_list:
        running = ""
        for pos in vtx:
            hex = float_to_hex(pos)
            hex = hex.replace("0x", "")
            hex = hex.upper()
            while len(hex) < 8:
                hex = "0" + hex
            running += hex
        ascii_list.append(running)
    return ascii_list

def get_ascii_verts(an_obj):
    vert_list = get_vertices(an_obj)
    return verts_to_ascii(vert_list)

def get_faces(an_obj):
    lines = an_obj.split("\n")
    face_list = []
    material = MAT_CONST + "8046"
    for line in lines:
        if len(line) > 2:
            if line[0] == "u":
                material = MAT_CONST + line.split(" ")[1]
                continue
            if line[0] == "f" and line[1] == " ":
                face = []
                group_list = line.split(" ")
                for group in group_list:
                    if group != "f":
                        face.append(group.split("/")[0])
                if len(group_list) == 4:
                    face.append(group_list[3].split("/")[0])
                face_list.append(face)
                face_list.append([material])
    for face in face_list:
        if len(face) == 4:
            three = face[2]
            four = face[3]
            face[2] = four
            face[3] = three
    return face_list

def compile_model(face_list, vert_list):
    compiled_model = ""
    compiled_mats = ""
    for face in face_list:
        counter = 0
        if len(face) == 1:
            compiled_mats += face[0]
            continue
        compiled_model += START_OP
        for vert_index in face:
            counter += 1
            compiled_model += vert_list[int(vert_index) - 1]
            if counter == 2:
                compiled_model += POLY_OP
    compiled_model += END_OP
    return [compiled_model, compiled_mats]

def convert_obj(in_obj):
    verts = get_ascii_verts(in_obj)
    faces = get_faces(in_obj)
    return compile_model(faces, verts)

def stf_to_file(out_stf, label):
    model_label = "./" + label + ".stfmdl"
    mat_label = "./" + label + ".stfmat"
    if os.path.exists(model_label):
        os.remove(model_label)
    mdl = open(model_label, "x")
    mdl.write(out_stf[0])
    mdl.close()
    if os.path.exists(mat_label):
        os.remove(mat_label)
    mat = open(mat_label, "x")
    mat.write(out_stf[1])
    mat.close()

def swap_endian(address):
    new_address = ""
    address = address.replace("0x", "")
    i = 0
    while i < len(address):
        if i == 0 and len(address) % 2 != 0:
            new_address += "0" + address[0]
            i += 1
            continue
        else:
            new_address = address[i] + address[i+1] + new_address
            i += 2
    while len(new_address) != 8:
        new_address += "0"
    return new_address

def addr_to_model_ptr(address):
    if "0x" in address:
        address = int(address, 0)
    else:
        address = int(address, 16)
    address += ROM_POL_OFFSET
    address /= 4
    address = hex(int(address))
    address = swap_endian(address)
    return address.upper()

def addr_to_mat_ptr(address):
    if "0x" in address:
        address = int(address, 0)
    else:
        address = int(address, 16)
    address /= 2
    address = hex(int(address))
    address = swap_endian(address)
    return address.upper()

def model_ptr_to_addr(address):
    address = swap_endian(address)
    address = int(address, 16)
    address *= 4
    address -= ROM_POL_OFFSET
    address = hex(int(address)).replace("0x", "")
    return address.upper()

def mat_ptr_to_addr(address):
    address = swap_endian(address)
    address = int(address, 16)
    address *= 2
    address = hex(int(address)).replace("0x", "")
    return address.upper()

def read_json(in_json):
    jsonf = open(in_json)
    jsons = jsonf.read()
    jsonf.close()
    return json.loads(jsons)

def rom_data_name(name):
    map = ROM_DATA_MAP
    for model in map["rom_data"]:
        if model["name"] == name:
            return model

def rom_data_index(name):
    map = ROM_DATA_MAP
    i = 0xE0004
    for model in map["rom_data"]:
        if model["name"] == name:
            return i
        i += 16

def rom_data_by_index(index):
    map = ROM_DATA_MAP
    i = 0
    for model in map["rom_data"]:
        if i == index:
            return model
        i += 1

def get_property(prop_name):
    for prop in CONFIG:
        if prop[0] == prop_name:
            return prop[1]

def inject(rom, address, data):
    f = open(get_property("ROM_DIR") + "\\" + rom, "r+b")
    if "0x" in address:
        address = int(address, 0)
    else:
        address = int(address, 16)
    j = 0
    f.seek(address)
    for i in range(address, address + int(len(data)/2)):
        f.write(int(data[j] + data[j+1], 16).to_bytes(1, 'big'))
        j += 2
    f.close()

def inject_model_pointer(address, data):
    base = rom_data_index(address)
    base += 8
    inject("rom_data.bin", hex(base), data)

def inject_mat_pointer(address, data):
    base = rom_data_index(address)
    base += 4
    inject("rom_data.bin", hex(base), data)

def import_settings():
    f = open("./config.ini")
    s = f.read()
    f.close()
    s = s.replace("\r", "")
    l = s.split("\n")
    settings = []
    for line in l:
        e = line.split("=")
        if len(e) == 2:
            CONFIG.append([e[0].strip().upper(), e[1].strip()])

CONFIG = []
ROM_DATA_MAP = read_json("./rom_data.json")

def main():
    import_settings()
    print(f"Converting model...\n\n")
    in_obj = open_obj("./in.obj")
    current = rom_data_name("sonic_head_idle_right")
    print(rom_data_by_index(3028))
    print(model_ptr_to_addr(current["rom_pol"]))
    print(mat_ptr_to_addr(current["rom_tex"]))
    out_stf = convert_obj(in_obj)
    stf_to_file(out_stf, "out")
    mdl_ptr = addr_to_model_ptr("0xEC2590")
    mat_ptr = addr_to_mat_ptr("0x7B45E0")
    inject_model_pointer("sonic_head_idle_right", mdl_ptr)
    inject_mat_pointer("sonic_head_idle_right", mat_ptr)
    inject("rom_pol.bin", "0xEC2590", out_stf[0])
    inject("rom_tex.bin", "0x7B45E0", out_stf[1])


main()
