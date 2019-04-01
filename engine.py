import math, map, globals, pymunk, physics, pygame

screen = None
stickFigures = []

s_w = 1280
s_h = 720


class Cam:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.z = 0
        self.xRot = 0
        self.yRot = 0


class DepthObject:
    def draw(self):
        f_v = self.front_side_vertices
        b_v = self.back_side_vertices

        nf_v = list()
        nb_v = list()

        for i in range(len(f_v)):
            nf_v.append(distort_point_map(f_v[i][0], f_v[i][1], f_v[i][2]))
            nb_v.append(distort_point_map(b_v[i][0], b_v[i][1], b_v[i][2]))

        # Draw the Front and Back Side Polygons
        # Fill A Polygon
        if self.fill_color != (-1, -1, -1):
            pygame.draw.polygon(screen, self.fill_color, nf_v, 0)
            pygame.draw.polygon(screen, self.fill_color, nb_v, 0)

        pygame.draw.polygon(screen, self.outline_color, nf_v, self.outline_width)
        pygame.draw.polygon(screen, self.outline_color, nb_v, self.outline_width)

        # Draw Connecting Segments
        for i in range(len(nf_v)):
            pygame.draw.line(screen, self.outline_color, nf_v[i], nb_v[i], self.outline_width)

    def __init__(self, vertices, depth, fill_color, outline_color, outline_width):
        # FILL COLOR (-1, -1, -1) = NO FILL
        v = vertices

        self.front_side_vertices = list()
        self.back_side_vertices = list()
        self.fill_color = fill_color
        self.outline_color = outline_color
        self.outline_width = outline_width

        for i in range(len(vertices)):
            # One at Z = 0, One at Z = Depth
            self.front_side_vertices.append([v[i][0], v[i][1], -depth/2])
            self.back_side_vertices.append([v[i][0], v[i][1], depth/2])


class Platform:
    def draw(self):
        gv = global_vertices(self.poly.get_vertices(), self.body)
        # Translate Into Map Coordinates:
        fv = list()
        for v in gv:
            fv.append((v[0]/100, v[1]/100))

        # Create new Depth Object
        depth_object = DepthObject(fv, self.depth, (-1, -1, -1), (0, 0, 0), 3)
        depth_object.draw()

    def __init__(self, x, y, length, width, depth):
        self.body = pymunk.Body(0, 0, pymunk.Body.STATIC)
        self.body.position = x, y

        self.poly = pymunk.Poly.create_box(self.body, (length, width), 0)
        globals.space.add(self.body, self.poly)

        self.depth = depth


class Map:
    def __init__(self, init_function, run_time_function):
        self.init_function = init_function
        self.run_time_function = run_time_function


