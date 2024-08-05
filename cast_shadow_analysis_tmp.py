'''
tmp to deevelop the cast shadows analysis. Get occluder-shadow pairs in a painting to discover the light source location.

Display an image. Zoom in to a section, Select the point of the cast shadow, and then 2 points on the occluder. These 2 points
indicate the range where the user thinks is possible to locate the occluder point of the cast shadow. The apperture of the cone defines angular uncertainty. 

Use -h on your keyboard to display the help guide to use the tool. 

To do:
- Convert cone appertures to probabilities
- Add self-shadows as half-plane constrains
- Use probabilities to compute MLE of the light source location. 

'''

import cv2
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np


parent_dir = 'C:/Users/pepel/PROJECTS/FaceArt/SynergyNet/masks/'
img_filename = os.path.join(parent_dir, 'bhim00037016.jpg')

img_path = os.path.join(parent_dir, img_filename)
image = mpimg.imread(img_path)

selected_points = []
mode = 'zoom'
stored_triangles = []
point_size = 2  # Initial point size
show_help = False

help_text = """
Help Guide:
The tool starts in zoom mode.
- Press 'p' to enter point select mode
- Press 'z' to go back to zoom mode
- Click to select points (3 points form a triangle)
- Press 't' to save the current triangle
- Press 'r' to remove the last saved triangle
- Press '+' to increase point size resolution
- Press '-' to decrease point size resolution
- Press 'h' to toggle this help guide
"""

def onclick(event):
    global selected_points, mode
    if mode == 'point select' and event.xdata is not None and event.ydata is not None:
        selected_points.append((int(event.xdata), int(event.ydata)))
        draw_current_selections()
        if len(selected_points) == 3:
            draw_aperture(selected_points)
            mode = 'zoom'

def draw_point(point, img):
    cv2.circle(img, point, point_size, (255, 0, 0), -1)

def add_help_text(img):
    y0, dy = 30, 30
    for i, line in enumerate(help_text.strip().split('\n')):
        y = y0 + i * dy
        cv2.putText(img, line, (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)

def draw_help_text():
    global image, show_help
    img_with_help = image.copy()
    if show_help:
        add_help_text(img_with_help)
    plt.imshow(img_with_help)
    plt.axis('off')  # Hide axis
    plt.draw()

def draw_current_selections():
    global image
    img_with_points = image.copy()
    # Draw stored triangles
    for tri in stored_triangles:
        draw_aperture(tri, img=img_with_points, draw_now=False)
    # Draw the current points with full opacity
    for pt in selected_points:
        draw_point(pt, img_with_points)
        # Draw help text if enabled
    plt.imshow(img_with_points)
    plt.draw()

def draw_aperture(points, img=None, draw_now=True):
    if img is None:
        img = image.copy()
    pt1, pt2, pt3 = points
    # Draw lines representing the aperture
    cv2.line(img, pt1, pt2, (255, 0, 0), 2)
    cv2.line(img, pt1, pt3, (255, 0, 0), 2)
    # Extend lines for better visualization
    line_length = 1000
    extended_pt2 = (pt2[0] + line_length * (pt2[0] - pt1[0]), pt2[1] + line_length * (pt2[1] - pt1[1]))
    extended_pt3 = (pt3[0] + line_length * (pt3[0] - pt1[0]), pt3[1] + line_length * (pt3[1] - pt1[1]))
    cv2.line(img, pt1, extended_pt2, (255, 0, 0), 2)
    cv2.line(img, pt1, extended_pt3, (255, 0, 0), 2)
    if draw_now:
        plt.imshow(img)
        plt.draw()

def save_triangle(event):
    global selected_points, stored_triangles
    if event.key == 't' and len(selected_points) == 3:
        stored_triangles.append(list(selected_points))
        print(f"Triangle saved: {selected_points}")
        selected_points.clear()
        draw_current_selections()

def remove_last_triangle(event):
    global stored_triangles
    if event.key == 'r' and stored_triangles:
        removed_triangle = stored_triangles.pop()
        print(f"Triangle removed: {removed_triangle}")
        draw_current_selections()

def change_point_size(change):
    global point_size
    point_size = max(1, point_size + change)
    print(f"Point size changed to: {point_size}")
    draw_current_selections()

def toggle_mode(event):
    global mode, show_help
    if event.key == 'p':
        mode = 'point select'
        print("Mode changed to: Point Select")
    elif event.key == 'z':
        mode = 'zoom'
        print("Mode changed to: Zoom")
    elif event.key == '+':
        change_point_size(1)
    elif event.key == '-':
        change_point_size(-1)
    elif event.key == 'h':
        show_help = not show_help
        draw_help_text()
        print("Help guide toggled")


fig, ax = plt.subplots()
ax.imshow(image)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
kid = fig.canvas.mpl_connect('key_press_event', toggle_mode)
sid = fig.canvas.mpl_connect('key_press_event', save_triangle)
rid = fig.canvas.mpl_connect('key_press_event', remove_last_triangle)
ax.axes('off')
plt.axis('off')
plt.show()



