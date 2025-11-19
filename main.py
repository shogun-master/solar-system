import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
import sys
from PIL import Image
import random


pygame.init()

# Get screen dimensions for fullscreen
info = pygame.display.Info()
width, height = info.current_w, info.current_h
pygame.display.set_mode((width, height), DOUBLEBUF | OPENGL | FULLSCREEN)

# Hide the default mouse cursor
pygame.mouse.set_visible(False)

glEnable(GL_DEPTH_TEST)
glEnable(GL_TEXTURE_2D)
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

glMatrixMode(GL_PROJECTION)
gluPerspective(45, width / height, 0.1, 2000)
glMatrixMode(GL_MODELVIEW)

# --------------------------
# Load a texture from image
# --------------------------
def load_texture(filename):
    try:
        img = Image.open(filename)
    except FileNotFoundError:
        print(f"Error: Texture file not found at '{filename}'. Creating a placeholder.")
        # Create a white placeholder texture
        img = Image.new('RGBA', (256, 256), (255, 255, 255, 255))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img_data = img.convert("RGBA").tobytes()

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height,
                 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    return texture_id

# --------------------------
# Load textures
# --------------------------
textures = {
    "Sun": load_texture("2k_sun.jpg"),
    "Mercury": load_texture("2k_mercury.jpg"),
    "Venus": load_texture("2k_venus_surface.jpg"),
    "Earth": load_texture("2k_earth_daymap.jpg"),
    "Mars": load_texture("2k_mars.jpg"),
    "Jupiter": load_texture("2k_jupiter.jpg"),
    "Saturn": load_texture("2k_saturn.jpg"),
    "Uranus": load_texture("2k_uranus.jpg"),
    "Neptune": load_texture("2k_neptune.jpg"),
    "Stars": load_texture("2k_stars_milky_way.jpg"),
    "Saturn_Ring": load_texture("2k_saturn_ring.png"),
    "Moon": load_texture("2k_moon.jpg"),
    "Phobos": load_texture("phobos.jpg"),
    "Deimos": load_texture("deimos.jpg"),
    "Rocket": load_texture("rocket.png"),
    "Metal": load_texture("metal_texture.jpg"),
    "BlackHole": load_texture("black_hole.png"),
}

# --------------------------
# Draw textured sphere
# --------------------------
def draw_sphere(radius, orientation=GLU_OUTSIDE):
    quad = gluNewQuadric()
    gluQuadricTexture(quad, True)
    gluQuadricOrientation(quad, orientation)
    gluSphere(quad, radius, 50, 50)

# --------------------------
# Draw textured ring
# --------------------------
def draw_ring(inner_radius, outer_radius):
    quad = gluNewQuadric()
    gluQuadricTexture(quad, True)
    gluDisk(quad, inner_radius, outer_radius, 50, 50)

# --------------------------
# Draw an orbit line
# --------------------------
def draw_orbit(radius):
    glBegin(GL_LINE_LOOP)
    num_segments = 100
    for i in range(num_segments + 1):
        angle = 2 * math.pi * i / num_segments
        x = radius * math.cos(angle)
        z = radius * math.sin(angle)
        glVertex3f(x, 0, z)
    glEnd()

