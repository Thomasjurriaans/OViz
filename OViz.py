import time
import DataHandling
import Drawing
import APIconfig

start_time = time.time()

refresh = True                                                              # If true, reprocess all history data, station data, and retrieve information from API's, also redraw base for drawing.
print("Getting railmap...")                                                 # set to true whenever things (eg. resolution) are changed

railmap = DataHandling.get_railmap_data(APIconfig.ns_app_key, refresh=refresh)                    # Get the Railmap from NS's API

print("Getting history, stations...")
history, stations = DataHandling.get_csv_data(APIconfig.ns_app_key, railmap, refresh=refresh)     # Prepare journey history, and station list

print("Writing frames...")
Drawing.draw(history, railmap)                             # Draw all the frames, render the video with FFmpeg

print("Finished: %s seconds" % (time.time() - start_time))
