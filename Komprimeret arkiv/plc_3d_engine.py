import math

class Engine3D:
    def __init__(self):
        self.angle_x = 0.3
        self.angle_y = 0.5
        self.zoom = 200.0
        
        self.time_counter = 0.0
        self.conveyor_counter = 0.0
        
        self.rot_base = 0.0
        self.rot_under = 0.0
        self.rot_over = 0.0

    def project_3d(self, x, y, z, canvas_w, canvas_h, off_x=0, off_y=0, off_z=0):
        x += off_x
        y += off_y
        z += off_z

        cos_x, sin_x = math.cos(self.angle_x), math.sin(self.angle_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

        cos_y, sin_y = math.cos(self.angle_y), math.sin(self.angle_y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

        cx = canvas_w / 2
        cy = canvas_h / 2
        
        screen_x = cx + (x * self.zoom) / (1 + z * 0.1)
        screen_y = cy - (y * self.zoom) / (1 + z * 0.1)
        return screen_x, screen_y

    def render_box(self, canvas, w, h, d, color, is_wire, cx, cy, ox=0, oy=0, oz=0):
        vertices = [
            (-w/2, -h/2, -d/2), (w/2, -h/2, -d/2), (w/2, h/2, -d/2), (-w/2, h/2, -d/2),
            (-w/2, -h/2, d/2),  (w/2, -h/2, d/2),  (w/2, h/2, d/2),  (-w/2, h/2, d/2)
        ]
        # RETTELSE: Pakker de 3 tupler (X, Y, Z) ud som separate værdier
        points = [self.project_3d(v[0], v[1], v[2], cx, cy, ox, oy, oz) for v in vertices]
        faces = [(0,1,2,3), (4,5,6,7), (0,1,5,4), (2,3,7,6), (0,3,7,4), (1,2,6,5)]

        if is_wire:
            for face in faces:
                for i in range(4):
                    canvas.create_line(points[face[i]], points[face[(i+1)%4]], fill=color, width=2)
        else:
            for face in faces:
                poly = []
                for idx in face: poly.extend(points[idx])
                canvas.create_polygon(poly, fill=color, outline="#1e293b", width=1)

    def render_cylinder(self, canvas, radius, height, color, cx, cy, ox=0, oy=0, oz=0, r_x=0.0, r_y=0.0):
        segments = 8
        vertices = []
        h = height / 2

        for i in range(segments):
            angle = (i * 2 * math.pi) / segments
            x_c = radius * math.cos(angle)
            z_c = radius * math.sin(angle)
            vertices.append((x_c, -h, z_c))
            vertices.append((x_c, h, z_c))

        cos_y, sin_y = math.cos(r_y), math.sin(r_y)
        cos_x, sin_x = math.cos(r_x), math.sin(r_x)
        rotated_vertices = []
        for vx, vy, vz in vertices:
            vy_new = vy * cos_x - vz * sin_x
            vz_new = vy * sin_x + vz * cos_x
            vx_new = vx * cos_y + vz_new * sin_y
            vz_final = -vx * sin_y + vz_new * cos_y
            rotated_vertices.append((vx_new, vy_new, vz_final))

        # RETTELSE: Pakker de 3 tupler (X, Y, Z) ud som separate værdier
        points = [self.project_3d(v[0], v[1], v[2], cx, cy, ox, oy, oz) for v in rotated_vertices]

        for i in range(segments):
            b1 = i * 2
            t1 = b1 + 1
            b2 = ((i + 1) % segments) * 2
            t2 = b2 + 1
            
            side_poly = []
            side_poly.extend(points[b1])
            side_poly.extend(points[b2])
            side_poly.extend(points[t2])
            side_poly.extend(points[t1])
            canvas.create_polygon(side_poly, fill=color, outline="#1e293b", width=1)
