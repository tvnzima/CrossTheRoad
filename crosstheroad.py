from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random


player_pos = [0, -800, 60] 
player_cloth_color = [1, 0, 0]  
lives = 3  
points = 0 
game_over = False
game_won = False
vehicles = [] 
logs = []  
coins = []  
camera_pos = [0, -400, 400]  
fovY = 90 
GRID_LENGTH = 600
ZEBRA_X_MIN, ZEBRA_X_MAX = -100, 100
GOAL_Y = 0 
god_mode = False  
level = 1
max_levels = 3 
maps = []  
map_y_ranges = []  
safe_y_ranges = []  
last_map = 'highway'

def reset_game():
    global player_pos, player_cloth_color, lives, points, game_over, game_won, vehicles, logs, coins, god_mode, maps, map_y_ranges, safe_y_ranges, GOAL_Y, last_map
    player_pos = [0, -800, 60] 
    player_cloth_color = [random.random(), random.random(), random.random()]
    lives = 3
    points = 0  
    game_over = False
    game_won = False
    vehicles.clear()
    logs.clear()
    coins.clear() 
    god_mode = False
   
    map_y_ranges.clear()
    
    if last_map == 'river':
        maps = ['highway', 'river', 'highway']  
    else:
        maps = random.choice([
            ['highway', 'river', 'highway'],
            ['highway', 'river', 'highway', 'highway'],
            ['highway', 'highway', 'river', 'highway']
        ])
   
    safe_y_ranges = [(-800, -600)]  
    y_start = -600
    for i, map_type in enumerate(maps):
        map_y_ranges.append((y_start, y_start + 200))
        if i < len(maps) - 1:
            safe_y_ranges.append((y_start + 200, y_start + 250))
        y_start += 250
    GOAL_Y = map_y_ranges[-1][1]  
    safe_y_ranges.append((GOAL_Y, GOAL_Y + 250))  
    last_map = maps[-1]
    init_vehicles()
    init_logs()
    init_coins()
    print(f"Reset game: maps={maps}, map_y_ranges={map_y_ranges}, safe_y_ranges={safe_y_ranges}, GOAL_Y={GOAL_Y}")

def init_vehicles():
    global vehicles
    vehicles = []
    for i, (y_min, y_max) in enumerate(map_y_ranges):
        if maps[i] != 'highway':
            continue
        for _ in range(3):  
            y = random.uniform(y_min, y_max)
            x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            vtype = random.choice(['car', 'truck', 'bus'])
            speed = random.uniform(0.2, 0.4) + 0.05 * (level - 1)
            speed *= random.choice([-1, 1])
            vehicles.append([x, y, 60, vtype, speed, i])  
            print(f"Spawned vehicle {vtype} at x={x}, y={y}, map_index={i} (highway: {y_min} to {y_max})")

def init_logs():
    global logs
    logs = []
    for i, (y_min, y_max) in enumerate(map_y_ranges):
        if maps[i] != 'river':
            continue
        for _ in range(8):  
            y = random.uniform(y_min, y_max)
            x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            speed = (0.2 + 0.05 * (level - 1)) * random.choice([-1, 1])
            logs.append([x, y, 60, speed])
            print(f"Spawned log at x={x}, y={y} (river: {y_min} to {y_max})")

def init_coins():
    global coins
    coins = []
  
    for i, (y_min, y_max) in enumerate(map_y_ranges):
        if maps[i] != 'highway':
            continue
        for _ in range(3): 
            x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            y = random.uniform(y_min, y_max)
            coins.append([x, y, 60, True])  
            print(f"Spawned coin at x={x}, y={y} (highway: {y_min} to {y_max})")
 
    for y_min, y_max in safe_y_ranges:
        for _ in range(2):  
            x = random.uniform(-GRID_LENGTH, GRID_LENGTH)
            y = random.uniform(y_min, y_max)
            coins.append([x, y, 60, True]) 
            print(f"Spawned coin at x={x}, y={y} (safe zone: {y_min} to {y_max})")

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
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

def draw_student():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], player_pos[2])
  
    glColor3fv(player_cloth_color)
    glutSolidCube(40)

    glPushMatrix()
    glTranslatef(0, 0, 30)
    glColor3f(0, 0, 0)
    gluSphere(gluNewQuadric(), 15, 10, 10)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(-10, 0, -20)
    glColor3f(0.5, 0.5, 0.5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 30, 10, 10)
    glPopMatrix()
  
    glPushMatrix()
    glTranslatef(10, 0, -20)
    glColor3f(0.5, 0.5, 0.5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 5, 5, 30, 10, 10)
    glPopMatrix()
  
    glPushMatrix()
    glTranslatef(0, 10, 0)
    glColor3f(1, 1, 1)
    glutSolidCube(10)
 
    glColor3f(0, 0, 1)
    glTranslatef(0, 0, 5)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 1, 1, 20, 10, 10)

    glColor3f(1, 1, 1)
    glTranslatef(0, 0, 20)
    gluSphere(gluNewQuadric(), 3, 10, 10)
    glPopMatrix()
    glPopMatrix()

