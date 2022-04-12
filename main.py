from re import S
import wx
import json
import os




def JsonToMenu(menubar, file):
    with open(file) as f:
        data = json.load(f)

    match = {}

    for m in data:
        menu = wx.Menu()
        for i in data[m]:
            if i == "-"*10:
                menu.AppendSeparator()
            else:
                match[i[0]] = eval(f"menubar.{i[3]}")
                args = [eval(i[0]), f"&{i[1]}\t{i[2]}"]
                menu.Append(*args)
        menubar.Append(menu, m)

    menubar.Bind(wx.EVT_MENU, lambda e: match[str(e.GetId())]())





CURSOR_DEFAULT   = 803
CURSOR_IDLE      = 809
CURSOR_DOWN      = 804


class Cursor:
    def __init__(self, panel, file, folder="", pos=(0,0), children=False):
        if not file.endswith(".ico"):
            file += ".ico"
        if not folder.endswith("/") and folder != "":
            folder += "/"

        cursor = wx.Cursor(f"{folder}{file}", wx.BITMAP_TYPE_ICO, pos[0], pos[1])
        panel.SetCursor(cursor)
        if children:
            for child in panel.Children:
                child.SetCursor(cursor)

        self.panel, self.folder, self.pos, self.children = panel, folder, pos, children
        self.cursors = {
            CURSOR_DEFAULT: cursor,
            CURSOR_IDLE:    cursor,
            CURSOR_DOWN:    cursor
        }
        self.func = False

        self.panel.Bind(wx.EVT_MOUSE_EVENTS, self._MouseEvents)
    


    def Link(self, file, id, pos=None):
        if not file.endswith(".ico"):
            file += ".ico"
        if pos == None:
            pos = self.pos
        cursor = wx.Cursor(f"{self.folder}{file}", wx.BITMAP_TYPE_ICO, pos[0], pos[1])
        self.cursors[id] = cursor
        if self.children:
            for child in self.panel.Children:
                child.SetCursor(cursor)
    


    def Set(self, id, pos=None):
        if pos == None:
            pos = self.pos
        self.panel.SetCursor(self.cursors[id])


    def Bind(self, func):
        self.func = func
    


    def _MouseEvents(self, event):
        if self.func != False:
            self.func(event)
        if event.LeftDown():
            cursor = self.cursors[CURSOR_DOWN]
            self.panel.SetCursor(cursor)
            if self.children:
                for child in self.panel.Children:
                    child.SetCursor(cursor)
        elif event.LeftUp():
            cursor = self.cursors[CURSOR_DEFAULT]
            self.panel.SetCursor(cursor)
            if self.children:
                for child in self.panel.Children:
                    child.SetCursor(cursor)
        
        # event.Skip()





class Hierarchy(wx.Panel):
    def __init__(self, panel, pos=(0,0), size=(200,500)):
        wx.Panel.__init__(self, panel, pos=pos, size=size)

        self.y = 0




    class File(wx.Panel):
        def __init__(self, hierarchy, path, pos=(0,0), size=(200,24), x=20):
            wx.Panel.__init__(self, hierarchy, pos=pos, size=size)
            self.SetBackgroundColour((255,255,255))

            self.hierarchy, self.path, self.x = hierarchy, path, x


            self.label = wx.StaticText(self, label=path.split("/")[-1])
            self.label.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            self.label.SetForegroundColour((0,0,0))
            self.label.SetPosition((x,self.Size[1]//2-self.label.Size[1]//2))

            
            self.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)


    
        def MouseEvents(self, event):
            if event.LeftDown():
                os.system(f"open {self.path}")

            self.Refresh()



        def Move(self, y):
            self.SetPosition((self.Position[0], self.Position[1]+y))




    class Folder(wx.Panel):
        def __init__(self, hierarchy, path, parent=None, pos=(0,0), size=(200,24), x=20):
            wx.Panel.__init__(self, hierarchy, pos=pos, size=size)
            self.SetBackgroundColour((255,255,255))

            self.hierarchy, self.path, self.parent, self.x = hierarchy, path, parent, x
            self.children = self.ListChildren()
            self.expanded = False


            self.label = wx.StaticText(self, label=self.path.split("/")[-1])
            self.label.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            self.label.SetForegroundColour((0,0,0))
            self.label.SetPosition((x,self.Size[1]//2-self.label.Size[1]//2))


            self.label.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)
            self.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)
            self.Bind(wx.EVT_PAINT, self.Paint)


    
        def MouseEvents(self, event):
            if event.LeftDown():
                if self.expanded:
                    self.Collapse()
                else:
                    self.Expand()

            self.Refresh()



        def Move(self, y):
            try:
                for child in self.children:
                    child.Move(y)
            except AttributeError:
                pass
            self.SetPosition((self.Position[0], self.Position[1]+y))



        def Expand(self):
            self.expanded = True

            y = self.Position[1]
            h = self.Size[1]
            children = []
            count = 0
            for child in self.children:
                y += h
                path = os.path.join(self.path, child)
                if os.path.isdir(path):
                    c = self.hierarchy.Folder(self.hierarchy, path, self, pos=(0,y), size=self.Size, x=self.x+20)
                elif os.path.isfile(path):
                    c = self.hierarchy.File(self.hierarchy, path, pos=(0,y), size=self.Size, x=self.x+20)
                children.append(c)
                count += 1
            self.children = children

            parent = self.parent
            if parent != None:
                index = parent.children.index(self)
                while True:
                    for child in parent.children[index+1::]:
                        child.Move(h*count)
                    if parent.parent != None:
                        index = parent.parent.children.index(parent)
                        parent = parent.parent
                    else:
                        break



        def Collapse(self):
            self.expanded = False

            count = 0
            for child in self.children:
                if type(child) == Hierarchy.Folder:
                    if child.expanded:
                        child.Collapse()
                child.Destroy()
                count += 1
            
            parent = self.parent
            if parent != None:
                index = parent.children.index(self)
                while True:
                    for child in parent.children[index+1::]:
                        child.Move(-(self.Size[1]*count))
                    if parent.parent != None:
                        index = parent.parent.children.index(parent)
                        parent = parent.parent
                    else:
                        break
            
            self.children = self.ListChildren()
        


        def ListChildren(self):
            folders = []
            files = []
            for child in os.listdir(self.path):
                path = os.path.join(self.path, child)
                if os.path.isfile(path):
                    files.append(child)
                elif os.path.isdir(path):
                    folders.append(child)

            return(folders + files)



        def Paint(self, event):
            dc = wx.PaintDC(self)
            gc = wx.GraphicsContext.Create(dc)

            size = self.Size
            x = self.x
            y = size[1]/2

            if gc:
                gc.SetPen(wx.Pen((0,0,0)))
                if self.expanded:
                    path = gc.CreatePath()
                    path.MoveToPoint(x-13, y-2)
                    path.AddLineToPoint(x-9, y+2)
                    path.AddLineToPoint(x-5, y-2)
                    gc.StrokePath(path)
                else:
                    path = gc.CreatePath()
                    path.MoveToPoint(x-10, y-4)
                    path.AddLineToPoint(x-7, y)
                    path.AddLineToPoint(x-10, y+4)
                    gc.StrokePath(path)