# --------------------------
# Draw a 3D rocket model
# --------------------------
def draw_3d_rocket(size):
    quad = gluNewQuadric()
    gluQuadricTexture(quad, True) # Enable texturing for the rocket parts

    glBindTexture(GL_TEXTURE_2D, textures["Metal"])
    glColor3f(1.0, 1.0, 1.0) # Use white color to not tint the texture

    # --- Main Body (First Stage) ---
    body_height = size * 0.7
    body_radius = size / 5.0
    gluCylinder(quad, body_radius, body_radius, body_height, 20, 5)
    # Add a cap to the top of the first stage
    glPushMatrix()
    glTranslatef(0, 0, body_height)
    gluDisk(quad, 0, body_radius, 20, 1)
    glPopMatrix()

    # --- Second Stage ---
    glPushMatrix()
    glTranslatef(0, 0, body_height)
    stage2_height = size * 0.5
    stage2_radius = body_radius * 0.7
    gluCylinder(quad, stage2_radius, stage2_radius, stage2_height, 20, 5)
    # Add a cap to the top of the second stage
    gluDisk(quad, 0, stage2_radius, 20, 1)
    glPopMatrix()

    # --- Nose Cone ---
    glColor3f(0.9, 0.2, 0.2) # Red nose cone
    glPushMatrix()
    glTranslatef(0, 0, body_height + stage2_height) # Position at the top of the second stage
    cone_height = size / 2.0
    gluCylinder(quad, stage2_radius, 0.0, cone_height, 20, 5) # Cone is a cylinder with top radius 0
    glPopMatrix()

    # --- Fins (3 fins, 120 degrees apart) ---
    glBindTexture(GL_TEXTURE_2D, textures["Metal"])
    glColor3f(1.0, 1.0, 1.0)
    fin_height = size / 2.0
    fin_width = size / 3.0
    for i in range(3):
        glPushMatrix()
        glRotatef(i * 120, 0, 0, 1) # Rotate around the Z-axis (rocket's length)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(body_radius, 0, 0)
        glTexCoord2f(1, 0); glVertex3f(body_radius + fin_width, 0, fin_height * 0.2)
        glTexCoord2f(1, 1); glVertex3f(body_radius + fin_width, 0, fin_height)
        glTexCoord2f(0, 1); glVertex3f(body_radius, 0, fin_height)
        glEnd()
        glPopMatrix()

    # --- Engine Bell ---
    glColor3f(0.4, 0.4, 0.4) # Dark metallic color for engine
    glPushMatrix()
    glTranslatef(0, 0, -size * 0.1) # Position slightly behind the body
    gluCylinder(quad, body_radius * 0.8, body_radius * 0.5, size * 0.2, 20, 5)
    glPopMatrix()

# --------------------------
# Draw a 3D UFO model
# --------------------------
def draw_ufo(size):
    quad = gluNewQuadric()

    # Main saucer body
    glPushMatrix()
    glColor3f(0.6, 0.6, 0.7) # Metallic grey
    glScalef(1.0, 0.3, 1.0) # Flatten the sphere into a saucer
    gluSphere(quad, size, 30, 10)
    glPopMatrix()

    # Cockpit dome
    glPushMatrix()
    glColor3f(0.5, 0.8, 0.9) # Glowing light blue
    glTranslatef(0, size * 0.2, 0)
    glScalef(0.5, 0.5, 0.5)
    gluSphere(quad, size, 20, 10)
    glPopMatrix()

    # Underside light
    glColor3f(0.8, 1.0, 0.8) # Glowing green
    gluDisk(quad, 0, size * 0.3, 20, 1)

# --------------------------
# Particle class for smoke
# --------------------------
class Particle:
    def __init__(self, x, y):
        self.x = x + random.uniform(-3, 3) # Start with slight horizontal spread
        self.y = y + random.uniform(-3, 3)
        self.vx = random.uniform(-0.3, 0.3)
        self.vy = random.uniform(2, 4) # Move upwards faster
        self.lifetime = random.uniform(30, 50)
        self.initial_lifetime = self.lifetime
        self.size = random.uniform(8, 18)
        # Start with a fiery color
        self.r, self.g, self.b = 1.0, random.uniform(0.3, 0.6), 0.1

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        # Shrink particle over time
        self.size *= 0.97
        # Fade to grey
        self.g = max(0.5, self.g * 0.98)
        self.b = max(0.5, self.b * 1.02)

# --------------------------
# Shooting Star class
# --------------------------
class ShootingStar:
    def __init__(self, screen_width, screen_height):
        self.w, self.h = screen_width, screen_height
        # Start from a random edge
        edge = random.choice(['top', 'bottom', 'left', 'right'])
        if edge == 'top':
            self.x, self.y = random.uniform(0, self.w), -10
            self.vx, self.vy = random.uniform(-4, 4), random.uniform(5, 15)
        elif edge == 'bottom':
            self.x, self.y = random.uniform(0, self.w), self.h + 10
            self.vx, self.vy = random.uniform(-4, 4), random.uniform(-15, -5)
        elif edge == 'left':
            self.x, self.y = -10, random.uniform(0, self.h)
            self.vx, self.vy = random.uniform(5, 15), random.uniform(-4, 4)
        else: # right
            self.x, self.y = self.w + 10, random.uniform(0, self.h)
            self.vx, self.vy = random.uniform(-15, -5), random.uniform(-4, 4)

        self.lifetime = 1.0 # Represents alpha, from 1.0 down to 0.0
        self.length = random.uniform(50, 150)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 0.01 # Fade out

    def is_dead(self):
        return self.lifetime <= 0 or \
               self.x < -self.length or self.x > self.w + self.length or \
               self.y < -self.length or self.y > self.h + self.length

