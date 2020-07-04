import os
import codecs

class Predefined_Points():
    def __init__(self):
        self.predefined_points_skeleton_path = os.path.join(
            'data', 'predefined_points_skeleton.txt'
        )
    def define_points_links(self):
        point_link = []
        if os.path.exists(self.predefined_points_skeleton_path) is True:
            with codecs.open(self.predefined_points_skeleton_path, 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if not line == '\n':
                        points = line.strip().split(',')
                        point_link.append([int(points[0]), int(points[1])])
        return point_link