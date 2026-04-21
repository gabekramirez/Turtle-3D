# Turtle 3D

This project implements a 3D renderer in Python using only the turtle library as a fun programming challenge. It is not a very serious program outside of being a challege, as there is no practical reason for a program like this to only use the turtle library.


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
- PATH_SEPERATOR - String used to seperate directory levels in file system
- TRIG_PRECISION - How far the turtle moves to calculate trig functions
- DEFAULT_COLOR - Fall back color when none is specified
- Vec2 - tuple of 2 floats (x, y)
- Vec3 - tuple of 3 floats (x, y, z)
- Tri - tuple of 5 ints: 3 vertex indices, 1 normal vector index, 1 color index
- Exit - Exception raised when trying to access a closed turtle window

### Basic Math Functions
- cos(angle: float) -> float
- sin(angle: float) -> float
- tan(angle: float) -> float
- rotate2(x: float, y: float, angle: float) -> Vec2
- rotate3(x: float, y: float, z: float, yaw: float, pitch: float, roll: float) -> Vec3
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
- .bg_color: tuple[float, float, float] = DEFAULT_COLOR
- .mouse_x: float = 0.5
- .mouse_y: float = 0.5
- .set_icon(icon: str) -> None
- .reset() -> None
- .toggle_fullscreen() -> None
- .mouse_clicked(button: int, keybind_name: str) -> bool
- .key_pressed(key: str) -> bool
- .key_tapped(key: str, keybind_name: str) -> bool
- .add_keybind(self, key: str) -> None
- .update(self) -> bool

### Mesh Class
- Mesh(vertices: list[Vec3], normals: list[Vec3], colors: list[Vec3], tris: list[Tri]) -> Mesh

### Scene Class
- Scene(meshes: list[Mesh])) -> Scene
- .vertices: Vec3
- .normals = normals
- .colors = colors
- .tris = tris
- .x = 0
- .y = 0
- .z = 0
- .yaw = 0
- .pitch = 0
- .roll = 0


## Example

Example code to open an obj file using this Python script:

```shell
import turtle_3d


def main():
    input_directory = input("Enter directory: ")
    input_file_name = input("Enter obj file name: ")
    input_camera_z = input("Enter camera z: ")
    input_speed = input("Enter speed: ")

    window = turtle_3d.Window(500, 500, "3D Viewer")
    mesh = turtle_3d.read_obj(input_directory, input_file_name)
    scene = turtle_3d.Scene([mesh])

    scene.camera_z = float(input_camera_z)
    move_speed = float(input_speed)
    turn_speed = float(input_speed) * 30

    try:
        while True:
            window.update()

            delta_pitch = (window.key_pressed("Right") - window.key_pressed("Left")) * turn_speed
            delta_yaw = (window.key_pressed("Up") - window.key_pressed("Down")) * turn_speed
            scene.move_camera(0, 0, 0, delta_pitch, delta_yaw, 0)
            delta_x = (window.key_pressed("d") - window.key_pressed("a")) * move_speed
            delta_y = (window.key_pressed("space") - window.key_pressed("Shift_L")) * move_speed
            delta_z = (window.key_pressed("w") - window.key_pressed("s")) * move_speed
            delta_z, delta_x = turtle_3d.rotate2(delta_z, delta_x, scene.camera_pitch)
            scene.move_camera(delta_x, delta_y, delta_z, 0, 0, 0)

            scene.draw(window)
    except turtle_3d.Exit:
        pass


if __name__ == "__main__":
    main()

```

This example is the same program ran if you try running the turtle_3d script as main.