# --------------------------
# Asteroid class
# --------------------------
class Asteroid:
    def __init__(self):
        # Position in polar coordinates, then convert to cartesian
        angle = random.uniform(0, 2 * math.pi)
        # Place them in a belt between Mars and Jupiter
        radius = random.uniform(280, 340)
        
        self.x = radius * math.cos(angle)
        self.y = random.uniform(-15, 15) # Give them some vertical displacement
        self.z = radius * math.sin(angle)

        # Size
        self.size = random.uniform(0.5, 3.5)

        # Orbital speed - slower for farther asteroids to simulate Kepler's laws
        self.speed = random.uniform(0.2, 0.35) * (340 / radius)

        # Random rotation axis and speed for tumbling effect
        self.rot_speed = random.uniform(-40, 40)
        self.rot_axis = (random.uniform(-1, 1), random.uniform(-1, 1), random.uniform(-1, 1))
        # Normalize rotation axis vector
        norm = math.sqrt(sum(i*i for i in self.rot_axis))
        self.rot_axis = tuple(i/norm for i in self.rot_axis)

# --------------------------
# UFO class
# --------------------------
class UFO:
    def __init__(self):
        self.size = 15.0
        self.rot_speed = random.uniform(20, 50)
        self.reset()

    def update(self, dt):
        for i in range(3):
            self.pos[i] += self.vel[i] * dt
        
        # If UFO goes too far, reset it
        if abs(self.pos[0]) > 1000 or abs(self.pos[1]) > 1000 or abs(self.pos[2]) > 1000:
            self.reset()

    def reset(self):
        # Start at a random edge of a large box
        self.pos = [random.uniform(-800, 800), random.uniform(-300, 300), random.uniform(-800, 800)]
        # Aim towards the center of the box
        target = [random.uniform(-200, 200), 0, random.uniform(-200, 200)]
        direction = [target[i] - self.pos[i] for i in range(3)]
        norm = math.sqrt(sum(d*d for d in direction))
        speed = random.uniform(40, 80)
        self.vel = [d / norm * speed for d in direction]

# --------------------------
# Rocket class for 3D flight
# --------------------------
class Rocket:
    def __init__(self):
        self.pos = [0.0, 0.0, 300.0] # Start in front of the sun
        self.vel = [0.0, 0.0, 0.0]
        # Forward vector (where the rocket is pointing)
        self.forward = [0.0, 0.0, -1.0]
        self.size = 20.0
        self.is_collapsing = False
        self.collapse_timer = 0.0
        self.initial_pos = [0.0, 0.0, 300.0]
        self.thrust = 0.0

    def update(self, dt, keys):
        # --- Handle Controls ---
        self.thrust = 0.0
        if keys[K_w]:
            self.thrust = 150.0
        if keys[K_s]:
            self.thrust = -100.0

        if self.is_collapsing:
            self.size *= 0.90 # Shrink rapidly
            self.collapse_timer -= dt
            if self.collapse_timer <= 0:
                self.reset()
            return # No other physics when collapsing

        # --- Update Physics ---
        # Apply thrust
        for i in range(3):
            self.vel[i] += self.forward[i] * self.thrust * dt

        # Apply drag/friction
        for i in range(3):
            self.vel[i] *= 0.98

        # Update position
        for i in range(3):
            self.pos[i] += self.vel[i] * dt

    def start_collapse(self, black_hole_pos):
        if self.is_collapsing: return
        self.is_collapsing = True
        self.collapse_timer = 2.0 # Time until reset
        # Set velocity to pull towards black hole
        direction = [black_hole_pos[i] - self.pos[i] for i in range(3)]
        self.vel = [d * 3 for d in direction] # Strong pull

    def reset(self):
        self.pos = list(self.initial_pos)
        self.vel = [0.0, 0.0, 0.0]
        self.forward = [0.0, 0.0, -1.0]
        self.size = 20.0
        self.is_collapsing = False

    def update_orientation(self, mouse_dx, mouse_dy):
        # Simple yaw and pitch based on mouse movement
        yaw_angle = -mouse_dx * 0.005
        pitch_angle = -mouse_dy * 0.005

        # Rotate forward vector around Y-axis (yaw)
        x, z = self.forward[0], self.forward[2]
        self.forward[0] = x * math.cos(yaw_angle) - z * math.sin(yaw_angle)
        self.forward[2] = x * math.sin(yaw_angle) + z * math.cos(yaw_angle)

        # Rudimentary pitch (clamped to avoid flipping over)
        self.forward[1] += pitch_angle
        self.forward[1] = max(-0.8, min(0.8, self.forward[1]))

