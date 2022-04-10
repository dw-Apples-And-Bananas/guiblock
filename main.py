import wx




CURSOR_DEFAULT   = 803
CURSOR_IDLE      = 809
CURSOR_DOWN      = 804


class Cursor:
    def __init__(self, panel, file, folder="", pos=(0,0)):
        if not file.endswith(".ico"):
            file += ".ico"
        if not folder.endswith("/") and folder != "":
            folder += "/"

        cursor = wx.Cursor(f"{folder}{file}", wx.BITMAP_TYPE_ICO, pos[0], pos[1])
        panel.SetCursor(cursor)

        self.panel, self.folder, self.pos = panel, folder, pos
        self.cursors = {
            CURSOR_DEFAULT: cursor,
            CURSOR_IDLE:    cursor,
            CURSOR_DOWN:    cursor
        }

        self.panel.Bind(wx.EVT_MOUSE_EVENTS, self._MouseEvents)
    


    def Link(self, file, id, pos=None):
        if not file.endswith(".ico"):
            file += ".ico"
        if pos == None:
            pos = self.pos
        cursor = wx.Cursor(f"{self.folder}{file}", wx.BITMAP_TYPE_ICO, pos[0], pos[1])
        self.cursors[id] = cursor
    


    def Set(self, id, pos=None):
        if pos == None:
            pos = self.pos
        self.panel.SetCursor(self.cursors[id])


    def Bind(self, func):
        self.func = func
    


    def _MouseEvents(self, event):
        self.func(event)
        if event.LeftDown():
            self.panel.SetCursor(self.cursors[CURSOR_DOWN])
        elif event.LeftUp():
            self.panel.SetCursor(self.cursors[CURSOR_DEFAULT])
