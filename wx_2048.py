#coding=utf-8
import wx
import os
from random import randrange, choice
import copy
class Frame(wx.Frame):
    def __init__(self,title):
        super(Frame,self).__init__(None,-1,title,
                style=wx.DEFAULT_FRAME_STYLE|wx.MAXIMIZE_BOX|wx.RESIZE_BORDER)
        self.bgFont = wx.Font(50,wx.SWISS,wx.NORMAL,wx.BOLD)
        self.scFont = wx.Font(18,wx.SWISS,wx.NORMAL,wx.BOLD)
        self.nuFont = wx.Font(36,wx.SWISS,wx.NORMAL,wx.BOLD)
        self.smFont = wx.Font(16,wx.SWISS,wx.NORMAL,wx.NORMAL)
        self.ssFont = wx.Font(16,wx.SWISS,wx.NORMAL,wx.BOLD)
        self.colors = {0:(204,192,179),2:(238, 228, 218),4:(237, 224, 200),
                8:(242, 177, 121),16:(245, 149, 99),32:(246, 124, 95),
                64:(246, 94, 59)}
        #The maximal number could appear in 2048 is 131072, which is 2**17, so this is enough.
        for i in range(11):
            self.colors[2**(7+i)] = (237, 207, 114)
        self.setIcon()
        self.width = 4
        self.height = 4
        self.win_value = 2048
        self.initGame()
        panel = wx.Panel(self)
        panel.Bind(wx.EVT_KEY_DOWN,self.onKeyDown)
        panel.SetFocus()
        self.initBuffer()
        self.Bind(wx.EVT_SIZE,self.onSize) 
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.Bind(wx.EVT_CLOSE,self.onClose)
        self.SetClientSize((505,720))
        self.Center()
        self.Show()
    
    def onPaint(self,event):
        dc = wx.BufferedPaintDC(self,self.buffer)
    
    def onClose(self,event):
        self.saveScore()
        self.Destroy()

    def setIcon(self):
        icon = wx.Icon("icon.ico",wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)
        
    def loadScore(self):
        if os.path.exists("bestscore"):
            ff = open("bestscore")
            self.bstScore = ff.read()
            ff.close()

    def saveScore(self):
        ff = open("bestscore","w")
        ff.write(str(self.bstScore))
        ff.close()

    def initGame(self):
        self.curScore = 0
        self.bstScore = 0
        self.loadScore()
        self.data = [[0 for i in range(self.width)] for j in range(self.height)]

        self.putTile()
        self.putTile()

    def initBuffer(self):
        w,h = self.GetClientSize()
        self.buffer = wx.EmptyBitmap(w,h)

    def transpose(self,data):
    	return [list(row) for row in zip(*data)]

    def onSize(self,event):
        self.initBuffer()
        self.drawAll()

    def putTile(self):
        for row in self.data:
            if 0 in row:
                row,col = choice([(row, col) for row in range(self.width) 
                	for col in range(self.height) if self.data[row][col] == 0])
                self.data[row][col] = 4 if randrange(100) > 89 else 2
                return True
        return False
    def update(self,vlist,direct):
        score = 0
        if direct: #up or left
            i = 1
            while i<len(vlist):
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i += 1
                i += 1
        else:
            i = len(vlist)-1
            while i>0:
                if vlist[i-1]==vlist[i]:
                    del vlist[i]
                    vlist[i-1] *= 2
                    score += vlist[i-1]
                    i -= 1
                i -= 1      
        return score
    def slideLeftRight(self,left):
        score = 0
        numRows,numCols = len(self.data),len(self.data[0])
        oldData = copy.deepcopy(self.data)
        for row in range(numRows):
            rvl = [self.data[row][col] for col in range(numCols) if self.data[row][col]!=0]
            if len(rvl)>=2:           
                score += self.update(rvl,left)
            for i in range(numCols-len(rvl)):
                if left: rvl.append(0)
                else: rvl.insert(0,0)
            for col in range(numCols): self.data[row][col] = rvl[col]
        return oldData!=self.data,score    	

    def slideUpDown(self,up):
    	self.data=self.transpose(self.data)
    	if up:
    		ret = self.slideLeftRight(True)
    	else:
    		ret = self.slideLeftRight(False)
    	self.data=self.transpose(self.data)
    	return ret[0],ret[1]

    def isGameOver(self):
        copyData = copy.deepcopy(self.data)
        flag = False
        if not self.slideUpDown(True)[0] and not self.slideUpDown(False)[0] and \
                not self.slideLeftRight(True)[0] and not self.slideLeftRight(False)[0]:
            flag = True
        if not flag: self.data = copyData
        return flag
    def doMove(self,move,score):
        if move:
            self.putTile()
            self.drawChange(score)
            if self.isGameOver():
                if wx.MessageBox(u"游戏结束，是否重新开始？",u"哈哈",
                        wx.YES_NO|wx.ICON_INFORMATION)==wx.YES:
                    bstScore = self.bstScore
                    self.initGame()
                    self.bstScore = bstScore
                    self.drawAll()
    def onKeyDown(self,event):
        keyCode = event.GetKeyCode()
        if keyCode==wx.WXK_UP:
            self.doMove(*self.slideUpDown(True))
        elif keyCode==wx.WXK_DOWN:
            self.doMove(*self.slideUpDown(False))
        elif keyCode==wx.WXK_LEFT:
            self.doMove(*self.slideLeftRight(True))
        elif keyCode==wx.WXK_RIGHT:
            self.doMove(*self.slideLeftRight(False))        
                
    def drawBg(self,dc):
        dc.SetBackground(wx.Brush((250,248,239)))
        dc.Clear()
        dc.SetBrush(wx.Brush((187,173,160)))
        dc.SetPen(wx.Pen((187,173,160)))
        dc.DrawRoundedRectangle(15,150,475,475,5)
    def drawLogo(self,dc):
        dc.SetFont(self.bgFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"2048",15,46)
    def drawLabel(self,dc):
        dc.SetFont(self.smFont)
        dc.SetTextForeground((119,110,101))
        dc.DrawText(u"Join the numbers and get to the ",15,114)
        dc.DrawText(u"Use your                     to move the tiles. When ",135,639)
        dc.DrawText(u"two tiles with the same number touch, they ",15, 660)
        dc.SetFont(self.ssFont)
        dc.DrawText(u"HOW TO PLAY:",15,639)
        dc.DrawText(u"2048 tile!",245,114)
        dc.DrawText(u"arrow keys ",205,639)
        dc.DrawText(u"merge into one!",320,660)
    def drawScore(self,dc):            
        dc.SetFont(self.scFont)
        scoreLabelSize,bestLabelSize = dc.GetTextExtent(u"SCORE"),dc.GetTextExtent(u"BEST")
        curScoreBoardMinW,bstScoreBoardMinW = 15*2+scoreLabelSize[0],15*2+bestLabelSize[0]
        curScoreSize,bstScoreSize = dc.GetTextExtent(str(self.curScore)),dc.GetTextExtent(str(self.bstScore))
        curScoreBoardNedW,bstScoreBoardNedW = 10+curScoreSize[0],10+bstScoreSize[0]
        curScoreBoardW = max(curScoreBoardMinW,curScoreBoardNedW)
        bstScoreBoardW = max(bstScoreBoardMinW,bstScoreBoardNedW)
        dc.SetBrush(wx.Brush((187,173,160)))
        dc.SetPen(wx.Pen((187,173,160)))
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW,40,bstScoreBoardW,50,3)
        dc.DrawRoundedRectangle(505-15-bstScoreBoardW-5-curScoreBoardW,40,curScoreBoardW,50,3)
        dc.SetTextForeground((238,228,218))
        dc.DrawText(u"BEST",505-15-bstScoreBoardW+(bstScoreBoardW-bestLabelSize[0])/2,48)
        dc.DrawText(u"SCORE",505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-scoreLabelSize[0])/2,48)
        dc.SetTextForeground((255,255,255))
        dc.DrawText(str(self.bstScore),505-15-bstScoreBoardW+(bstScoreBoardW-bstScoreSize[0])/2,68)
        dc.DrawText(str(self.curScore),505-15-bstScoreBoardW-5-curScoreBoardW+(curScoreBoardW-curScoreSize[0])/2,68)

    def drawTiles(self,dc):
        dc.SetFont(self.nuFont)
        for row in range(4):
            for col in range(4):
                value = self.data[row][col]
                color = self.colors[value]
                if value==2 or value==4:
                    dc.SetTextForeground((119,110,101))
                else:
                    dc.SetTextForeground((255,255,255))
                dc.SetBrush(wx.Brush(color))
                dc.SetPen(wx.Pen(color))
                dc.DrawRoundedRectangle(30+col*115,165+row*115,100,100,2)
                size = dc.GetTextExtent(str(value))
                while size[0]>100-15*2:
                    self.scFont = wx.Font(self.scFont.GetPointSize()*4/5,wx.SWISS,wx.NORMAL,wx.BOLD,face=u"Roboto")
                    dc.SetFont(self.scFont)
                    size = dc.GetTextExtent(str(value))
                if value!=0: dc.DrawText(str(value),30+col*115+(100-size[0])/2,165+row*115+(100-size[1])/2)
    def drawAll(self):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        self.drawBg(dc)
        self.drawLogo(dc)
        self.drawLabel(dc)
        self.drawScore(dc)
        self.drawTiles(dc)
    def drawChange(self,score):
        dc = wx.BufferedDC(wx.ClientDC(self),self.buffer)
        if score:
            self.curScore += score
            if self.curScore > self.bstScore:
                self.bstScore = self.curScore
            self.drawScore(dc)
        self.drawTiles(dc)
        
if __name__ == "__main__":
    app = wx.App()
    Frame(u"2048 v0.0.1 by 42binwang")
    app.MainLoop()