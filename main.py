from direct.showbase.ShowBase import ShowBase # import the bits of panda
from panda3d.core import GeoMipTerrain # that we need
from direct.showbase.Loader import Loader


class MyApp(ShowBase): # our class
	def __init__(self):
		ShowBase.__init__(self) # initialise
		terrain = GeoMipTerrain("worldTerrain") # create a terrain
		terrain.setHeightfield("heightmap.jpg") # set the height map
		tex = loader.loadTexture("texturemap.jpg")
		terrain.setBruteforce(True) # level of detail
		root = terrain.getRoot() # capture root
		root.reparentTo(render) # render from root
		root.setSz(60) # maximum height
		terrain.generate() # generate
		root.setTexture(tex)
		root.writeBamFile('world.bam') # create 3d model

app = MyApp() # our 'object'
app.run() # Here we go!