# --------------------------
# Planet data (bigger sizes)
# --------------------------
planets = [
    # Name, Distance, Size, Orbital Speed, Axial Tilt, Moons
    ("Mercury", 115,  8.0, 1.0, 2, []),
    ("Venus",   150, 15.0, 0.6, 177, []),
    ("Earth",   200, 17.0, 0.5, 23.5, [
        # Moon Name, Distance from planet, Size, Orbital Speed around planet
        ("Moon", 24, 4.5, 4.0)
    ]),
    ("Mars",    260, 14.0, 0.4, 25, [
        ("Phobos", 20, 4.0, 8.0),
        ("Deimos", 20, 3.0, 4.0)
    ]),
    ("Jupiter", 360, 40.0, 0.3, 3, []),
    ("Saturn",  490, 35.0, 0.25, 27, []),
    ("Uranus",  580, 20.0, 0.15, 98, []),
    ("Neptune", 640, 19.0, 0.1, 28, []),
]

clock = pygame.time.Clock()
start_time = time.time()

# List to hold smoke particles
smoke_particles = []

# List to hold asteroids
asteroids = []
for _ in range(200): # Create 200 asteroids
    asteroids.append(Asteroid())

# List to hold shooting stars
shooting_stars = []

# Create UFOs and Monsters
ufos = [UFO() for _ in range(2)]

# Black Hole properties
black_hole = {
    "pos": [2000, 500, 0], # Positioned far away from the solar system
    "radius": 40.0, # The black sphere itself (event horizon)
    "influence_radius": 100.0 # Where gravity starts to affect the rocket
}

# Create the 3D rocket object
rocket_3d = Rocket()

# Variables for interactive rocket cursor
last_mouse_x = 0
last_mouse_y = 0
rocket_tilt = 0.0
camera_mode = 'default' # Can be 'default' or 'follow_rocket'
is_mouse_focused = False # To handle mouse wrapping

