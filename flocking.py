"""
This module helps in the creation of triangles given a center and orientation and allows
for the computation of flocking force vectors. It is meant for convenience to show a real
visualization application rather than just the drawing of shapes.

Note that it makes two critical assumptions which are non-optimal (for simplicity of writing/reading the code):
first, a better implementation of this would represent each object in a class and make the simulation object
oriented; second, the orientation is stored in an angle instead of a vector which is technically more memory
efficient for large numbers of elements in storing their state, but it is not as efficient as storing
the unit vectors. This choice was made under the assumption that orientation as an angle would be
more intuitive for new graphics programmers.
"""

import numpy as np

def get_triangle_points(x, y, o, nose_length=30, wing_length=10, wing_angle=1.175):
    """
    Helper function to get points for a triangle around a centroid.

    x (float or int) - x component of center of triangle
    y (float or int) - y component of center of triangle
    o (float) - orientation of triangle in radians
    nose_length (int) - length of the long axis of the triangle
    wing_length (int) - length of the short axes of the triangle
    wing_angle (float) - angle between long and short axes in radians
    """
    # Compute the front point of the triangle
    beak_x = np.cos(o) * nose_length + x
    beak_y = np.sin(o) * nose_length + y
    # Compute the "left" point of the triangle
    left_wing_x = np.cos(o-wing_angle) * wing_length + x
    left_wing_y = np.sin(o-wing_angle) * wing_length + y
    # Compute the "right" point of the triangle
    right_wing_x = np.cos(o+wing_angle) * wing_length + x
    right_wing_y = np.sin(o+wing_angle) * wing_length + y
    # Find the centroid of the triangle
    centroid_offset = np.array([(beak_x + left_wing_x + right_wing_x)/3. - x, (beak_y + left_wing_y + right_wing_y)/3. - y])
    # Offset all the points according to the centroid so rotation is around that centroid
    beak = np.array([beak_x, beak_y]) - centroid_offset
    left_wing = np.array([left_wing_x, left_wing_y]) - centroid_offset
    right_wing = np.array([right_wing_x, right_wing_y]) - centroid_offset
    # Return the triangle points
    return np.array([beak, left_wing, right_wing])

def update_locations(xs, ys, os, canvas_size, speed=5.0, interaction_radius=200, weights=(1.0, 1.0, 1.0)):
    """
    Given a set of positions and orientations, speed, an interaction radius, and weightings for
    alignment, cohesion, and separation, determine the position and orientation of each entity on the next
    iteration.
    xs (list(int or float)) - a list of x coordinates
    ys (list(int or float)) - a list of y coordinates
    os (list(float)) - a list of orientations in radians
    canvas_size (tuple(int, int)) - a tuple representing the width and height of the draw canvas (for wrapping behaviors)
    speed (float) - a speed in pixels that all elements go
    interaction_radius (int or float) - the radius in which all elements interact
    weights (tuple(float, float, float)) - the relative weighting of alignment, cohesion, and separation forces
    """
    assert len(weights) == 3, "weights must contain three numbers, weighting the importance of alignment, cohesion, and separation, respectively"
    new_xs, new_ys, new_os = [], [], [] # a place to store new positions/orientations
    for i in range(len(xs)): # iterate through each element
        vector = np.array([np.cos(os[i]), np.sin(os[i])]) # compute the element's orientation vector
        nxs, nys, nos = find_neighbors(i, xs, ys, os, interaction_radius) # compute the neighbor information
        if len(nxs) != 0:
            mx, my = np.mean(nxs), np.mean(nys) # compute the mean of the neighbor positions
            alignment = np.mean([[np.cos(o), np.sin(o)] for o in nos], axis=0) # compute the mean of the neighbor orientations
            alignment_mag = np.linalg.norm(alignment) # compute the alignment vector norm
            cohesion = np.array([mx - xs[i], my - ys[i]]) # compute the difference between mean position and element position
            cohesion_mag = np.linalg.norm(cohesion) # compute the cohesion vector norm
            separation = np.array([-1*np.sum(nxs - xs[i]), -1*np.sum(nxs - xs[i])]) # compute the negative difference between the sum of neighbors and element positions
            separation_mag = np.linalg.norm(separation) # compute the separation vector norm
            # If each force element has a non-zero magnitude, weight it and add it to the original orientation vector
            if alignment_mag != 0.0:
                vector += alignment/alignment_mag * weights[0]
            if cohesion_mag != 0.0:
                vector += cohesion/cohesion_mag * weights[1]
            if separation_mag != 0.0:
                vector += separation/separation_mag * weights[2]
        vector = vector/np.linalg.norm(vector) * speed # normalize the final orientation vector and multiply by the speed
        angle = np.tanh(vector[1]/vector[0]) if vector[1] != 0 else 0 # find the new orientation angle
        # compute the new x and y positions, assuming the canvas wrapping should be toroidal
        new_xs.append((vector[0]+xs[i]) % canvas_size[0])
        new_ys.append((vector[1]+ys[i]) % canvas_size[1])
        new_os.append(angle)
    return new_xs, new_ys, new_os

def find_neighbors(idx, xs, ys, os, distance):
    """
    Find the neighbors of an element given the positions and orientations of the elements and a minimum distance.
    idx (int) - the index of the element to find neighbors for
    xs (list(int or float)) - a list of x coordinates
    ys (list(int or float)) - a list of y coordinates
    os (list(float)) - a list of orientations in radians
    distance (int or float) - the radius in which all elements interact
    """
    x0, y0 = xs[idx], ys[idx] # get the element coordinate in question
    adjacent_xs, adjacent_ys, adjacent_os = [], [], []
    for i, (x, y, o) in enumerate(zip(xs, ys, os)):
        if i == idx: # do not count self-neighbors
            continue
        if np.sqrt(np.power(x-x0, 2) + np.power(y-y0, 2)) < distance: # check euclidean distance, note this fails over boundaries
            adjacent_xs.append(x)
            adjacent_ys.append(y)
            adjacent_os.append(o)
    return np.array(adjacent_xs), np.array(adjacent_ys), np.array(adjacent_os)
