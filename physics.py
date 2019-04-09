import pygame
import math
import sys
import pymunk
import pymunk.pygame_util
import globals
import copy

space = globals.space
stick_figures = []
pymunk.pygame_util.positive_y_is_up = False

space.gravity = 0, 400
# Global Pi
pi = math.pi


class StickFigure:

    def remove_self_from_space(self):
        for key in self.segments:
            seg = self.segments[key]

            space.remove(seg.body, seg.poly)

    def scale_points(self):
        for i in range(len(self.segment_init_coord)):
            for i1 in range(len(self.segment_init_coord[i])):
                self.segment_init_coord[i][i1] *= self.scale

    def __init__(self, x, y, color, player_num):
        self.x = x  # The Center Line of Stick Figure
        self.y = y  # The Top Of Stick Figure
        self.color = color
        self.scale = globals.SEGMENT_SCALE
        self.player_num = player_num
        self.active_item = None
        self.active_item_type = ''

        # self.item = None

        self.segments = copy.deepcopy(globals.SEGMENTS)

        # Define Widths of Segments:
        for key in self.segments:
            seg = self.segments[key]

            seg.width *= globals.SEGMENT_SCALE
            seg.length *= globals.SEGMENT_SCALE
            mass = globals.SEGMENT_MASSES[key]

            seg.body = pymunk.Body(mass, pymunk.moment_for_box(mass, (seg.width, seg.length)))
            seg.body.position = -1, -1
            # seg.body.angular_velocity_limit = 0
            # seg.body.velocity_limit = 10

            seg.poly = pymunk.Poly.create_box(seg.body, (seg.length, seg.width), 1)
            seg.poly.friction = globals.PLAYER_FRICTION

        """
            |----|
            |    | width
            |____|
               length  
        """

        # Define Segment POS & OBJECTS (Initialization)

        self.segments['NECK'].body.position = \
            self.x, self.y + self.segments['NECK'].width/2

        self.segments['TORSO'].body.position = \
            self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width/2

        self.segments['L_BICEP'].body.position = \
            self.x - self.segments['TORSO'].length/2 - self.segments['L_BICEP'].length/2, \
            self.y + self.segments['NECK'].width + self.segments['L_BICEP'].width/2

        self.segments['R_BICEP'].body.position = \
            self.x + self.segments['TORSO'].length / 2 + self.segments['R_BICEP'].length/2, \
            self.y + self.segments['NECK'].width + self.segments['L_BICEP'].width/2

        self.segments['L_FOREARM'].body.position = \
            self.x - self.segments['TORSO'].length/2 - self.segments['L_BICEP'].length - \
            self.segments['L_FOREARM'].length/2, \
            self.y + self.segments['NECK'].width + self.segments['L_BICEP'].width/2

        self.segments['R_FOREARM'].body.position = \
            self.x + self.segments['TORSO'].length / 2 + \
            self.segments['R_BICEP'].length + self.segments['R_FOREARM'].length/2, \
            self.y + self.segments['NECK'].width + self.segments['R_BICEP'].width/2

        self.segments['L_THIGH'].body.position = \
            self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width + self.segments['L_THIGH'].width/2

        self.segments['R_THIGH'].body.position = self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width + self.segments['R_THIGH'].width/2

        self.segments['L_CALF'].body.position = \
            self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width + \
            self.segments['L_THIGH'].width + self.segments['L_CALF'].width/2

        self.segments['R_CALF'].body.position = \
            self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width + self.segments['R_THIGH'].width + self.segments['R_CALF'].width/2

        # Initialization of Head
        head_radius = 1.5 * globals.SEGMENT_SCALE
        self.segments['HEAD'] = globals.Segment((-1, -1), head_radius, head_radius)
        self.segments['HEAD'].body = pymunk.Body(10, pymunk.moment_for_circle(10, 0, self.segments['HEAD'].length))
        self.segments['HEAD'].body.position = self.x, self.y - self.segments['HEAD'].length
        self.segments['HEAD'].poly = pymunk.Circle(self.segments['HEAD'].body, self.segments['HEAD'].length)
        # space.add(self.segments['HEAD'].body, self.segments['HEAD'].poly)

        # Add Each Segment To Space
        for key in self.segments:
            seg = self.segments[key]

            # No Collision Between Limbs
            category = globals.COLLISION_TYPE['PLAYERS'][player_num]

            seg.poly.filter = pymunk.ShapeFilter(categories=category, mask=pymunk.ShapeFilter.ALL_MASKS ^ category)
            seg.poly.collision_type = globals.COLLISION_ID['PLAYERS'][player_num]

            space.add(seg.body, seg.poly)
        # Add Joints
        self.joints = {
            'L_SHOULDER': globals.Joint((self.x - self.segments['TORSO'].length,
                                         self.y + self.segments['NECK'].width + self.segments['L_BICEP'].width/2),
                                        (-pi/2, pi/2)),
            'R_SHOULDER': globals.Joint((self.x + self.segments['TORSO'].length,
                                         self.y + self.segments['NECK'].width + self.segments['R_BICEP'].width / 2),
                                        (-pi/2, pi/2)),
            'L_ELBOW': globals.Joint((self.x - self.segments['TORSO'].length - self.segments['L_BICEP'].length,
                                      self.y + self.segments['NECK'].width + self.segments['L_BICEP'].width/2),
                                     (-pi/2, pi/2)),
            'R_ELBOW': globals.Joint((self.x + self.segments['TORSO'].length + self.segments['R_BICEP'].length,
                                      self.y + self.segments['NECK'].width + self.segments['R_BICEP'].width / 2),
                                     (-pi/2, pi/2)),
            'L_HIP': globals.Joint((self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width),
                                   (-pi/2, 0)
                                   ),
            'R_HIP': globals.Joint((self.x, self.y + self.segments['NECK'].width + self.segments['TORSO'].width),
                                   (0, pi/2)
                                   ),
            'L_KNEE': globals.Joint((self.x, self.y + self.segments['NECK'].width +
                                     self.segments['TORSO'].width + self.segments['L_THIGH'].width),
                                    (pi - pi/16, 0)),
            'R_KNEE': globals.Joint((self.x, self.y + self.segments['NECK'].width +
                                     self.segments['TORSO'].width + self.segments['R_THIGH'].width),
                                    (-pi + pi/16, 0)),
            'NECK': globals.Joint((self.x, self.y),
                                  (0, 0)
                                  )
        }

        control_group = []
        control_group.extend(self.joints.keys())

        # pymunk Joint Initialization
        for key in self.joints:
            if key in control_group:
                joint = self.joints[key]
                pair = globals.JOINT_PAIRS[key]

                joint.pivot_joint = pymunk.PivotJoint(self.segments[pair[0]].body, self.segments[pair[1]].body,
                                                      joint.pos)
                joint.rotary_limit_joint = pymunk.RotaryLimitJoint(self.segments[pair[0]].body,
                                                                   self.segments[pair[1]].body, joint.range[0],
                                                                   joint.range[1])
                space.add(joint.pivot_joint)
                space.add(joint.rotary_limit_joint)

        """
         # The coordinate of the top of the limb
        self.segment_init_coord = [[0, 0, le], [-wi/2, 0, le], [wi/2, 0, le],
                                   [-wi/2, le - wi, le], [wi/2, le - wi, le], [0, le - wi, 1.5*le],
                                   [-wi/2, 2.5*le - 2 * wi, le],
                                   [wi/2, 2.5*le - 2 * wi, le], [-wi/2, 3.5*le - 3 * wi, le], [wi/2, 3.5*le - 3 * wi, le]]

        self.segment_pairs = [[1, 0], [2, 0], [3, 1], [4, 2],
                              [5, 0], [6, 5], [7, 5], [8, 6], [9, 7]]
        # L Elbow Neck, R Elbow Neck, L Hand L Elbow, R Hand R Elbow,
        # Neck Spine, L Thigh Spine, R Thigh Spine, L Knee, R Knee
        # Redo this *****
        self.rotary_limit_values = [[pi/16, pi-pi/16], [-pi + pi/16, -pi/16], [0, pi - pi/16], [-pi + pi/16, 0],
                                    [-pi/4, -pi + pi/4], [-pi/2, 0], [0, pi/2], [0, pi - pi/16], [-pi + pi/16, 0]]

        self.scale_points()

        # Segment Initiation

        self.body = list()
        self.poly = list()

        # self.filter = pymunk.ShapeFilter(categories=0b100, mask=pymunk.ShapeFilter.ALL_MASKS ^ 0b100)

        for segment in self.segment_init_coord:
            x = segment[0] + self.x
            y = segment[1] + self.y
            l = segment[2]

            # Base Draw Coordinates ( in counter clockwise)
            # Later Transform by factors x y l
            # bc = [[-(wi/2)*self.scale, 0], [-(wi/2)*self.scale, le], [(wi/2)*self.scale, le], [(wi/2)*self.scale, 0]]
            bc = [[0, 0], [0, l], [wi*self.scale, 0], [wi*self.scale, l]]
            b = pymunk.Body(10, 10)
            b.position = x, y
            p = pymunk.Poly(b, bc, None, 0)
            p.filter = pymunk.ShapeFilter(categories=1, mask=pymunk.ShapeFilter.ALL_MASKS ^ 1)
            self.body.append(b)
            self.poly.append(p)

            #space.add(b, p)

        self.joints = list()
        self.rotary_limits = list()

        # for pair in self.segment_pairs:
        for i in range(len(self.segment_pairs)):
            pair = self.segment_pairs[i]

            a = self.body[pair[0]]
            b = self.body[pair[1]]

            x, y = a.position
            x += wi * self.scale / 2
            y += wi * self.scale / 2

            j = pymunk.PivotJoint(a, b, (x, y))
            #space.add(j)
            self.joints.append(j)

            # Add Rotary Joint Limits
            print(self.rotary_limit_values[i][0])
            r = pymunk.RotaryLimitJoint(a, b, self.rotary_limit_values[i][0], self.rotary_limit_values[i][1])
            # space.add(r)
            self.rotary_limits.append(r)

        """


"""
def static_borders():
    sb = space.static_body
    wb = [pymunk.Segment(sb, (0, 0), (0, 720), 0.0),
          pymunk.Segment(sb, (0, 720), (1280, 720), 0.0),
          pymunk.Segment(sb, (1280, 720), (1280, 0), 0.0),
          pymunk.Segment(sb, (0, 0), (1280, 0), 0.0)
          ]

    for border in wb:
        border.elasticity = 0
        border.friction = 0

    space.add(wb)

"""
# static_borders()
# sf = StickFigure(400, 400, (0, 0, 0))
