import turtle
import math
import heapq
import time

"""
cyo.py

Creative energy-routing problem visualized with turtle.

Problem:
    - A power plant must deliver 100 energy units to a city.
    - The network has multiple intermediate nodes (solar farm, battery, wind farm).
    - Each transmission segment has a distance-based loss modified by an efficiency factor.
    - Find the route that minimizes total energy loss (Dijkstra on loss) and depict it.
    - Animate an "energy packet" moving along the chosen path and display total delivered energy.

Run: python cyo.py
"""


# --- Problem setup: nodes (x,y) and edges with efficiencies (0..1) ---
NODES = {
        "Plant": ( -250,  0),
        "Solar": ( -50,  120),
        "Battery": ( 100,  30),
        "Wind": ( -10, -110),
        "Substation": ( 220, -40),
        "City": ( 300,  80),
}

# adjacency: neighbor -> efficiency (fraction of energy transmitted)
# Loss for an edge = distance * (1 - efficiency)  (interpreted as units lost per unit distance)
EDGES = {
        "Plant":     [("Solar", 0.95), ("Wind", 0.9), ("Battery", 0.92)],
        "Solar":     [("Plant", 0.95), ("Battery", 0.97), ("Substation", 0.9)],
        "Wind":      [("Plant", 0.9), ("Battery", 0.88), ("Substation", 0.93)],
        "Battery":   [("Plant", 0.92), ("Solar", 0.97), ("Wind", 0.88), ("Substation", 0.96)],
        "Substation":[("Solar", 0.9), ("Wind", 0.93), ("Battery", 0.96), ("City", 0.98)],
        "City":      [("Substation", 0.98)],
}

START = "Plant"
TARGET = "City"
INITIAL_ENERGY = 100.0

# --- Utilities ---
def dist(a, b):
        (x1,y1), (x2,y2) = a, b
        return math.hypot(x2-x1, y2-y1)

def edge_loss(u, v, eff):
        d = dist(NODES[u], NODES[v])
        # interpret weight as expected absolute energy lost if 1 unit passes: loss_per_unit = d*(1-eff)
        # For shortest-path selection we want minimal total loss for INITIAL_ENERGY. Multiplying by INITIAL_ENERGY is monotonic, so skip.
        return d * (1.0 - eff)

# Dijkstra to minimize total loss from START to TARGET
def dijkstra_loss(start, target):
        pq = [(0.0, start, [])]  # (loss, node, path)
        seen = {}
        while pq:
                loss, node, path = heapq.heappop(pq)
                if node in seen and loss >= seen[node]:
                        continue
                seen[node] = loss
                path = path + [node]
                if node == target:
                        return loss, path
                for nbr, eff in EDGES.get(node, []):
                        w = edge_loss(node, nbr, eff)
                        heapq.heappush(pq, (loss + w, nbr, path))
        return float('inf'), []

# --- Drawing functions using turtle ---
screen = turtle.Screen()
screen.setup(900, 600)
screen.title("Energy routing — minimal-loss path visualization")
screen.bgcolor("white")

drawer = turtle.Turtle()
drawer.hideturtle()
drawer.speed(0)
drawer.pensize(2)

