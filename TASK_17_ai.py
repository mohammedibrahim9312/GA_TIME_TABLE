# =========================================================
# AI TIMETABLE SCHEDULER — GENETIC ALGORITHM
# CS212 Artificial Intelligence — Spring 2026
# =========================================================

import tkinter as tk
from tkinter import ttk, messagebox
import random
import copy

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except ImportError:
    MATPLOTLIB_OK = False

# =========================================================
# CONSTANTS
# =========================================================

ALL_DAYS  = ["Sat", "Sun", "Mon", "Tue", "Wed", "Thu"]
ALL_TIMES = ["8:00-10:00", "10:00-12:00", "12:00-14:00",
             "14:00-16:00", "16:00-18:00"]
ALL_ROOMS = ["A101", "B202", "C303", "Lab1", "Lab2"]

DAY_FULL = {
    "Sat": "Saturday", "Sun": "Sunday",  "Mon": "Monday",
    "Tue": "Tuesday",  "Wed": "Wednesday","Thu": "Thursday"
}

BG       = "#1a1a2e"
PANEL_BG = "#16213e"
HDR_BG   = "#0f3460"
ACCENT   = "#00d4ff"
GREEN    = "#00ff99"
RED      = "#ff4444"
YELLOW   = "#ffcc00"
MUTED    = "#aaaacc"
WHITE    = "#e0e0ff"
EMPTY_FG = "#2d3561"

# =========================================================
# FITNESS FUNCTION
# =========================================================

def calc_fitness(schedule):
    """
    Evaluates a schedule and returns (fitness_score, conflict_count).

    Hard constraints (penalised heavily):
      - Same room  + same day + same time  → -25
      - Same lecturer + same day + same time → -30
      - Same course   + same day + same time → -15

    Soft constraint:
      - All sessions of a course on the same day → -20
    """
    score     = 1000
    conflicts = 0

    for i in range(len(schedule)):
        for j in range(i + 1, len(schedule)):
            a, b = schedule[i], schedule[j]

            if a["day"] == b["day"] and a["time"] == b["time"]:
                conflict = False

                if a["room"]     == b["room"]:     score -= 25; conflict = True
                if a["lecturer"] == b["lecturer"]: score -= 30; conflict = True
                if a["course"]   == b["course"]:   score -= 15; conflict = True

                if conflict:
                    conflicts += 1

    # Soft constraint — avoid all sessions on the same day
    course_days = {}
    for e in schedule:
        course_days.setdefault(e["course"], []).append(e["day"])
    for days in course_days.values():
        if len(set(days)) == 1 and len(days) > 1:
            score -= 20

    return max(score, 0), conflicts

# =========================================================
# GA OPERATORS
# =========================================================

def generate_individual(course_data):
    """Create a random schedule — GA has full control over day/time/room."""
    schedule = []
    for course, hours, lecturer in course_data:
        for _ in range(hours):
            schedule.append({
                "course":   course,
                "lecturer": lecturer,
                "day":      random.choice(ALL_DAYS),
                "time":     random.choice(ALL_TIMES),
                "room":     random.choice(ALL_ROOMS),
            })
    return schedule


def crossover(p1, p2):
    """Single-point crossover."""
    cut = random.randint(1, len(p1) - 1)
    return copy.deepcopy(p1[:cut]) + copy.deepcopy(p2[cut:])


































def mutate(schedule, mutation_rate=0.25):
    """Randomly alter day, time, or room for each gene."""
    child = copy.deepcopy(schedule)
    for gene in child:
        if random.random() < mutation_rate:
            gene["day"]  = random.choice(ALL_DAYS)
        if random.random() < mutation_rate:
            gene["time"] = random.choice(ALL_TIMES)
        if random.random() < mutation_rate:
            gene["room"] = random.choice(ALL_ROOMS)
    return child


def tournament(population, k=5):
    """Tournament selection — pick best from k random individuals."""
    return max(
        random.sample(population, min(k, len(population))),
        key=lambda x: x["fitness"]
    )

