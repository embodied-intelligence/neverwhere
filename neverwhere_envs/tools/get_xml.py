from asyncio import sleep
from xml.dom import minidom

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
    dataset_root = Proto(env="NEVERWHERE_DATASETS")
    dataset_prefix = "gaps_fire_outlet_v3/"

    port = 9001

    template_path = "neverwhere_envs/tools/templates/mesh.xml"
    auto_add = Flag(help="Upon save, add to dog park task list. Overwrites existing file.")

    friction = 1.25


class SaveArgs:
    position = [0, 0, 0]
    rotation = [0, 0, 0]
    waypoints = []
    markers = []


MARKER_COLORS = ["red", "blue", "purple", "black"]
# after alignment:
# red marker: P0 (origin)
# blue marker: P1 (x-axis)
# purple marker: P2 (defines XY plane)
# black marker: P3 (defines handedness of coordinate system)

def prettify(elem):
    """Return a pretty-printed XML string for the Element."""
    rough_string = ET.tostring(elem, "utf-8")
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="    ")


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


def main(**deps):
    Args._update(deps)

    # first try load simplified collision geometry
    try:
        mesh_path = f"{Args.dataset_root}/{Args.dataset_prefix}/geometry/collision_simplified.obj"
    except FileNotFoundError:
        mesh_path = f"{Args.dataset_root}/{Args.dataset_prefix}/geometry/collision.obj"

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
        if key == "s":
            save_path = f"{Args.dataset_root}/{Args.dataset_prefix}/{Path(Args.dataset_prefix).stem}.xml"
            # Use f-string for formatting
            position = " ".join(map(str, SaveArgs.position))
            rotation = " ".join(map(str, SaveArgs.rotation))
            with open(Args.template_path, "r") as file:
                xml_data = file.read()
            formatted_xml = xml_data.format(
                scene_name=str(Path(Args.dataset_prefix).stem),
                mesh_pos=position,
                mesh_euler=rotation,
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
                task_folder = Path(__file__).parent.parent / "lucidsim" / "tasks"
                tree.write(f"{task_folder / Path(save_path).name}")

                print(f"Added to dog park task list..{task_folder / Path(save_path).name}")

            # with open(save_path, "w") as file:
            #     file.write(prettify(root))

            print(f"saved..{save_path}")

        elif key == "n":
            # add new waypoint
            next_waypoint_key = str(len(SaveArgs.waypoints))
            SaveArgs.waypoints.append(
                {
                    "position": [0, 0, 0],
                    "rotation": [0, 0, 0],
                }
            )
            # add new movable
            session.upsert @ Movable(
                Cylinder(
                    args=[0.04, 0.1, 0.25, 20],
                    rotation=[np.pi / 2, 0, 0],
                    position=[0, 0, 0.125],
                    material=dict(color="orange"),
                    key=f"sphere_{next_waypoint_key}",
                ),
                key=f"waypoint_{next_waypoint_key}",
                position=[0, 0, 3],
            )

            print("Created new waypoint", SaveArgs.waypoints)

        elif key == "m":
            # Add new marker
            next_marker_key = str(len(SaveArgs.markers))
            SaveArgs.markers.append(
                {
                    "position": [0, 0, 0],
                    "rotation": [0, 0, 0],
                }
            )
            # add new movable
            session.upsert @ Movable(
                Sphere(
                    args=[0.1, 16, 16], 
                    scale=0.3,
                    position=[0, 0, 0],
                    material=dict(color=MARKER_COLORS[int(next_marker_key)]),
                    key=f"sphere_{next_marker_key}",
                ),
                key=f"marker_{next_marker_key}",
                position=[0, 0, 3],
            )

            print("Created new marker", SaveArgs.markers)

        elif key == "t":
            # Assertions for proper marker setup
            assert len(SaveArgs.markers) == 4, f"we need 4 markers, got {len(SaveArgs.markers)}"
            
            # Compute transformation
            transform_matrix = compute_alignment_transform(
                np.array([marker["position"].copy() for marker in SaveArgs.markers])
            )

            position = transform_matrix[:3, 3]
            rotation = list(transforms3d.euler.mat2euler(transform_matrix[:3, :3], axes='rxyz'))

            # Apply transformation to mesh
            session.upsert(Movable(
                TriMesh(
                    key="trimesh", 
                    vertices=np.array(mesh.vertices),
                    faces=np.array(mesh.faces),
                    color="gray",
                ),
                key="mesh",
                position=position.tolist(),
                rotation=rotation
                )
            )
            SaveArgs.position = position.tolist()
            SaveArgs.rotation = rotation

            # Apply transformation to markers
            for i in range(4):
                marker_pos = np.append(SaveArgs.markers[i]["position"], 1)  # homogeneous coordinates
                transformed_pos = (transform_matrix @ marker_pos)[:3]  # back to 3D coordinates
                SaveArgs.markers[i]["position"] = transformed_pos.tolist()
                session.upsert @ Movable(
                    Sphere(
                        args=[0.1, 16, 16], 
                        scale=0.3,
                        position=[0, 0, 0],
                        material=dict(color=MARKER_COLORS[i]),
                        key=f"sphere_{i}",
                    ),
                    key=f"marker_{i}",
                    position=transformed_pos.tolist()
                )

            print("Transformed mesh and markers to align with requirements")

    @app.spawn(start=True)
    async def main(session):
        children = []
        session @ Set(
            DefaultScene(
                group(
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
                            defaultValue="save : 's' + enter, load next waypoint : 'n' + enter, load next marker : 'm' + enter, transform mesh : 't' + enter",
                            clearOnSubmit=True,
                            style={
                                "flex": "none",
                                "height": "100px",
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
