import wx
import guiblock as gb




class Hierarchy(gb.Hierarchy):
    def __init__(self, panel):
        gb.Hierarchy.__init__(self, panel, pos=(0,0), size=panel.Size)
        self.SetBackgroundColour((255,255,255))

        self.panel = panel

        self.Bind(wx.EVT_UPDATE_UI, self.UpdateUi)
    


    def UpdateUi(self, *args):
        self.SetSize(self.panel.Size)



class MenuBar(wx.MenuBar):
    def __init__(self, frame):
        wx.MenuBar.__init__(self, 0)

        self.frame = frame

        gb.JsonToMenu(self, "./demos/HierarchyDemo/menu.json")



    def Open(self):
        dialog = wx.DirDialog(self.frame, "", "", wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)

        if dialog.ShowModal() == wx.ID_OK:
            path = dialog.GetPath()
        dialog.Destroy()

        for child in hierarchy.Children:
            child.Destroy()
        hierarchy.Folder(hierarchy, path=path, size=(hierarchy.Size[0],24)).Expand()




if __name__ == "__main__":
    main = wx.App()

    frame = wx.Frame(None, size=(300,650))
    frame.Show()
    menubar = MenuBar(frame)
    frame.SetMenuBar(menubar)

    panel = wx.Panel(frame, size=frame.Size)

    hierarchy = Hierarchy(panel)

    main.MainLoop()