# Turtle 3D

This project implements a 3D renderer in Python using only the turtle library.

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
