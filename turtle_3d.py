import turtle


def monkey_patch_remove_scrollbars(self):
    self._canvas.xview_moveto(0.5 * (self.canvwidth - self._canvas.winfo_width()) / self.canvwidth)
    self._canvas.yview_moveto(0.5 * (self.canvheight - self._canvas.winfo_height()) / self.canvheight)
    self.hscroll.grid_forget()
    self.vscroll.grid_forget()


turtle.ScrolledCanvas.adjustScrolls = monkey_patch_remove_scrollbars

OUTLINE_MESH = False
PATH_SEPERATOR = "/"
TRIG_PRECISION = 100
DEFAULT_COLOR = (0.5, 0.5, 0.5)

Vec2 = tuple[float, float]
Vec3 = tuple[float, float, float]
Color = tuple[float, float, float]
Tri = tuple[int, int, int, int, int]

current_angle: float | None = None


def cos(angle: float) -> float:
    global current_angle
    if current_angle != angle:
        current_angle = angle
        turtle.penup()
        turtle.goto(0, 0)
        turtle.setheading(angle)
        turtle.forward(TRIG_PRECISION)
    return turtle.xcor() * 0.01


def sin(angle: float) -> float:
    global current_angle
    if current_angle != angle:
        current_angle = angle
        turtle.penup()
        turtle.goto(0, 0)
        turtle.setheading(angle)
        turtle.forward(TRIG_PRECISION)
    sine = turtle.ycor() * 0.01
    return sine


def tan(angle: float) -> float:
    global current_angle
    if current_angle != angle:
        current_angle = angle
        turtle.penup()
        turtle.goto(0, 0)
        turtle.setheading(angle)
        turtle.forward(TRIG_PRECISION)
    adjacent = turtle.xcor()
    if adjacent == 0:
        return float("inf")
    else:
        return turtle.ycor() / adjacent


def rotate2(x: float, y: float, angle: float) -> Vec2:
    cosine = cos(angle)
    sine = sin(angle)
    return x * cosine - y * sine, y * cosine + x * sine


def rotate3(x: float, y: float, z: float, yaw: float, pitch: float, roll: float) -> Vec3:
    y, x = rotate2(y, x, roll)
    z, x = rotate2(z, x, yaw)
    z, y = rotate2(z, y, pitch)
    return x, y, z


def lerp(a: float, b: float, f: float) -> float:
    return a * f + b * (1 - f)


def rlerp(a: float, b: float, t: float) -> float:
    if a == b:
        return 0.5
    else:
        return (t - b) / (a - b)


