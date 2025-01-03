from asyncio import sleep
from xml.dom import minidom
import os
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
    dataset_root = os.environ["NEVERWHERE_DATASET_ROOT"]
    # scene name
    scene_name = os.environ["NEVERWHERE_SCENE_NAME"]
    # viewer port
    port = 9012
    # text window hint
    text_window_hint = "Please follow the instructions below:\nStep 1: rotate the mesh to the desired orientation\nStep 2: add two markers, type 'm' + enter\nStep 3: scale and crop the mesh, type 'r(scale)' + enter\nStep 4: add waypoints, type 'n' + enter\nStep 5: save the xml, type 's' + enter\n"
    # whether to auto add to task list
    auto_add = True
    # prefix for the scene name
    prefix = "nw-"
    
class SaveArgs:
    waypoints = []

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

    mesh_path = f"{Args.dataset_root}/{Args.scene_name}/geometry/collision_mesh.obj"
    mesh = as_mesh(trimesh.load_mesh(mesh_path))

    app = Vuer(port=Args.port, queries=dict(grid=True))

    print(f"Loaded mesh with {mesh.vertices.shape} vertices and {mesh.faces.shape} faces")

    @app.add_handler("OBJECT_MOVE")
    async def on_move(event: ClientEvent, sess: VuerSession):        
        key_parts = event.key.split("_")
        if len(key_parts) < 2:
            return
        obj_type, obj_num = key_parts[0], key_parts[-1]
        if obj_type == "waypoint" and obj_num.isdigit() and int(obj_num) < len(SaveArgs.waypoints):
            SaveArgs.waypoints[int(obj_num)]["position"] = event.value["position"]
            SaveArgs.waypoints[int(obj_num)]["rotation"] = event.value["rotation"][:3]

    @app.add_handler("INPUT")
    async def s(event: ClientEvent, session: VuerSession):
        global vertices, sectioned_vertices, zip_index, bbox_coords, bbox_rot, size

        key = event.value.split("\n")[0]                                        
        if key == "n":
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
                
        elif key == "s":
            save_path = f"{Args.dataset_root}/{Args.scene_name}/{Path(Args.scene_name).stem}.xml"
            
            # Load the existing XML file
            tree = ET.parse(save_path)
            root = tree.getroot()

            # Clear old waypoints
            worldbody = root.find("worldbody")
            if worldbody is not None:
                for body in list(worldbody):
                    if body.attrib.get("name", "").startswith("waypoint-"):
                        worldbody.remove(body)

            # Add new waypoints
            add_waypoint_bodies(root)

            # Write the updated XML back to the file
            tree.write(save_path, encoding="unicode", xml_declaration=True)

            if Args.auto_add:
                task_folder = Path(__file__).parent.parent.parent / "neverwhere" / "tasks"
                tree.write(f"{task_folder / f'{Args.prefix}{Path(save_path).name}'}")

                print(f"Added to dog park task list..{task_folder / f'{Args.prefix}{Path(save_path).name}'}")

            print(f"saved..{save_path}")

    @app.spawn(start=True)
    async def main(session):
        children = []
        session @ Set(
            DefaultScene(
                TriMesh(
                    key="trimesh",
                    vertices=np.array(mesh.vertices),
                    faces=np.array(mesh.faces),
                    color="gray",
                    # wireframe=True,
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