class Player:
    def l_arm_boost(self):
        obj = self.sf.segments['L_FOREARM']
        total_force = globals.ARM_BOOST_FORCE
        di = obj.body.angle
        force_x = -total_force * math.cos(di)
        force_y = -total_force * math.sin(di)

        obj.body.apply_impulse_at_local_point((force_x, force_y), (0, obj.width / 2))
        # obj.body.apply_impulse_at_world_point((force_x, force_y), obj.body.local_to_world((0, obj.width / 2)))
        # print(force_x, force_y)
        # Draw Vectors
        xy1 = obj.body.position
        # print(xy1)
        scale_factor = globals.FLAME_SCALE
        xy2 = (xy1[0] + force_x * scale_factor, xy1[1] + force_y * scale_factor)

        xy1 = distort_point(xy1[0], xy1[1], 0)
        xy2 = distort_point(xy2[0], xy2[1], 0)

        pygame.draw.line(screen, globals.BOOSTER_COLOR, xy1, xy2, 5)

    def r_arm_boost(self):
        obj = self.sf.segments['R_FOREARM']
        total_force = globals.ARM_BOOST_FORCE
        di = obj.body.angle
        force_x = -total_force * math.cos(di)
        force_y = -total_force * math.sin(di)

        obj.body.apply_impulse_at_local_point((force_x, force_y), (obj.length, obj.width / 2))
        # obj.body.apply_impulse_at_world_point(\
        # (force_x, force_y), obj.body.local_to_world((obj.length, obj.width / 2)))
        # print(force_x, force_y)
        # Draw Vectors
        xy1 = obj.body.position
        # print(xy1)
        scale_factor = globals.FLAME_SCALE
        xy2 = (xy1[0] - force_x * scale_factor, xy1[1] - force_y * scale_factor)

        xy1 = distort_point(xy1[0], xy1[1], 0)
        xy2 = distort_point(xy2[0], xy2[1], 0)

        pygame.draw.line(screen, globals.BOOSTER_COLOR, xy1, xy2, 5)

    def l_leg_boost(self):
        obj = self.sf.segments['L_CALF']
        total_force = globals.ARM_BOOST_FORCE
        di = obj.body.angle - math.pi/2
        force_x = -total_force * math.cos(di)
        force_y = -total_force * math.sin(di)

        obj.body.apply_impulse_at_local_point((force_x, force_y), (obj.length / 2, 0))
        # obj.body.apply_impulse_at_world_point((force_x, force_y), obj.body.local_to_world((0, obj.width / 2)))
        # print(force_x, force_y)
        # Draw Vectors
        xy1 = obj.body.position
        # print(xy1)
        scale_factor = globals.FLAME_SCALE
        xy2 = (xy1[0] + force_x * scale_factor, xy1[1] + force_y * scale_factor)

        xy1 = distort_point(xy1[0], xy1[1], 0)
        xy2 = distort_point(xy2[0], xy2[1], 0)

        pygame.draw.line(screen, globals.BOOSTER_COLOR, xy1, xy2, 5)

    def r_leg_boost(self):
        obj = self.sf.segments['R_CALF']
        total_force = globals.ARM_BOOST_FORCE
        di = obj.body.angle + math.pi/2
        force_x = -total_force * math.cos(di)
        force_y = -total_force * math.sin(di)

        obj.body.apply_impulse_at_local_point((force_x, force_y), (obj.length, obj.width / 2))
        # obj.body.apply_impulse_at_world_point(\
        # (force_x, force_y), obj.body.local_to_world((obj.length, obj.width / 2)))
        # print(force_x, force_y)
        # Draw Vectors
        xy1 = obj.body.position
        # print(xy1)
        scale_factor = globals.FLAME_SCALE
        xy2 = (xy1[0] - force_x * scale_factor, xy1[1] - force_y * scale_factor)

        xy1 = distort_point(xy1[0], xy1[1], 0)
        xy2 = distort_point(xy2[0], xy2[1], 0)

        pygame.draw.line(screen, globals.BOOSTER_COLOR, xy1, xy2, 5)

    def reset_render_text(self):
        self.pre_rendered_text = globals.FONTS['HUD_FONT'].render(
            ('PLAYER ' + str(self.player_num)), False, (232, 232, 232))

    def __init__(self, color, keys, pos):

        self.keys = keys
        self.pos = pos
        self.color = color
        self.player_num = len(globals.PLAYERS)

        # Pre-Render Text
        self.pre_rendered_text = globals.FONTS['HUD_FONT'].render(
            ('PLAYER ' + str(self.player_num)), False, (232, 232, 232))

        """
            keys = {
                pygame.K_q: 'L_ARM_BOOSTER'
                .
                .
                .

            }
        """

        self.lives = 4
        # globals.PLAYERS.append(self)
        self.sf = physics.StickFigure(pos[0], pos[1], color, self.player_num)

        self.movement_functions = {
            'L_ARM_BOOSTER': self.l_arm_boost,
            'R_ARM_BOOSTER': self.r_arm_boost,
            'L_LEG_BOOSTER': self.l_leg_boost,
            'R_LEG_BOOSTER': self.r_leg_boost
        }
        # Input 'L_ARM_BOOSTER', etc

    def process_keys(self, key):
        # Associate Keys
        # print(self.keys[key])
        # print(self.movement_functions)
        self.movement_functions[self.keys[key]]()


TEMPLATE_PLAYERS = [
    Player((84, 255, 84),
           {
                pygame.K_q: 'L_ARM_BOOSTER',
                pygame.K_w: 'R_ARM_BOOSTER',
                pygame.K_a: 'L_LEG_BOOSTER',
                pygame.K_s: 'R_LEG_BOOSTER'
           }, (-1, -1)),
    Player((33, 240, 255),
           {
                pygame.K_t: 'L_ARM_BOOSTER',
                pygame.K_y: 'R_ARM_BOOSTER',
                pygame.K_g: 'L_LEG_BOOSTER',
                pygame.K_h: 'R_LEG_BOOSTER'
           }, (-1, -1)),
    Player((252, 255, 89),
           {
                pygame.K_p: 'L_ARM_BOOSTER',
                pygame.K_LEFTBRACKET: 'R_ARM_BOOSTER',
                pygame.K_SEMICOLON: 'L_LEG_BOOSTER',
                pygame.K_QUOTE: 'R_LEG_BOOSTER'
           }, (-1, -1)),
    Player((210, 89, 255),
           {
                pygame.K_KP8: 'L_ARM_BOOSTER',
                pygame.K_KP9: 'R_ARM_BOOSTER',
                pygame.K_KP5: 'L_LEG_BOOSTER',
                pygame.K_KP6: 'R_LEG_BOOSTER'
           }, (-1, -1))
]


