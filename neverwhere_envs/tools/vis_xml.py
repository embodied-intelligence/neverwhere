import numpy as np
import trimesh
import xml.etree.ElementTree as ET
from asyncio import sleep
from params_proto import ParamsProto, Proto
from vuer import Vuer, VuerSession
from vuer.events import Set, ClientEvent
from vuer.schemas import DefaultScene, TriMesh, Cylinder, group, Movable, InputBox, AutoScroll, div, Sphere
from pathlib import Path

class Args(ParamsProto):
    # dataset root
    dataset_root = "/SSD_7T/chenziyu/code/nw/neverwhere_envs/all_scans_v1_12292024"
    # scene name
    scene_name = "hurdle_three_grassy_courtyard_v2"
    # viewer port
    port = 8093
    
REORDER_AXES = [0, 1, 2]

class SaveArgs:
    # Default values
    position = [0, 0, 0]
    rotation = [0, 0, 0]
    waypoints = [{
        "position": [0, 0, 0],
        "rotation": [0, 0, 0]
    }]  # Default waypoint at origin

def as_mesh(scene_or_mesh):
    """Convert a possible scene to a mesh."""
    if isinstance(scene_or_mesh, trimesh.Scene):
        if len(scene_or_mesh.geometry) == 0:
            return None
        return trimesh.util.concatenate(
            tuple(trimesh.Trimesh(vertices=g.vertices, faces=g.faces) 
                 for g in scene_or_mesh.geometry.values())
        )
    return scene_or_mesh

def load_from_xml(xml_path):
    """Load mesh and waypoint positions from XML file"""
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    # Find main mesh position and rotation
    worldbody = root.find("worldbody")
    # Look for mesh body inside scene-group-2
    scene_group = worldbody.find(".//body[@name='scene-group-2']")
    if scene_group is not None:
        mesh_body = scene_group.find(".//body[@name='mesh']")
        if mesh_body is not None:
            SaveArgs.position = [float(x) for x in mesh_body.get("pos").split()]
            SaveArgs.rotation = [float(x) for x in mesh_body.get("euler").split()]
    
    # Find waypoints (direct children of worldbody)
    for body in worldbody.findall("body"):
        name = body.get("name", "")
        if name.startswith("waypoint-"):
            print(f"Found waypoint {name}")
            pos = [float(x) for x in body.get("pos").split()]
            SaveArgs.waypoints.append({
                "position": pos,
                "rotation": [0, 0, 0]  # Default rotation if not specified
            })

def main(**deps):
    Args._update(deps)
    
    # Load mesh
    mesh_path = f"{Args.dataset_root}/{Args.scene_name}/geometry/collision_mesh.obj"
    mesh = as_mesh(trimesh.load_mesh(mesh_path))
    
    # Load XML data
    xml_path = f"{Args.dataset_root}/{Args.scene_name}/{Path(Args.scene_name).stem}.xml"
    print(f"Loading XML from {xml_path}")
    load_from_xml(xml_path)
    
    print(f"Loaded mesh with {mesh.vertices.shape} vertices and {mesh.faces.shape} faces")
    print(f"Position: {SaveArgs.position}")
    print(f"Rotation: {SaveArgs.rotation}")
    print(f"Waypoints: {SaveArgs.waypoints}")
    
    app = Vuer(port=Args.port, queries=dict(grid=True))
    
    @app.spawn(start=True)
    async def main(session: VuerSession):
        children = []
        for i, waypoint in enumerate(SaveArgs.waypoints):
            print(f"Waypoint {i}: {waypoint}")
            children.append(
                Movable(
                    Cylinder(
                        args=[0.04, 0.1, 0.25, 20],
                        rotation=[np.pi / 2, 0, 0],
                        position=[0, 0, 0.125],
                        material=dict(color="red" if i == 0 else "orange"),  # First waypoint is red
                        key=f"sphere_{i}",
                    ),
                    key=f"waypoint_{i}",
                    position=[waypoint["position"][i] for i in REORDER_AXES],
                    rotation=[waypoint["rotation"][i] for i in REORDER_AXES],
                    scale=0.3,
                )
            )
        # Create mesh visualization
        session @ Set(
            DefaultScene(
                group(
                    TriMesh(
                        key="trimesh",
                        vertices=np.array(mesh.vertices),
                        faces=np.array(mesh.faces),
                        color="gray",
                        # wireframe=True,
                        position=[SaveArgs.position[i] for i in REORDER_AXES],
                        rotation=[SaveArgs.rotation[i] for i in REORDER_AXES],
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
