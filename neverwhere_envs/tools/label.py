from asyncio import sleep
from xml.dom import minidom
import json

import numpy as np
import trimesh
import transforms3d
import xml.etree.ElementTree as ET
from params_proto import ParamsProto, Proto, Flag
from pathlib import Path
from vuer import Vuer, VuerSession
from vuer.events import Set, ClientEvent
from vuer.schemas import DefaultScene, TriMesh, Cylinder, group, Movable, InputBox, AutoScroll, div, Sphere
from neverwhere_envs.utils.transform import compute_alignment_transform

class Args(ParamsProto):
    # dataset root
    dataset_root = "/SSD_7T/chenziyu/code/nw/neverwhere_envs/all_scans_v1_12292024"
    # scene name
    scene_name = "hurdle_three_grassy_courtyard_v2"
    # viewer port
    port = 8093
    # text window hint
    text_window_hint = "Please follow the instructions below:\nStep 1: rotate the mesh to the desired orientation\nStep 2: add two markers, type 'm' + enter\nStep 3: scale and crop the mesh, type 'r(scale)' + enter\nStep 4: add waypoints, type 'n' + enter\nStep 5: save the xml, type 's' + enter\n"
    # xml template
    template_path = "neverwhere_envs/tools/templates/mesh_v2.xml"
    # mesh params
    bounding_box = [-2, -3, -3, 10, 3, 3]
    friction = 1.25
    # whether to auto add to task list
    auto_add = True
    
class SaveArgs:
    position = [0, 0, 0]
    rotation = [0, 0, 0]
    scale = None
    waypoints = []
    markers = []

def as_mesh(scene_or_mesh):
    """
    Convert a possible scene to a mesh.

    If conversion occurs, the returned mesh has only vertex and face data.
    """
    if isinstance(scene_or_mesh, trimesh.Scene):
        if len(scene_or_mesh.geometry) == 0:
            mesh = None  # empty scene
        else:
            mesh = trimesh.util.concatenate(
                tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces) for g in scene_or_mesh.geometry.values())
            )
    else:
        assert isinstance(scene_or_mesh, trimesh.Trimesh)
        mesh = scene_or_mesh
    return mesh

def add_waypoint_bodies(root):
    # Find the worldbody element
    worldbody = root.find("worldbody")

    if worldbody is not None:
        for i in range(len(SaveArgs.waypoints)):
            # Create new body element
            position = " ".join(map(str, SaveArgs.waypoints[i]["position"]))
            body_elem = ET.Element("body", {"name": f"waypoint-{i}", "mocap": "true", "pos": position})

            # add cone geoms
            geom1_elem = ET.Element(
                "geom",
                {
                    "name": f"cone-{i}_1",
                    "mesh": "SM_TrafficCone_V0_4_0",
                    "material": "M_TraficCone_Additional",
                    "class": "traffic_cone",
                },
            )
            geom2_elem = ET.Element(
                "geom",
                {
                    "name": f"cone-{i}_2",
                    "mesh": "SM_TrafficCone_V0_4_1",
                    "material": "M_TraficCone_Main",
                    "class": "traffic_cone",
                },
            )
            body_elem.append(geom1_elem)
            body_elem.append(geom2_elem)

            # Append the new body element to the worldbody
            worldbody.append(body_elem)

