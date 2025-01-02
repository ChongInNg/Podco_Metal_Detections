from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.garden.graph import Graph, LinePlot
from kivy.clock import Clock
import random
import time


class AmplitudeData:
    def __init__(self, time, value: int):
        self.time = time
        self.value = value


class AnalyzerScreen(Screen):
    title = "Analyzer"

    def reset_data(self):
        pass

    def get_title(self):
        return self.title

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._create_graph()
        self.start_time = time.time() 
        self.data = []  
        self.count = 0 
        Clock.schedule_interval(self.update_graph, 0.1)

    def _create_graph(self):
        self.graph = Graph(
            xlabel="Time (s)",
            ylabel="Amplitude",
            x_ticks_minor=5, 
            x_ticks_major=1, 
            y_ticks_minor=5,
            y_ticks_major=500,
            y_grid_label=True,
            x_grid_label=True,
            xmin=0,
            xmax=10,  
            ymin=0,
            ymax=3000, 
            padding=5,
        )

        self.plot = LinePlot(color=[0, 1, 0, 1])
        self.plot.points = []

        self.threshold_plot = LinePlot(color=[1, 0, 0, 1])
        self.threshold_plot.points = []

        self.graph.add_plot(self.plot)
        self.graph.add_plot(self.threshold_plot)

        self.add_widget(self.graph)

    def update_graph(self, dt):
        current_time = time.time() - self.start_time
        current_second = int(current_time) 

        if self.count % 5 == 0:
            new_value = random.randint(0, 3000)
        else:
            new_value = random.randint(0, 0)
        
        self.data.append(AmplitudeData(current_time, new_value))
        self.count += 1

        self.data = [d for d in self.data if d.time >= current_time - 10]
        self.plot.points = [(d.time, d.value) for d in self.data]

        self.threshold_plot.points = [
            (current_time - 11, 1500),
            (current_time + 2, 1500),
        ]

        self.graph.xmin = max(0, current_second - 10)
        self.graph.xmax = max(current_second + 1, 1)



