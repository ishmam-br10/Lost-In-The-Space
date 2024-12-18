from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random

# Colors gula initiate korlam
white = (1.0, 1.0, 1.0)
red = (1.0, 0.0, 0.0)
teal = (0.0, 1.0, 1.0)
amber = (1.0, 0.75, 0.0)
green = (0.0, 1.0, 0.0)
background = (0.0, 0.0, 0.0)
pulse_frame_counter = 0
# Screen dimensions
width, height = 800, 800
game_state = 'khelchi'


thrust_length = 15  # Initial length of the thrust flames
thrust_step = 1  # Step size for increasing or decreasing thrust length

# buttons
b_width, b_height = 120, 200
b_padding = 10

# circle
shooter_position = width // 2
center_x, center_y = width //2, height // 2
radius = 20
cir_color = (1.0, 0.0, 0.0) #lal
game_state = 'khelchi'
quit = False
fall_circle = [] # je britto gule niche porse
bubbles = [] # shape change kora britto ra
projectiles = []
score = 0
miss = 0 # miss kora cirlce gula
miss_shot = 0 #koto gula shot miss korsi
timer = False

# projectile shooter banabo
def draw_projectiles():
    glColor3f(1.0, 0.5, 0.0)
    for i,j, rad in projectiles:
        draw_britto(i, j, rad)

for i in range(8):
    x = random.randint(25, width-25) # x er ekta andaje
    y = random.randint(665, 700) # random ekta y (ektu window bad diyem karon okhane amar shooter)
    rad = random.randint(20, 30) # random ekta radious
    is_pulsating = random.random() < 0.2 # 20% pulsing bubble add korbe 
    radius_step = 0.1
    if is_pulsating:
        radius_step = 2
    fall_circle.append([x, y, rad, is_pulsating, radius_step])

def init():
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
        gluOrtho2D(0, width, 0, height)

# implement eight way symmetry
def zone_finder(x1, y1, x2, y2):
    dy = y2 - y1
    dx = x2 - x1
    if abs(dy) > abs(dx):
        if dy >= 0 and dx >= 0:
            return 1
        elif dy >= 0 and dx <= 0:
            return 2
        elif dy <= 0 and dx <= 0:
            return 5
        elif dy <= 0 and dx >= 0:
            return 6
    else:
        if dy >= 0 and dx >= 0:
            return 0
        elif dy >= 0 and dx <= 0:
            return 3
        elif dy <= 0 and dx <= 0:
            return 4
        elif dy <= 0 and dx >= 0:
            return 7
# eight way symmetry other to zero ------ zero to other (translate)
def symmetry_shunno_theke_onno(x0, y0, zone):
    if zone == 0:
        return x0, y0
    elif zone == 1: #1(y,x)
        return y0, x0
    elif zone == 2: #2(-y, x)
        return -y0, x0
    elif zone == 3: #3(-x, y)
        return -x0, y0
    elif zone == 4:
        return -x0, -y0
    elif zone == 5:
        return -y0, -x0
    elif zone == 6:
        return y0, -x0
    elif zone == 7:
        return x0, -y0

def symmetry_onno_theke_shunno(x1, y1, x2, y2, zone):
    if zone == 1:
        return y1, x1, y2, x2
    elif zone == 2:
        return y1, -x1, y2, -x2
    elif zone == 3:
        return -x1, y1, -x2, y2
    elif zone == 4:
        return -x1, -y1, -x2, -y2
    elif zone == 5:
        return -y1, -x1, -y2, -x2
    elif zone == 6:
        return -y1, x1, -y2, x2
    elif zone == 7:
        return x1, -y1, x2, -y2
    return x1, y1, x2, y2


def draw_britto(xcenter, ycenter, rad, color = cir_color):
    x = 0
    y = rad
    decision_parameter = 1 - rad #decision parameter
    glPointSize(3)
    glColor3f(*color)
    glBegin(GL_POINTS)

    plot_britto_points(xcenter, ycenter, x, y)

    while x<y:
        x = x + 1
        if decision_parameter < 0:
            decision_parameter = decision_parameter + (2* (x+1))
        else:
             y = y -1
             decision_parameter = decision_parameter + (2 * ((x-y)+1))
        plot_britto_points(xcenter, ycenter, x, y)
    
    glEnd()

def plot_britto_points(xcenter, ycenter, x, y):
     for zone in range(8):
        x_transformed, y_transformed = symmetry_shunno_theke_onno(x, y, zone)
        glVertex2f(xcenter + x_transformed, ycenter + y_transformed)