def draw_node(name, pos, color="black", size=16):
        x,y = pos
        drawer.penup()
        drawer.goto(x, y - size//2)
        drawer.pendown()
        drawer.color(color)
        drawer.begin_fill()
        drawer.circle(size//2)
        drawer.end_fill()
        drawer.penup()
        drawer.goto(x + size//2 + 6, y - size//2)
        drawer.color("black")
        drawer.write(name, font=("Arial", 12, "normal"))

def draw_edge(u, v, eff):
        x1,y1 = NODES[u]
        x2,y2 = NODES[v]
        # color by efficiency
        if eff >= 0.96:
                col = "#2e8b57"  # green
        elif eff >= 0.92:
                col = "#ff8c00"  # orange
        else:
                col = "#b22222"  # red
        drawer.color(col)
        drawer.penup()
        drawer.goto(x1, y1)
        drawer.pendown()
        drawer.goto(x2, y2)
        # label efficiency
        mx, my = (x1+x2)/2, (y1+y2)/2
        drawer.penup()
        drawer.goto(mx+6, my+6)
        drawer.color("gray")
        drawer.write(f"{eff:.2f}", font=("Arial", 9, "normal"))

def draw_network():
        drawer.clear()
        # draw edges
        drawn = set()
        for u, nbrs in EDGES.items():
                for v, eff in nbrs:
                        key = tuple(sorted((u, v)))
                        if key in drawn:
                                continue
                        draw_edge(u, v, eff)
                        drawn.add(key)
        # draw nodes
        for name, pos in NODES.items():
                if name == START:
                        draw_node(name, pos, color="#1e90ff")
                elif name == TARGET:
                        draw_node(name, pos, color="#ff4500")
                else:
                        draw_node(name, pos, color="#ffd700")
        screen.update()

# Animation of energy packet along polyline path
energy_turtle = turtle.Turtle()
energy_turtle.shape("circle")
energy_turtle.shapesize(0.8)
energy_turtle.color("#00bfff")
energy_turtle.penup()
energy_turtle.speed(0)

def animate_path(path, initial_energy):
        # compute losses per segment and animate movement
        pos_seq = [NODES[n] for n in path]
        energy = initial_energy
        info = turtle.Turtle()
        info.hideturtle()
        info.penup()
        info.goto(-420, 240)
        info.color("black")
        info.write(f"Routing {initial_energy:.1f} units from {START} to {TARGET}", font=("Arial", 12, "bold"))
        info.goto(-420, 220)
        for i in range(len(path)-1):
                u = path[i]; v = path[i+1]
                eff = next(e for nb, e in EDGES[u] if nb == v)
                d = dist(NODES[u], NODES[v])
                lost = d * (1.0 - eff)
                delivered = energy - lost
                # move energy_turtle along segment
                x1,y1 = NODES[u]; x2,y2 = NODES[v]
                steps = max(int(d/5), 10)
                for s in range(steps+1):
                        t = s/steps
                        x = x1 + (x2-x1)*t
                        y = y1 + (y2-y1)*t
                        energy_turtle.goto(x, y)
                        # draw small glow
                        if s % 4 == 0:
                                energy_turtle.stamp()
                        screen.update()
                        time.sleep(0.01)
                energy = max(0.0, delivered)
                info.clear()
                info.write(f"Segment {u} -> {v}: eff={eff:.2f} loss≈{lost:.2f}  energy remaining≈{energy:.2f}", font=("Arial", 12, "normal"))
                time.sleep(0.4)
        # final summary
        info.clear()
        info.goto(-420, 220)
        info.write(f"Delivered to {TARGET}: {energy:.2f} units (started {initial_energy})", font=("Arial", 14, "bold"))

def main():
        draw_network()
        total_loss, path = dijkstra_loss(START, TARGET)
        delivered = INITIAL_ENERGY - total_loss  # approximate delivered energy
        # highlight chosen path
        hl = turtle.Turtle()
        hl.hideturtle()
        hl.pensize(4)
        hl.color("#00bfff")
        hl.penup()
        for i in range(len(path)-1):
                x1,y1 = NODES[path[i]]
                x2,y2 = NODES[path[i+1]]
                hl.goto(x1,y1)
                hl.pendown()
                hl.goto(x2,y2)
                hl.penup()
        # annotate path and loss
        ann = turtle.Turtle()
        ann.hideturtle()
        ann.penup()
        ann.goto(-420, 260)
        ann.write(f"Chosen path (min loss): {' -> '.join(path)}", font=("Arial", 12, "bold"))
        ann.goto(-420, 240)
        ann.write(f"Estimated total loss ≈ {total_loss:.2f} units  |  Estimated delivered ≈ {delivered:.2f}", font=("Arial", 12, "normal"))
        screen.update()
        time.sleep(1.0)
        animate_path(path, INITIAL_ENERGY)
        # keep window open
        turtle.done()

if __name__ == "__main__":
        main()