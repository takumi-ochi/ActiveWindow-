import wx
from back import WindowManager

class WindowSelector(wx.Frame):
    def __init__(self, *args, **kw):
        super(WindowSelector, self).__init__(*args, **kw)

        self.panel = wx.Panel(self)
        self.sort_criteria = "初期値"  # 初期ソート基準を初期値に設定
        self.SetTitle(f'ウィンドウ選択 - {self.sort_criteria}')  # ウィンドウタイトルを設定

        self.manager = WindowManager(self)
        self.windows = self.manager.get_filtered_windows()

        if not self.windows:
            wx.MessageBox('開いているウィンドウがありません。', '情報', wx.OK | wx.ICON_INFORMATION)
            self.Close()
            return

        self.list_ctrl = wx.ListCtrl(self.panel, style=wx.LC_REPORT)
        self.list_ctrl.InsertColumn(0, 'ファイル名', width=200)
        self.list_ctrl.InsertColumn(1, 'アプリケーション名', width=200)

        self.window_data = [self.manager.split_title(title) for title in self.windows]
        self.original_data = list(self.window_data)  # 初期データを保持
        self.populate_list()

        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_select)
        self.list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self.on_col_click)
        self.list_ctrl.Bind(wx.EVT_LIST_COL_RIGHT_CLICK, self.on_col_right_click)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 10)
        self.panel.SetSizer(sizer)

        self.manager.load_config()

        # フレーム全体でキーイベントをキャッチ
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_down)

        # ウィンドウが閉じられるときのイベントをバインド
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # ウィンドウが非アクティブになったときのイベントをバインド
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

        self.sort_index = [2, 2]  # 各列のソートインデックスを初期値に設定

    def populate_list(self):
        self.list_ctrl.DeleteAllItems()
        for file_name, app_name, _ in self.window_data:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), file_name)
            self.list_ctrl.SetItem(index, 1, app_name)

    def on_select(self, event):
        self.manager.activate_selected_window(self.list_ctrl, self.window_data)
        self.Close()  # アプリケーションを終了

    def on_key_down(self, event):
        if event.GetKeyCode() == wx.WXK_RETURN:  # Enterキーが押された場合
            self.manager.activate_selected_window(self.list_ctrl, self.window_data)
            self.Close()  # アプリケーションを終了
        else:
            event.Skip()  # 他のキーイベントを処理するためにスキップ

    def on_col_click(self, event):
        col = event.GetColumn()
        # ソート処理を行う前に、現在のソート状態を確認し、次のソート状態を決定
        self.manager.sort_list(self.window_data, col, self.original_data)
        self.SetTitle(f'ウィンドウ選択 - {self.manager.sort_criteria}')
        self.populate_list()

    def on_col_right_click(self, event):
        col = event.GetColumn()
        menu = wx.Menu()

        # チェック可能なメニュー項目を追加
        if col == 0:
            item1 = menu.AppendCheckItem(1, "名前 (昇順)")
            item2 = menu.AppendCheckItem(2, "名前 (降順)")
            item3 = menu.AppendCheckItem(3, "初期値")
            if self.manager.sort_criteria == "ファイル名 (昇順)":
                menu.Check(item1.GetId(), True)
            elif self.manager.sort_criteria == "ファイル名 (降順)":
                menu.Check(item2.GetId(), True)
            elif self.manager.sort_criteria == "初期値":
                menu.Check(item3.GetId(), True)
        elif col == 1:
            item4 = menu.AppendCheckItem(4, "名前 (昇順)")
            item5 = menu.AppendCheckItem(5, "名前 (降順)")
            item6 = menu.AppendCheckItem(6, "初期値")
            if self.manager.sort_criteria == "アプリケーション名 (昇順)":
                menu.Check(item4.GetId(), True)
            elif self.manager.sort_criteria == "アプリケーション名 (降順)":
                menu.Check(item5.GetId(), True)
            elif self.manager.sort_criteria == "初期値":
                menu.Check(item6.GetId(), True)

        # メニュー項目の選択時にソートを変更
        def on_menu_selection(evt):
            self.manager.sort_list(self.window_data, col, self.original_data, evt.GetId())
            self.SetTitle(f'ウィンドウ選択 - {self.manager.sort_criteria}')
            self.populate_list()

        self.Bind(wx.EVT_MENU, on_menu_selection, id=1)
        self.Bind(wx.EVT_MENU, on_menu_selection, id=2)
        self.Bind(wx.EVT_MENU, on_menu_selection, id=3)
        self.Bind(wx.EVT_MENU, on_menu_selection, id=4)
        self.Bind(wx.EVT_MENU, on_menu_selection, id=5)
        self.Bind(wx.EVT_MENU, on_menu_selection, id=6)

        self.PopupMenu(menu)
        menu.Destroy()

    def on_close(self, event):
        self.manager.save_config(self.list_ctrl)
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