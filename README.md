# Turtle 3D

This project implements a 3D renderer in Python using only the turtle library as a fun programming challenge. It is not a very serious program outside of being a challenge, as there is no practical reason for a program like this to only use the turtle library.


Table of Contents
=================
* [Documentation](#documentation)
  * [Constants](#constants)
  * [Basic Math Functions](#basic-math-functions)
  * [More Complex Rendering Functions](#more-complex-rendering-functions)
  * [Window Class](#window-class)
  * [Mesh Class](#window-class)
  * [Scene Class](#window-class)
* [Example](#example)


## Documentation

### Constants
- OUTLINE_MESH - If True, a black outline is drawn around every triangle
- PATH_SEPERATOR - String used to separate directory levels in file system
- TRIG_PRECISION - How far the turtle moves to calculate trig functions
- DEFAULT_COLOR - Fall back color when none is specified
- Vec2 - tuple of 2 floats (x, y)
- Vec3 - tuple of 3 floats (x, y, z)
- Rot3 - tuple of 3 floats (yaw, pitch, roll) - measured in degrees
- Color - tuple of 3 floats (r, g, b) - each float in the range [0, 1]
- Tri - tuple of 5 ints: 3 vertex indices, 1 normal vector index, 1 color index

### Basic Math Functions
- cos(angle: float) -> float
- sin(angle: float) -> float
- tan(angle: float) -> float
- rotate2(x: float, y: float, angle: float) -> Vec2
- rotate3(x: float, y: float, z: float, yaw: float, pitch: float, roll: float) -> Vec3
- clamp_rotation(yaw: float, pitch: float, roll: float) -> Rot3
- lerp(a: float, b: float, f: float) -> float
- rlerp(a: float, b: float, t: float) -> float
- dot_product(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float
- cross_product(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> Vec3

### More Complex Rendering Functions
- clip2(v1: Vec2, v2: Vec2, axis: int, amount: float) -> Vec2
- clip3(v1: Vec3, v2: Vec3, z: float) -> Vec3
- screen_coordinates(x: float, y: float, width: float, height: float) -> Vec2
- draw_tri(a: Vec2, b: Vec2, c: Vec2, width: float, height: float) -> None
- read_obj(directory: str, obj_file_name: str, *, flip: bool = False) -> Mesh
- write_obj(directory: str, obj_file_name: str, mtl_file_name: str, mesh: Mesh) -> None

### Window Class
- Window(width: int, height: int, title: str | None = None, icon: str | None = None) -> Window
- .title: str = turtle's default title
- .is_fullscreen: bool = False
- .default_width: int
- .default_height: int
- .width: int
- .height: int
- .bg_color: Color = DEFAULT_COLOR
- .mouse_x: float = 0.5
- .mouse_y: float = 0.5
- .set_icon(icon: str) -> None
- .reset() -> None
- .toggle_fullscreen() -> None
- .mouse_down(button: int) -> bool
- .mouse_clicked(button: int, keybind_name: str) -> bool
- .key_pressed(key: str) -> bool
- .key_tapped(key: str, keybind_name: str) -> bool
- .add_keybind(key: str) -> None
- .update() -> bool

### Mesh Class
- Mesh(vertices: list[Vec3], normals: list[Vec3], colors: list[Color], tris: list[Tri]) -> Mesh
- .vertices: list[Vec3]
- .normals: list[Vec3]
- .colors: list[Color]
- .tris: list[Tri]
- .x: float = 0
- .y: float = 0
- .z: float = 0
- .yaw: float = 0
- .pitch: float = 0
- .roll: float = 0

### Scene Class
- Scene(meshes: list[Mesh])) -> Scene
- .meshes: list[Mesh]
- .camera_x: float = 0
- .camera_y: float = 0
- .camera_z: float = 0
- .camera_yaw: float = 0
- .camera_pitch: float = 0
- .camera_roll: float = 0
- .camera_fov: float = 90
- .camera_z_near: float = 0.01
- .draw(window: Window) -> None


## Example

Example code to open an obj file using this Python script:

```python
import turtle_3d


def main():
    directory = input("Enter directory: ")
    file_name = input("Enter obj file name: ")
    move_speed = float(input("Enter speed: "))

    window = turtle_3d.Window(500, 500, "3D Viewer")
    mesh = turtle_3d.read_obj(directory, file_name)
    scene = turtle_3d.Scene([mesh])

    held_mouse_x = 0
    held_mouse_y = 0

    running = True
    while running:
        delta_yaw = 0
        delta_pitch = 0
        if window.mouse_clicked(1, "drag"):
            held_mouse_x = window.mouse_x
            held_mouse_y = window.mouse_y
        elif window.mouse_down(1):
            delta_yaw = (window.mouse_x - held_mouse_x) * 180
            delta_pitch = (window.mouse_y - held_mouse_y) * -180
            held_mouse_x = window.mouse_x
            held_mouse_y = window.mouse_y
        scene.camera_yaw, scene.camera_pitch, scene.camera_roll = turtle_3d.clamp_rotation(
            scene.camera_yaw + delta_yaw, scene.camera_pitch + delta_pitch, 0)
        delta_x = (window.key_pressed("d") - window.key_pressed("a")) * move_speed
        delta_y = (window.key_pressed("space") - window.key_pressed("Shift_L")) * move_speed
        delta_z = (window.key_pressed("w") - window.key_pressed("s")) * move_speed
        delta_z, delta_x = turtle_3d.rotate2(delta_z, delta_x, scene.camera_yaw)
        scene.camera_x += delta_x
        scene.camera_y += delta_y
        scene.camera_z += delta_z

        scene.draw(window)
        running = window.update()


if __name__ == "__main__":
    main()

```

This example is the same program ran if you try running the turtle_3d script as main.
