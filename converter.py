import struct
import os

START_OP = "01040400000000000000000000000000"
POLY_OP = "011580C8000000000000000000000000"
END_OP = "00000000"
MAT_CONST = "09400000001A"

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

def main():
    print(f"Converting model...\n\n")
    in_obj = open_obj("./in.obj")
    out_stf = convert_obj(in_obj)
    stf_to_file(out_stf, "out")

main()
