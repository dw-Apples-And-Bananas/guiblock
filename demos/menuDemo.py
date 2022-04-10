import wx
import guiblock as gb




class MenuBar(wx.MenuBar):
    def __init__(self, frame):
        wx.MenuBar.__init__(self, 0)

        gb.JsonToMenu(self, "./demos/menu.json")



    def New(self):
        print("new")
    
    def Open(self):
        print("open")
    
    def Save(self):
        print("save")

    def SaveAs(self):
        print("save as")


    def Undo(self):
        print("undo")
    
    def Redo(self):
        print("redo")
    
    def Cut(self):
        print("cut")

    def Copy(self):
        print("copy")
    
    def Paste(self):
        print("paste")




if __name__ == "__main__":
    main = wx.App()

    frame = wx.Frame(None, size=(480,320))
    frame.Show()

    menubar = MenuBar(frame)
    frame.SetMenuBar(menubar)

    main.MainLoop()