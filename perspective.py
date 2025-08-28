'''
Script ot analyze perspective in painting
'''

import matplotlib.pyplot as plt
import cv2
import numpy as np
import os

def onclick(event):
    global selected_points, modze
    if mode == 'point select' and event.xdata is not None and event.ydata is not None:
        selected_points.append((int(event.xdata), int(event.ydata)))
        draw_current_selections()

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
    _show(img_with_help)

def draw_current_selections():
    global image
    img_with_points = image
    for pt in selected_points:
        draw_point(pt, img_with_points)
    # Draw stored lines
    for line_points in stored_lines:
        draw_extended_line(line_points, img_with_points, draw_now=False)
    _show(img_with_points)

def draw_extended_line(points, img, draw_now=True, extend_to_boundaries=True):
    pt1, pt2 = points
    h, w, _ = img.shape
    dx, dy = pt2[0] - pt1[0], pt2[1] - pt1[1]
    if extend_to_boundaries:
        # Find intersections with image borders
        def get_intersection(x0, y0, dx, dy, w, h):
            intersections = []
            if dx != 0:
                for x in [0, w]:
                    y = y0 + (x - x0) * dy / dx
                    if 0 <= y <= h:
                        intersections.append((int(x), int(y)))
            if dy != 0:
                for y in [0, h]:
                    x = x0 + (y - y0) * dx / dy
                    if 0 <= x <= w:
                        intersections.append((int(x), int(y)))
            return intersections
        line_ends = get_intersection(pt1[0], pt1[1], dx, dy, w, h)
        if len(line_ends) == 2:
            cv2.line(img, line_ends[0], line_ends[1], (255, 255, 255), 3)
    else:
        # Extend the line only in the direction of pt2
        t = 10  # Scaling factor for line extension
        new_pt2 = (int(pt2[0] + t * dx), int(pt2[1] + t * dy))
        cv2.line(img, pt1, new_pt2, (255, 255, 0), 1)
    if draw_now:
        _show(img)

def save_line(event):
    global selected_points, stored_lines
    if event.key == 't' and len(selected_points) == 2:
        # Save line and draw it
        stored_lines.append(list(selected_points))
        draw_current_selections()
        selected_points.clear()  # Clear after saving

def change_point_size(change):
    global point_size
    point_size = max(1, point_size + change)
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

def toggle_extension_mode(event):
    global extend_to_boundaries
    if event.key == 'e':  # Toggle between boundary extension and directional extension
        extend_to_boundaries = not extend_to_boundaries
        mode = "Boundary Extension" if extend_to_boundaries else "Directional Extension"
        print(f"Extension mode changed to: {mode}")

def calculate_vanishing_point(img):
    # Load the image
    img_height, img_width = img.shape[:2]
    # Initialize the user-selected coordinates
    user_selected_point = []
    # Define a click event handler
    def onclick(event):
        # Check if the mouse button is pressed within the image boundaries
        if event.xdata is not None and event.ydata is not None:
            # Check if toolbar is active (zoom or pan)
            if fig.canvas.toolbar.mode == '':
                # Store the x and y coordinates
                user_selected_point.append((event.xdata, event.ydata))
                print(f"User clicked on: ({event.xdata:.2f}, {event.ydata:.2f})")
                # Disconnect the event and close the plot
                fig.canvas.mpl_disconnect(cid)
                plt.close()
            else:
                # Toolbar is active (zoom or pan), ignore the click
                pass
    # Display the image
    fig, ax = plt.subplots()
    ax.imshow(img)
    plt.title("Zoom and pan to locate the light source.\nThen deactivate zoom/pan and click on the light source location.")
    plt.axis('off')  # Hide axis ticks and labels for better visibility
    # Connect the click event handler
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    # Show the plot and wait for the user to click
    plt.show()
    # After the plot is closed, check if the user has selected a point
    if len(user_selected_point) == 0:
        print("No point was selected.")
        return None
    # Get the user-selected coordinates
    x_user, y_user = user_selected_point[0]
    return np.array([x_user, y_user])

def _show(img):
    """Display an OpenCV image with the correct channel order."""
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.draw()



# Load your image
# parent_dir = 'C:/Users/pepel/PROJECTS/DATA/Caravaggio/images'
# img_filename = str(39) + '.jpg'
# img_path = os.path.join(parent_dir, img_filename)
img_path = 'imgs/flagellazione-gndm-full.jpg'
image = cv2.imread(img_path)
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

selected_points = []
stored_lines = []
mode = 'zoom'
point_size = 2
show_help = False
extend_to_boundaries = True

help_text = """
Help Guide:
- Press 'p' to enter point select mode
- Press 'z' to go back to zoom mode
- Click to select two points
- Press 't' to draw the line from last two points and clear points
- Press '+' to increase point size
- Press '-' to decrease point size
- Press 'e' to toggle line extension mode (Boundary/Directional)
- Press 'h' to toggle this help guide
"""
# load vanishing point
# vanishing_point = np.load('results/vanishing_point_flagellation.npy')
fig, ax = plt.subplots()
ax.imshow(image_rgb)
cid = fig.canvas.mpl_connect('button_press_event', onclick)
kid = fig.canvas.mpl_connect('key_press_event', toggle_mode)
tid = fig.canvas.mpl_connect('key_press_event', save_line)
# plot vanishing point
# plt.plot(vanishing_point[0], vanishing_point[1], 'ro', markersize=3)
plt.axis('off')
plt.show()


# save image
cv2.imwrite('results/beheadingjohn.jpg', image)
# Calculate the vanishing point
# vanishing_point = calculate_vanishing_point(image)
# np.save('results/vanishing_point_flagellation.npy', vanishing_point)