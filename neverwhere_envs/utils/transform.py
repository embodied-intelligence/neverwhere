import numpy as np

def compute_alignment_transform(points):
    """
    Compute a transformation matrix to align four points such that:
    - First point becomes the origin (0,0,0)
    - Second point lies on positive X-axis
    - Third point lies in XY plane (z=0)
    - Fourth point is left unchanged
    
    Parameters:
        points (np.ndarray): An array of shape (4, 3) containing four points.
        
    Returns:
        np.ndarray: A 4x4 transformation matrix.
    """
    if points.shape != (4, 3):
        raise ValueError("Input must be a numpy array with shape (4, 3)")

    # Ensure points are float type
    points = points.astype(float).copy()

    P0, P1, P2, P3 = points

    # Step 1: Translate P0 to origin
    translated_points = points - P0

    # Step 2: Compute new X axis (from P0 to P1)
    x_axis = translated_points[1]
    norm_x = np.linalg.norm(x_axis)
    if norm_x == 0:
        raise ValueError("P0 and P1 cannot be the same point.")
    x_axis /= norm_x

    # Step 3: Compute new Y axis
    # Project P2 onto plane perpendicular to X axis
    v = translated_points[2]
    proj_v_on_x = np.dot(v, x_axis) * x_axis
    y_axis = v - proj_v_on_x
    norm_y = np.linalg.norm(y_axis)
    if norm_y == 0:
        raise ValueError("P0, P1, and P2 are colinear.")
    y_axis /= norm_y

    # Step 4: Compute new Z axis
    z_axis = np.cross(x_axis, y_axis)
    norm_z = np.linalg.norm(z_axis)
    if norm_z == 0:
        raise ValueError("Cannot compute a valid Z axis; check the input points.")
    z_axis /= norm_z

    # Check P3's z-coordinate in the new coordinate system
    p3_new = np.dot(translated_points[3], z_axis)
    if p3_new < 0:
        z_axis = -z_axis

    # Rotation matrix: columns are the new axes
    rotation = np.vstack([x_axis, y_axis, z_axis]).T

    # Correctly construct the transformation matrix using rotation.T
    transform_matrix = np.eye(4)
    transform_matrix[:3, :3] = rotation.T  # Use transpose
    transform_matrix[:3, 3] = -rotation.T @ P0  # Translation part

    return transform_matrix

# Usage example
if __name__ == "__main__":
    import numpy as np

    points = np.array([
        [1.0, 0.0, 3.0],    # P0
        [4.0, 5.0, 6.0],    # P1
        [7.0, 9.0, 5.0],    # P2
        [10.0, 17.0, 19.0]  # P3
    ])

    transform = compute_alignment_transform(points)

    print("Transformation Matrix:")
    print(transform)

    P0_transformed = transform @ np.append(points[0], 1)
    P1_transformed = transform @ np.append(points[1], 1)
    P2_transformed = transform @ np.append(points[2], 1)
    P3_transformed = transform @ np.append(points[3], 1)

    print("\nTransformed P0:", P0_transformed[:3])
    print("Transformed P1:", P1_transformed[:3])
    print("Transformed P2:", P2_transformed[:3])
    print("Transformed P3:", P3_transformed[:3])