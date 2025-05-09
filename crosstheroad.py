from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import sys
import time


class GameState:
    def __init__(self):
        self.player_pos = [0, -800, 0] 
        self.player_color = [random.random(), random.random(), random.random()]
        self.lives = 3
        self.points = 0  
        self.level = 1
        self.max_levels = 3
        self.game_over = False
        self.game_won = False
        self.god_mode = False
        self.night_mode = False
        self.vehicles = []
        self.logs = []
        self.coins = [] 
        self.current_log = None
        self.invincible_until = None
        self.camera_pos = [100, -400, 400]
        self.fovY = 110
        self.GRID_LENGTH = 600
        self.RIVER_WIDTH = 500
        self.ZEBRA_X_MIN, self.ZEBRA_X_MAX = -100, 100
        self.GOAL_Y = 0
        self.maps = []
        self.map_y_ranges = []
        self.safe_y_ranges = []
        self.last_map = 'highway'
        self.last_move_key = None

    def reset(self):
        self.player_pos = [0, -800, 0]  
        self.player_color = [random.random(), random.random(), random.random()]
        self.lives = 3
        self.points = 0  
        self.game_over = False
        self.game_won = False
        self.god_mode = False
        self.invincible_until = None
        self.vehicles.clear()
        self.logs.clear()
        self.coins.clear() 
        self.current_log = None
        self.last_move_key = None
        self.maps = random.choice([
            ['highway', 'river', 'highway'],
            ['highway', 'river', 'highway', 'highway'],
            ['highway', 'highway', 'river', 'highway']
        ]) if self.last_map != 'river' else ['highway', 'river', 'highway']
        self.map_y_ranges = []
        self.safe_y_ranges = [(-800, -600)]
        y_start = -600
        for i, map_type in enumerate(self.maps):
            self.map_y_ranges.append((y_start, y_start + 200))
            if i < len(self.maps) - 1:
                self.safe_y_ranges.append((y_start + 200, y_start + 250))
            y_start += 250
        self.GOAL_Y = self.map_y_ranges[-1][1]
        self.safe_y_ranges.append((self.GOAL_Y, self.GOAL_Y + 250))
        self.last_map = self.maps[-1]
        self.init_vehicles()
        self.init_logs()
        self.init_coins()

    def init_vehicles(self):
        self.vehicles = []
        for i, (y_min, y_max) in enumerate(self.map_y_ranges):
            if self.maps[i] != 'highway':
                continue
            for _ in range(1):
                y = random.uniform(y_min + 20, y_max)
                x = random.uniform(-self.GRID_LENGTH, self.GRID_LENGTH)
                vtype = random.choice(['car', 'truck', 'bus'])
                speed = random.uniform(0.6, 1.0) + 0.1 * (self.level - 1)
                speed *= random.choice([-1, 1])
                self.vehicles.append([x, y, 0, vtype, speed])  

    def init_logs(self):
        self.logs = []
        lane_positions = [50, 100, 150]
        directions = [1, -1, 1]
        for i, (y_min, y_max) in enumerate(self.map_y_ranges):
            if self.maps[i] != 'river':
                continue
            for j, lane_y in enumerate(lane_positions):
                y = y_min + lane_y
                speed = (0.5 + 0.1 * (self.level - 1)) * directions[j]
                spacing = 100
                start_x = -self.RIVER_WIDTH if directions[j] > 0 else self.RIVER_WIDTH
                for k in range(-int(self.RIVER_WIDTH / spacing) - 1, int(self.RIVER_WIDTH / spacing) + 2):
                    x = start_x + k * spacing
                    if -self.RIVER_WIDTH <= x <= self.RIVER_WIDTH:
                        self.logs.append([x, y, 0, speed])  

    def init_coins(self):
        self.coins = []
        highway_ranges = [(y_min, y_max) for i, (y_min, y_max) in enumerate(self.map_y_ranges) if self.maps[i] == 'highway']
        grid_step = 50
        used_positions = set() 
        while len(self.coins) < 5:
            y_range = random.choice(highway_ranges)
            x_grid = random.randint(-self.GRID_LENGTH // grid_step, self.GRID_LENGTH // grid_step)
            x = x_grid * grid_step
            y_min, y_max = y_range[0] + 20, y_range[1] - 20
            y_grid = random.randint(int(y_min // grid_step), int(y_max // grid_step))
            y = y_grid * grid_step
            if y_range[0] <= y <= y_range[1] and (x, y) not in used_positions:
                self.coins.append([x, y, 0])  
                used_positions.add((x, y))

game = GameState()

def setup_lighting():
    try:
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        if game.night_mode:
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.5, 0.5, 0.5, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
            light_pos = [game.player_pos[0], game.player_pos[1], 200, 1.0]
            glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
            glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 45.0)
            spot_direction = [0.0, 0.0, -1.0]
            glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spot_direction)
            glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 2.0)
        else:
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.8, 0.8, 0.8, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [0.0, 0.0, 0.0, 1.0])
            glLightfv(GL_LIGHT0, GL_POSITION, [0, 0, 1000, 0.0])
            glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 180.0)
    except Exception as e:
        print(f"Error in setup_lighting: {e}")

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    try:
        glColor3f(1, 1, 1)
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        gluOrtho2D(0, 800, 0, 600)
        glMatrixMode(GL_MODELVIEW)
        glPushMatrix()
        glLoadIdentity()
        glRasterPos2f(x, y)
        for ch in text:
            glutBitmapCharacter(font, ord(ch))
        glPopMatrix()
        glMatrixMode(GL_PROJECTION)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
    except Exception as e:
        print(f"Error in draw_text: {e}")

