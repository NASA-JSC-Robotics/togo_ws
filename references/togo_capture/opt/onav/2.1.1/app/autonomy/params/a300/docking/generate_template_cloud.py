#!/usr/bin/env python3

import numpy as np
   
def generate_point_vector(x1, y1, x2, y2, thickness, density=500):
    dx = x2 - x1
    dy = y2 - y1
    length = np.sqrt(dx*dx + dy*dy)
    if length == 0:
        return np.array([])
        
    nx = -dy/length * thickness/2
    ny = dx/length * thickness/2
    num_length = int(np.ceil(length * density))
    num_width = int(np.ceil(thickness * density))
    t_length = np.linspace(0, 1, num_length)
    t_width = np.linspace(-1, 1, num_width)
    tt_length, tt_width = np.meshgrid(t_length, t_width)
    x = x1 + dx * tt_length + nx * tt_width
    y = y1 + dy * tt_length + ny * tt_width
    z = np.zeros_like(x)
    points = np.column_stack((x.ravel(), y.ravel(), z.ravel()))
    return points

def save_pcd(filename, points):
    num_points = points.shape[0]

    with open(filename, 'w') as f:
        # Standard PCD header (ASCII)
        f.write("VERSION .7\n")
        f.write("FIELDS x y z\n")
        f.write("SIZE 4 4 4\n")
        f.write("TYPE F F F\n")
        f.write("COUNT 1 1 1\n")
        f.write(f"WIDTH {num_points}\n")
        f.write("HEIGHT 1\n")
        f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
        f.write(f"POINTS {num_points}\n")
        f.write("DATA ascii\n")
        for p in points:
            f.write(f"{p[0]} {p[1]} {p[2]}\n")

def main():
    # dimensions:
    # 11 cm
    # 26.5 cm
    # 29.5 cm
    # 11 cm
    #  l1
    # ______
    #      |
    #      | l2
    #      |_ _ _ _l3_____
    #                    |
    #                    | l4
    #                    |
    
    L1 = 0.11
    L2 = 0.265
    L3 = 0.295
    L4 = 0.11
    D = 750
    
    thickness=0.005
    l1 = generate_point_vector(0, 0, -L1, 0, thickness)
    l2 = generate_point_vector(0, 0, 0, -L2, thickness)
    l3 = generate_point_vector(0, -L2, L3, -L2, thickness)
    l4 = generate_point_vector(L3, -L2, L3, -(L2+L4), thickness)
    
    l1 = generate_point_vector(0, 0, 0, L1, thickness)
    l2 = generate_point_vector(0, 0, -L2, 0, thickness)
    l3 = generate_point_vector(-L2, 0, -L2, -L3, thickness)
    l4 = generate_point_vector(-L2, -L3, -(L2+L4), -L3, thickness)
    
    points = np.vstack((l1, l2, l3, l4))
    points = np.unique(points, axis=0)
    save_pcd("a300_side_dock_target.pcd", points)
    print(f"Saved L-shape point cloud to 'a300_side_dock_target.pcd'.")
    
if __name__ == "__main__":
    main()