# =========================================================
# RUN GA
# =========================================================

def run_ga(course_data, pop_size=60, generations=200, mutation_rate=0.25):
    """
    Full Genetic Algorithm loop.
    Returns best individual and fitness_history list.
    """
    # ── Initialise population ──────────────────────────────
    population = []
    for _ in range(pop_size):
        s = generate_individual(course_data)
        f, c = calc_fitness(s)
        population.append({"schedule": s, "fitness": f, "conflicts": c})

    best = copy.deepcopy(max(population, key=lambda x: x["fitness"]))
    fitness_history = []

    # ── Evolution loop ─────────────────────────────────────
    for generation in range(generations):
        population.sort(key=lambda x: x["fitness"], reverse=True)
        fitness_history.append(population[0]["fitness"])

        # Elitism — carry top 2 unchanged
        new_population = [
            copy.deepcopy(population[0]),
            copy.deepcopy(population[1]),
        ]

        while len(new_population) < pop_size:
            parent1 = tournament(population)
            parent2 = tournament(population)

            child_s = crossover(parent1["schedule"], parent2["schedule"])
            child_s = mutate(child_s, mutation_rate)

            f, c = calc_fitness(child_s)
            new_population.append({"schedule": child_s, "fitness": f, "conflicts": c})

        population = new_population

        gen_best = max(population, key=lambda x: x["fitness"])
        if gen_best["fitness"] > best["fitness"]:
            best = copy.deepcopy(gen_best)

        # Early stop if perfect solution found
        if best["conflicts"] == 0:
            fitness_history += [best["fitness"]] * (generations - generation - 1)
            break

    # Final re-verify
    best["fitness"], best["conflicts"] = calc_fitness(best["schedule"])
    best["history"] = fitness_history
    return best

