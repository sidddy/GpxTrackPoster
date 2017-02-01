# Copyright 2016-2017 Florian Pigorsch & Contributors. All rights reserved.
#
# Use of this source code is governed by a MIT-style
# license that can be found in the LICENSE file.

from . import utils
import urllib.request

class TracksDrawer:
    def __init__(self):
        self.poster = None

    def draw(self, poster, d, w, h, offset_x, offset_y):
        self.poster = poster

        xy_polylines = []
        xy_polylines_special = []
        for track in self.poster.tracks:
            track_xy = []
            for polyline in track.polylines:
                if polyline:
                    subline = []
                    lastLat = 0.0
                    lastLng = 0.0
                    for (lat, lng) in polyline:
                        if abs(lat - lastLat) > 0.02 or abs(lng - lastLng) > 0.02:
                            if subline:
                                track_xy.append(subline)
                            subline = []
                        subline.append(utils.latlng2xy(lat, lng))
                        lastLng = lng
                        lastLat = lat
                    if subline:
                        track_xy.append(subline)
                    #track_xy.append([utils.latlng2xy(lat, lng) for (lat, lng) in polyline])
            if track_xy:
                xy_polylines.extend(track_xy)
                if track.special:
                    xy_polylines_special.extend(track_xy)

        if not xy_polylines:
            return

        (min_x, min_y, max_x, max_y) = utils.compute_bounds_xy(xy_polylines)
        d_x = max_x - min_x
        d_y = max_y - min_y

        #print ("{:f}\n".format(max_x(max_y - min_y), (h / (d_y * scale) - 1) / 2))

        # compute scale
        if self.poster.map_url and self.poster.map_provider:
            if w/h <= d_x/d_y:
                scale = w/d_x
                max_y_ = max_y + (max_y - min_y) * (h / (d_y * scale) - 1) / 2
                min_y_ = min_y - (max_y - min_y) * (h / (d_y * scale) - 1) / 2
                max_x_ = max_x
                min_x_ = min_x
            else:
                scale = h/d_y
                max_x_ = max_x + (max_x - min_x) * (w / (d_x * scale) - 1) / 2
                min_x_ = min_x - (max_x - min_x) * (w / (d_x * scale) - 1) / 2
                max_y_ = max_y
                min_y_ = min_y

            (min_lat, min_lng) = utils.xy2latlng(min_x_, min_y_)
            (max_lat, max_lng) = utils.xy2latlng(max_x_, max_y_)

            backgroundImage = "{}?bounds={:f},{:f},{:f},{:f}&size=2048x2048&maptype={}";
            urllib.request.urlretrieve(backgroundImage.format(self.poster.map_url, min_lat, min_lng, max_lat, max_lng, self.poster.map_provider), "img/map.png")
            d.add(d.image("img/map.png", insert=(offset_x, offset_y), size=(w, h)))
        else:
            scale = w/d_x if w/h <= d_x/d_y else h/d_y

        # compute offsets such that projected track is centered in its rect
        offset_x += 0.5 * w - 0.5 * scale * d_x
        offset_y += 0.5 * h - 0.5 * scale * d_y

        scaled_lines = []
        for line in xy_polylines:
            scaled_line = []
            for (x, y) in line:
                scaled_x = offset_x + scale * (x - min_x)
                scaled_y = offset_y + scale * (y - min_y)
                scaled_line.append((scaled_x, scaled_y))
            scaled_lines.append(scaled_line)
        scaled_lines_special = []
        for line in xy_polylines_special:
            scaled_line = []
            for (x, y) in line:
                scaled_x = offset_x + scale * (x - min_x)
                scaled_y = offset_y + scale * (y - min_y)
                scaled_line.append((scaled_x, scaled_y))
            scaled_lines_special.append(scaled_line)

        color = self.poster.colors["track"]
        color_special = self.poster.colors["special"]

        for line in scaled_lines:
            d.add(d.polyline(points=line, stroke=color, stroke_opacity=0.02, fill='none', stroke_width=0.5, stroke_linejoin='round', stroke_linecap='round'))
        for line in scaled_lines:
            d.add(d.polyline(points=line, stroke=color, stroke_opacity=0.05, fill='none', stroke_width=0.2, stroke_linejoin='round', stroke_linecap='round'))
        for line in scaled_lines:
            d.add(d.polyline(points=line, stroke=color, fill='none', stroke_width=0.05, stroke_linejoin='round', stroke_linecap='round'))
        for line in scaled_lines_special:
            d.add(d.polyline(points=line, stroke=color_special, fill='none', stroke_width=0.05, stroke_linejoin='round', stroke_linecap='round'))
