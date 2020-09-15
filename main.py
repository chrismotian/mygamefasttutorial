from direct.showbase.ShowBase import ShowBase # import the bits of panda
from direct.task import Task
import sys
from direct.interval.LerpInterval import LerpTexOffsetInterval, LerpPosInterval
from panda3d.core import CompassEffect, CollisionTraverser, CollisionNode
from panda3d.core import CollisionSphere, CollisionHandlerQueue, Material
from panda3d.core import VBase4, VBase3, TransparencyAttrib
from panda3d.core import AmbientLight, DirectionalLight, Vec4, Vec3, Fog
from panda3d.core import BitMask32, Texture, TextNode, TextureStage
from panda3d.core import NodePath, PandaNode
from direct.gui.OnscreenText import OnscreenText

class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # relevant for DEBUG
        self.debug = True
        self.debugLabel = self.makeStatusLabel(0)
        if(self.debug):
            self.debugLabel.setText("Debug Mode ON")
        else:
            self.debugLabel.setText("Debug Mode OFF")
        self.statusLabel = self.makeStatusLabel(1)
        self.collisionLabel = self.makeStatusLabel(2)

        self.world = self.loader.loadModel("world.bam")
        self.world.reparentTo(self.render)

        # relevant for world boundaries
        self.worldsize = 1024

        self.player = self.loader.loadModel("alliedflanker.egg")
        self.player.setPos(200,200,65)
        self.player.setH(self.world,225)
        self.player.reparentTo(self.render)

        # A task to run every frame, some keyboard setup and our speed
        self.taskMgr.add(self.updateTask,"update")
        self.keyboardSetup()
        self.speed = 10.0
        self.maxspeed = 100.0
        self.player.setScale(.2,.2,.2)

        #performance (to be masked later by fog) and view:
        self.maxdistance = 300
        self.camLens.setFar(self.maxdistance)
        self.camLens.setFov(60)

        self.createEnviroment()

        # relevant for collision and DEBUG
        self.setupCollisions()
        self.textCounter = 0

    # relevant for DEBUG
    def makeStatusLabel(self, i):
        return OnscreenText(style=2, fg=(.5,1,.5,1), pos=(-1.3,0.92-(.08*i)),\
                align=TextNode.ALeft, scale = .08, mayChange = 1)

    # relevant for collision and DEBUG
    def setupCollisions(self):
        self.collTrav = CollisionTraverser()


        self.playerGroundSphere = CollisionSphere(0,1.5,56,1)
        self.playerGroundCol = CollisionNode('playerSphere')
        self.playerGroundCol.addSolid(self.playerGroundSphere)

        # bitmask
        self.playerGroundCol.setFromCollideMask(BitMask32.bit(0))
        self.playerGroundCol.setIntoCollideMask(BitMask32.allOff())
        self.world.setCollideMask(BitMask32.bit(0))

        # and done
        self.playerGroundColNp = self.player.attachNewNode(self.playerGroundCol)
        self.playerGroundHandler = CollisionHandlerQueue()
        self.collTrav.addCollider(self.playerGroundColNp, self.playerGroundHandler)

        # DEBUG
        if (self.debug == True):
            self.playerGroundColNp.show()
            self.collTrav.showCollisions(self.render)

    def keyboardSetup(self):
        self.keyMap = {"left":0, "right":0, "climb":0, "fall":0, "accelerate":0, "decelerate":0, "fire":0}
        self.accept("escape", sys.exit)
        self.accept("a", self.setKey,["accelerate",1])
        self.accept("a-up",self.setKey,["accelerate",0])
        self.accept("z",self.setKey,["decelerate",1])
        self.accept("z-up",self.setKey,["decelerate",0])
        self.accept("arrow_left",self.setKey,["left",1])
        self.accept("arrow_left-up",self.setKey,["left",0])
        self.accept("arrow_right",self.setKey,["right",1])
        self.accept("arrow_right-up",self.setKey,["right",0])
        self.accept("arrow_down", self.setKey,["climb",1])
        self.accept("arrow_down-up", self.setKey,["climb",0])
        self.accept("arrow_up", self.setKey,["fall",1])
        self.accept("arrow_up-up", self.setKey,["fall",0])
        self.accept("space", self.setKey, ["fire",1])
        self.accept("space-up", self.setKey, ["fire",0])
        base.disableMouse() # or updateCamera will fail

    def createEnviroment(self):
        # Fog to hide performance tweak:
        colour = (0.0,0.0,0.0)
        expfog = Fog("scene-wide-fog")
        expfog.setColor(*colour)
        expfog.setExpDensity(0.004)
        render.setFog(expfog)
        base.setBackgroundColor(*colour)

        # Our sky
        skydome = loader.loadModel('sky.egg')
        skydome.setEffect(CompassEffect.make(self.render))    
        skydome.setScale(self.maxdistance/2) # bit less than "far"
        skydome.setZ(-30) # sink it
        # NOT render - you`ll fly through the sky!:
        skydome.reparentTo(self.camera)

        # Our lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor(Vec4(.6, .6, .6, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection(Vec3(0,-10,-10))
        directionalLight.setColor(Vec4(1,1,1,1))
        directionalLight.setSpecularColor(Vec4(1,1,1,1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))

    def setKey(self, key, value):
        self.keyMap[key] = value

    def updateTask(self, task):
        self.updatePlayer()
        self.updateCamera()
        #relevant for collision and DEBUG
        self.collTrav.traverse(self.render)
        for i in range(self.playerGroundHandler.getNumEntries()):
            entry = self.playerGroundHandler.getEntry(i)
            if (self.debug == True):
                self.collisionLabel.setText("HIT:"+str(globalClock.getFrameTime()))
            # we will later deal with 'what to do' when the player hits
        return Task.cont

    def updatePlayer(self):
        #Global Clock
        #by default, panda runs as fast as it can frame to frame
        scalefactor = (globalClock.getDt()*self.speed)
        climbfactor = scalefactor * 0.5
        bankfactor = scalefactor
        speedfactor = scalefactor *2.9

        #Climb and Fall
        if(self.keyMap["climb"]!=0 and self.speed>0.00):
        #faster you go, quicker you climb
            self.player.setZ(self.player.getZ()+climbfactor)
            self.player.setR(self.player.getR()+climbfactor)
            #quickest return: (:avoids uncoil/unwind)
            if(self.player.getR()>= 180):
                self.player.setR(-180)
        elif(self.keyMap["fall"]!=0 and self.speed>0.00):
            self.player.setZ(self.player.getZ()-climbfactor)
            self.player.setR(self.player.getR()-climbfactor)
            #quickest return
            if(self.player.getR() <=-180):
                self.player.setR(180) #autoreturn - add a bit regardless to make sure it happens 
        elif(self.player.getR()>0): 
            self.player.setR(self.player.getR()-(climbfactor+0.1))
            if(self.player.getR()<0): 
                self.player.setR(0) #avoid jitter 
        elif(self.player.getR()<0): 
            self.player.setR(self.player.getR()+(climbfactor+0.1)) 
            if(self.player.getR()>0): 
                self.player.setR(0)

        #Left and Right
        if(self.keyMap["left"]!=0 and self.speed>0.0):
            self.player.setH(self.player.getH()+bankfactor)
            self.player.setP(self.player.getP()+bankfactor)
            #quickest return:
            if(self.player.getP()>=180):
                self.player.setP(-180)
        elif(self.keyMap["right"]!=0 and self.speed>0.0):
            self.player.setH(self.player.getH()-bankfactor)
            self.player.setP(self.player.getP()-bankfactor)
            if(self.player.getP()<=-180): 
                self.player.setP(180) 
            
        #autoreturn 
        elif (self.player.getP()>0): 
            self.player.setP(self.player.getP()-(bankfactor+0.1))
        if (self.player.getP()<0): 
            self.player.setP(0) 
        elif(self.player.getP()<0): 
            self.player.setP(self.player.getP()+(bankfactor+0.1)) 
        if(self.player.getP()>0): 
            self.player.setP(0)
        
        #throttle control
        if(self.keyMap["accelerate"]!=0): 
            self.speed += 1
        if(self.speed>self.maxspeed): 
            self.speed = self.maxspeed
        elif(self.keyMap["decelerate"]!=0): 
            self.speed -=1
        if(self.speed<0.0): 
            self.speed =0.0 

        #move forwards - our X/Y is inverted, see the issue 
        self.player.setX(self.player,-speedfactor)#respect max camera distance else you cannot see the floor post loop the loop! 
        if(self.player.getZ()>self.maxdistance):
            self.player.setZ(self.maxdistance)
            #should never happen once we add collision, but in case:
        elif(self.player.getZ()<0):
            self.player.setZ(0) # and now the X/Y world boundaries; 
            if(self.player.getX()<0):
                self.player.setX(0) 
            elif(self.player.getX()>self.worldsize): 
                self.player.setX(self.worldsize)
            
        if (self.player.getY()<0): 
            self.player.setY(0) 
        elif(self.player.getY()> self.worldsize): 
            self.player.setY(self.worldsize)

    def updateCamera(self):
        #see issue content for how we calculated these:
        self.camera.setPos(self.player,25.6226,3.8807,10.2779)
        self.camera.setHpr(self.player,94.8996,-16.6549,1.55508)

        
app = MyApp()
app.run()