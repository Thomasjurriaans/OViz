from Functions import *
import cv2 as cv
import math
import numpy as np
from VideoRenderer import VideoRenderer

min_lat = 50.750277
max_lat = 53.555994

min_lon = 3.326407
max_lon = 7.17

max_x = 3495
max_y = 4124
ratio = max_x/max_y

print_height = 1020
print_width = int((print_height*ratio))

FPS = 60


def draw(history, railmap):
    video = VideoRenderer()                                        # Makes video object

    base = redraw_base(railmap, video)                             # Makes base map to draw on, also makes start animation.
    frame = base.copy()  # Reset frame to base
    add_pause_frames(30, video, frame)

    visited_places = []

    for row in history.iterrows():
        row = row[1]                                                # Extract from tuple
        frame = base.copy()                                         # Reset frame to base

        show_visited_places(frame, visited_places)
        show_trip_text(row, frame, visited_places)

        add_pause_frames(1, video, frame)

        write_trip_frames(row, video, frame, visited_places)

    frame = base.copy()                                             # Reset for final overview
    show_visited_places(frame, visited_places)
    add_pause_frames(60, video, frame)

    black = np.zeros((print_height, print_width, 3), np.uint8)      # makes a black background
    show_title_screen(220, video, black)
    video.render()


def write_trip_frames(row, video, frame, visited_places):
    for between_stops in row['route_coords']:
        i, prev_x, prev_y = 0, 0, 0
        for begin_coords, next_coords in current_and_next(between_stops):
            if next_coords is None: break                                                               # If destination is reached
            from_x, from_y, to_x, to_y = lonx(float(begin_coords[0])), laty(float(begin_coords[1])), lonx(float(next_coords[0])), laty(float(next_coords[1]))   # Convert all lon lat to x y

            cv.line(frame, (from_x, from_y), (to_x, to_y), (143, 55, 26), 2, lineType=cv.LINE_AA)

            dst = math.sqrt((to_x-prev_x)**2 + (to_y-prev_y)**2)
            if dst > 500:                                                                               # Arbitrary value to speed things up
                i += 1
                if i % 8 == 0:                                                                          # Only write 1 out of 8 frames that would actually be written
                    video.write(frame)
                    prev_x, prev_y = to_x, to_y                                                         # Used to calculate how far we've travelled since last written frame
    add_dest_visited_places(row, visited_places)
    for _ in range(0, 6):
        video.write(frame)                                                                              # Write 6 pause frames after destination has been reached


def add_pause_frames(amount, video, frame):
    for _ in range(0, amount):
        video.write(frame)


def add_dest_visited_places(row, visited_places):
    to_x, to_y = lonx(float(row['to_lon'])), laty(float(row['to_lat']))  # Convert all lon lat to x y
    to = [(to_x, to_y), row['Bestemming']]

    if to not in visited_places:
        visited_places.append(to)


def show_visited_places(frame, visited_places):
    for place in visited_places:
        x = place[0][0]
        y = place[0][1]
        cv.rectangle(frame, (x+4, y+4), (x-4, y-4), (143, 55, 26), thickness=-1)


def show_trip_text(row, frame, visited_places):
    from_x, from_y, to_x, to_y = lonx(float(row['from_lon'])), laty(float(row['from_lat'])), lonx(float(row['to_lon'])), laty(float(row['to_lat']))  # Convert all lon lat to x y

    origin = [(from_x, from_y), row['Vertrek']]
    to = [(to_x, to_y), row['Bestemming']]

    if origin not in visited_places:
        visited_places.append(origin)

    show_visited_places(frame, visited_places)

    cv.putText(frame, row['Datum'], (15, 40), cv.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=1, lineType=cv.LINE_AA)
    cv.putText(frame, origin[1], (15, 65), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness=1, lineType=cv.LINE_8)
    cv.arrowedLine(frame, (45, 77), (45, 85), (120, 120, 120), tipLength=0.4)
    cv.putText(frame, to[1], (15, 105), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), thickness=1,  lineType=cv.LINE_8)


def show_title_screen(duration, video, black):
    cv.putText(black, "Made with Python:", (print_width//4, 250), cv.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), thickness=2, lineType=cv.LINE_AA)
    cv.putText(black, "Using Pandas & OpenCV", (print_width//6, 350), cv.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), thickness=2, lineType=cv.LINE_AA)

    cv.putText(black, "Thomas Jurriaans", (print_width//4, int(print_height*0.95)), cv.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), thickness=1, lineType=cv.LINE_AA)

    for _ in range(duration):
        video.write(black)


def redraw_base(railmap, video):
    im = cv.imread("img/start_map_orange.png")
    im = cv.resize(im, (print_width, print_height), interpolation=cv.INTER_AREA)

    overlay = im.copy()
    inbetween = im.copy()

    i = 0
    for coords in railmap['coordinates']:
        coords = list(map(lambda c: [lonx(c[0]), laty(c[1])], coords))                              # Convert all lat, lon values to pixel values
        for current, next in current_and_next(coords):
            if next is None: break
            cv.line(inbetween, tuple(current), tuple(next), (77, 5, 202), 1, lineType=cv.LINE_AA)  # This image is used for the map initialisation animation.
            cv.line(overlay, tuple(current), tuple(next), (77, 5, 202), 1, lineType=cv.LINE_AA)    # Draw line with anti-aliasing
        if i % 5 == 0:
            video.write(inbetween)
        i += 1

    im = cv.addWeighted(overlay, 0.8, im, 0.2, 0)                                                   # Overlays image over same im without lines, so lines are half opacity
    cv.imwrite("img/base.png", im)
    return im


def laty(lat):
    return int(remap(lat, min_lat, max_lat, print_height, 0))       # map lat to y pixel


def lonx(lon):
    return int(remap(lon, min_lon, max_lon, 0, print_width))       # map lon to x pixel

