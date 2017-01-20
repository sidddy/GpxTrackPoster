from . import utils


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

        # compute scale
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
