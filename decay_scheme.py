from matplotlib import pyplot, figure
from typing import List, Union, Tuple
class Level:
    def __init__(self, energy: float, label: str = "", Ibeta_label: str = "", logft_label: str = "") -> None:
        self.parent_levels: set['Level']  = set()
        self.child_levels: set['Level'] = set()
        self.energy: float = energy
        self.label = label
        self.Ibeta_label = Ibeta_label
        self.logft_label = logft_label

    def __lt__(self, other: 'Level') -> bool:
        if not isinstance(other, Level):
            raise TypeError("Other must be of type Level")
        return self.energy < other.energy

    def add_child(self, other: 'Level') -> None:
        if not isinstance(other, Level):
            raise TypeError("Other must be of type Level")
        self.child_levels.add(other)

    def remove_child(self, other : 'Level') -> None:
        if other in self.child_levels:
            self.child_levels.remove(other)

    def add_parent(self, other: 'Level') -> None:
        if not isinstance(other, Level):
            raise TypeError("Other must be of type Level")
        self.parent_levels.add(other)

    def remove_parent(self, other : 'Level') -> None:
        if other in self.parent_levels:
            self.parent_levels.remove(other)

    def is_root(self) -> bool:
        return len(self.child_levels) == 0

    def is_top_level(self) -> bool:
        return len(self.parent_levels) == 0

    def delta(self, other: 'Level') -> float:
        return self.energy - other.energy

    def draw(self, x1: float, x2: float, ax: pyplot.Axes, logft_label_x: float, ibeta_label_x: float) -> None:
        ax.hlines(self.energy, xmin=x1, xmax=x2)
        ax.annotate(self.label, (x1 *1.01, self.energy), ha="left", va = "bottom")
        ax.annotate(f"{self.energy:.1f}", (x2 * 0.99, self.energy), ha="right", va="bottom")
        if self.Ibeta_label != "":
            ax.annotate(self.Ibeta_label, (ibeta_label_x, self.energy), ha="left", va = "bottom")
        if self.logft_label != "":
            ax.annotate(self.logft_label, (logft_label_x, self.energy), ha="left", va = "bottom")
    
class LevelTransition:
    def __init__(self, parent: float, child: float):
        self.parent: float = parent
        self.child: float = child

    def draw(self, x1: float, x2: float, ax: pyplot.Axes, head_length: float = 5, head_width: float = 1) -> None:
        ax.arrow(x1, self.parent, x2, self.child - self.parent, head_width = head_width, head_length = head_length, length_includes_head=True)




    

class DecayScheme:
    def __init__(self):
        self.levels: dict[float, Level] = {}
        self.fig = 0
        self.ax = 0

    def add_level(self, level: Level) -> None:
        if not isinstance(level, Level):
            raise TypeError("Other must be of type Level")
        self.levels[level.energy] = level
    
    def remove_level(self, level: Level) -> None:
        if level.energy in self.levels:
            self.levels.pop(level.energy)
    
    def get_levels_sorted(self) -> List[Level]:
        ret: List[Level] = [i for i in self.levels.values()]
        ret.sort()        
        return ret
    
    def draw(self, xstart: float = 2, x_buffer: Tuple[float, float] = (2, 2), y_buffer: Tuple[float, float] = (20, 100), xstep: float = 2) -> None:
        lvls = self.get_levels_sorted()
        transitions: List[LevelTransition] = []
        for i in lvls:
            children = [j for j in i.child_levels]
            for j in children:
                transitions.append(LevelTransition(i.energy, j.energy))
        xct = xstart + 1
        maxlvl = 0
        fig, ax = pyplot.subplots()
        for i in transitions:
            xct += xstep
        plotwidth = xct + 2 * x_buffer[1] + xstart
        for i in lvls:
            if i.energy > maxlvl:
                maxlvl = i.energy
        xstartoffset = 0
        for i in lvls:
            i.draw(xstart, xct, ax, xstart - plotwidth * 0.2, xstart - plotwidth * 0.1)

        trans_head_len = (maxlvl + 2 * y_buffer[1]) * 0.01
        trans_head_width = (xct + 2 * x_buffer[1] - xstart) * 0.01
        for i in range(len(transitions)):
            transx = xstart + xstep + xstep * i
            transitions[i].draw(transx, 0, ax, head_length=trans_head_len, head_width=trans_head_width)
        fig.set_figwidth(10)
        fig.set_figheight(10)
        ax.set_xlim(-x_buffer[0], xct + x_buffer[1])
        ax.set_ylim(-y_buffer[0], maxlvl + y_buffer[1])
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.tick_params(bottom=False, left=False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        self.fig = fig
        self.ax = ax

    def savefig(self, path: str, *args, **kwargs):
        if isinstance(self.fig, figure.Figure):
            self.fig.savefig(path, *args, **kwargs)
    
    def add_levels(self, levelData: List[Tuple[float, str, List[float], str, str]]) -> None:
        levelData.sort()
        levels = {}
        for i in levelData:
            levels[i[0]] = Level(i[0], i[1], i[3], i[4])
            for j in i[2]:
                levels[i[0]].add_child(levels[j])
        for i in levels.values():
            self.add_level(i)
        


if __name__ == "__main__":
    
    levelData = [
        (0,    "$3/2^-$", [], "20", "5.2"),
        (484,  "($3/2^-$)", [0], "<1.2", ">6.4"),
        (545,  "", [0], "9", "5.5"),
        (705,  "($1/2^+$,$3/2^+$,$5/2^+$)", [0, 484], "7", "5.6"),
        (1242, "($1/2^+$,$3/2^+$,$5/2^+$)", [0, 484], "2.9", "6.0")
    ]
    levelData.sort()

    levels = {}
    for ch in levelData:
        levels[ch[0]] = Level(ch[0], ch[1], ch[3], ch[4])
        for j in ch[2]:
            levels[ch[0]].add_child(levels[j])
    scheme = DecayScheme()
    for ch in levels.values():
        scheme.add_level(ch)
    
    scheme.draw()
    scheme.savefig("test.png")


    