def draw_vehicles():
    for x, y, z, vtype, _, _ in vehicles:
        glPushMatrix()
        glTranslatef(x, y, z)
        if vtype == 'car':
            glColor3f(1, 0, 0)
            glutSolidCube(60)
        elif vtype == 'truck':
            glColor3f(0, 1, 0)
            glScalef(1.5, 1, 1)
            glutSolidCube(80)
        elif vtype == 'bus':
            glColor3f(1, 1, 0)
            glScalef(2, 0.8, 1)
            glutSolidCube(60)
        glPopMatrix()

def draw_logs():
    for x, y, z, _ in logs:
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(0.6, 0.4, 0.2)
        glScalef(3, 1.5, 0.5)  
        glutSolidCube(40)
        glPopMatrix()

def draw_coins():
    for x, y, z, active in coins:
        if not active:
            continue
        glPushMatrix()
        glTranslatef(x, y, z)
        glColor3f(1, 1, 0) 
        gluSphere(gluNewQuadric(), 10, 10, 10)  
        glPopMatrix()

def keyboardListener(key, x, y):
    global player_pos, game_over, game_won, god_mode, points
    if game_over or game_won:
        if key == b'r':
            global level
            level = 1  
            points = 0  
            reset_game()
        return
    if key in [b'g', b'G']: 
        god_mode = not god_mode
        return
    grid_step = 40
    x, y, z = player_pos
    new_x, new_y = x, y
    if key == b'w' and y < GOAL_Y:
        new_y += grid_step
    if key == b's' and y > -GRID_LENGTH:
        new_y -= grid_step
    if key == b'a' and x > -GRID_LENGTH:
        new_x -= grid_step
    if key == b'd' and x < GRID_LENGTH:
        new_x += grid_step
    player_pos[0], player_pos[1] = new_x, new_y
    print(f"Player moved to x={player_pos[0]}, y={player_pos[1]}, z={player_pos[2]}")

def specialKeyListener(key, x, y):
    global camera_pos
    x, y, z = camera_pos
    if key == GLUT_KEY_LEFT:
        x -= 10
    if key == GLUT_KEY_RIGHT:
        x += 10
    if key == GLUT_KEY_UP:
        z += 10
    if key == GLUT_KEY_DOWN:
        z = max(100, z - 10)
    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    pass 

def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    x, y, z = camera_pos
    target_x, target_y, target_z = player_pos
 
    camera_y = max(-500, min(GOAL_Y - 200, target_y - 300))
    gluLookAt(x, camera_y, z, target_x, target_y, target_z, 0, 0, 1)

