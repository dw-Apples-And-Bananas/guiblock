import wx
import json
import os





def print(*args):
    arg = ""
    space = " " if len(args) > 1 else ""
    for a in args:
        arg += f"{a}{space}"
    os.system(f'echo "{arg}"')





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

    menubar.Bind(wx.EVT_MENU, lambda e: MenuEvent(match, e))


def MenuEvent(match, event):
    try:
        match[str(event.GetId())]()
    except:
        event.Skip()





CURSOR_DEFAULT   = 803
CURSOR_IDLE      = 809
CURSOR_DOWN      = 804


class Cursor:
    def __init__(self, panel, file, folder="", pos=(0,0), children=False):
        if not file.endswith(".ico"):
            file += ".ico"
        if not folder.endswith("/") and folder != "":
            folder += "/"
        self.path = folder + file

        cursor = wx.Cursor(self.path, wx.BITMAP_TYPE_ICO, pos[0], pos[1])
        panel.SetCursor(cursor)
        if children:
            for child in panel.Children:
                child.cursor = self

        self.panel, self.folder, self.pos, self.children = panel, folder, pos, children
        self.cursors = {
            CURSOR_DEFAULT: cursor,
            CURSOR_IDLE:    cursor,
            CURSOR_DOWN:    cursor
        }
        self.currCursor = self.cursors[CURSOR_DEFAULT]

        self.func = False
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
        if self.func != False:
            self.func(event)

        cursor = self.cursors[CURSOR_DEFAULT]
        if event.LeftDown():
            cursor = self.cursors[CURSOR_DOWN]
        
        if cursor != self.currCursor:
            self.panel.SetCursor(cursor)
            if self.children:
                for child in self.panel.Children:
                    child.cursor = self





class Hierarchy(wx.Panel):
    def __init__(self, panel, pos=(0,0), size=(200,500), cursor=None):
        wx.Panel.__init__(self, panel, pos=pos, size=size)
        self.SetColours()

        if cursor != None:
            self.cursor = Cursor(self, cursor)

        self.y = 0
        self.selectFunc = None



    def SetColours(self, background=(255,255,255), 
                    hover=(255,255,255),
                    select=(255,255,255),
                    label=(0,0,0),
                    label_hover=(0,0,0),
                    label_select=(0,0,0)):
        self.colours = {
            "background": background,
            "hover": hover,
            "select": select,
            "label": label,
            "label_hover": label_hover,
            "label_select": label_select
        }
        self.SetBackgroundColour(background)



    def BindSelect(self, func):
        self.selectFunc = func




    class File(wx.Panel):
        def __init__(self, hierarchy, path, pos=(0,0), size=(200,22), x=20):
            wx.Panel.__init__(self, hierarchy, pos=pos, size=size)
            self.SetBackgroundColour(hierarchy.colours["background"])

            self.hierarchy, self.path, self.x = hierarchy, path, x
            self.selected = False


            self.label = wx.StaticText(self, label=path.split("/")[-1])
            self.label.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            self.label.SetPosition((x,self.Size[1]//2-self.label.Size[1]//2))
            self.label.SetForegroundColour(self.hierarchy.colours["label"])

            
            if hierarchy.cursor != None:
                self.cursor = Cursor(self, hierarchy.cursor.path)
                self.cursor.Bind(self.MouseEvents)
                self.labelCursor = Cursor(self.label, hierarchy.cursor.path)
                self.labelCursor.Bind(self.MouseEvents)
            else:
                self.label.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)
                self.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)


    
        def MouseEvents(self, event):
            if event.LeftDown():
                if self.hierarchy.selectFunc != None:
                    self.hierarchy.selectFunc(self)
                for child in self.hierarchy.Children:
                    if type(child) == Hierarchy.File:
                        child.selected = False
                        child.label.SetForegroundColour(self.hierarchy.colours["label"])
                        child.SetBackgroundColour(self.hierarchy.colours["background"])
                        child.Refresh()
                self.selected = True
                self.label.SetForegroundColour(self.hierarchy.colours["label_select"])
                self.SetBackgroundColour(self.hierarchy.colours["select"])

            if not self.selected:
                if event.Entering():
                    self.label.SetForegroundColour(self.hierarchy.colours["label_hover"])
                    self.SetBackgroundColour(self.hierarchy.colours["hover"])
                elif event.Leaving() and event.EventObject != self.label:
                    self.label.SetForegroundColour(self.hierarchy.colours["label"])
                    self.SetBackgroundColour(self.hierarchy.colours["background"])

            self.Refresh()



        def Move(self, y):
            self.SetPosition((self.Position[0], self.Position[1]+y))




    class Folder(wx.Panel):
        def __init__(self, hierarchy, path, parent=None, pos=(0,0), size=(200,22), x=20):
            wx.Panel.__init__(self, hierarchy, pos=pos, size=size)
            self.SetBackgroundColour(hierarchy.colours["background"])

            self.hierarchy, self.path, self.parent, self.x = hierarchy, path, parent, x
            self.children = self.ListChildren()
            self.expanded = False
            self.hovering = False


            self.label = wx.StaticText(self, label=self.path.split("/")[-1])
            self.label.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
            self.label.SetPosition((x,self.Size[1]//2-self.label.Size[1]//2))
            self.label.SetForegroundColour(self.hierarchy.colours["label"])


            if hierarchy.cursor != None:
                self.cursor = Cursor(self, hierarchy.cursor.path)
                self.cursor.Bind(self.MouseEvents)
                self.labelCursor = Cursor(self.label, hierarchy.cursor.path)
                self.labelCursor.Bind(self.MouseEvents)
            else:
                self.label.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)
                self.Bind(wx.EVT_MOUSE_EVENTS, self.MouseEvents)

            self.Bind(wx.EVT_PAINT, self.Paint)


    
        def MouseEvents(self, event):
            if event.LeftDown():
                if self.expanded:
                    self.Collapse()
                else:
                    self.Expand()
            
            if event.Entering():
                self.hovering = True
                self.label.SetForegroundColour(self.hierarchy.colours["label_hover"])
                self.SetBackgroundColour(self.hierarchy.colours["hover"])
            elif event.Leaving() and event.EventObject != self.label:
                self.hovering = False
                self.label.SetForegroundColour(self.hierarchy.colours["label"])
                self.SetBackgroundColour(self.hierarchy.colours["background"])

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
                if self.hovering:
                    gc.SetPen(wx.Pen(self.hierarchy.colours["label_hover"]))
                else:
                    gc.SetPen(wx.Pen(self.hierarchy.colours["label"]))
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