# midpoint line algo implement:
def draw_midpoint_line(xp1, yp1, xp2, yp2):
    original_zone = zone_finder(xp1, yp1, xp2, yp2)
    x1_0, y1_0, x2_0, y2_0 = symmetry_onno_theke_shunno(xp1, yp1, xp2, yp2, original_zone)

    dx = x2_0 - x1_0
    dy = y2_0 - y1_0
    d = 2 * dy - dx
    dE = 2 * dy
    dNE = 2 * (dy - dx)
    x = x1_0
    y = y1_0
    glPointSize(2)
    glBegin(GL_POINTS)
    while x <= x2_0:
        a, b = symmetry_shunno_theke_onno(x, y, original_zone)
        glVertex2f(a, b)
        if d < 0:
            x += 1
            d += dE
        else:
            x += 1
            y += 1
            d += dNE
    glEnd()

# arrow akano function
def arrow_akao(x, y, dir, size):
    scale = size / 60
    if dir == 'left':
        draw_midpoint_line(x - 20 * scale, y - 10 * scale, x - 30 * scale, y)  # Left
        draw_midpoint_line(x - 20 * scale, y + 10 * scale, x - 30 * scale, y)  # Right
        draw_midpoint_line(x - 30 * scale, y, x - 10 * scale, y)  # Base


# play pause akao
def playPause(x, y, size):
    scale = size / 60
    if game_state == 'khelchi':
        draw_midpoint_line(x - 10 * scale, y + 5 * scale, x - 10 * scale, y - 10 * scale)  # Left vertical line
        draw_midpoint_line(x + 10 * scale, y + 5 * scale, x + 10 * scale, y - 10 * scale)  # Right vertical line
    else:
        draw_midpoint_line(x - 10 * scale, y + 10 * scale, x + 10 * scale, y)  # Triangle 1
        draw_midpoint_line(x - 10 * scale, y - 10 * scale, x + 10 * scale, y)  # Triangle 2
        draw_midpoint_line(x - 10 * scale, y + 10 * scale, x - 10 * scale, y - 10 * scale)

# Cross akao 
def cross(x, y, size):
    scale = size / 60
    draw_midpoint_line(x - 10 * scale, y - 10 * scale, x + 10 * scale, y + 10 * scale) 
    draw_midpoint_line(x - 10 * scale, y + 10 * scale, x + 10 * scale, y - 10 * scale)  


