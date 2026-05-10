import pygame
import csv
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT


class StatsVisualizer:
    def __init__(self):
        self.csv_file = 'game_stats.csv'
        self.data = self.load_data()
        self.current_tab = 'steps'
        self.tabs = ['steps', 'time', 'enemies', 'score', 'results']
        self.tab_names = {
            'steps': 'Steps',
            'time': 'Time',
            'enemies': 'Enemies',
            'score': 'Score',
            'results': 'Results'
        }
        # Chart type per tab: 'bar' or 'line' (results always pie)
        self.chart_types = {
            'steps': 'bar',
            'time': 'line',
            'enemies': 'bar',
            'score': 'bar',
        }
        self.colors = {
            'win': (76, 175, 80),
            'loss': (244, 67, 54),
            'bar': (66, 165, 245),
            'bar_alt': (156, 39, 176),
            'line': (255, 193, 7),
            'text': (255, 255, 255),
            'text_secondary': (220, 220, 220),
            'bg': (20, 25, 40),
            'panel_bg': (35, 45, 65),
            'accent1': (102, 255, 178),
            'accent2': (255, 87, 34),
            'grid': (60, 70, 90),
            'button_normal': (50, 60, 80),
            'button_active': (80, 100, 150),
        }
        self.menu_buttons = self._create_menu_buttons()
        self.chart_buttons = self._create_chart_buttons()

    def set_active_tab(self, tab_name):
        """Switch the active tab in the stats visualization"""
        valid_tabs = ['steps', 'time', 'enemies', 'score', 'results']
        if tab_name in valid_tabs:
            self.current_tab = tab_name
    
    def draw_all_stats(self, surface):
        """Draw stats based on active tab"""
        # ... existing drawing code ...
        # Modify your draw logic to only show the selected tab
        if self.active_tab == 'steps':
            self.draw_steps_chart(surface)
        elif self.active_tab == 'time':
            self.draw_time_chart(surface)
        elif self.active_tab == 'enemies':
            self.draw_enemies_chart(surface)
        elif self.active_tab == 'score':
            self.draw_score_chart(surface)
        elif self.active_tab == 'results':
            self.draw_results(surface)

    def _create_menu_buttons(self):
        """Create button rectangles for tab menu."""
        buttons = {}
        button_width = 120
        button_height = 40
        start_x = 30
        spacing = 10
        for i, tab in enumerate(self.tabs):
            x = start_x + i * (button_width + spacing)
            y = 15
            buttons[tab] = pygame.Rect(x, y, button_width, button_height)
        return buttons

    def _create_chart_buttons(self):
        """Create Bar / Line toggle buttons shown inside the graph area."""
        return {
            'bar': pygame.Rect(SCREEN_WIDTH - 170, 65, 70, 28),
            'line': pygame.Rect(SCREEN_WIDTH - 90, 65, 70, 28),
        }

    def load_data(self):
        """Load game statistics from CSV file."""
        data = {
            'game_ids': [],
            'steps': [],
            'times': [],
            'enemies': [],
            'scores': [],
            'results': [],
        }
        try:
            with open(self.csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['Game_ID']:
                        data['game_ids'].append(int(row['Game_ID']))
                        data['steps'].append(int(row['Steps']))
                        data['times'].append(int(row['Time']))
                        data['enemies'].append(int(row['Enemies_Encountered']))
                        data['scores'].append(int(row['Score']))
                        data['results'].append(row['Result'])
        except Exception as e:
            print(f"Error loading data: {e}")
        return data

    def refresh_data(self):
        """Reload the game statistics data from CSV file."""
        self.data = self.load_data()

    def handle_click(self, mouse_x, mouse_y):
        """Handle menu button clicks (tab + chart type)."""
        for tab, rect in self.menu_buttons.items():
            if rect.collidepoint(mouse_x, mouse_y):
                self.current_tab = tab
                return True
        if self.current_tab != 'results':
            for chart_type, rect in self.chart_buttons.items():
                if rect.collidepoint(mouse_x, mouse_y):
                    self.chart_types[self.current_tab] = chart_type
                    return True
        return False

    def draw_menu(self, surface):
        """Draw the tab menu at the top."""
        button_font = pygame.font.SysFont('arial', 14, bold=True)
        for tab, rect in self.menu_buttons.items():
            if tab == self.current_tab:
                pygame.draw.rect(surface, self.colors['button_active'], rect)
                pygame.draw.rect(surface, self.colors['accent1'], rect, 3)
            else:
                pygame.draw.rect(surface, self.colors['button_normal'], rect)
                pygame.draw.rect(surface, self.colors['grid'], rect, 2)
            label = self.tab_names[tab]
            text_surface = button_font.render(label, True, self.colors['text'])
            text_rect = text_surface.get_rect(center=rect.center)
            surface.blit(text_surface, text_rect)

    def draw_chart_type_buttons(self, surface):
        """Draw Bar / Line toggle buttons in the top-right area."""
        if self.current_tab == 'results':
            return
        btn_font = pygame.font.SysFont('arial', 13, bold=True)
        current_type = self.chart_types.get(self.current_tab, 'bar')
        labels = {'bar': 'Bar', 'line': 'Line'}
        for chart_type, rect in self.chart_buttons.items():
            is_active = (chart_type == current_type)
            bg_color = self.colors['button_active'] if is_active else self.colors['button_normal']
            border_color = self.colors['accent1'] if is_active else self.colors['grid']
            pygame.draw.rect(surface, bg_color, rect, border_radius=5)
            pygame.draw.rect(surface, border_color, rect, 2, border_radius=5)
            text = btn_font.render(labels[chart_type], True, self.colors['text'])
            surface.blit(text, text.get_rect(center=rect.center))

    # ------------------------------------------------------------------
    # Y-axis tick helper
    # ------------------------------------------------------------------
    def _nice_ticks(self, max_value, num_ticks=8):
        """Return a list of nice rounded tick values from 0 up to >= max_value."""
        if max_value <= 0:
            return [0]
        raw_step = max_value / num_ticks
        magnitude = 10 ** math.floor(math.log10(raw_step))
        nice_step = math.ceil(raw_step / magnitude) * magnitude
        ticks = []
        v = 0
        while v <= max_value + nice_step:
            ticks.append(int(v))
            v += nice_step
        return ticks

    def _draw_y_axis(self, surface, graph_x, graph_y, graph_width, graph_height,
                     raw_max, grid_font):
        """Draw Y-axis ticks and gridlines; returns the ceiling tick value used for scaling."""
        ticks = self._nice_ticks(raw_max, num_ticks=8)
        top_value = ticks[-1] if ticks else raw_max

        for value in ticks:
            if top_value == 0:
                continue
            ratio = value / top_value
            tick_y = graph_y + graph_height - int(graph_height * ratio)

            # Grid line style
            if value == 0:
                grid_color = (100, 120, 150)
                thickness = 2
            elif len(ticks) > 1 and ticks[1] != 0 and value % (ticks[1] * 2) == 0:
                grid_color = (90, 105, 130)
                thickness = 2
            else:
                grid_color = (65, 78, 100)
                thickness = 1

            pygame.draw.line(surface, grid_color,
                             (graph_x, tick_y), (graph_x + graph_width, tick_y), thickness)

            # Tick mark
            pygame.draw.line(surface, self.colors['accent1'],
                             (graph_x - 6, tick_y), (graph_x, tick_y), 2)

            # Right-aligned label
            label_surf = grid_font.render(str(value), True, self.colors['text_secondary'])
            surface.blit(label_surf, (graph_x - 12 - label_surf.get_width(), tick_y - 7))

        return top_value

    # ------------------------------------------------------------------
    # Detailed histogram
    # ------------------------------------------------------------------
    def draw_detail_histogram(self, surface, title, data_list, max_value=None):
        """Draw a detailed histogram filling the window."""
        if not data_list:
            return

        raw_max = max(data_list) if data_list else 1
        min_value = min(data_list)
        avg_value = sum(data_list) / len(data_list)

        graph_x, graph_y = 90, 105
        graph_width, graph_height = SCREEN_WIDTH - 180, SCREEN_HEIGHT - 210

        # Background panel
        panel_surface = pygame.Surface((graph_width + 40, graph_height + 80), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (30, 40, 60, 200), (0, 0, graph_width + 40, graph_height + 80))
        pygame.draw.rect(panel_surface, (100, 200, 255, 100), (0, 0, graph_width + 40, graph_height + 80), 2)
        surface.blit(panel_surface, (graph_x - 20, graph_y - 20))

        title_font = pygame.font.SysFont('arial', 32, bold=True)
        surface.blit(title_font.render(title, True, self.colors['accent1']), (graph_x, graph_y - 52))

        stats_font = pygame.font.SysFont('arial', 14)
        surface.blit(stats_font.render(
            f"Avg: {avg_value:.1f}  |  Min: {min_value}  |  Max: {raw_max}",
            True, self.colors['text_secondary']), (graph_x, graph_y - 22))

        # Y-axis ticks (returns ceiling used for scaling)
        grid_font = pygame.font.SysFont('arial', 13)
        top_value = self._draw_y_axis(surface, graph_x, graph_y, graph_width, graph_height,
                                      raw_max, grid_font)
        max_value = top_value

        # Average line
        if max_value > 0:
            avg_y = graph_y + graph_height - int(graph_height * avg_value / max_value)
            pygame.draw.line(surface, (100, 255, 100), (graph_x, avg_y), (graph_x + graph_width, avg_y), 2)
            avg_lbl = stats_font.render("Avg", True, (100, 255, 100))
            surface.blit(avg_lbl, (graph_x + graph_width - avg_lbl.get_width() - 5, avg_y - 18))

        # Axes
        pygame.draw.line(surface, self.colors['accent1'],
                         (graph_x, graph_y), (graph_x, graph_y + graph_height), 4)
        pygame.draw.line(surface, self.colors['accent1'],
                         (graph_x, graph_y + graph_height),
                         (graph_x + graph_width, graph_y + graph_height), 4)

        surface.blit(stats_font.render("Games", True, self.colors['text_secondary']),
                     (graph_x + graph_width - 60, graph_y + graph_height + 20))
        surface.blit(stats_font.render("Value", True, self.colors['text_secondary']),
                     (graph_x - 85, graph_y - 5))

        # Bars
        num_bars = min(len(data_list), 40)
        bar_width = graph_width / num_bars if num_bars > 0 else 1

        for i, value in enumerate(data_list[-num_bars:]):
            bar_height = graph_height * (value / max_value) if max_value > 0 else 0
            bar_x = graph_x + i * bar_width + 2
            bar_y = graph_y + graph_height - bar_height

            pygame.draw.rect(surface, (20, 20, 30), (bar_x + 2, bar_y + 2, bar_width - 4, bar_height))

            color = ((100, 255, 100) if value >= raw_max * 0.75 else
                     (100, 200, 255) if value >= raw_max * 0.5 else (255, 150, 100))

            pygame.draw.rect(surface, color, (bar_x, bar_y, bar_width - 4, bar_height))
            pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width - 4, bar_height), 1)

            if bar_height > 5:
                lighter = tuple(min(255, c + 40) for c in color)
                pygame.draw.line(surface, lighter,
                                 (bar_x + 1, bar_y + 1), (bar_x + bar_width - 5, bar_y + 1), 1)

            if i % 3 == 0 or bar_height > 40 or i == num_bars - 1:
                value_font = pygame.font.SysFont('arial', 11)
                val_text = value_font.render(str(int(value)), True, self.colors['text'])
                text_x = bar_x + (bar_width - 4) / 2 - val_text.get_width() / 2
                surface.blit(val_text, (int(text_x), int(bar_y) - 16))

        label_font = pygame.font.SysFont('arial', 11)
        for i in range(0, num_bars, max(1, num_bars // 8)):
            game_num = len(data_list) - num_bars + i + 1
            lbl = label_font.render(f"#{game_num}", True, self.colors['text_secondary'])
            lx = graph_x + i * bar_width + bar_width / 2 - lbl.get_width() / 2
            surface.blit(lbl, (int(lx), graph_y + graph_height + 8))

    # ------------------------------------------------------------------
    # Detailed line graph
    # ------------------------------------------------------------------
    def draw_detail_line_graph(self, surface, title, data_list, max_value=None):
        """Draw a detailed line graph filling the window."""
        if not data_list:
            return

        raw_max = max(data_list) if data_list else 1
        min_value = min(data_list)
        avg_value = sum(data_list) / len(data_list)

        graph_x, graph_y = 90, 105
        graph_width, graph_height = SCREEN_WIDTH - 180, SCREEN_HEIGHT - 210

        panel_surface = pygame.Surface((graph_width + 40, graph_height + 80), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (30, 40, 60, 200), (0, 0, graph_width + 40, graph_height + 80))
        pygame.draw.rect(panel_surface, (100, 200, 255, 100), (0, 0, graph_width + 40, graph_height + 80), 2)
        surface.blit(panel_surface, (graph_x - 20, graph_y - 20))

        title_font = pygame.font.SysFont('arial', 32, bold=True)
        surface.blit(title_font.render(title, True, self.colors['accent1']), (graph_x, graph_y - 52))

        stats_font = pygame.font.SysFont('arial', 14)
        surface.blit(stats_font.render(
            f"Avg: {avg_value:.1f}  |  Min: {min_value}  |  Max: {raw_max}",
            True, self.colors['text_secondary']), (graph_x, graph_y - 22))

        grid_font = pygame.font.SysFont('arial', 13)
        top_value = self._draw_y_axis(surface, graph_x, graph_y, graph_width, graph_height,
                                      raw_max, grid_font)
        max_value = top_value

        if max_value > 0:
            avg_y = graph_y + graph_height - int(graph_height * avg_value / max_value)
            pygame.draw.line(surface, (100, 255, 100), (graph_x, avg_y), (graph_x + graph_width, avg_y), 2)
            avg_lbl = stats_font.render("Avg", True, (100, 255, 100))
            surface.blit(avg_lbl, (graph_x + graph_width - avg_lbl.get_width() - 5, avg_y - 18))

        pygame.draw.line(surface, self.colors['accent1'],
                         (graph_x, graph_y), (graph_x, graph_y + graph_height), 4)
        pygame.draw.line(surface, self.colors['accent1'],
                         (graph_x, graph_y + graph_height),
                         (graph_x + graph_width, graph_y + graph_height), 4)

        surface.blit(stats_font.render("Games", True, self.colors['text_secondary']),
                     (graph_x + graph_width - 60, graph_y + graph_height + 20))
        surface.blit(stats_font.render("Value", True, self.colors['text_secondary']),
                     (graph_x - 85, graph_y - 5))

        num_points = min(len(data_list), 60)
        point_spacing = graph_width / (num_points - 1) if num_points > 1 else 0
        points = []

        for i, value in enumerate(data_list[-num_points:]):
            px = graph_x + i * point_spacing
            py = (graph_y + graph_height - graph_height * value / max_value
                  if max_value > 0 else graph_y + graph_height)
            points.append((px, py, value))

        if len(points) > 1:
            area_pts = ([(points[0][0], graph_y + graph_height)] +
                        [(p[0], p[1]) for p in points] +
                        [(points[-1][0], graph_y + graph_height)])
            pygame.draw.polygon(surface, (100, 150, 255, 50), area_pts)

        if len(points) > 1:
            for i in range(len(points) - 1):
                pygame.draw.line(surface, (0, 0, 0),
                                 (points[i][0], points[i][1] + 1),
                                 (points[i + 1][0], points[i + 1][1] + 1), 4)
                pygame.draw.line(surface, self.colors['line'],
                                 (points[i][0], points[i][1]),
                                 (points[i + 1][0], points[i + 1][1]), 3)

        value_font = pygame.font.SysFont('arial', 11)
        for i, (px, py, val) in enumerate(points):
            pygame.draw.circle(surface, (0, 0, 0), (int(px), int(py) + 1), 5)
            point_color = ((100, 255, 100) if val >= raw_max * 0.75 else
                           (100, 200, 255) if val >= raw_max * 0.5 else (255, 150, 100))
            pygame.draw.circle(surface, point_color, (int(px), int(py)), 6)
            pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 3)
            if i % 6 == 0 or i == 0 or i == num_points - 1:
                vt = value_font.render(str(int(val)), True, self.colors['text_secondary'])
                surface.blit(vt, (int(px - vt.get_width() / 2), int(py) - 22))

        label_font = pygame.font.SysFont('arial', 11)
        for i in range(0, num_points, max(1, num_points // 8)):
            game_num = len(data_list) - num_points + i + 1
            lbl = label_font.render(f"#{game_num}", True, self.colors['text_secondary'])
            lx = graph_x + i * point_spacing - lbl.get_width() / 2
            surface.blit(lbl, (int(lx), graph_y + graph_height + 8))

    # ------------------------------------------------------------------
    # Detailed pie chart
    # ------------------------------------------------------------------
    def draw_detail_pie_chart(self, surface, title, results):
        if not results:
            return
        wins = results.count('Win')
        losses = results.count('Loss')
        total = wins + losses
        if total == 0:
            return

        panel_surface = pygame.Surface((SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (30, 40, 60, 200), (0, 0, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40))
        pygame.draw.rect(panel_surface, (100, 200, 255, 100), (0, 0, SCREEN_WIDTH - 40, SCREEN_HEIGHT - 40), 2)
        surface.blit(panel_surface, (20, 20))

        title_font = pygame.font.SysFont('arial', 36, bold=True)
        title_text = title_font.render(title, True, self.colors['accent1'])
        surface.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 50))

        center_x, center_y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20
        radius = 140
        win_percent = wins / total * 100
        loss_percent = losses / total * 100
        win_angle = win_percent / 100 * 360
        loss_angle = 360 - win_angle

        pygame.draw.circle(surface, (0, 0, 0, 80), (center_x + 3, center_y + 3), radius + 10)
        pygame.draw.circle(surface, self.colors['panel_bg'], (center_x, center_y), radius + 8)
        pygame.draw.circle(surface, self.colors['accent1'], (center_x, center_y), radius + 8, 4)

        self._draw_pie_slice_detailed(surface, center_x, center_y, radius, -90, win_angle, self.colors['win'])
        self._draw_pie_slice_detailed(surface, center_x, center_y, radius, -90 + win_angle, loss_angle, self.colors['loss'])

        pygame.draw.circle(surface, self.colors['accent1'], (center_x, center_y), radius, 4)
        pygame.draw.circle(surface, (20, 25, 40), (center_x, center_y), radius // 3)
        pygame.draw.circle(surface, self.colors['accent1'], (center_x, center_y), radius // 3, 2)

        label_font = pygame.font.SysFont('arial', 14, bold=True)
        win_mid = -90 + win_angle / 2
        wlx = center_x + radius * 0.65 * math.cos(math.radians(win_mid))
        wly = center_y + radius * 0.65 * math.sin(math.radians(win_mid))
        wl = label_font.render(f"{win_percent:.1f}%", True, (0, 0, 0))
        surface.blit(wl, (int(wlx - wl.get_width() // 2), int(wly - wl.get_height() // 2)))

        loss_mid = -90 + win_angle + loss_angle / 2
        llx = center_x + radius * 0.65 * math.cos(math.radians(loss_mid))
        lly = center_y + radius * 0.65 * math.sin(math.radians(loss_mid))
        ll = label_font.render(f"{loss_percent:.1f}%", True, (0, 0, 0))
        surface.blit(ll, (int(llx - ll.get_width() // 2), int(lly - ll.get_height() // 2)))

        stats_font = pygame.font.SysFont('arial', 18, bold=True)
        detail_font = pygame.font.SysFont('arial', 14)
        box_y = SCREEN_HEIGHT - 180

        pygame.draw.rect(surface, (30, 60, 30), (60, box_y, 200, 140))
        pygame.draw.rect(surface, self.colors['win'], (60, box_y, 200, 140), 3)
        surface.blit(stats_font.render("Wins", True, self.colors['win']), (75, box_y + 10))
        surface.blit(detail_font.render(f"Count: {wins}", True, self.colors['text']), (75, box_y + 45))
        surface.blit(detail_font.render(f"Percentage: {win_percent:.1f}%", True, self.colors['text']), (75, box_y + 75))

        lx = SCREEN_WIDTH - 260
        pygame.draw.rect(surface, (60, 30, 30), (lx, box_y, 200, 140))
        pygame.draw.rect(surface, self.colors['loss'], (lx, box_y, 200, 140), 3)
        surface.blit(stats_font.render("Losses", True, self.colors['loss']), (lx + 15, box_y + 10))
        surface.blit(detail_font.render(f"Count: {losses}", True, self.colors['text']), (lx + 15, box_y + 45))
        surface.blit(detail_font.render(f"Percentage: {loss_percent:.1f}%", True, self.colors['text']), (lx + 15, box_y + 75))

        total_font = pygame.font.SysFont('arial', 20, bold=True)
        tt = total_font.render(f"Total Games: {total}", True, self.colors['accent1'])
        surface.blit(tt, (SCREEN_WIDTH // 2 - tt.get_width() // 2, SCREEN_HEIGHT - 50))

        win_rate = wins / total * 100
        wrt = detail_font.render(f"Win Rate: {win_rate:.1f}%", True,
                                  (100, 255, 100) if win_rate >= 50 else (255, 150, 100))
        surface.blit(wrt, (SCREEN_WIDTH // 2 - wrt.get_width() // 2, SCREEN_HEIGHT - 20))

    def _draw_pie_slice_detailed(self, surface, x, y, radius, start_angle, angle, color):
        points = [(x, y)]
        steps = max(int(angle / 1.5), 3)
        for i in range(steps + 1):
            a = start_angle + (angle * i / steps)
            points.append((x + radius * math.cos(math.radians(a)),
                            y + radius * math.sin(math.radians(a))))
        if len(points) > 2:
            pygame.draw.polygon(surface, (0, 0, 0, 80), [(p[0]+1, p[1]+1) for p in points])
            pygame.draw.polygon(surface, color, points)
            pygame.draw.line(surface, (255, 255, 255), points[0], points[1], 1)
            pygame.draw.line(surface, (255, 255, 255), points[0], points[-1], 1)

    # ------------------------------------------------------------------
    # Main draw dispatcher
    # ------------------------------------------------------------------
    def draw_all_stats(self, surface):
        """Draw the appropriate tab view."""
        if not self.data['game_ids']:
            font = pygame.font.SysFont('arial', 36, bold=True)
            text = font.render("No game data yet", True, self.colors['accent1'])
            surface.blit(text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 20))
            small_font = pygame.font.SysFont('arial', 18)
            subtext = small_font.render("Play some games to see statistics",
                                        True, self.colors['text_secondary'])
            surface.blit(subtext, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 30))
            return

        self.draw_menu(surface)
        self.draw_chart_type_buttons(surface)

        tab = self.current_tab
        chart_type = self.chart_types.get(tab, 'bar')

        if tab == 'steps':
            if chart_type == 'line':
                self.draw_detail_line_graph(surface, "Steps Per Game", self.data['steps'])
            else:
                self.draw_detail_histogram(surface, "Steps Per Game", self.data['steps'])
        elif tab == 'time':
            if chart_type == 'bar':
                self.draw_detail_histogram(surface, "Time Per Game (s)", self.data['times'])
            else:
                self.draw_detail_line_graph(surface, "Time Per Game (s)", self.data['times'])
        elif tab == 'enemies':
            if chart_type == 'line':
                self.draw_detail_line_graph(surface, "Enemies Encountered", self.data['enemies'])
            else:
                self.draw_detail_histogram(surface, "Enemies Encountered", self.data['enemies'])
        elif tab == 'score':
            if chart_type == 'line':
                self.draw_detail_line_graph(surface, "Score Per Game", self.data['scores'])
            else:
                self.draw_detail_histogram(surface, "Score Per Game", self.data['scores'])
        elif tab == 'results':
            self.draw_detail_pie_chart(surface, "Win/Loss Ratio", self.data['results'])

    # ------------------------------------------------------------------
    # Legacy small-panel methods (kept for compatibility)
    # ------------------------------------------------------------------
    def draw_panel_border(self, surface, x, y, width, height):
        pygame.draw.rect(surface, self.colors['accent1'], (x, y, width, height), 3)
        corner_size = 15
        pygame.draw.line(surface, self.colors['accent2'], (x, y), (x + corner_size, y), 3)
        pygame.draw.line(surface, self.colors['accent2'], (x, y), (x, y + corner_size), 3)

    def draw_histogram(self, surface, title, data_list, x, y, width, height, max_value=None):
        if not data_list:
            return
        if max_value is None:
            max_value = max(data_list) if data_list else 1
        avg_value = sum(data_list) / len(data_list) if data_list else 0
        panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surface, (35, 50, 70, 220), (0, 0, width, height))
        surface.blit(panel_surface, (x, y))
        self.draw_panel_border(surface, x, y, width, height)
        font = pygame.font.SysFont('arial', 18, bold=True)
        surface.blit(font.render(title, True, self.colors['accent1']), (x + 15, y + 8))
        small_font = pygame.font.SysFont('arial', 9)
        surface.blit(small_font.render(f"Max: {max_value} | Avg: {avg_value:.1f}", True,
                                        self.colors['text_secondary']), (x + 15, y + 25))
        grid_font = pygame.font.SysFont('arial', 9)
        for i in range(4):
            gy = y + 40 + (height - 60) * i // 3
            line_color = (80, 90, 110) if i % 2 == 0 else (60, 70, 90)
            pygame.draw.line(surface, line_color, (x + 10, gy), (x + width - 10, gy), 1 if i % 2 else 2)
            vl = grid_font.render(str(int(max_value * (3 - i) / 3)), True, self.colors['text_secondary'])
            surface.blit(vl, (x - 28, gy - 4))
        if max_value > 0:
            avg_line_y = y + height - 25 - (height - 60) * (avg_value / max_value)
            pygame.draw.line(surface, (100, 255, 100), (x + 10, int(avg_line_y)), (x + width - 10, int(avg_line_y)), 1)
        num_bars = min(len(data_list[-15:]), 15)
        bar_width = (width - 40) / num_bars if num_bars > 0 else 1
        start_x = x + 20
        for i, value in enumerate(data_list[-num_bars:]):
            bar_height = (height - 60) * (value / max_value) if max_value > 0 else 0
            bar_x = start_x + i * bar_width
            bar_y = y + height - 25 - bar_height
            color = ((100, 255, 100) if value >= max_value * 0.75 else
                     (100, 200, 255) if value >= max_value * 0.5 else (255, 150, 100))
            pygame.draw.rect(surface, (20, 20, 30), (bar_x + 1, bar_y + 1, bar_width - 2, bar_height))
            pygame.draw.rect(surface, color, (bar_x, bar_y, bar_width - 2, bar_height))
            pygame.draw.rect(surface, (200, 200, 200), (bar_x, bar_y, bar_width - 2, bar_height), 1)
            if bar_height > 3:
                lighter = tuple(min(255, c + 30) for c in color)
                pygame.draw.line(surface, lighter, (bar_x + 1, bar_y + 1), (bar_x + bar_width - 3, bar_y + 1), 1)
        pygame.draw.line(surface, self.colors['accent1'], (x + 10, y + height - 25), (x + width - 10, y + height - 25), 2)
        pygame.draw.line(surface, self.colors['accent1'], (x + 10, y + 40), (x + 10, y + height - 25), 2)

    def draw_summary(self, surface):
        if not self.data['game_ids']:
            return
        wins = self.data['results'].count('Win')
        losses = self.data['results'].count('Loss')
        total = len(self.data['game_ids'])
        avg_steps = sum(self.data['steps']) / len(self.data['steps']) if self.data['steps'] else 0
        avg_time = sum(self.data['times']) / len(self.data['times']) if self.data['times'] else 0
        total_score = sum(self.data['scores'])
        summary_x, summary_y = 20, 470
        summary_width, summary_height = SCREEN_WIDTH - 40, 110
        pygame.draw.rect(surface, self.colors['panel_bg'], (summary_x, summary_y, summary_width, summary_height))
        self.draw_panel_border(surface, summary_x, summary_y, summary_width, summary_height)
        font = pygame.font.SysFont('arial', 20, bold=True)
        surface.blit(font.render("SUMMARY", True, self.colors['accent1']), (summary_x + 15, summary_y + 10))
        stat_font = pygame.font.SysFont('arial', 14)
        row1 = [f"Games: {total}", f"Wins: {wins}", f"Losses: {losses}", f"Avg Steps: {avg_steps:.0f}"]
        row2 = [f"Avg Time: {avg_time:.0f}s", f"Total Score: {total_score}",
                f"Win Rate: {(wins/total*100):.1f}%" if total > 0 else "Win Rate: 0%"]
        for i, stat in enumerate(row1):
            surface.blit(stat_font.render(stat, True, self.colors['text']),
                         (summary_x + 20 + i * 140, summary_y + 35))
        for i, stat in enumerate(row2):
            surface.blit(stat_font.render(stat, True, self.colors['text']),
                         (summary_x + 20 + i * 140, summary_y + 60))