def dot_product(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> float:
    return x1 * x2 + y1 * y2 + z1 * z2


def cross_product(x1: float, y1: float, z1: float, x2: float, y2: float, z2: float) -> Vec3:
    return (z1 * y2 - y1 * z2,
            x1 * z2 - z1 * x2,
            y1 * x2 - x1 * y2)


def project(v: Vec3, z_near: float | None, tan_half_fov: float) -> Vec2 | None:
    if z_near is not None and v[2] < z_near:
        return None
    else:
        scale = tan_half_fov / v[2]
        return v[0] * scale, v[1] * scale


def normalize(x: float, y: float, z: float) -> Vec3:
    d = (x * x + y * y + z * z) ** 0.5
    if d != 0:
        d = 1 / d
    return x * d, y * d, z * d


def clip2(v1: Vec2, v2: Vec2, axis: int, amount: float) -> Vec2:
    if axis == 0:
        return amount, lerp(v1[1], v2[1], rlerp(v1[0], v2[0], amount))
    else:
        return lerp(v1[0], v2[0], rlerp(v1[1], v2[1], amount)), amount


def clip3(v1: Vec3, v2: Vec3, z: float) -> Vec3:
    f = rlerp(v1[2], v2[2], z)
    x = lerp(v1[0], v2[0], f)
    y = lerp(v1[1], v2[1], f)
    return x, y, z


def screen_coordinates(x: float, y: float, width: float, height: float) -> Vec2:
    return (x * height + width) * 0.5, (y + 1) * height * 0.5


def draw_tri(a: Vec2, b: Vec2, c: Vec2, width: float, height: float):
    global current_angle
    current_angle = None

    vertices = [a, b, c]
    aspect_ratio = width / height
    for sign, axis, amount in ((-1, 0, -aspect_ratio), (1, 0, aspect_ratio), (-1, 1, -1), (1, 1, 1)):
        is_off_screen = True
        new_vertices = 0
        vertex_index = 0
        while vertex_index < len(vertices):
            v2 = vertices[vertex_index]
            if v2[axis] * sign > amount * sign:
                v1 = vertices[(vertex_index - 1) % len(vertices)]
                v3 = vertices[(vertex_index + 1) % len(vertices)]
                v4: Vec2 | None = None
                v1_on_screen = v1[axis] * sign <= amount * sign
                v3_on_screen = v3[axis] * sign <= amount * sign
                if v1_on_screen:
                    v4 = clip2(v2, v1, axis, amount)
                if v3_on_screen:
                    if v1_on_screen:
                        v5 = clip2(v2, v3, axis, amount)
                        vertices.insert(vertex_index + 1, v5)
                        new_vertices += 2
                    else:
                        v4 = clip2(v2, v3, axis, amount)
                if v4 is None:
                    vertices.pop(vertex_index)
                    vertex_index -= 1
                else:
                    vertices[vertex_index] = v4
            elif new_vertices == 0:
                is_off_screen = False
            if new_vertices > 0:
                new_vertices -= 1
            vertex_index += 1
        if is_off_screen:
            return

    x, y = vertices.pop(0)
    p = screen_coordinates(x, y, width, height)
    turtle.goto(p)
    if OUTLINE_MESH:
        turtle.pencolor(0, 0, 0)
    turtle.pendown()
    turtle.begin_fill()
    for x, y in vertices:
        turtle.goto(screen_coordinates(x, y, width, height))
    turtle.end_fill()
    if OUTLINE_MESH:
        turtle.goto(p)
    turtle.penup()


class Window:
    def __init__(self, width: int, height: int, title: str | None = None, icon: str | None = None):
        self._turtle_screen = turtle.Screen()
        self._canvas = self._turtle_screen.getcanvas()
        self._root = self._canvas.winfo_toplevel()
        if icon is not None:
            self.set_icon(icon)
        if title is None:
            title = self._root.title()
        self.title = title

        self.default_width = width
        self.default_height = height
        self.is_fullscreen = False
        self.width = 0
        self.height = 0
        self._last_width = 0
        self._last_height = 0
        self._last_geometry = ""
        self.bg_color = DEFAULT_COLOR
        self.reset()
        turtle.tracer(0, 0)

        self._binds: set[str] = set()
        self._keybinds: dict[str, bool] = {}

        self._mouse_binds: dict[str, int] = {}
        self._mouse_buttons: set[int] = set()
        self.mouse_x = 0.5
        self.mouse_y = 0.5
        def mouse_press(event):
            self._mouse_binds.clear()
            self._mouse_buttons.add(event.num)
        self._root.bind("<ButtonPress>", mouse_press)
        def mouse_release(event):
            self._mouse_binds.clear()
            self._mouse_buttons.remove(event.num)
        self._root.bind("<ButtonRelease>", mouse_release)
        def mouse_move(event):
            self.mouse_x = event.x / self.width
            self.mouse_y = event.y / self.height
        self._root.bind("<Motion>", mouse_move)

        turtle.listen()

    def set_icon(self, icon: str):
        self._root.iconbitmap(icon)

    def reset(self):
        if self.is_fullscreen:
            self.toggle_fullscreen()
        self.width = self.default_width
        self.height = self.default_height
        self._last_width = 0
        self._last_height = 0
        turtle.setup(self.default_width, self.default_height)

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self._root.overrideredirect(self.is_fullscreen)
        if self.is_fullscreen:
            self._last_geometry = self._root.geometry()
            self._turtle_screen.setup(width=1.0, height=1.0)
        else:
            self._root.geometry(self._last_geometry)

    def mouse_down(self, button: int) -> bool:
        return button in self._mouse_buttons

    def mouse_clicked(self, button: int, keybind_name: str) -> bool:
        if self.mouse_down(button):
            if keybind_name not in self._mouse_binds.keys():
                self._mouse_binds[keybind_name] = button
                return True
        elif keybind_name in self._mouse_binds.keys():
            self._mouse_binds.pop(keybind_name)
        return False

    def key_pressed(self, key: str) -> bool:
        if key not in self._keybinds.keys():
            self.add_keybind(key)
        return self._keybinds[key]

    def key_tapped(self, key: str, keybind_name: str) -> bool:
        if self.key_pressed(key):
            if keybind_name not in self._binds:
                self._binds.add(keybind_name)
                return True
        elif keybind_name in self._binds:
            self._binds.remove(keybind_name)
        return False

    def add_keybind(self, key: str):
        """https://www.tcl-lang.org/man/tcl8.4/TkCmd/keysyms.htm"""
        self._keybinds[key] = False
        def key_pressed(keybind_key=key):
            self._keybinds[keybind_key] = True
        def key_released(keybind_key=key):
            self._keybinds[keybind_key] = False
        turtle.onkeypress(key_pressed, key)
        turtle.onkeyrelease(key_released, key)

    def update(self) -> bool:
        turtle.title(self.title)
        turtle.bgcolor(self.bg_color)
        try:
            turtle.update()
            turtle.clear()
            self.width = turtle.window_width()
            self.height = turtle.window_height()
            if not (self.width == self._last_width and self.height == self._last_height):
                turtle.setworldcoordinates(10, 10, self.width, self.height)
                turtle.hideturtle()
                self._last_width = self.width
                self._last_height = self.height
            if self.key_tapped("F10", "F10"):
                self.reset()
            elif self.key_tapped("F11", "F11"):
                self.toggle_fullscreen()
            return True
        except turtle.Terminator:
            return False


class Mesh:
    def __init__(self, vertices: list[Vec3], normals: list[Vec3], colors: list[Color], tris: list[Tri]):
        self.vertices = vertices
        self.normals = normals
        self.colors = colors
        self.tris = tris
        self.x = 0
        self.y = 0
        self.z = 0
        self.yaw = 0
        self.pitch = 0
        self.roll = 0


def read_obj(directory: str, obj_file_name: str, *, flip: bool = False) -> Mesh:
    if directory:
        directory += PATH_SEPERATOR
    if flip:
        normal_sign = -1
    else:
        normal_sign = 1

    obj_path = directory + obj_file_name
    with open(obj_path, "r") as obj_file:
        obj_text = obj_file.read()

    vertices: list[Vec3] = []
    normals: list[Vec3] = []
    colors: list[Color] = [DEFAULT_COLOR]
    tris: list[Tri] = []

    mtls: list[str] = [""]
    selected_mtl = 0

    for obj_line in obj_text.split("\n"):
        if obj_line.split(" ")[0] == "vn":
            normals.append((0, 0, 0))

    for obj_line in obj_text.split("\n"):
        obj_data = obj_line.split(" ")
        if obj_data[0] == "mtllib":

            mtl_path = directory + obj_data[1]
            with open(mtl_path, "r") as mtl_file:
                mtl_text = mtl_file.read()

            current_mtl = ""
            for mtl_line in mtl_text.split("\n"):
                mtl_data = mtl_line.split(" ")
                if mtl_data[0] == "newmtl":
                    current_mtl = mtl_data[1]
                    if current_mtl not in mtls:
                        mtls.append(current_mtl)
                        colors.append((0, 0, 0))
                elif mtl_data[0] == "Kd":
                    colors[mtls.index(current_mtl)] = (float(mtl_data[1]),
                                                       float(mtl_data[2]),
                                                       float(mtl_data[3]))

        elif obj_data[0] == "usemtl":
            selected_mtl = mtls.index(obj_data[1])
        elif obj_data[0] == "v":
            vertices.append((float(obj_data[1]),
                             float(obj_data[2]),
                             float(obj_data[3])))
        elif obj_data[0] == "vn":
            normals.append((float(obj_data[1]) * normal_sign,
                            float(obj_data[2]) * normal_sign,
                            float(obj_data[3]) * normal_sign))
        elif obj_data[0] == "f":
            a = int(obj_data[1].split("/")[0]) - 1
            b = int(obj_data[2].split("/")[0]) - 1
            c = int(obj_data[3].split("/")[0]) - 1
            if len(obj_data[1].split("/")) == 3:
                normal = int(obj_data[1].split("/")[2]) - 1
            elif len(obj_data[2].split("/")) == 3:
                normal = int(obj_data[2].split("/")[2]) - 1
            elif len(obj_data[3].split("/")) == 3:
                normal = int(obj_data[3].split("/")[2]) - 1
            else:
                x1 = vertices[b][0] - vertices[a][0]
                y1 = vertices[b][1] - vertices[a][1]
                z1 = vertices[b][2] - vertices[a][2]
                x2 = vertices[c][0] - vertices[a][0]
                y2 = vertices[c][1] - vertices[a][1]
                z2 = vertices[c][2] - vertices[a][2]
                nx, ny, nz = cross_product(x1, y1, z1, x2, y2, z2)
                new_normal = normalize(nx * normal_sign, ny * normal_sign, nz * normal_sign)
                if new_normal not in normals:
                    normals.append(new_normal)
                normal = normals.index(new_normal)
            tris.append((a, b, c, normal, selected_mtl))

    return Mesh(vertices, normals, colors, tris)


def write_obj(directory: str, obj_file_name: str, mtl_file_name: str, mesh: Mesh):
    obj_text = f"mtllib {mtl_file_name}\n"
    mtl_text = ""
    selected_mtl = 0
    mesh.tris.sort(key=lambda p_tri: p_tri[4])
    for x, y, z in mesh.vertices:
        obj_text += f"v {x} {y} {z}\n"
    for x, y, z in mesh.normals:
        obj_text += f"vn {x} {y} {z}\n"
    for a, b, c, n, mtl in mesh.tris:
        color = mesh.colors[mtl]
        if mtl != selected_mtl:
            mtl_text += f"newmtl {mtl}\n"
            mtl_text += f"Kd {color[0]} {color[1]} {color[2]}\n"
            obj_text += f"usemtl {mtl}\n"
            selected_mtl = mtl
        obj_text += f"f {a + 1}//{n + 1} {b + 1}//{n + 1} {c + 1}//{n + 1}\n"
    if directory:
        directory += PATH_SEPERATOR
    obj_path = directory + obj_file_name
    mtl_path = directory + mtl_file_name
    with open(obj_path, "w") as obj_file:
        obj_file.write(obj_text)
    with open(mtl_path, "w") as mtl_file:
        mtl_file.write(mtl_text)


class Scene:
    def __init__(self, meshes: list[Mesh]):
        self.meshes = meshes
        self._view_vertices: list[Vec3] = []
        self._world_normals: list[Vec3] = []
        self._draw_vertices: list[Vec2] = []
        self._draw_tris: list[tuple[float, Vec2, Vec2, Vec2, Vec3]] = []
        self.camera_x = 0
        self.camera_y = 0
        self.camera_z = 0
        self.camera_yaw = 0
        self.camera_pitch = 0
        self.camera_roll = 0
        self.camera_fov = 90
        self.camera_z_near = 0.01

    def move_camera(self, x: float = 0, y: float = 0, z: float = 0, yaw: float = 0, pitch: float = 0, roll: float = 0):
        self.camera_x += x
        self.camera_y += y
        self.camera_z += z
        self.camera_yaw += yaw
        self.camera_pitch += pitch
        self.camera_roll += roll
        self.camera_yaw = 180 - (180 - self.camera_yaw) % 360
        if self.camera_pitch > 90:
            self.camera_pitch = 90
        elif self.camera_pitch < -90:
            self.camera_pitch = -90
        self.camera_roll = 180 - (180 - self.camera_roll) % 360

    def draw(self, window: Window):
        tan_half_fov = tan(self.camera_fov * 0.5)
        self._draw_tris.clear()
        for mesh_index, mesh in enumerate(self.meshes):
            self._view_vertices.clear()
            self._world_normals.clear()
            for x, y, z in mesh.vertices:
                self._view_vertices.append(rotate3(x + mesh.x - self.camera_x,
                                                   y + mesh.y - self.camera_y,
                                                   z + mesh.z - self.camera_z,
                                                   mesh.yaw - self.camera_yaw,
                                                   mesh.pitch - self.camera_pitch,
                                                   mesh.roll - self.camera_roll))
            for x, y, z in mesh.normals:
                self._world_normals.append(rotate3(x, y, z,
                                                   mesh.yaw - self.camera_yaw,
                                                   mesh.pitch - self.camera_pitch,
                                                   mesh.roll  - self.camera_roll))
            self._draw_vertices.clear()
            for vertex in self._view_vertices:
                self._draw_vertices.append(project(vertex, self.camera_z_near, tan_half_fov))
            for tri_index, tri in enumerate(mesh.tris):
                a, b, c, n, m = tri
                pa = self._draw_vertices[a]
                pb = self._draw_vertices[b]
                pc = self._draw_vertices[c]
                a_seen = pa is not None
                b_seen = pb is not None
                c_seen = pc is not None
                in_view = a_seen + b_seen + c_seen
                if in_view != 0:
                    va = self._view_vertices[a]
                    vb = self._view_vertices[b]
                    vc = self._view_vertices[c]
                    normal = self._world_normals[n]
                    nx, ny, nz = normal
                    color = ((mesh.colors[m][0] * 0.8 + 0.1) * (0.6 - nz * 0.4),
                             (mesh.colors[m][1] * 0.8 + 0.1) * (0.6 - nz * 0.4),
                             (mesh.colors[m][2] * 0.8 + 0.1) * (0.6 - nz * 0.4))
                    sx = va[0] + vb[0] + vc[0]
                    sy = va[1] + vb[1] + vc[1]
                    sz = va[2] + vb[2] + vc[2]
                    if dot_product(nx, ny, nz, sx, sy, sz) <= 0:
                        if in_view == 3:
                            self._draw_tris.append((sz, pa, pb, pc, color))
                        else:
                            one_in_front = 2 - in_view
                            if a_seen == one_in_front:
                                i1 = a
                                i2 = b
                                i3 = c
                            elif b_seen == one_in_front:
                                i1 = b
                                i2 = c
                                i3 = a
                            else:
                                i1 = c
                                i2 = a
                                i3 = b
                            v1 = self._view_vertices[i1]
                            v2 = self._view_vertices[i2]
                            v3 = self._view_vertices[i3]
                            v4 = clip3(v1, v2, self.camera_z_near)
                            v5 = clip3(v1, v3, self.camera_z_near)
                            p1 = self._draw_vertices[i1]
                            p2 = self._draw_vertices[i2]
                            p3 = self._draw_vertices[i3]
                            p4 = project(v4, None, tan_half_fov)
                            p5 = project(v5, None, tan_half_fov)
                            if in_view == 1:
                                self._draw_tris.append((sz, p1, p4, p5, color))
                            else:
                                self._draw_tris.append((sz, p2, p3, p5, color))
                                self._draw_tris.append((sz, p5, p4, p2, color))
        self._draw_tris.sort(key=lambda p_tri: p_tri[0], reverse=True)
        for _, a, b, c, color in self._draw_tris:
            turtle.color(color)
            draw_tri(a, b, c, window.width, window.height)


def main():
    directory = input("Enter directory: ")
    file_name = input("Enter obj file name: ")
    move_speed = float(input("Enter speed: "))

    window = Window(500, 500, "3D Viewer")
    mesh = read_obj(directory, file_name)
    scene = Scene([mesh])

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
        scene.move_camera(0, 0, 0, delta_yaw, delta_pitch, 0)
        delta_x = (window.key_pressed("d") - window.key_pressed("a")) * move_speed
        delta_y = (window.key_pressed("space") - window.key_pressed("Shift_L")) * move_speed
        delta_z = (window.key_pressed("w") - window.key_pressed("s")) * move_speed
        delta_z, delta_x = rotate2(delta_z, delta_x, scene.camera_yaw)
        scene.move_camera(delta_x, delta_y, delta_z, 0, 0, 0)

        scene.draw(window)
        running = window.update()


if __name__ == "__main__":
    main()
