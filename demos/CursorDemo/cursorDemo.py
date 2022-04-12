import wx
import guiblock as gb




class Frame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=(480,320))

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour((255,255,255))

        self.cursor = gb.Cursor(self.panel, "cursor", "./demos/CursorDemo")
        self.cursor.Link("cursor2", gb.CURSOR_DOWN)
        self.cursor.Bind(self.MouseEvents)



    def MouseEvents(self, event):
        if event.LeftDown():
            print("Left Down")
        elif event.LeftUp():
            print("Left Up")




if __name__ == "__main__":
    main = wx.App()
    frame = Frame()
    frame.Show()
    main.MainLoop()