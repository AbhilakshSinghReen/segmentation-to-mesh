import os
import nibabel as nib
import numpy as np
from skimage import measure


segment_value_to_name = {
    1: "spleen",
    2: "kidney_right",
    3: "kidney_left",
    4: "gallbladder",
    5: "liver",
}

def get_polygonal_mesh_from_voxel_data(volume_data, voxel_spacing):
    # TODO (Abhilaksh): For some segments, measure.marching_cubes fails to create surfaces, fix that.
    verts, faces, normals, values = measure.marching_cubes(
        volume_data,
        level=None,
        spacing=voxel_spacing,
        step_size=1,
        allow_degenerate=False,
    )
    faces = faces + 1
    return verts, faces, normals, values

def write_obj_file(output_path, verts, faces, normals, values):
    with open(output_path, 'w') as obj_file:
        for item in verts:
            obj_file.write("v {0} {1} {2}\n".format(item[0],item[1],item[2]))

        for item in normals:
            obj_file.write("vn {0} {1} {2}\n".format(item[0],item[1],item[2]))

        for item in faces:
            obj_file.write("f {0}//{0} {1}//{1} {2}//{2}\n".format(item[0],item[1],item[2]))

def save_segment_as_object(output_path, volume_data, voxel_spacing, segment_value):
   volume_data[volume_data != segment_value] = 0
   volume_data[volume_data == segment_value] = 1
   verts, faces, normals, values = get_polygonal_mesh_from_voxel_data(volume_data, voxel_spacing)
   ###
   # TODO (Dr. Amit): (verts, faces, normals, values) represent the mesh generated. We have to:
   # Remove excess polygons/triangles from this Mesh
   # Make the edges smoother to make it look better
   # Make the mesh watertight

   # After making changes to the mesh you can write the file using the function below if you have (verts, faces, normals) 
   # or you can write .obj using the library you used to edit the mesh.
   write_obj_file(output_path, verts, faces, normals, values)

def total_segmentator_output_to_objs(ts_out_file_path, objs_save_folder):
    nifti_file = nib.load(ts_out_file_path)
    voxel_spacing = nifti_file.header.get_zooms()
    volume_data = nifti_file.get_fdata()

    segment_values = np.unique(volume_data)

    for segment_value in segment_values:
        if int(segment_value) == 0: # background
            continue

        segment_name = segment_value_to_name.get(int(segment_value), None)
        if segment_name is None:
            print(f"No name found for segment value {segment_value}. Skipping this segment...")
            continue

        segment_obj_output_path = os.path.join(objs_save_folder, f"{segment_name}.obj")
        save_segment_as_object(segment_obj_output_path, volume_data, voxel_spacing, segment_value)
        print(f"Saved segment {segment_name} as {segment_name}.obj")

if __name__ == "__main__":
    file_path = '1-tsoc.nii.gz'
    output_dir = "1-tsoc"
    os.makedirs(output_dir, exist_ok=True)

    total_segmentator_output_to_objs(file_path, output_dir)