def activate_players(n):

    # Clear Space:
    physics.space.remove(physics.space.bodies, physics.space.shapes)
    globals.PLAYER_KEY_ASSOCIATION = dict()
    globals.PLAYERS = dict()

    # Activate N Players
    globals.PLAYERS = TEMPLATE_PLAYERS[:n]

    # Reset Player Numbers & Keys
    for i in range(len(globals.PLAYERS)):
        player = globals.PLAYERS[i]

        player.player_num = i
        # Reset Stick Figure
        player.sf = physics.StickFigure(player.pos[0], player.pos[1], player.color, player.player_num)
        player.reset_render_text()

        for key in player.keys:
            globals.PLAYER_KEY_ASSOCIATION[key] = player.player_num


cam = Cam()
back_cam = Cam()


class Velocity:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Block:
    def __init__(self, x, y, z, w, h, color=(0, 0, 0)):
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.h = h
        self.color = color


def rotate_point(x, y, theta):
    si = math.sin(theta)
    co = math.cos(theta)

    x = x*co-y*si
    y = y*co+x*si

    return [x, y]


def distort_point_map(x, y, z):
    x -= back_cam.x
    y -= back_cam.y
    z -= back_cam.z

    xzr = rotate_point(x, z, back_cam.xRot)
    x = xzr[0]
    z = xzr[1]
    yzr = rotate_point(y, z, back_cam.yRot)
    y = yzr[0]
    z = yzr[1]

    zd = ((s_w / 2) / z)

    x *= zd
    y *= zd

    x += s_w / 2
    y += s_h / 2

    # print(x, y)
    return [x, y]


def distort_point(x, y, z):

    x -= cam.x
    y -= cam.y
    z -= cam.z

    xzr = rotate_point(x, z, cam.xRot)
    x = xzr[0]
    z = xzr[1]
    yzr = rotate_point(y, z, cam.yRot)
    y = yzr[0]
    z = yzr[1]

    zd = (((s_w * 0.01) / 2) / z)

    x *= zd
    y *= zd

    x += s_w / 2
    y += s_h / 2

    # print(x, y)
    return [x, y]


def draw_block(o):
    vt = list()

    vt.append([o.x - (o.w / 2), o.y - (o.w / 2), o.z + (o.w / 2)])
    vt.append([o.x - (o.w / 2), o.y + (o.w / 2), o.z + (o.w / 2)])
    vt.append([o.x + (o.w / 2), o.y + (o.w / 2), o.z + (o.w / 2)])
    vt.append([o.x + (o.w / 2), o.y - (o.w / 2), o.z + (o.w / 2)])
    vt.append([o.x - (o.w / 2), o.y - (o.w / 2), o.z - (o.w / 2)])
    vt.append([o.x - (o.w / 2), o.y + (o.w / 2), o.z - (o.w / 2)])
    vt.append([o.x + (o.w / 2), o.y + (o.w / 2), o.z - (o.w / 2)])
    vt.append([o.x + (o.w / 2), o.y - (o.w / 2), o.z - (o.w / 2)])

    d_c = list()

    for i in range(0, len(vt)):
        x = vt[i][0]
        y = vt[i][1]
        z = vt[i][2]

        d_c.append(distort_point_map(x, y, z))

    edges = []

    segments = [[0, 1], [1, 2], [2, 3], [3, 0], [0, 4], [1, 5], [6, 2], [3, 7], [4, 5], [5, 6], [6, 7], [7, 4]]

    """
    ff segments: 01, 12, 23, 30
    face connectors: 04, 15, 62, 37
    bf segments: 45, 56, 67, 74
    """

    # Fill Polygon for Each Face
    # Coordinates Of Each Face of Rect
    # faces = [[0, 1, 2, 3], [4, 5, 6, 7], [0, 1, 5, 4], [3, 2, 6, 7], [1, 2, 5, 6], [0, 4, 3, 7]]

    # Define Coordinates for Segment
    for i in range(0, len(segments)):
        edges.append([d_c[segments[i][0]], d_c[segments[i][1]]])

    # print(edges)
    # Draw Lines For Each Segment
    for i in range(0, len(edges)):
        pygame.draw.line(screen, o.color, [edges[i][0][0], edges[i][0][1]], [edges[i][1][0], edges[i][1][1]], 1)