def update_game():
    global vehicles, logs, coins, lives, points, game_over, game_won, player_pos, level, last_map
    if game_over or game_won:
        return
   
    for vehicle in vehicles:
        x, y, z, vtype, speed, map_index = vehicle
        vehicle[0] += speed 
       
        if map_index < len(maps) and maps[map_index] == 'highway':
            y_min, y_max = map_y_ranges[map_index]
            if vehicle[0] < -GRID_LENGTH - 100:
                vehicle[0] = GRID_LENGTH + 100
                vehicle[1] = random.uniform(y_min, y_max)
                print(f"Respawned vehicle {vtype} at x={vehicle[0]}, y={vehicle[1]}, map_index={map_index} (highway: {y_min} to {y_max})")
            elif vehicle[0] > GRID_LENGTH + 100:
                vehicle[0] = -GRID_LENGTH - 100
                vehicle[1] = random.uniform(y_min, y_max)
                print(f"Respawned vehicle {vtype} at x={vehicle[0]}, y={vehicle[1]}, map_index={map_index} (highway: {y_min} to {y_max})")
         
            vehicle[1] = max(y_min, min(y_max, vehicle[1]))
        else:
            print(f"Warning: Vehicle {vtype} has invalid map_index={map_index}, y={y}")
       
        px, py, pz = player_pos
        in_safe_zone = any(y_min <= py <= y_max for y_min, y_max in safe_y_ranges)
        if in_safe_zone:
            continue
        vx, vy, vz = vehicle[:3]
        size = 60 if vtype == 'car' else 80 if vtype == 'truck' else 100
        if abs(px - vx) < size / 2 and abs(py - vy) < 40 and not god_mode:
            lives -= 1
            if lives <= 0:
                game_over = True
            else:
                player_pos = [0, -800, 60]

    for log in logs:
        log[0] += log[3]
        for i, (y_min, y_max) in enumerate(map_y_ranges):
            if log[1] >= y_min and log[1] <= y_max:
                if log[0] < -GRID_LENGTH - 100:
                    log[0] = GRID_LENGTH + 100
                    log[1] = random.uniform(y_min, y_max)
                    print(f"Respawned log at x={log[0]}, y={log[1]} (river: {y_min} to {y_max})")
                elif log[0] > GRID_LENGTH + 100:
                    log[0] = -GRID_LENGTH - 100
                    log[1] = random.uniform(y_min, y_max)
                    print(f"Respawned log at x={log[0]}, y={log[1]} (river: {y_min} to {y_max})")
                break

    px, py, pz = player_pos
    in_river = False
    for i, (y_min, y_max) in enumerate(map_y_ranges):
        if maps[i] == 'river' and y_min < py < y_max:
            in_river = True
            on_log = False
            for log in logs:
                lx, ly, lz = log[:3]
                if abs(px - lx) < 120 and abs(py - ly) < 60:  
                    on_log = True
                    player_pos[0] += log[3] 
                    player_pos[0] = max(-GRID_LENGTH, min(GRID_LENGTH, player_pos[0]))
                    break
            if not on_log and not god_mode:
                lives -= 1
                if lives <= 0:
                    game_over = True
                else:
                    player_pos = [0, -800, 60]
            break
  
    for coin in coins:
        cx, cy, cz, active = coin
        if not active:
            continue
        
        if abs(px - cx) < 20 and abs(py - cy) < 20 and abs(pz - cz) < 20:
            coin[3] = False 
            points += 1
            print(f"Collected coin at x={cx}, y={cy}, points={points}")
  
    if py > safe_y_ranges[-1][0]:
        player_pos[1] = safe_y_ranges[-1][0]
        print(f"Clamped y to {player_pos[1]} to prevent overshooting goal")
    
    if player_pos[1] >= GOAL_Y:
        last_map = maps[-1] 
        level += 1
        if level > max_levels:
            game_won = True
        else:
            player_pos = [0, -800, 60]
            vehicles.clear()
            logs.clear()
            coins.clear()
            reset_game()
    print(f"Update: Player at x={px}, y={py}, z={pz}, in_river={in_river}")
   
    for i, (x, y, _, vtype, _, map_index) in enumerate(vehicles):
        for j, (y_min, y_max) in enumerate(map_y_ranges):
            if maps[j] == 'river' and y_min <= y <= y_max:
                print(f"Warning: Vehicle {vtype} #{i} in river at x={x}, y={y}, map_index={map_index}")

def idle():
    update_game()
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    setupCamera()

   
    glBegin(GL_QUADS)
   
    for y_min, y_max in safe_y_ranges:
        if y_min >= GOAL_Y: 
            glColor3f(0, 1, 0) 
        else:
            glColor3f(0.53, 0.53, 0.53)  
        glVertex3f(-GRID_LENGTH, y_min, 0)
        glVertex3f(GRID_LENGTH, y_min, 0)
        glVertex3f(GRID_LENGTH, y_max, 0)
        glVertex3f(-GRID_LENGTH, y_max, 0)
  
    for i, (y_min, y_max) in enumerate(map_y_ranges):
        if maps[i] == 'highway':
            glColor3f(0, 0, 0)  
        else:  
            glColor3f(0, 0, 1)  
        glVertex3f(-GRID_LENGTH, y_min, 0)
        glVertex3f(GRID_LENGTH, y_min, 0)
        glVertex3f(GRID_LENGTH, y_max, 0)
        glVertex3f(-GRID_LENGTH, y_max, 0)
    glEnd()
 
    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    for i, (y_min, y_max) in enumerate(map_y_ranges):
        if maps[i] != 'highway':
            continue
        for y in range(int(y_min), int(y_max) - 1, 40):
            glVertex3f(ZEBRA_X_MIN, y, 1)
            glVertex3f(ZEBRA_X_MAX, y, 1)
            glVertex3f(ZEBRA_X_MAX, y + 20, 1)
            glVertex3f(ZEBRA_X_MIN, y + 20, 1)
    glEnd()

    draw_student()
    draw_vehicles()
    draw_logs()
    draw_coins()

    draw_text(10, 770, f"Lives: {lives}")
    draw_text(200, 770, f"Points: {points}")
    draw_text(400, 770, f"Level: {level}")
    if god_mode:
        draw_text(800, 770, "God Mode: ON")
    if game_over:
        draw_text(400, 400, "Game Over! Press R to Restart")
    if game_won:
        draw_text(400, 400, "You Win! Press R to Restart")

    glutSwapBuffers()

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Campus Crossing")
    glEnable(GL_DEPTH_TEST)
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    reset_game()
    glutMainLoop()

if __name__ == "__main__":
    main()
