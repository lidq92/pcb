import os
import argparse
import pymeshlab


#pwd mesuh be mesh_path
def mesh_to_pc(mesh_path, pc_path, width=1024, height=1024, binary=False):
    ms = pymeshlab.MeshSet()
    ms.load_new_mesh(mesh_path)
    ms.texel_sampling(texturew=width, textureh=height, texturespace=False, recovercolor=True)
    ms.save_current_mesh(pc_path, binary=binary, save_vertex_quality=False, save_face_color=False)
    return 


if __name__ == "__main__":

    mesh_path = 'D:\\Downloads\\Sketchfab\\animals-pets\\terror-bird-nhmw-optimized-obj\\source\\rapid.obj'
    pc_path = 'D:\\Downloads\\Sketchfab\\animals-pets\\terror-bird-nhmw-optimized-obj\\source\\rapid.ply'
    # mesh_path = 'rapid.obj'
    # pc_path = 'rapid.ply'

    parser =argparse.ArgumentParser(description='PCC')
    parser.add_argument('--mesh_path', default=mesh_path, type=str,
                        help='')
    parser.add_argument('--pc_path', default=pc_path, type=str,
                        help='')
    args = parser.parse_args()

    mesh_to_pc(mesh_path, pc_path)
