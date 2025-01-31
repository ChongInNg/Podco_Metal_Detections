from kivy.app import App
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy_garden.graph import Graph, LinePlot
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
        self.start_time = time.time()
        self.data = []
        self.external_data = {line_name: [] for line_name in self.external_lines.keys()}
        self.count = 0
        self.ch1_p_plot.points = []
        self.threshold_plot.points = []
        for line_plot in self.external_lines.values():
            line_plot.points = []
        self.event = Clock.schedule_interval(self.update_graph, 0.1)

    def get_title(self):
        return self.title

    def stop(self):
        Clock.unschedule(self.update_graph)
        self.event.cancel()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.external_lines = {}
        self._create_graph()

    def _create_graph(self):
        layout = BoxLayout(orientation="vertical")

        # Graph widget
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
            padding=1,
            label_options={"color": [1, 1, 1, 1], "bold": True},
        )

        # Internal line plots
        self.ch1_p_plot = LinePlot(color=[0, 1, 0, 1])  # Green
        self.threshold_plot = LinePlot(color=[1, 0, 0, 1], line_width=2)  # Red

        self.graph.add_plot(self.ch1_p_plot)
        self.graph.add_plot(self.threshold_plot)

        # External lines (4 additional lines)
        self.external_lines = {
            "Line 1": LinePlot(color=[1, 0.5, 0, 1]),  # Orange
            "Line 2": LinePlot(color=[0, 0.5, 1, 1]),  # Blue
            "Line 3": LinePlot(color=[1, 0, 1, 1]),    # Purple
            "Line 4": LinePlot(color=[0.5, 1, 0, 1]),  # Light Green
        }

        for line_name, line_plot in self.external_lines.items():
            self.graph.add_plot(line_plot)

        # Add the graph to the layout
        layout.add_widget(self.graph)

        # Legend layout
        legend_layout = BoxLayout(size_hint_y=0.1)

        legend_items = [
            ("Ch1 Positive", [0, 1, 0, 1]),
            ("Threshold", [1, 0, 0, 1]),
            ("Line 1", [1, 0.5, 0, 1]),
            ("Line 2", [0, 0.5, 1, 1]),
            ("Line 3", [1, 0, 1, 1]),
            ("Line 4", [0.5, 1, 0, 1]),
        ]

        for name, color in legend_items:
            label = Label(text=name, color=color)
            legend_layout.add_widget(label)

        # Add the legend to the layout
        layout.add_widget(legend_layout)
        self.add_widget(layout)

    def update_graph(self, dt):
        current_time = time.time() - self.start_time
        current_second = int(current_time)

        # Update internal data (Ch1 Positive line)
        if self.count % 5 == 0:
            new_value = random.randint(0, 3000)
        else:
            new_value = random.randint(0, 0)

        self.data.append(AmplitudeData(current_time, new_value))
        self.count += 1

        # Keep only data from the last 10 seconds
        self.data = [d for d in self.data if d.time >= current_time - 10]

        # Update internal line plots
        self.ch1_p_plot.points = [(d.time, d.value) for d in self.data]
        self.threshold_plot.points = [
            (current_time - 11, 1500),
            (current_time + 2, 1500),
        ]

        # Update external line plots
        for line_name, line_data in self.external_data.items():
            self.external_lines[line_name].points = [
                (d.time, d.value) for d in line_data if d.time >= current_time - 10
            ]

        # Adjust x-axis range
        self.graph.xmin = max(0, current_second - 10)
        self.graph.xmax = max(current_second + 1, 1)

    def update_external_data(self, line_name: str, amplitude_data: AmplitudeData):
        if line_name in self.external_data:
            self.external_data[line_name].append(amplitude_data)


class TestApp(App):
    def build(self):
        screen = AnalyzerScreen()
        screen.reset_data()

        # Simulate external data updates
        def simulate_external_data(dt):
            current_time = time.time() - screen.start_time
            for i, line_name in enumerate(screen.external_lines.keys()):
                new_data = AmplitudeData(current_time, random.randint(0, 3000))
                screen.update_external_data(line_name, new_data)

        Clock.schedule_interval(simulate_external_data, 0.2)
        return screen


if __name__ == "__main__":
    TestApp().run()
