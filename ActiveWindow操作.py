import wx
import pygetwindow as gw
import json
import os

CONFIG_FILE = 'config.json'

class WindowSelector(wx.Frame):
    def __init__(self, *args, **kw):
        super(WindowSelector, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.SetTitle('ウィンドウ選択')  # ウィンドウタイトルを設定

        self.windows = gw.getAllTitles()
        # 不要なウィンドウタイトルを除外
        self.windows = [w for w in self.windows if w and w not in ["Windows 入力エクスペリエンス", "Program Manager", self.GetTitle()]]

        if not self.windows:
            wx.MessageBox('開いているウィンドウがありません。', '情報', wx.OK | wx.ICON_INFORMATION)
            self.Close()
            return

        self.list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, 'ファイル名', width=200)
        self.list_ctrl.InsertColumn(1, 'アプリケーション名', width=200)

        for window_title in self.windows:
            file_name, app_name = self.split_title(window_title)
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), file_name)
            self.list_ctrl.SetItem(index, 1, app_name)

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(sizer)

        self.load_config()

        # フレーム全体でキーイベントをキャッチ
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

        # ウィンドウが閉じられるときのイベントをバインド
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # ウィンドウが非アクティブになったときのイベントをバインド
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

    def split_title(self, title):
        # タイトルをファイル名とアプリケーション名に分割
        parts = title.split(' - ')
        if len(parts) > 1:
            return parts[0], parts[-1]
        return title, ''

    def on_select(self, event):
        self.activate_selected_window()

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:  # Enterキーが押された場合
            self.activate_selected_window()
        else:
            event.Skip()  # 他のキーイベントを処理するためにスキップ

    def activate_selected_window(self):
        selected_index = self.list_ctrl.GetFirstSelected()
        if selected_index != -1:
            selected_title = self.windows[selected_index]
            window = gw.getWindowsWithTitle(selected_title)
            if window:
                if window[0].isMinimized:
                    window[0].maximize()  # ウィンドウが最小化されている場合は最大化
                window[0].activate()
        self.Close()  # アプリケーションを終了

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                size = tuple(config.get('size', (400, 300)))
                self.SetSize(size)

        # マウスカーソルの位置を取得してウィンドウの位置を設定
        mouse_position = wx.GetMousePosition()
        self.SetPosition(mouse_position)

    def save_config(self):
        config = {
            'size': self.GetSize().Get(),  # wx.Sizeをタプルに変換
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)

    def on_close(self, event):
        self.save_config()
        self.Destroy()  # ウィンドウを破棄してアプリケーションを終了

    def on_activate(self, event):
        if not event.GetActive():  # ウィンドウが非アクティブになった場合
            self.Close()  # アプリケーションを終了
        event.Skip()

class WindowSwitcherApp(wx.App):
    def OnInit(self):
        self.frame = WindowSelector(None)
        self.frame.Show()
        return True

if __name__ == '__main__':
    app = WindowSwitcherApp()
    app.MainLoop()