def draw_human():
    try:
        glPushMatrix()
        glTranslatef(game.player_pos[0], game.player_pos[1], game.player_pos[2])
        time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        swing_angle = 20 * math.sin(3 * time) if game.last_move_key else 0
        glColor3fv(game.player_color)
        glPushMatrix()
        glTranslatef(0, 0, 15)
        glScalef(1, 0.5, 1.5)
        glutSolidCube(15)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, 35)
        glColor3f(1, 0.8, 0.6)
        gluSphere(gluNewQuadric(), 8, 8, 8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-10, 0, 25)
        glRotatef(-45, 0, 1, 0)
        glRotatef(-swing_angle, 1, 0, 0)
        glScalef(0.3, 0.3, 1.2)
        glColor3f(0.5, 0.5, 0.5)
        glutSolidCube(8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(10, 0, 25)
        glRotatef(45, 0, 1, 0)
        glRotatef(swing_angle, 1, 0, 0)
        glScalef(0.3, 0.3, 1.2)
        glColor3f(0.5, 0.5, 0.5)
        glutSolidCube(8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(-5, 0, 0)
        glRotatef(swing_angle, 1, 0, 0)
        glScalef(0.3, 0.3, 1.2)
        glColor3f(0.5, 0.5, 0.5)
        glutSolidCube(8)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(5, 0, 0)
        glRotatef(-swing_angle, 1, 0, 0)
        glScalef(0.3, 0.3, 1.2)
        glColor3f(0.5, 0.5, 0.5)
        glutSolidCube(8)
        glPopMatrix()
        glPopMatrix()
    except Exception as e:
        print(f"Error in draw_human: {e}")

def draw_vehicles():
    try:
        time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        for vehicle in game.vehicles:
            x, y, z, vtype, speed = vehicle
            glPushMatrix()
            glTranslatef(x, y, z)
            if speed < 0:
                glRotatef(180, 0, 0, 1)
            if vtype == 'car':
                glColor3f(1, 0, 0)
                glPushMatrix()
                glScalef(1, 0.5, 0.5)
                glutSolidCube(50)
                glPopMatrix()
            elif vtype == 'truck':
                glColor3f(0, 1, 0)
                glPushMatrix()
                glScalef(1.5, 0.6, 0.6)
                glutSolidCube(60)
                glPopMatrix()
            elif vtype == 'bus':
                glColor3f(1, 1, 0)
                glPushMatrix()
                glScalef(2, 0.4, 0.5)
                glutSolidCube(50)
                glPopMatrix()
            wheel_rotation = 200 * time * abs(speed)
            wheel_color = [0.2, 0.2, 0.2]
            wheel_scale = 0.3
            wheel_positions = [
                (-15, 10, -8), (-15, -10, -8),
                (15, 10, -8), (15, -10, -8)
            ]
            for wx, wy, wz in wheel_positions:
                glPushMatrix()
                glTranslatef(wx, wy, wz)
                glRotatef(wheel_rotation, 0, 1, 0)
                glScalef(wheel_scale, wheel_scale, 0.1)
                glColor3fv(wheel_color)
                glutSolidCube(15)
                glPopMatrix()
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glColor4f(0, 0.5, 1, 0.5)
            if vtype == 'car':
                glBegin(GL_QUADS)
                glVertex3f(24, -10, 5)
                glVertex3f(24, 10, 5)
                glVertex3f(24, 10, 20)
                glVertex3f(24, -10, 20)
                glEnd()
            elif vtype == 'truck':
                glBegin(GL_QUADS)
                glVertex3f(44, -12, 6)
                glVertex3f(44, 12, 6)
                glVertex3f(44, 12, 24)
                glVertex3f(44, -12, 24)
                glEnd()
            elif vtype == 'bus':
                glBegin(GL_QUADS)
                glVertex3f(49, -15, 5)
                glVertex3f(49, 15, 5)
                glVertex3f(49, 15, 20)
                glVertex3f(49, -15, 20)
                glEnd()
            glDisable(GL_BLEND)
            glPopMatrix()
    except Exception as e:
        print(f"Error in draw_vehicles: {e}")

def draw_logs():
    try:
        time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        for log in game.logs:
            x, y, z, speed = log
            glPushMatrix()
            glTranslatef(x, y, z + 7.5)
            if speed < 0:
                glRotatef(180, 0, 0, 1)
            glColor3f(0.6, 0.4, 0.2)
            glPushMatrix()
            glScalef(4, 1.5, 0.5)
            glutSolidCube(30)
            glPopMatrix()
            glPopMatrix()
    except Exception as e:
        print(f"Error in draw_logs: {e}")

def draw_coins():
    try:
        time = glutGet(GLUT_ELAPSED_TIME) / 1000.0
        for coin in game.coins:
            x, y, z = coin
            glPushMatrix()
            glTranslatef(x, y, z + 15)
            glColor3f(1.0, 1.0, 0.0)
            glRotatef(90, 1, 0, 0)
            glRotatef(45 * time, 0, 0, 1)
            glutSolidTorus(2, 10, 8, 8)
            glPopMatrix()
    except Exception as e:
        print(f"Error in draw_coins: {e}")

def keyboard_listener(key, x, y):
    if game.game_over or game.game_won:
        if key == b'r':
            game.level = 1
            game.reset()
        return
    if key in [b'g', b'G']:
        game.god_mode = not game.god_mode
        return
    if key in [b'n', b'N']:
        game.night_mode = not game.night_mode
        setup_lighting()
        return
    grid_step = 50
    new_x, new_y, z = game.player_pos
    in_river = False
    current_river_y_min, current_river_y_max = None, None
    for i, (y_min, y_max) in enumerate(game.map_y_ranges):
        if game.maps[i] == 'river' and y_min <= game.player_pos[1] < y_max:
            in_river = True
            current_river_y_min, current_river_y_max = y_min, y_max
            break
    if key == b'w' and new_y < game.GOAL_Y:
        new_y += grid_step
        if in_river:
            new_y = min(new_y, current_river_y_max)
        game.last_move_key = b'w'
    elif key == b's' and new_y > -game.GRID_LENGTH:
        new_y -= grid_step
        if in_river:
            new_y = max(new_y, current_river_y_min)
        game.last_move_key = b's'
    elif key == b'a' and new_x > -game.GRID_LENGTH:
        new_x -= grid_step
        game.last_move_key = b'a'
    elif key == b'd' and new_x < game.GRID_LENGTH:
        new_x += grid_step
        game.last_move_key = b'd'
    else:
        game.last_move_key = None
    if in_river and game.current_log and key in [b'a', b'd']:
        lx, ly, lz, _ = game.current_log
        if abs(new_y - ly) <= 22.5:
            new_x = lx
    game.player_pos[0], game.player_pos[1] = new_x, new_y

def special_key_listener(key, x, y):
    x, y, z = game.camera_pos
    if key == GLUT_KEY_LEFT:
        x -= 10
    elif key == GLUT_KEY_RIGHT:
        x += 10
    elif key == GLUT_KEY_UP:
        z += 10
    elif key == GLUT_KEY_DOWN:
        z = max(100, z - 10)
    game.camera_pos = [x, y, z]

def setup_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(game.fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = game.camera_pos
    target_x, target_y, target_z = game.player_pos
    camera_y = max(-500, min(game.GOAL_Y - 200, target_y - 300))
    gluLookAt(x, camera_y, z, target_x, target_y, target_z, 0, 0, 1)

def update_game():
    if game.game_over or game.game_won:
        return
    if game.player_pos[1] >= game.GOAL_Y:
        game.last_map = game.maps[-1]
        game.level += 1
        if game.level > game.max_levels:
            game.game_won = True
        else:
            game.player_pos = [0, -800, 0]
            game.current_log = None
            game.invincible_until = None
            game.reset()
        return
    for vehicle in game.vehicles:
        vehicle[0] += vehicle[4]
        for y_min, y_max in game.map_y_ranges:
            if vehicle[1] >= y_min and vehicle[1] <= y_max:
                if vehicle[0] < -game.GRID_LENGTH - 100:
                    vehicle[0] = game.GRID_LENGTH + 100
                    vehicle[1] = random.uniform(y_min + 20, y_max)
                elif vehicle[0] > game.GRID_LENGTH + 100:
                    vehicle[0] = -game.GRID_LENGTH - 100
                    vehicle[1] = random.uniform(y_min + 20, y_max)
                break
    for log in game.logs:
        log[0] += log[3]
        for y_min, y_max in game.map_y_ranges:
            if log[1] >= y_min and log[1] <= y_max:
                lane_y = log[1]
                if log[3] > 0 and log[0] > game.RIVER_WIDTH:
                    log[0] = -game.RIVER_WIDTH
                    log[1] = lane_y
                elif log[3] < 0 and log[0] < -game.RIVER_WIDTH:
                    log[0] = game.RIVER_WIDTH
                    log[1] = lane_y
                break
    px, py, pz = game.player_pos
    in_river = False
    current_river_y_min, current_river_y_max = None, None
    for i, (y_min, y_max) in enumerate(game.map_y_ranges):
        if game.maps[i] == 'river' and y_min <= py < y_max:
            in_river = True
            current_river_y_min, current_river_y_max = y_min, y_max
            break
    if any(y_min <= py <= y_max for y_min, y_max in game.safe_y_ranges) or not in_river:
        game.current_log = None
        if not in_river:
            game.invincible_until = time.time() + 1.0
    if not game.god_mode and (game.invincible_until is None or time.time() > game.invincible_until):
        
        coins_to_remove = []
        for i, coin in enumerate(game.coins):
            cx, cy, cz = coin
            if abs(px - cx) < 50 and abs(py - cy) < 50:  
                game.points += 1
                coins_to_remove.append(i)
                print("Collected coin! Points:", game.points)
        for i in sorted(coins_to_remove, reverse=True):
            game.coins.pop(i)
        
        for vehicle in game.vehicles:
            if any(y_min <= py <= y_max for y_min, y_max in game.safe_y_ranges):
                continue
            vx, vy, vz = vehicle[:3]
            vtype = vehicle[3]
            size = 50 if vtype == 'car' else 60 if vtype == 'truck' else 50
            if abs(px - vx) < size / 2 and abs(py - vy) < 40:
                print(f"Hit by {vtype}!")
                time.sleep(0.5)
                game.lives -= 1
                if game.lives <= 0:
                    game.game_over = True
                else:
                    game.player_pos = [0, -800, 0]
                    game.current_log = None
                    game.invincible_until = None
                break
    
        if in_river and not any(y_min <= py <= y_max for y_min, y_max in game.safe_y_ranges):
            if game.current_log:
                lx, ly, lz, speed = game.current_log
                log_valid = (-game.RIVER_WIDTH <= lx <= game.RIVER_WIDTH and
                             current_river_y_min <= ly < current_river_y_max and
                             game.current_log in game.logs and
                             abs(py - ly) <= 22.5)
                if log_valid:
                    game.player_pos[0] = lx
                    game.player_pos[1] = ly
                else:
                    game.current_log = None
            if not game.current_log:
                on_log = False
                for log in game.logs:
                    lx, ly, lz, _ = log
                    if abs(px - lx) <= 60 and abs(py - ly) <= 22.5:
                        on_log = True
                        game.current_log = log
                        game.player_pos[0] = lx
                        game.player_pos[1] = ly
                        break
                if not on_log:
                    print("Fell in river!")
                    time.sleep(0.5)
                    game.lives -= 1
                    if game.lives <= 0:
                        game.game_over = True
                    else:
                        game.player_pos = [0, -800, 0]
                        game.current_log = None
                        game.invincible_until = None

def idle():
    update_game()
    glutPostRedisplay()
    time.sleep(0.01)

def show_screen():
    try:
        if game.night_mode:
            glClearColor(0.1, 0.1, 0.3, 1.0)
        else:
            glClearColor(0.5, 0.7, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glViewport(0, 0, 800, 600)
        setup_camera()
        setup_lighting()
        glBegin(GL_QUADS)
        for y_min, y_max in game.safe_y_ranges:
            if y_min >= game.GOAL_Y:
                glColor3f(0, 1, 0) if not game.night_mode else glColor3f(0, 0.5, 0)
            else:
                glColor3f(0.53, 0.53, 0.53) if not game.night_mode else glColor3f(0.3, 0.3, 0.3)
            glVertex3f(-game.GRID_LENGTH, y_min, 0)
            glVertex3f(game.GRID_LENGTH, y_min, 0)
            glVertex3f(game.GRID_LENGTH, y_max, 0)
            glVertex3f(-game.GRID_LENGTH, y_max, 0)
        for i, (y_min, y_max) in enumerate(game.map_y_ranges):
            if game.maps[i] == 'highway':
                glColor3f(0, 0, 0) if not game.night_mode else glColor3f(0.2, 0.2, 0.2)
            else:
                glColor3f(0, 0, 1) if not game.night_mode else glColor3f(0, 0, 0.5)
            glVertex3f(-game.GRID_LENGTH, y_min, 0)
            glVertex3f(game.GRID_LENGTH, y_min, 0)
            glVertex3f(game.GRID_LENGTH, y_max, 0)
            glVertex3f(-game.GRID_LENGTH, y_max, 0)
        glEnd()
        glBegin(GL_QUADS)
        glColor3f(1, 1, 1) if not game.night_mode else glColor3f(0.8, 0.8, 0.8)
        for i, (y_min, y_max) in enumerate(game.map_y_ranges):
            if game.maps[i] != 'highway':
                continue
            for y in range(int(y_min), int(y_max) - 1, 40):
                glVertex3f(game.ZEBRA_X_MIN, y, 1)
                glVertex3f(game.ZEBRA_X_MAX, y, 1)
                glVertex3f(game.ZEBRA_X_MAX, y + 20, 1)
                glVertex3f(game.ZEBRA_X_MIN, y + 20, 1)
        glEnd()
        draw_human()
        draw_vehicles()
        draw_logs()
        draw_coins()
        draw_text(10, 570, f"Lives: {game.lives}")
        draw_text(150, 570, f"Points: {game.points}")
        draw_text(300, 570, f"Level: {game.level}")
        if game.god_mode:
            draw_text(600, 570, "God Mode: ON")
        draw_text(600, 550, "Night Mode" if game.night_mode else "Day Mode")
        if game.game_over:
            draw_text(300, 300, "Game Over! Press R to Restart")
        if game.game_won:
            draw_text(300, 300, "You Win! Press R to Restart")
        glutSwapBuffers()
    except Exception as e:
        print(f"Rendering error: {e}")
        game.game_over = True

def main():
    try:
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(0, 0)
        glutCreateWindow(b"Cross the Road")
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glutDisplayFunc(show_screen)
        glutKeyboardFunc(keyboard_listener)
        glutSpecialFunc(special_key_listener)
        glutIdleFunc(idle)
        game.reset()
        setup_lighting()
        glutMainLoop()
    except Exception as e:
        print(f"Error initializing OpenGL/GLUT: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
