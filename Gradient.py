import math

def err(s):
    print("Error: "+s) 


class LinearGrad:
    def __init__(self, aspect, angle):
        self.aspect = aspect
        self.dx = math.sin(angle)
        self.dy = math.cos(angle)
        # Project corners onto gradient direction to find span
        corners = [(0, 0), (aspect, 0), (0, 1), (aspect, 1)]
        projections = [cx * self.dx + cy * self.dy for cx, cy in corners]
        self.min_proj = min(projections)
        self.max_proj = max(projections)
        self.span = self.max_proj - self.min_proj
        self.y = 0

    def setY(self, y):
        self.y = y

    def getX(self, x):
        # Project point (x, y) onto gradient direction and normalize
        proj = x * self.dx + self.y * self.dy
        if self.span == 0:
            return 0
        return (proj - self.min_proj) / self.span

class RadialGrad:
    def __init__(self, aspect, cx=0.5, cy=0.5, size="farthest-corner"):
        self.aspect = aspect
        self.cx = cx
        self.cy = cy
        self.size = size
        self.y = 0
        self.max_dist = self._compute_max_dist()
        #print(f"c={self.cx},{self.cy} a={aspect} d={self.max_dist}")

    def _corner_dist(self, x, y):
        dx = x - self.cx
        dy = y - self.cy
        return math.sqrt(dx*dx + dy*dy)

    def _compute_max_dist(self):
        if self.size == "closest-side":
            x_side = min(self.cx, 1 - self.cx)
            y_side = min(self.cy, 1 - self.cy)
            return min(x_side, y_side)
        elif self.size == "farthest-side":
            x_side_far = max(self.cx, 1 - self.cx)
            y_side_far = max(self.cy, 1 - self.cy)
            return max(x_side_far, y_side_far)
        corners = [(0, 0), (1, 0), (0, 1), (1, 1)]
        corner_dists = [self._corner_dist(x, y) for x, y in corners]
        if self.size == "closest-corner":
            return min(corner_dists)
        # farthest-corner default
        return max(corner_dists)

    def setY(self, y):
        self.y = y

    def getX(self, x):
        dx = (x / self.aspect - self.cx)
        dy = self.y - self.cy
        dist = math.sqrt(dx*dx + dy*dy)
        r= dist / (self.max_dist if self.max_dist != 0 else 1)
        #print(f"{x},{self.y} = {r}")
        return r
    
def GetGradient(cmd,aspect):
    typ = cmd.get("type", "linear")
    if typ == "radial":
        center = cmd.get("center", [0.5, 0.5])
        cx, cy = center
        size = cmd.get("size", "farthest-corner")
        return RadialGrad(aspect, cx, cy, size)
    elif typ == "linear":
        ang = cmd.get("angle", 0)
        ang = math.radians(ang)
        return LinearGrad(aspect, ang)
    else:
        err(f"unknown grad type: {typ}")
        return None