def draw_block_set(a):
    for i in range(len(a)):
        draw_block(a[i])


class RenderMap:
    def __init__(self, block_list, body, poly):
        self.block_list = block_list
        self.body = body
        self.poly = poly

        self.outline_color = globals.COLORS['BLACK']
        self.fill_color = globals.COLORS['WHITE']
        self.outline_width = 4


defaultMap = map.Map('maps/test.csv')

render_map = RenderMap(None, None, None)


def global_vertices(vertices, body):
    # Get Vertices Returns Local Coordinates -----> Convert these into global by transforming
    # with angle and x, y
    to_return = []

    for v in vertices:
        x, y = v.rotated(body.angle) + body.position
        to_return.append((x, y))

    return to_return


def draw_poly_map(m):
    for i in range(len(m.body)):
        body = m.body[i]
        poly = m.poly[i]

        draw_poly(poly, body, m.outline_color, m.fill_color, m.outline_width)


def draw_poly(poly, body, outline_color, fill_color, outline_width):
    vertices = poly.get_vertices()
    # Returns Local Points Around (0, 0)
    # Expand Vertices

    # print(vertices)
    vertices = global_vertices(vertices, body)
    # print(vertices)
    # Transform Points
    for i in range(len(vertices)):
        v = vertices[i]
        vertices[i] = distort_point(v[0], v[1], 0)

    pygame.draw.polygon(screen, fill_color, vertices, 0)
    pygame.draw.polygon(screen, outline_color, vertices, outline_width)


def draw_stick_figure(sf):
    for key in sf.segments:
        segment = sf.segments[key]
        if key != 'HEAD' and key != 'NECK':
            draw_poly(segment.poly, segment.body, globals.COLORS['BLACK'], sf.color, 4)

    head = sf.segments['HEAD']
    h_pos = distort_point(head.body.position[0], head.body.position[1], 0)

    pygame.draw.circle(screen, sf.color, [round(h_pos[0]), round(h_pos[1])], 10, 0)
    pygame.draw.circle(screen, globals.COLORS['BLACK'], [round(h_pos[0]), round(h_pos[1])], 10, 4)


def set_map(m=defaultMap):
    global render_map

    d = m.data

    block_width, block_height = 100, 100

    # Adjust Camera Position
    cam.x = m.w * block_width/2 - 1/2 * block_width
    cam.y = m.h * block_height/2 - 1/2 * block_height

    back_cam.x = m.w/2 - 1/2
    back_cam.y = m.h/2 - 1/2
    print('CAM', cam.x, cam.y)

    render_map.block_list = list()
    render_map.body = list()
    render_map.poly = list()

    print(d)

    for a in range(len(d)):
        for b in range(len(d[a])):
            if d[a][b] == '1':

                # Reversed B, A because going through array (y, x)
                render_map.block_list.append(Block(b, a, 0, 1, 1))

                # Apply Map to Physics Engine
                # Infinite Mass & Moment => Static Object
                body = pymunk.Body(0, 0, pymunk.Body.STATIC)
                body.position = b * block_width, a * block_height
                poly = pymunk.Poly.create_box(body, (block_width, block_height), 0)

                globals.space.add(body, poly)
                render_map.body.append(body)
                render_map.poly.append(poly)


def magnitude(x, y):
    return math.sqrt(x*x+y*y)


def draw_hud():
    # Template
    # Template
    width = s_w/4

    for i in range(len(globals.PLAYERS)):
        player = globals.PLAYERS[i]
        start_x = round(i * width)

        # Draw Rectangle
        pygame.draw.rect(screen, (68, 68, 68), pygame.Rect((start_x + 50, s_h - 80), (150, 20)), 0)
        pygame.draw.rect(screen, (0, 0, 0), pygame.Rect((start_x + 50, s_h - 80), (150, 20)), 3)

        # Display PLAYER TEXT
        screen.blit(player.pre_rendered_text, (start_x + 90, s_h - 82.5))

        # Draw Lives Icons
        for i1 in range(player.lives):
            x = start_x + 85 + i1 * 30
            screen.blit(globals.ASSETS['STICK_FIGURE_IMG'], (x, s_h - 45))

        # Draw Circle (Player Icon)
        # Fill
        pygame.draw.circle(screen, player.color, (start_x + 50, s_h - 50), 30, 0)
        pygame.draw.circle(screen, (0, 0, 0), (start_x + 50, s_h - 50), 30, 3)


