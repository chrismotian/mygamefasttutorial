from direct.showbase.ShowBase import ShowBase # import the bits of panda

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)
        
app = MyApp()
app.run()