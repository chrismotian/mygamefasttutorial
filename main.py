from direct.showbase.ShowBase import ShowBase # import the bits of panda

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        self.player = self.loader.loadModel("alliedflanker.egg")
        self.player.setPos(0,0,65)
        self.player.setH(225)
        self.player.reparentTo(self.render)
        
app = MyApp()
app.run()