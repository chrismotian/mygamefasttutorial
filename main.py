from direct.showbase.ShowBase import ShowBase # import the bits of panda

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        self.player = self.loader.loadModel("alliedflanker.egg")
        self.player.setPos(0,500,65)
        self.player.setH(-180)
        self.player.setScale(100,100,100)
        self.player.setR(45)
        self.player.setP(45)
        self.player.reparentTo(self.render)
        
app = MyApp()
app.run()