def main(**deps):
    Args._update(deps)

    mesh_path = f"{Args.dataset_root}/{Args.scene_name}/geometry/visual_mesh_simplified.obj"
    mesh = as_mesh(trimesh.load_mesh(mesh_path))

    app = Vuer(port=Args.port, queries=dict(grid=True))

    print(f"Loaded mesh with {mesh.vertices.shape} vertices and {mesh.faces.shape} faces")

    @app.add_handler("OBJECT_MOVE")
    async def on_move(event: ClientEvent, sess: VuerSession):
        if event.key == "mesh":
            SaveArgs.position = event.value["position"]
            SaveArgs.rotation = event.value["rotation"][:3]
            return
        
        key_parts = event.key.split("_")
        if len(key_parts) < 2:
            return
        obj_type, obj_num = key_parts[0], key_parts[-1]
        if obj_type == "waypoint" and obj_num.isdigit() and int(obj_num) < len(SaveArgs.waypoints):
            SaveArgs.waypoints[int(obj_num)]["position"] = event.value["position"]
            SaveArgs.waypoints[int(obj_num)]["rotation"] = event.value["rotation"][:3]
        elif obj_type == "marker" and obj_num.isdigit() and int(obj_num) < len(SaveArgs.markers):
            SaveArgs.markers[int(obj_num)]["position"] = event.value["position"]
            SaveArgs.markers[int(obj_num)]["rotation"] = event.value["rotation"][:3]

    @app.add_handler("INPUT")
    async def s(event: ClientEvent, session: VuerSession):
        global vertices, sectioned_vertices, zip_index, bbox_coords, bbox_rot, size

        key = event.value.split("\n")[0]                                        
        if key == "m":
            """
            Create markers (up to 2) and save them to SaveArgs.markers
            """
            if len(SaveArgs.markers) >= 2:
                print("Already have 2 markers, skipping")
                return

            marker_num = len(SaveArgs.markers)
            position = [2, 0, 1] if marker_num == 0 else \
                      SaveArgs.markers[marker_num-1]["position"] + np.array([0, 0, 1])

            SaveArgs.markers.append({
                "position": position,
                "rotation": [0, 0, 0]
            })

            session.add @ Movable(
                Sphere(
                    args=[0.1, 16, 16],
                    scale=0.1, 
                    position=[0, 0, 0],
                    material=dict(color="red"),
                    key=f"sphere_{marker_num}"
                ),
                key=f"marker_{marker_num}",
                position=position
            )

            print(f"Created marker {marker_num}", SaveArgs.markers)
                
        elif key == "n":
            """
            Add a new waypoint
            """
            waypoint_num = len(SaveArgs.waypoints)
            position = [1, 0, 0.5] if waypoint_num == 0 else \
                      SaveArgs.waypoints[waypoint_num-1]["position"] + np.array([1, 0, 0])

            SaveArgs.waypoints.append({
                "position": position,
                "rotation": [0, 0, 0]
            })

            session.add @ Movable(
                Cylinder(
                    args=[0.04, 0.1, 0.25, 20],
                    rotation=[np.pi / 2, 0, 0], 
                    position=[0, 0, 0.125],
                    material=dict(color="orange"),
                    key=f"sphere_{waypoint_num}"
                ),
                key=f"waypoint_{waypoint_num}",
                position=position
            )

            print("Created new waypoint", SaveArgs.waypoints)
                
        elif key[0] == "r":
            """
            1. Transform the mesh according to the rotation and position
            2. Rescale the mesh according to the markers
            3. Crop the mesh according to the bounding box
            4. Save the mesh and the rotation and position to json
            """
            # load the original mesh
            mesh_path = f"{Args.dataset_root}/{Args.scene_name}/geometry/visual_mesh_simplified.obj"
            mesh = as_mesh(trimesh.load_mesh(mesh_path))
            
            # transform the mesh according to the rotation and position
            rotation = SaveArgs.rotation
            rotation_matrix = transforms3d.euler.euler2mat(*rotation, axes='rxyz')
            translation = SaveArgs.position
            transformation_matrix = np.eye(4)
            transformation_matrix[:3, :3] = rotation_matrix
            transformation_matrix[:3, 3] = translation
            mesh.apply_transform(transformation_matrix)
            
            # rescale the mesh according to the markers
            length = np.linalg.norm(np.array(SaveArgs.markers[0]["position"]) - np.array(SaveArgs.markers[1]["position"]))
            real_length = float(key[1:])
            scale = real_length / length
            print(f"Rescaling mesh by {scale} times")
            mesh.apply_scale(scale)
            SaveArgs.scale = scale
            # Crop the mesh according to the bounding box
            bounding_box = np.array(Args.bounding_box).reshape(2, 3)
            planes = [
                (bounding_box[0], [1, 0, 0]),  # left plane
                (bounding_box[1], [-1, 0, 0]), # right plane
                (bounding_box[0], [0, 1, 0]),  # bottom plane
                (bounding_box[1], [0, -1, 0]), # top plane
                (bounding_box[0], [0, 0, 1]),  # front plane
                (bounding_box[1], [0, 0, -1])  # back plane
            ]
            for origin, normal in planes:
                mesh = mesh.slice_plane(origin, normal)
            
            session.upsert @ TriMesh(
                key="trimesh_processed",
                vertices=np.array(mesh.vertices),
                faces=np.array(mesh.faces),
                color="gray",
            )
            
            # remove the mesh and the markers in visualizer
            session.remove @ ["trimesh", "mesh", "marker_0", "marker_1", "sphere_0", "sphere_1"]
            
            # save the new mesh and the rotation and position to json
            mesh.export(
                f"{Args.dataset_root}/{Args.scene_name}/geometry/collision_mesh.obj"
            )
        
        if key == "s":
            save_path = f"{Args.dataset_root}/{Args.scene_name}/{Path(Args.scene_name).stem}.xml"
            
            # get transformation with order: transform, rescale
            tf = np.eye(4)
            tf[:3, :3] = transforms3d.euler.euler2mat(*SaveArgs.rotation, axes='rxyz')
            tf[:3, 3] = SaveArgs.position
            scale_mat = np.diag([SaveArgs.scale, SaveArgs.scale, SaveArgs.scale, 1])
            tf = np.dot(scale_mat, tf)
            
            # T = np.dot(tf, scale_mat_inv)
            scale_mat_inv = np.diag([1/SaveArgs.scale, 1/SaveArgs.scale, 1/SaveArgs.scale, 1])
            T = np.dot(tf, scale_mat_inv)
            
            # transform T to pos and euler
            mesh_pos = T[:3, 3]
            mesh_euler = transforms3d.euler.mat2euler(T[:3, :3], axes='rxyz')
            mesh_scale = [SaveArgs.scale, SaveArgs.scale, SaveArgs.scale]
            
            # Use f-string for formatting
            with open(Args.template_path, "r") as file:
                xml_data = file.read()
            formatted_xml = xml_data.format(
                scene_name=str(Path(Args.scene_name).stem),
                mesh_pos=" ".join(map(str, mesh_pos)),
                mesh_euler=" ".join(map(str, mesh_euler)),
                mesh_scale=" ".join(map(str, mesh_scale)),
                friction=str(Args.friction),
            )

            with open(save_path, "w") as file:
                file.write(formatted_xml)

            print("parsing")

            tree = ET.parse(save_path)
            root = tree.getroot()

            print(f"Loaded template..{Args.template_path}")

            add_waypoint_bodies(root)

            tree.write(save_path, encoding="unicode", xml_declaration=True)

            if Args.auto_add:
                task_folder = Path(__file__).parent.parent.parent / "neverwhere" / "tasks"
                tree.write(f"{task_folder / f'neverwhere_{Path(save_path).name}'}")

                print(f"Added to dog park task list..{task_folder / f'neverwhere_{Path(save_path).name}'}")

            print(f"saved..{save_path}")
            
            # save the transformation matrix
            with open(f"{Args.dataset_root}/{Args.scene_name}/geometry/collision_tf.json", "w") as f:
                json.dump({
                    "mesh_scale": SaveArgs.scale,
                    "mesh_pos": mesh_pos.tolist(),
                    "mesh_euler": list(mesh_euler),
                }, f)

    @app.spawn(start=True)
    async def main(session):
        children = []
        session @ Set(
            DefaultScene(
                Movable(
                    TriMesh(
                        key="trimesh",
                        vertices=np.array(mesh.vertices),
                        faces=np.array(mesh.faces),
                        color="gray",
                        # wireframe=True,
                    ),
                    # anchor=[0, 1, 0],
                    scale=3.0,
                    key="mesh",
                ),
                *children,
                backgroundChildren=[],
                htmlChildren=[
                    div(
                        AutoScroll(
                            key="chat-history",
                            style={
                                "flex": "auto",
                                "overflowY": "auto",
                            },
                        ),
                        InputBox(
                            key="text_input",
                            # value="",
                            defaultValue=Args.text_window_hint,
                            clearOnSubmit=True,
                            style={
                                "flex": "none",
                                "height": "150px",
                            },
                        ),
                        style={
                            "display": "flex",
                            "flexDirection": "column",
                            # need to make this pop in the front, because the canvas is z-index 10.
                            "overflowY": "auto",
                            "zIndex": 20,
                            "float": "right",
                            "width": "600px",
                            "height": "100vh",
                            "padding": "20px",
                            "position": "absolute",
                            "top": 0,
                            "right": 0,
                        },
                    )
                ],
                style={
                    "marginRight": "600px",
                    "height": "100vh",
                    "maxHeight": "100vh",
                    "width": "calc(100% - 600px)",
                    "boxSizing": "border-box",
                },
                # style={"width": "0px", "height": "0px", "maxHeight": "100%", "boxSizing": "border-box"},
                up=[0, 0, 1],
            ),
        )

        while True:
            await sleep(0.016)


if __name__ == "__main__":
    main()
