import wx  # 追加
import pygetwindow as gw
import json
import os

CONFIG_FILE = 'config.json'

class WindowManager:
    def __init__(self, frame):
        self.frame = frame
        self.sort_criteria = "名前 (昇順)"

    def get_filtered_windows(self):
        windows = gw.getAllTitles()
        return [w for w in windows if w and w not in ["Windows 入力エクスペリエンス", "Program Manager", self.frame.GetTitle()]]

    def split_title(self, title):
        parts = title.split(' - ')
        if len(parts) > 1:
            return parts[0], parts[-1], title
        return title, '', title

    def activate_selected_window(self, list_ctrl, window_data):
        selected_index = list_ctrl.GetFirstSelected()
        if selected_index != -1:
            _, _, selected_title = window_data[selected_index]
            window = gw.getWindowsWithTitle(selected_title)
            if window:
                if window[0].isMinimized:
                    window[0].maximize()
                window[0].activate()

    def sort_list(self, window_data, col, original_data, id=None):
        column_name = "ファイル名" if col == 0 else "アプリケーション名"
        sort_orders = [
            (f"{column_name} (昇順)", lambda x: x[col]),
            (f"{column_name} (降順)", lambda x: x[col], True),
            ("初期値", lambda x: original_data.index(x))
        ]

        if id is not None:
            if id in [1, 4]:  # 名前 (昇順)
                window_data.sort(key=lambda x: x[col])
                self.sort_criteria = f"{column_name} (昇順)"
            elif id in [2, 5]:  # 名前 (降順)
                window_data.sort(key=lambda x: x[col], reverse=True)
                self.sort_criteria = f"{column_name} (降順)"
            elif id in [3, 6]:  # 初期値
                window_data[:] = original_data
                self.sort_criteria = "初期値"
        else:
            # 現在のソート状態をトグル
            current_index = self.frame.sort_index[col]
            sort_order = sort_orders[current_index]
            window_data.sort(key=sort_order[1], reverse=len(sort_order) > 2 and sort_order[2])
            self.sort_criteria = sort_order[0]
            self.frame.sort_index[col] = (current_index + 1) % len(sort_orders)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                size = tuple(config.get('size', (400, 300)))
                self.frame.SetSize(size)
                column_widths = config.get('column_widths', [200, 200])
                for i, width in enumerate(column_widths):
                    self.frame.list_ctrl.SetColumnWidth(i, width)

        mouse_position = wx.GetMousePosition()
        self.frame.SetPosition(mouse_position)

    def save_config(self, list_ctrl):
        config = {
            'size': self.frame.GetSize().Get(),
            'column_widths': [list_ctrl.GetColumnWidth(i) for i in range(list_ctrl.GetColumnCount())]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)