# =========================================================
# GUI
# =========================================================

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Timetable Scheduler — Genetic Algorithm")
        self.root.geometry("1280x720")
        self.root.configure(bg=BG)
        self._build_header()
        self._build_body()

    # ── Header ────────────────────────────────────────────
    def _build_header(self):
        f = tk.Frame(self.root, bg=HDR_BG)
        f.pack(fill="x")
        tk.Label(f, text="🎓  AI Timetable Scheduler — Genetic Algorithm",
                 bg=HDR_BG, fg=ACCENT,
                 font=("Courier New", 14, "bold")).pack(side="left", padx=20, pady=10)
        tk.Label(f, text="CS212 Artificial Intelligence",
                 bg=HDR_BG, fg=MUTED,
                 font=("Courier New", 9)).pack(side="right", padx=20)

    # ── Body ──────────────────────────────────────────────
    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=12, pady=10)
        self._build_left(body)
        self._build_right(body)

    # ── Left panel ────────────────────────────────────────
    def _build_left(self, parent):
        outer = tk.Frame(parent, bg=PANEL_BG, width=340)
        outer.pack(side="left", fill="y", padx=(0, 10))
        outer.pack_propagate(False)

        ybar = tk.Scrollbar(outer, orient="vertical", bg=HDR_BG)
        ybar.pack(side="right", fill="y")
        lc = tk.Canvas(outer, bg=PANEL_BG, yscrollcommand=ybar.set, highlightthickness=0)
        lc.pack(fill="both", expand=True)
        ybar.config(command=lc.yview)

        self.left = tk.Frame(lc, bg=PANEL_BG)
        lc.create_window((0, 0), window=self.left, anchor="nw")
        self.left.bind("<Configure>", lambda e: lc.configure(scrollregion=lc.bbox("all")))

        # Title
        tk.Label(self.left, text="Course Data", bg=PANEL_BG, fg=ACCENT,
                 font=("Courier New", 11, "bold")).pack(anchor="w", padx=12, pady=(14, 4))

        # Column headers
        hdr = tk.Frame(self.left, bg=PANEL_BG)
        hdr.pack(fill="x", padx=8, pady=(0, 2))
        for text, w in [("Course", 10), ("Hrs", 5), ("Lecturer", 13)]:
            tk.Label(hdr, text=text, bg=HDR_BG, fg=ACCENT,
                     font=("Courier New", 8, "bold"), width=w,
                     relief="flat").pack(side="left", padx=1)

        # Rows
        self.rows_frame = tk.Frame(self.left, bg=PANEL_BG)
        self.rows_frame.pack(fill="x", padx=8, pady=2)
        self.rows = []
        for d in [("Math", "2", "Dr.Ahmed"),
                  ("Physics", "3", "Dr.Sara"),
                  ("AI", "2", "Dr.Mona"),
                  ("English", "1", "Dr.Ali")]:
            self._add_row(d)

        # Add / Remove
        btn_row = tk.Frame(self.left, bg=PANEL_BG)
        btn_row.pack(fill="x", padx=8, pady=6)
        tk.Button(btn_row, text="+ Add", bg=HDR_BG, fg=ACCENT,
                  font=("Courier New", 9), relief="flat", cursor="hand2",
                  command=lambda: self._add_row()).pack(side="left", padx=(0, 4))
        tk.Button(btn_row, text="− Remove", bg=HDR_BG, fg=RED,
                  font=("Courier New", 9), relief="flat", cursor="hand2",
                  command=self._remove_row).pack(side="left")

        tk.Frame(self.left, bg=HDR_BG, height=1).pack(fill="x", padx=8, pady=8)

        # Stats
        self.fitness_var  = tk.StringVar(value="Fitness:   —")
        self.conflict_var = tk.StringVar(value="Conflicts: —")
        self.status_var   = tk.StringVar(value="● Ready")

        self.fit_label = tk.Label(self.left, textvariable=self.fitness_var,
                                  bg=PANEL_BG, fg=GREEN,
                                  font=("Courier New", 10, "bold"), anchor="w")
        self.fit_label.pack(fill="x", padx=14, pady=1)

        self.con_label = tk.Label(self.left, textvariable=self.conflict_var,
                                  bg=PANEL_BG, fg=GREEN,
                                  font=("Courier New", 10, "bold"), anchor="w")
        self.con_label.pack(fill="x", padx=14, pady=1)

        tk.Label(self.left, textvariable=self.status_var, bg=PANEL_BG, fg=YELLOW,
                 font=("Courier New", 9), anchor="w").pack(fill="x", padx=14, pady=4)

        # Generate button
        tk.Button(self.left, text="▶   Generate Timetable",
                  bg=ACCENT, fg=BG,
                  font=("Courier New", 12, "bold"),
                  activebackground=GREEN, activeforeground=BG,
                  relief="flat", cursor="hand2", pady=10,
                  command=self._run).pack(fill="x", padx=12, pady=(4, 12))

    def _add_row(self, defaults=("", "1", "")):
        f = tk.Frame(self.rows_frame, bg=PANEL_BG)
        f.pack(fill="x", pady=2)
        entries = []
        for val, w in zip(defaults, [10, 5, 13]):
            e = tk.Entry(f, width=w, bg=BG, fg=WHITE,
                         insertbackground=ACCENT, font=("Courier New", 8),
                         relief="flat", bd=2)
            e.insert(0, val)
            e.pack(side="left", padx=1)
            entries.append(e)
        self.rows.append((f, entries))

    def _remove_row(self):
        if len(self.rows) > 1:
            f, _ = self.rows.pop()
            f.destroy()

    # ── Right panel — notebook with 2 tabs ────────────────
    def _build_right(self, parent):
        right = tk.Frame(parent, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=BG, borderwidth=0)
        style.configure("TNotebook.Tab", background=HDR_BG, foreground=MUTED,
                         font=("Courier New", 10, "bold"), padding=[12, 5])
        style.map("TNotebook.Tab",
                  background=[("selected", PANEL_BG)],
                  foreground=[("selected", ACCENT)])

        self.nb = ttk.Notebook(right)
        self.nb.pack(fill="both", expand=True)

        # Tab 1 — Timetable Grid
        self.tab_grid = tk.Frame(self.nb, bg=PANEL_BG)
        self.nb.add(self.tab_grid, text="📅  Timetable")
        self._build_grid_tab(self.tab_grid)

        # Tab 2 — Evolution Plot
        self.tab_plot = tk.Frame(self.nb, bg=BG)
        self.nb.add(self.tab_plot, text="📈  Evolution Plot")
        self._build_plot_tab(self.tab_plot)

    # ── Timetable Grid tab ────────────────────────────────
    def _build_grid_tab(self, parent):
        xbar = tk.Scrollbar(parent, orient="horizontal", bg=HDR_BG)
        ybar = tk.Scrollbar(parent, orient="vertical",   bg=HDR_BG)
        xbar.pack(side="bottom", fill="x")
        ybar.pack(side="right",  fill="y")

        self.tcanvas = tk.Canvas(parent, bg=PANEL_BG,
                                 xscrollcommand=xbar.set,
                                 yscrollcommand=ybar.set,
                                 highlightthickness=0)
        self.tcanvas.pack(fill="both", expand=True)
        xbar.config(command=self.tcanvas.xview)
        ybar.config(command=self.tcanvas.yview)

        self.grid_frame = tk.Frame(self.tcanvas, bg=PANEL_BG)
        self.tcanvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.grid_frame.bind("<Configure>",
            lambda e: self.tcanvas.configure(scrollregion=self.tcanvas.bbox("all")))

        self._draw_grid()

    def _draw_grid(self, schedule=None):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        lookup = {}
        if schedule:
            for e in schedule:
                lookup.setdefault((e["day"], e["time"]), []).append(e)

        # Detect actual conflicts per slot
        conflict_slots = set()
        if schedule:
            for (day, time), entries in lookup.items():
                if len(entries) > 1:
                    # Check if any real conflict
                    for i in range(len(entries)):
                        for j in range(i+1, len(entries)):
                            a, b = entries[i], entries[j]
                            if (a["room"] == b["room"] or
                                a["lecturer"] == b["lecturer"] or
                                a["course"] == b["course"]):
                                conflict_slots.add((day, time))

        CELL_W, TIME_W = 20, 13

        # Corner
        tk.Label(self.grid_frame, text="Time  ╲  Day",
                 bg=HDR_BG, fg=ACCENT, font=("Courier New", 9, "bold"),
                 width=TIME_W, relief="ridge", bd=1
                 ).grid(row=0, column=0, padx=1, pady=1, sticky="nsew", ipady=10)

        # Day headers
        for c, day in enumerate(ALL_DAYS):
            tk.Label(self.grid_frame, text=DAY_FULL[day],
                     bg=HDR_BG, fg=ACCENT, font=("Courier New", 9, "bold"),
                     width=CELL_W, relief="ridge", bd=1
                     ).grid(row=0, column=c+1, padx=1, pady=1, sticky="nsew", ipady=10)

        # Time rows
        for r, time_slot in enumerate(ALL_TIMES):
            tk.Label(self.grid_frame, text=time_slot,
                     bg=HDR_BG, fg=MUTED, font=("Courier New", 8, "bold"),
                     width=TIME_W, relief="ridge", bd=1
                     ).grid(row=r+1, column=0, padx=1, pady=1, sticky="nsew", ipady=14)

            for c, day in enumerate(ALL_DAYS):
                entries = lookup.get((day, time_slot), [])
                is_conflict = (day, time_slot) in conflict_slots

                if entries:
                    lines = []
                    for e in entries:
                        lines += [e["course"], e["lecturer"], f"🚪 {e['room']}"]
                        if is_conflict:
                            lines.append("⚠ CONFLICT")
                    text = "\n".join(lines)
                    bg_c = "#3a1010" if is_conflict else "#0d2b1a"
                    fg_c = RED       if is_conflict else GREEN
                else:
                    text = "—"
                    bg_c = PANEL_BG
                    fg_c = EMPTY_FG

                tk.Label(self.grid_frame, text=text,
                         bg=bg_c, fg=fg_c,
                         font=("Courier New", 7),
                         width=CELL_W, wraplength=140,
                         justify="center", relief="ridge", bd=1
                         ).grid(row=r+1, column=c+1, padx=1, pady=1,
                                sticky="nsew", ipady=7)

    # ── Evolution Plot tab ────────────────────────────────
    def _build_plot_tab(self, parent):
        self.plot_frame = tk.Frame(parent, bg=BG)
        self.plot_frame.pack(fill="both", expand=True)

        if not MATPLOTLIB_OK:
            tk.Label(self.plot_frame,
                     text="Install matplotlib:\npip install matplotlib",
                     bg=BG, fg=RED,
                     font=("Courier New", 11)).pack(expand=True)

    def _draw_plot(self, history):
        if not MATPLOTLIB_OK:
            return

        for w in self.plot_frame.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor(BG)
        ax.set_facecolor(PANEL_BG)

        gens = list(range(1, len(history) + 1))
        ax.plot(gens, history, color=ACCENT, linewidth=2, label="Best Fitness")
        ax.fill_between(gens, history, alpha=0.15, color=ACCENT)

        # Mark the generation where conflicts = 0 (fitness stops changing)
        for i in range(1, len(history)):
            if history[i] == history[-1] and history[i] > history[i-1]:
                ax.axvline(x=i+1, color=GREEN, linestyle="--",
                           linewidth=1, alpha=0.6, label=f"Converged at gen {i+1}")
                break

        ax.set_xlabel("Generation", color=MUTED, fontsize=10)
        ax.set_ylabel("Fitness Score", color=MUTED, fontsize=10)
        ax.set_title("GA Evolution — Fitness over Generations",
                     color=ACCENT, fontsize=12, pad=12)
        ax.tick_params(colors=MUTED)
        for spine in ax.spines.values():
            spine.set_color("#333355")
        ax.legend(facecolor=PANEL_BG, edgecolor="#333355", labelcolor=WHITE,
                  fontsize=9)
        ax.grid(True, color="#2a2a4a", linestyle="--", alpha=0.5)
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    # ── Run ───────────────────────────────────────────────
    def _run(self):
        try:
            course_data = []
            for _, entries in self.rows:
                course   = entries[0].get().strip()
                hrs_str  = entries[1].get().strip()
                lecturer = entries[2].get().strip()

                if not course or not lecturer or not hrs_str:
                    continue

                hours = int(hrs_str)
                if hours <= 0:
                    raise ValueError("Hours must be positive.")

                course_data.append((course, hours, lecturer))

            if not course_data:
                messagebox.showerror("Error", "Please enter at least one course.")
                return

            self.status_var.set("⏳ Running GA...")
            self.fit_label.config(fg=YELLOW)
            self.con_label.config(fg=YELLOW)
            self.root.update()

            result = run_ga(course_data)

            f_val = result["fitness"]
            c_val = result["conflicts"]

            self.fitness_var.set(f"Fitness:   {f_val}")
            self.conflict_var.set(f"Conflicts: {c_val}")
            self.fit_label.config(fg=GREEN if c_val == 0 else RED)
            self.con_label.config(fg=GREEN if c_val == 0 else RED)
            self.status_var.set("✅ No conflicts!" if c_val == 0
                                else f"⚠  {c_val} conflict(s) — try again")

            self._draw_grid(result["schedule"])
            self._draw_plot(result["history"])

            # Switch to timetable tab after generation
            self.nb.select(0)

        except ValueError as ve:
            messagebox.showerror("Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", str(e))


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