# button gula akaite hobe
def button_akao():
    bt_w = b_width
    bt_h = b_height
    vertical_offset = 100

    #restart button
    res_x, res_y = 50, height - bt_h - 50 + vertical_offset
    glColor3f(*amber)
    arrow_akao(res_x + bt_w // 2, res_y + bt_h //2, 'left', bt_w)


    # play pause
    playPauseX = width // 2 -bt_w // 2
    playPauseY = height - b_height - 50 + vertical_offset
    glColor3f(*amber)
    playPause(playPauseX + bt_w // 2, playPauseY + bt_h //2, bt_w)
    
    # quit button
    QuitX = width - bt_w - 50
    QuitY = height - bt_h - 50 +vertical_offset
    glColor3f(*red)
    cross(QuitX + bt_w // 2, QuitY + bt_h //2, bt_w)


# shooter 
def draw_shooter():
    global thrust_length
    x = shooter_position
    y = 50
    width = 20  
    height = 40  
    head_height = 20  
    base_height = 10  
    thrust_height = thrust_length 

    # Rectangle body
    glColor3f(0.0, 0.0, 1.0)
    draw_midpoint_line(x - width // 2, y, x - width // 2, y + height)  # Left side
    draw_midpoint_line(x + width // 2, y, x + width // 2, y + height)  # Right side
    draw_midpoint_line(x - width // 2, y + height, x + width // 2, y + height)  # Top side
    draw_midpoint_line(x - width // 2, y, x + width // 2, y)  # Bottom

    # Triangle head
    draw_midpoint_line(x - width // 2, y + height, x, y + height + head_height)  # Left diagonal
    draw_midpoint_line(x + width // 2, y + height, x, y + height + head_height)  # Right diagonal
    draw_midpoint_line(x - width // 2, y + height, x + width // 2, y + height)  # Base of the head

    # Rocket fins
    fin_height = 10  # Height of the fins
    fin_width = 10  # Width of the fins

    # Left fin
    draw_midpoint_line(x - width // 2, y, x - width // 2 - fin_width, y - fin_height)  # Left diagonal
    draw_midpoint_line(x - width // 2 - fin_width, y - fin_height, x - width // 2, y - base_height)  # Bottom line

    # Right fin
    draw_midpoint_line(x + width // 2, y, x + width // 2 + fin_width, y - fin_height)  # Right diagonal
    draw_midpoint_line(x + width // 2 + fin_width, y - fin_height, x + width // 2, y - base_height)  # Bottom line

    # Rocket thrust (flames)
    glColor3f(1.0, 1.0, 0.0)
    thrust_width = width // 6  # Width of each thrust line
    draw_midpoint_line(x - thrust_width * 2, y - base_height, x - thrust_width * 2, y - base_height - thrust_height)  # Left thrust
    draw_midpoint_line(x, y - base_height, x, y - base_height - thrust_height)  # Middle thrust
    draw_midpoint_line(x + thrust_width * 2, y - base_height, x + thrust_width * 2, y - base_height - thrust_height)  # Right thrust



def draw_falling_britto():
    global fall_circle
    for i in fall_circle:
        x, y, rad, is_pulsating, radius_step = i
        if is_pulsating:
            # pulse_color = (0.0, 1.0, 0.0)
            pulse_color = (random.uniform(0.5, 1.0), random.uniform(0.5, 1.0), random.uniform(0.5, 1.0))
            draw_britto(x, y, rad, pulse_color)  # Purple for pulsing bubbles
            # print("Creating pulsing Bubble")
            # rad += radius_step
            # if rad > 30 or rad < 15:  # Pulse limits
                # radius_step = -radius_step
        else:
            glColor3f(*cir_color)  # Default color
            draw_britto(x, y, rad)

# Button click operator
def button_click_control(x, y):
    global game_state, shooter_position, score, miss, miss_shot, projectiles
    button_w = b_width
    button_h = b_height
    vertical_offset = 70 # eigula old button_akao theke
    restX, restY = 50, height - b_height - 50 + vertical_offset # prev

    # game reset button press
    if restX <= x <= restX + b_width and restY <= y <= restY + b_height:
        reset_game()
    
    # pause button
    playPause_X = width // 2 -b_width // 2
    playPause_Y = height - b_height - 50 + vertical_offset
    if playPause_X <= x <= playPause_X + b_width and playPause_Y <= y <= playPause_Y + b_height:
        if game_state == 'khelchi':
            game_state = 'thamo'
        else:
            game_state = 'khelchi'
    
    # Quit button er kaj
    quitX = width - b_width -50
    quitY = height - b_height - 50 + vertical_offset
    if quitX <= x <= quitX + b_width and quitY <= y <= quitY + button_h:
        print("Game has been stopped")
        glutLeaveMainLoop()
        return

def reset_game():
    # mainly sob data clear kore reset kora lagbe
    global fall_circle, projectiles, score, miss, miss_shot, game_state, timer, shooter_position

    fall_circle.clear()
    projectiles.clear()
    shooter_position = width // 2
    score = 0
    miss = 0
    miss_shot = 0

    # notun kore falling cirlce
    for i in range(8):
        x = random.randint(25, width-25) # x er ekta andaje
        y = random.randint(665, 700) # random ekta y (ektu window bad diyem karon okhane amar shooter)
        rad = random.randint(20, 30) # random ekta radious
        is_pulsating = random.random() < 0.2 # 20% pulsing bubble add korbe 
        radius_step = 0
        if is_pulsating:
            radius_step = 0.1
        fall_circle.append([x, y, rad, is_pulsating, radius_step])

    
    game_state = 'khelchi'
    glutPostRedisplay()

    if not timer:
        glutTimerFunc(25, update, 0)
        timer = True

# take keyboad and mouse inputs
def mouse(button, state, x, y):
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        button_click_control(x, height - y)

def keyboard(key, x, y):
    global quit
    global shooter_position

    increament = 10
    if key == b'a':
        shooter_position = shooter_position - increament # left side e jacche

        # corner case
        if shooter_position - 20 < 0:
            print("Cannot go left anymore")
            shooter_position = 20 # 20 hoche rocket er widht
    
    elif key == b'd':
        shooter_position = shooter_position + increament
        if shooter_position + 20 > width: # right e screen er baire na jay
            shooter_position = width - 20
    
    elif key == b' ':
        projectiles.append((shooter_position, 50, 10))

import math
def guli_khaise(C1X, C1Y, C1R, C2X, C2Y, C2R):
    # guli ar ball er modder radius er distance calculate kora lagbe
    # d = root((x2 - x1)^2 + (y2 - y1)^2)
    radius_2_radius = math.sqrt((C2X - C1X)**2 + (C2Y- C1Y)**2)
    flag = 0

    if radius_2_radius < (C1R + C2R):
        flag = True
    else:
        flag = False
    return flag

def rect_circle_collision(rx, ry, rw, rh, cx, cy, cr):
    # Find the closest point on the rectangle to the circle's center
    closest_x = max(rx, min(cx, rx + rw))
    closest_y = max(ry, min(cy, ry + rh))
    
    # Calculate the distance from the circle's center to this closest point
    distance = math.sqrt((cx - closest_x) ** 2 + (cy - closest_y) ** 2)
    
    # Check if the distance is less than the circle's radius
    return distance < cr




def update(value):
    global pulse_frame_counter, fall_circle, projectiles, game_state, height, width, score, miss, miss_shot, timer
    global thrust_length, thrust_step
    if game_state == 'thamo':
        glutTimerFunc(25, update, 0)
        return

    if game_state == 'khelchi':
        pulse_frame_counter += 1
        new_guli = []
        thrust_length += thrust_step
        if thrust_length > 25 or thrust_length < 15:  # Oscillate between 15 and 25
            thrust_step = -thrust_step

        for guli in projectiles:
            guliX, guliY, guliR = guli
            guli_lagse = False

            for i in range(len(fall_circle) - 1, -1, -1):
                FallCircleX, FallCircleY, FallR, is_pulsating, radius_step = fall_circle[i]
                if guli_khaise(FallCircleX, FallCircleY, FallR, guliX, guliY, guliR):
                    if is_pulsating:
                        score += 5
                        print("You hit a pulsing bubble! +5 points!")
                    else:
                        score += 1
                    print(f"Score: {score}")
                    fall_circle.pop(i)
                    guli_lagse = True

                    # Generate a new circle
                    Nx = random.randint(25, width - 25)
                    Ny = random.randint(665, 700)
                    Nrad = random.randint(20, 30)
                    Nis_pulsating = random.random() < 0.2
                    Nradius_step = 0.1 if Nis_pulsating else 0
                    fall_circle.append([Nx, Ny, Nrad, Nis_pulsating, Nradius_step])
                    break

            if not guli_lagse:
                Ny = guliY + 40
                if Ny < height:
                    new_guli.append((guliX, Ny, guliR))
                else:
                    miss_shot += 1
                    print(f"Missed shots : {miss_shot}")  # Missed shot

        projectiles = new_guli

    # Update falling circles
    for i in range(len(fall_circle)):
        Fx, Fy, rad, is_pulsating, radius_step = fall_circle[i]
        Fy -= 0.8  # Move down
        if is_pulsating and pulse_frame_counter % 15 == 0:
            # print(f"Creating pulsing Bubble, radius is {rad}, radius step is {radius_step}")
            if rad < 10:
                rad = rad + 10
            rad += (radius_step+ 2)
            if rad > 30 or rad < 21:  # Pulse limits
                # print("Entered here !")
                radius_step = -(radius_step + 5)
                # print(f"Current radius step: {radius_step}")
        if Fy + rad < 0:  # Circle exits screen
            Fx = random.randint(25, width - 25)
            Fy = random.randint(rad, width - rad)
            miss += 1
        fall_circle[i] = [Fx, Fy, rad, is_pulsating, radius_step]
        # print(fall_circle)

        # Check for collision with shooter
        shooter_x = shooter_position - 10
        shooter_y = 50
        shooter_width = 20
        shooter_height = 40
        if rect_circle_collision(shooter_x, shooter_y, shooter_width, shooter_height, Fx, Fy, rad):
            game_state = 'Shesh'
            fall_circle.clear()
            glutPostRedisplay()
            print("Game Over, Rocket has experienced Collision with Circle")
            print(f"Final Score: {score}")
            break
        if miss_shot >=3:
                game_state = 'Shesh'
                fall_circle.clear()
                glutPostRedisplay()
                print("Game Over: 3 Shot Miss!")
                print(f"Final Score: {score}")
                break

        if miss >= 3:
            game_state = 'Shesh'
            fall_circle.clear()
            glutPostRedisplay()
            print("Game Over: 3 Circle Miss!")
            print(f"Final Score: {score}")
            # game_over(score)
            break

    if game_state != 'Shesh':
        glutPostRedisplay()
        glutTimerFunc(25, update, 0)
    else:
        timer = False

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    button_akao()
    draw_shooter()
    draw_falling_britto()
    draw_projectiles()
    glutSwapBuffers()

glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(width, height)
glutInitWindowPosition(100, 100)
glutCreateWindow(b"Lost In the Space")
init()  # Set up initial OpenGL environment
glutDisplayFunc(display)  # Register display callback
glutMouseFunc(mouse)  # Register mouse click callback
glutKeyboardFunc(keyboard)  # Register keyboard for special keys
glutTimerFunc(25, update, 0)  # Initially register the timer callback to start updates
glutMainLoop()