# --------------------------
# Main loop
# --------------------------
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
            elif event.key == K_x:
                if camera_mode != 'follow_rocket':
                    camera_mode = 'follow_rocket'
                    is_mouse_focused = True
                    pygame.event.set_grab(True) # Confine mouse to window
                    pygame.mouse.set_visible(False)
            elif event.key == K_z:
                if camera_mode != 'default':
                    camera_mode = 'default'
                    is_mouse_focused = False
                    pygame.event.set_grab(False) # Release mouse
                    # Force a cursor state reset by showing then hiding the OS cursor.
                    # This fixes the custom cursor not appearing after grab is released.
                    pygame.mouse.set_visible(True)
                    pygame.mouse.set_visible(False)
                    # Immediately update last_mouse_x to current mouse position
                    # to prevent a jump in rocket tilt calculation
                    last_mouse_x, last_mouse_y = pygame.mouse.get_pos()

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Get time delta for physics calculations
    dt = clock.get_time() / 1000.0 # Delta time in seconds
    t = time.time() - start_time

    # --------------------------
    # Camera Setup
    # --------------------------
    if camera_mode == 'default':
        # Default static camera view
        glTranslatef(0, 0, -1200)
        glRotatef(25, 1, 0, 0)
    elif camera_mode == 'follow_rocket':
        # --- Update Rocket ---
        if is_mouse_focused:
            mouse_dx, mouse_dy = pygame.mouse.get_rel()
            rocket_3d.update_orientation(mouse_dx, mouse_dy)
        keys = pygame.key.get_pressed()
        rocket_3d.update(dt, keys)

        # --- Black Hole Collision Check ---
        dist_vec = [rocket_3d.pos[i] - black_hole['pos'][i] for i in range(3)]
        dist_sq = sum(d*d for d in dist_vec)
        if dist_sq < black_hole['radius']**2:
            rocket_3d.start_collapse(black_hole['pos'])

        # --- Update Camera to follow rocket ---
        # Camera is positioned behind the rocket
        cam_dist = 50.0
        cam_pos = [
            rocket_3d.pos[0] - rocket_3d.forward[0] * cam_dist,
            rocket_3d.pos[1] - rocket_3d.forward[1] * cam_dist + 15, # Slightly above
            rocket_3d.pos[2] - rocket_3d.forward[2] * cam_dist
        ]
        # Look at a point slightly in front of the rocket
        look_at = [
            rocket_3d.pos[0] + rocket_3d.forward[0] * 20,
            rocket_3d.pos[1] + rocket_3d.forward[1] * 20,
            rocket_3d.pos[2] + rocket_3d.forward[2] * 20
        ]

        gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],  # Camera position
                  look_at[0], look_at[1], look_at[2],  # Point to look at
                  0, 1, 0)                             # Up vector

        # Center mouse to prevent it from hitting screen edges
        if is_mouse_focused:
            pygame.mouse.set_pos([width / 2, height / 2])
            # Clear relative motion after recentering to avoid jump
            pygame.mouse.get_rel()

    # --------------------------
    # Draw Starfield Background
    # --------------------------
    glPushMatrix()
    # Disable depth writing so the background is always behind everything
    glDepthMask(GL_FALSE)

    # Use GL_REPLACE to ensure the texture is drawn as-is, without color or lighting affecting it.
    # This is the standard way to draw a skybox.
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
    glBindTexture(GL_TEXTURE_2D, textures["Stars"])
    glColor3f(1, 1, 1)
    # The sphere should be large enough to contain the entire solar system
    draw_sphere(800, orientation=GLU_INSIDE)

    # Re-enable depth writing for the rest of the scene. This is crucial!
    glDepthMask(GL_TRUE) 
    # Reset texture environment to default for the rest of the objects
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    glPopMatrix()


    # --------------------------
    # Glowing Animated Sun
    # --------------------------
    glPushMatrix()

    glRotatef(t * 10, 0, 1, 0)  # Rotate the sun on its own axis

    glBindTexture(GL_TEXTURE_2D, textures["Sun"])

    glow = 1.0 + (math.sin(t * 2) * 0.2)  # subtle shimmering glow
    glColor3f(1.0 * glow, 0.8 * glow, 0.6 * glow)

    draw_sphere(100)  # Sun

    glPopMatrix()

    # --------------------------
    # Draw Orbits
    # --------------------------
    # Orbits are not textured, so disable texturing
    glDisable(GL_TEXTURE_2D)

    # To create a glow effect, we draw each orbit multiple times
    # with different thickness and alpha values.
    glow_layers = [
        (4.0, 0.15),  # Thinner, brighter outer glow
        (2.0, 0.3),   # Thinner, brighter mid glow
        (1.0, 0.8)    # A strong, bright core line
    ]

    for line_width, alpha in glow_layers:
        glLineWidth(line_width)
        # Set a dim, semi-transparent grey color for the orbits
        glColor4f(0.3, 0.3, 0.3, alpha)
        for name, dist, size, speed, tilt, moons in planets:
            draw_orbit(dist)

    # Reset line width to default for any other line drawing
    glLineWidth(1.0)

    # Re-enable texturing for the planets
    glEnable(GL_TEXTURE_2D)

    # --------------------------
    # Draw Asteroids
    # --------------------------
    glBindTexture(GL_TEXTURE_2D, textures["Phobos"]) # Use Phobos texture for all asteroids
    for asteroid in asteroids:
        glPushMatrix()

        # Asteroids revolve around the sun at their own speed
        # We use the asteroid's initial (x,z) as a starting point in the orbit circle
        orbit_angle = t * asteroid.speed * 10
        cos_a = math.cos(math.radians(orbit_angle))
        sin_a = math.sin(math.radians(orbit_angle))
        
        # Manual rotation calculation
        current_x = asteroid.x * cos_a - asteroid.z * sin_a
        current_z = asteroid.x * sin_a + asteroid.z * cos_a

        glTranslatef(current_x, asteroid.y, current_z)
        glRotatef(t * asteroid.rot_speed, asteroid.rot_axis[0], asteroid.rot_axis[1], asteroid.rot_axis[2])
        
        draw_sphere(asteroid.size)
        glPopMatrix()

    # --------------------------
    # Draw UFOs
    # --------------------------
    glDisable(GL_TEXTURE_2D)
    for ufo in ufos:
        ufo.update(dt)
        glPushMatrix()
        glTranslatef(ufo.pos[0], ufo.pos[1], ufo.pos[2])
        glRotatef(t * ufo.rot_speed, 0, 1, 0) # Spin the UFO
        draw_ufo(ufo.size)
        glPopMatrix()
    glEnable(GL_TEXTURE_2D)

    # --------------------------
    # Draw Black Hole (only in follow mode)
    # --------------------------
    if camera_mode == 'follow_rocket':
        glPushMatrix()
        glTranslatef(black_hole['pos'][0], black_hole['pos'][1], black_hole['pos'][2])

        # --- Billboard the black hole image to always face the camera ---
        # Get the current modelview matrix to extract camera orientation
        modelview = glGetFloatv(GL_MODELVIEW_MATRIX)
        
        # The first three columns of the matrix are the camera's right, up, and forward vectors.
        # By applying their transpose, we undo the camera's rotation for this object.
        camera_x = [modelview[0][0], modelview[1][0], modelview[2][0]]
        camera_y = [modelview[0][1], modelview[1][1], modelview[2][1]]
        
        # Draw the textured quad
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures["BlackHole"])
        glColor4f(1, 1, 1, 1) # Use full color and opacity from texture
        
        s = black_hole['radius'] * 2 # Make the image size relative to the black hole radius
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0); glVertex3f(-s * camera_x[0] - s * camera_y[0], -s * camera_x[1] - s * camera_y[1], -s * camera_x[2] - s * camera_y[2])
        glTexCoord2f(1, 0); glVertex3f( s * camera_x[0] - s * camera_y[0],  s * camera_x[1] - s * camera_y[1],  s * camera_x[2] - s * camera_y[2])
        glTexCoord2f(1, 1); glVertex3f( s * camera_x[0] + s * camera_y[0],  s * camera_x[1] + s * camera_y[1],  s * camera_x[2] + s * camera_y[2])
        glTexCoord2f(0, 1); glVertex3f(-s * camera_x[0] + s * camera_y[0], -s * camera_x[1] + s * camera_y[1], -s * camera_x[2] + s * camera_y[2])
        glEnd()

        glPopMatrix()

    # --------------------------
    # Draw 3D Rocket in follow mode
    # --------------------------
    if camera_mode == 'follow_rocket':
        glPushMatrix()
        # Move to the rocket's position
        glTranslatef(rocket_3d.pos[0], rocket_3d.pos[1], rocket_3d.pos[2])

        # --- Orient the rocket to match its forward vector ---
        yaw = math.degrees(math.atan2(rocket_3d.forward[0], rocket_3d.forward[2]))
        pitch = math.degrees(math.asin(-rocket_3d.forward[1]))
        glRotatef(yaw, 0, 1, 0)
        glRotatef(pitch, 1, 0, 0)

        glDisable(GL_TEXTURE_2D) # Our simple model is not textured
        draw_3d_rocket(rocket_3d.size)
        glEnable(GL_TEXTURE_2D)
        glPopMatrix()

    # --------------------------
    # Draw planets with textures
    # --------------------------
    for name, dist, size, speed, tilt, moons in planets:
        glPushMatrix()

        # revolve around the Sun
        glRotatef(t * speed * 10, 0, 1, 0)

        # move away from Sun
        glTranslatef(dist, 0, 0)

        # The following push/pop ensures that the planet's axial rotation
        # does not affect other objects, like Saturn's rings.
        glPushMatrix()
        # rotate the planet itself (axial spin)
        glRotatef(t * 50, 0, 1, 0)

        # Rotate the sphere so the texture maps correctly (poles on Y-axis)
        glRotatef(-90, 1, 0, 0)

        glBindTexture(GL_TEXTURE_2D, textures[name])
        glColor3f(1, 1, 1)
        draw_sphere(size)
        glPopMatrix()

        if name == "Saturn":
            glBindTexture(GL_TEXTURE_2D, textures["Saturn_Ring"])
            glColor3f(1, 1, 1)
            draw_ring(size + 10, size + 25)

        # --------------------------
        # Draw Moons
        # --------------------------
        for moon_name, moon_dist, moon_size, moon_speed in moons:
            glPushMatrix()

            # Revolve around the parent planet
            glRotatef(t * moon_speed * 20, 0, 1, 0)
            glTranslatef(moon_dist, 0, 0)

            # rotate the moon itself and fix texture
            glPushMatrix()
            glRotatef(t * 30, 0, 1, 0)
            glRotatef(-90, 1, 0, 0)
            glBindTexture(GL_TEXTURE_2D, textures[moon_name])
            glColor3f(1, 1, 1)
            draw_sphere(moon_size)
            glPopMatrix()

            glPopMatrix()


        glPopMatrix()


    # ----------------------------------
    # Switch to 2D Orthographic mode for UI
    # ----------------------------------
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, height, 0) # Flipped Y-axis (0 at top)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable depth testing for 2D elements
    glDisable(GL_DEPTH_TEST)

    # --------------------------
    # Draw Shooting Stars
    # --------------------------
    # Randomly add a new shooting star
    if random.random() < 0.015: # Adjust probability for more/fewer stars
        if len(shooting_stars) < 5: # Limit concurrent stars
            shooting_stars.append(ShootingStar(width, height))

    glDisable(GL_TEXTURE_2D)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for star in reversed(shooting_stars):
        star.update()
        if star.is_dead():
            shooting_stars.remove(star)
        else:
            # Draw a line representing the star's trail
            glColor4f(1.0, 1.0, 0.8, star.lifetime * 0.8) # Bright, fading yellow-white
            glVertex2f(star.x, star.y)
            glVertex2f(star.x - star.vx * (star.length / 20), star.y - star.vy * (star.length / 20))
    glEnd()

    # --------------------------
    # Draw Rocket and Smoke
    # --------------------------
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Only update tilt and smoke when in default mode
    if camera_mode == 'default':
        # Calculate 2D rocket tilt based on mouse velocity
        mouse_dx = mouse_x - last_mouse_x
        last_mouse_x = mouse_x
        last_mouse_y = mouse_y
        
        target_tilt = mouse_dx * 1.5
        target_tilt = max(-25.0, min(25.0, target_tilt)) # Clamp between -25 and 25 degrees
        # Smoothly interpolate to the target tilt for a nice easing effect
        rocket_tilt += (target_tilt - rocket_tilt) * 0.1
    rocket_w, rocket_h = 64, 64 # Rocket sprite size

    # Add new particles at the rocket's tail
    if camera_mode == 'default':
        if len(smoke_particles) < 100: # Limit total particles
            for _ in range(3): # Emit 3 particles per frame
                smoke_particles.append(Particle(mouse_x + rocket_w / 2, mouse_y + rocket_h))

    # Update and draw particles
    glBegin(GL_QUADS)
    for particle in reversed(smoke_particles):
        particle.update()
        if particle.lifetime <= 0:
            smoke_particles.remove(particle)
        else:
            # Fade out over time
            alpha = (particle.lifetime / particle.initial_lifetime) * 0.5
            glColor4f(particle.r, particle.g, particle.b, alpha)
            
            x, y, size = particle.x, particle.y, particle.size
            glVertex2f(x - size / 2, y - size / 2)
            glVertex2f(x + size / 2, y - size / 2)
            glVertex2f(x + size / 2, y + size / 2)
            glVertex2f(x - size / 2, y + size / 2)
    glEnd()
    glEnable(GL_TEXTURE_2D)

    # --------------------------
    # Draw Rocket Cursor
    # --------------------------
    if camera_mode == 'default':
        glPushMatrix()

        # Move to the center of where the rocket will be
        glTranslatef(mouse_x + rocket_w / 2, mouse_y + rocket_h / 2, 0)
        # Apply the tilt rotation
        glRotatef(rocket_tilt, 0, 0, 1)

        glBindTexture(GL_TEXTURE_2D, textures["Rocket"])
        glColor4f(1, 1, 1, 1) # Ensure full opacity
        glBegin(GL_QUADS)
        # Flip texture coordinates vertically to correct the rocket's orientation
        glTexCoord2f(0, 1); glVertex2f(-rocket_w / 2, -rocket_h / 2)
        glTexCoord2f(1, 1); glVertex2f( rocket_w / 2, -rocket_h / 2)
        glTexCoord2f(1, 0); glVertex2f( rocket_w / 2,  rocket_h / 2)
        glTexCoord2f(0, 0); glVertex2f(-rocket_w / 2,  rocket_h / 2)
        glEnd()
        glPopMatrix()

    # Restore 3D perspective projection
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()

    pygame.display.flip()
    clock.tick(60)
