import math

class SceneManager:
    def __init__(self, engine):
        self.engine = engine

    def draw(self, canvas, plc_color, ar_color, robot_active):
        canvas.delete("all")
        w = max(canvas.winfo_width(), 10)
        h = max(canvas.winfo_height(), 10)
        
        # 1. Tegn Gitter (Gulv)
        for i in range(-5, 6, 2):
            p1 = self.engine.project_3d(i*0.3, -0.9, -1, w, h)
            p2 = self.engine.project_3d(i*0.3, -0.9, 1, w, h)
            canvas.create_line(p1, p1, p2, p2, fill="#1e293b")
            p3 = self.engine.project_3d(-1, -0.9, i*0.3, w, h)
            p4 = self.engine.project_3d(1, -0.9, i*0.3, w, h)
            canvas.create_line(p3, p3, p4, p4, fill="#1e293b")

        # 2. Tegn Styreskabet og PLC-komponenter
        self.engine.render_box(canvas, 1.2, 1.8, 0.5, "#334155", False, w, h)
        self.engine.render_box(canvas, 0.8, 0.2, 0.05, "#1e293b", False, w, h, 0, 0.2, 0.26)
        
        plc_x, plc_y, plc_z = -0.2, 0.2, 0.3
        self.engine.render_box(canvas, 0.2, 0.3, 0.15, plc_color, False, w, h, plc_x, plc_y, plc_z)
        for i in range(3):
            self.engine.render_box(canvas, 0.12, 0.3, 0.12, "#475569", False, w, h, 0.05 + (i * 0.15), 0.2, 0.28)
        
        # --- TRANSPORTBÅND & KASSEBEREGNING (PLAN MED GULVET FORAN ROBOTTEN) ---
        conv_x, conv_y, conv_z = 0.6, -0.8, 0.4
        
        if robot_active:
            self.engine.time_counter += 0.04
            self.engine.conveyor_counter += 0.012 

        target_box_x = 0.0
        
        # Tegn de 2 produktionskasser på båndet
        for k in range(2):
            box_offset = (self.engine.conveyor_counter + (k * 0.6)) % 1.2
            box_x = (conv_x + 0.6) - box_offset
            # Justeret højde og flad form, så de ligger rigtigt oven på det vandrette bånd
            box_y = conv_y + 0.08
            box_z = conv_z
            
            if k == 0:
                target_box_x = box_x
                
            # RETTELSE: Rettet dimensioner (w=0.12, h=0.08, d=0.12) så kassen er flad mod gulvet
            self.engine.render_box(canvas, 0.12, 0.08, 0.12, "#b45309", False, w, h, box_x, box_y, box_z)

        # RETTELSE: Rettet dimensioner på båndet (w=1.2, h=0.04, d=0.25) så det ligger helt fladt og plan med gulvet
        self.engine.render_box(canvas, 1.2, 0.04, 0.25, "#1e293b", False, w, h, conv_x, conv_y, conv_z)
        
        # Benene er tilpasset det flade bånd, så de står stabilt på gulvgitteret
        self.engine.render_box(canvas, 0.05, 0.1, 0.2, "#334155", False, w, h, conv_x - 0.5, conv_y - 0.05, conv_z)
        self.engine.render_box(canvas, 0.05, 0.1, 0.2, "#334155", False, w, h, conv_x + 0.5, conv_y - 0.05, conv_z)

        # --- 🎯 GEOMETRISK INVERS KINEMATIK TIL 3-ARMS SERIEL ROBOT ---
        len_1 = 0.2   # Højde på Base
        len_2 = 0.45  # Højde på Underarm
        len_3 = 0.35  # Højde på Overarm
        
        bx, by, bz = 0.6, -0.8, 0.6  # Robottens bund på gulvet

        if robot_active:
            # 1. Base rotation (J1 / Yaw)
            delta_x = target_box_x - bx
            delta_z = conv_z - bz
            self.engine.rot_base = math.atan2(-delta_x, delta_z)
            
            # 2. Invers Kinematik til J2 og J3 (Målet tilpasses den nye flade kassehøjde)
            target_y = conv_y + 0.12
            dist_xz = math.sqrt(delta_x**2 + delta_z**2)
            j2_height = by + len_1
            dist_y = target_y - j2_height
            
            hypotenuse = math.sqrt(dist_xz**2 + dist_y**2)
            hypotenuse = min(hypotenuse, (len_2 + len_3) * 0.99)
            
            cos_j3 = (len_2**2 + len_3**2 - hypotenuse**2) / (2 * len_2 * len_3)
            cos_j3 = max(-1.0, min(1.0, cos_j3))
            angle_j3 = math.acos(cos_j3)
            
            angle_base_to_target = math.atan2(dist_xz, -dist_y)
            cos_j2 = (len_2**2 + hypotenuse**2 - len_3**2) / (2 * len_2 * hypotenuse)
            cos_j2 = max(-1.0, min(1.0, cos_j2))
            angle_j2_inner = math.acos(cos_j2)
            
            self.engine.rot_under = -(angle_base_to_target - angle_j2_inner)
            self.engine.rot_over = -(math.pi - angle_j3)
            
        # --- TEGN CYLINDER-KÆDEN ---
        # J1: Base Cylinder
        c1_y = by + (len_1 / 2)
        self.engine.render_cylinder(canvas, 0.15, len_1, "#4b5563", w, h, bx, c1_y, bz, r_y=self.engine.rot_base)

        # J2: Underarm Cylinder
        c2_x = bx + (len_2 / 2) * math.sin(self.engine.rot_under) * math.sin(self.engine.rot_base)
        c2_y = (by + len_1) + (len_2 / 2) * math.cos(self.engine.rot_under)
        c2_z = bz + (len_2 / 2) * math.sin(self.engine.rot_under) * math.cos(self.engine.rot_base)
        self.engine.render_cylinder(canvas, 0.07, len_2, "#f59e0b", w, h, c2_x, c2_y, c2_z, r_x=self.engine.rot_under, r_y=self.engine.rot_base)

        # J3: Overarm Cylinder (Rammer nu den flade overflade perfekt)
        j2_end_x = bx + len_2 * math.sin(self.engine.rot_under) * math.sin(self.engine.rot_base)
        j2_end_y = by + len_1 + len_2 * math.cos(self.engine.rot_under)
        j2_end_z = bz + len_2 * math.sin(self.engine.rot_under) * math.cos(self.engine.rot_base)
        
        total_pitch = self.engine.rot_under + self.engine.rot_over
        c3_x = j2_end_x + (len_3 / 2) * math.sin(total_pitch) * math.sin(self.engine.rot_base)
        c3_y = j2_end_y + (len_3 / 2) * math.cos(total_pitch)
        c3_z = j2_end_z + (len_3 / 2) * math.sin(total_pitch) * math.cos(self.engine.rot_base)
        self.engine.render_cylinder(canvas, 0.04, len_3, "#10b981", w, h, c3_x, c3_y, c3_z, r_x=total_pitch, r_y=self.engine.rot_base)

        # 4. Ydre AR Trådnet (Hologram omkring styreskabet)
        self.engine.render_box(canvas, 1.3, 1.9, 0.6, ar_color, True, w, h)

        # --- DYNAMISKE 3D TEKSTLABELS ---
        text_plc_x, text_plc_y = self.engine.project_3d(plc_x, plc_y + 0.25, plc_z, w, h)
        canvas.create_text(text_plc_x, text_plc_y, text="[ SAFETY PLC ]", fill="#38bdf8", font=("Arial", 9, "bold"))

        text_rob_x, text_rob_y = self.engine.project_3d(bx, by + 1.1, bz, w, h)
        canvas.create_text(text_rob_x, text_rob_y, text="[ 3-AXIS ROBOT ]", fill="#fbbf24", font=("Arial", 9, "bold"))
