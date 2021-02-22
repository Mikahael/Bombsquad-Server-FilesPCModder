#first mod released to the public by PC||Modder/PC231392/PC290717
#kindly do give some credit to me for those using.
#thankyou for using PC Server Files
#they work on all server files from 1.4.148 and up
#the distance between you and success is fear.
#Thanks to God
import bsPowerup
from bsPowerup import *
import bs
import bsSpaz
from fire import *
import fire
import bsUtils
from bsSpaz import Spaz
import random

from bsPowerup import PowerupMessage, PowerupAcceptMessage, _TouchedMessage, PowerupFactory, Powerup

defaultPowerupInterval = 8000

class _TouchedMessage(object):
    pass

class PowerupFactory(object):
    """
    category: Game Flow Classes
    
    Wraps up media and other resources used by bs.Powerups.
    A single instance of this is shared between all powerups
    and can be retrieved via bs.Powerup.getFactory().

    Attributes:

       model
          The bs.Model of the powerup box.

       modelSimple
          A simpler bs.Model of the powerup box, for use in shadows, etc.

       texBox
          Triple-bomb powerup bs.Texture.

       texPunch
          Punch powerup bs.Texture.

       texIceBombs
          Ice bomb powerup bs.Texture.

       texStickyBombs
          Sticky bomb powerup bs.Texture.

       texShield
          Shield powerup bs.Texture.

       texImpactBombs
          Impact-bomb powerup bs.Texture.

       texHealth
          Health powerup bs.Texture.

       texLandMines
          Land-mine powerup bs.Texture.

       texCurse
          Curse powerup bs.Texture.

       healthPowerupSound
          bs.Sound played when a health powerup is accepted.

       powerupSound
          bs.Sound played when a powerup is accepted.

       powerdownSound
          bs.Sound that can be used when powerups wear off.

       powerupMaterial
          bs.Material applied to powerup boxes.

       powerupAcceptMaterial
          Powerups will send a bs.PowerupMessage to anything they touch
          that has this bs.Material applied.
    """

    def __init__(self):
        """
        Instantiate a PowerupFactory.
        You shouldn't need to do this; call bs.Powerup.getFactory()
        to get a shared instance.
        """

        self._lastPowerupType = None

        self.model = bs.getModel("powerup")
        self.modelSimple = bs.getModel("powerupSimple")

        self.texBomb = bs.getTexture("powerupBomb")
        self.texPunch = bs.getTexture("powerupPunch")
        self.texIceBombs = bs.getTexture("powerupIceBombs")
        self.texStickyBombs = bs.getTexture("powerupStickyBombs")
        self.texShield = bs.getTexture("powerupShield")
        self.texImpactBombs = bs.getTexture("powerupImpactBombs")
        self.texHealth = bs.getTexture("powerupHealth")
        self.texLandMines = bs.getTexture("powerupLandMines")
        self.texCurse = bs.getTexture("powerupCurse")
        self.texSloMo = bs.getTexture("achievementFlawlessVictory")
        self.texTNT = bs.getTexture("achievementTNT")
        self.texStrongICE = bs.getTexture("menuButton")
        self.texSpeedBoots = bs.getTexture("achievementGotTheMoves")
        self.texChamp = bs.getTexture("achievementBoxer")
        self.texTroll = bs.getTexture("achievementOffYouGo")
        self.texSpazColor = bs.getTexture("crossOutMask")
        self.texCharacter = bs.getTexture("wizardIcon")
        self.texInvisible = bs.getTexture("ouyaOButton")

        self.healthPowerupSound = bs.getSound("healthPowerup")
        self.powerupSound = bs.getSound("powerup01")
        self.powerdownSound = bs.getSound("powerdown01")
        self.dropSound = bs.getSound("boxDrop")

        # material for powerups
        self.powerupMaterial = bs.Material()

        # material for anyone wanting to accept powerups
        self.powerupAcceptMaterial = bs.Material()

        # pass a powerup-touched message to applicable stuff
        self.powerupMaterial.addActions(
            conditions=(("theyHaveMaterial",self.powerupAcceptMaterial)),
            actions=(("modifyPartCollision","collide",True),
                     ("modifyPartCollision","physical",False),
                     ("message","ourNode","atConnect",_TouchedMessage())))

        # we dont wanna be picked up
        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('pickupMaterial')),
            actions=( ("modifyPartCollision","collide",False)))

        self.powerupMaterial.addActions(
            conditions=("theyHaveMaterial",
                        bs.getSharedObject('footingMaterial')),
            actions=(("impactSound",self.dropSound,0.5,0.1)))

        self._powerupDist = []
        for p,freq in getDefaultPowerupDistribution():
            for i in range(int(freq)):
                self._powerupDist.append(p)
                
    def getRandomPowerupType(self,forceType=None,excludeTypes=[]):
        """
        Returns a random powerup type (string).
        See bs.Powerup.powerupType for available type values.

        There are certain non-random aspects to this; a 'curse' powerup,
        for instance, is always followed by a 'health' powerup (to keep things
        interesting). Passing 'forceType' forces a given returned type while
        still properly interacting with the non-random aspects of the system
        (ie: forcing a 'curse' powerup will result
        in the next powerup being health).
        """
        if forceType:
            t = forceType
        else:
            # if the last one was a curse, make this one a health to
            # provide some hope
            if self._lastPowerupType == 'curse':
                t = 'health'
            else:
                while True:
                    t = self._powerupDist[
                        random.randint(0, len(self._powerupDist)-1)]
                    if t not in excludeTypes:
                        break
        self._lastPowerupType = t
        return t
        
def getDefaultPowerupDistribution():
    return (('tripleBombs',3),
            ('iceBombs',3),
            ('punch',3),
            ('impactBombs',3),
            ('landMines',2),
            ('stickyBombs',2),
            ('shield',2),
            ('health',1),
            ('sloMo',4),
            ('TNT',2),
            ('strongICE',3),
            ('speedBoots',2),
            ('champ',1),#if too strong just enable 0 which removes it from pwp dist or lower the chances of getting it.
            ('troll',3),
            ('spazColor',3),
            ('character',4),
            ('invisible',2),
            ('curse',1))

class Powerup(bs.Actor):#PCModder
    """
    category: Game Flow Classes

    A powerup box.
    This will deliver a bs.PowerupMessage to anything that touches it
    which has the bs.PowerupFactory.powerupAcceptMaterial applied.

    Attributes:

       powerupType
          The string powerup type.  This can be 'tripleBombs', 'punch',
          'iceBombs', 'impactBombs', 'landMines', 'stickyBombs', 'shield',
          'health', or 'curse'.

       node
          The 'prop' bs.Node representing this box.
    """

    def __init__(self,position=(0,1,0),powerupType='tripleBombs',expire=True):
        """
        Create a powerup-box of the requested type at the requested position.

        see bs.Powerup.powerupType for valid type strings.
        """
        
        bs.Actor.__init__(self)

        factory = self.getFactory()
        self.powerupType = powerupType;
        self._powersGiven = False

        if powerupType == 'tripleBombs': tex = factory.texBomb
        elif powerupType == 'punch': tex = factory.texPunch
        elif powerupType == 'iceBombs': tex = factory.texIceBombs
        elif powerupType == 'impactBombs': tex = factory.texImpactBombs
        elif powerupType == 'landMines': tex = factory.texLandMines
        elif powerupType == 'stickyBombs': tex = factory.texStickyBombs
        elif powerupType == 'shield': tex = factory.texShield
        elif powerupType == 'health': tex = factory.texHealth
        elif powerupType == 'curse': tex = factory.texCurse
        elif powerupType == 'sloMo': tex = factory.texSloMo
        elif powerupType == 'TNT': tex = factory.texTNT
        elif powerupType == 'strongICE': tex = factory.texStrongICE
        elif powerupType == 'speedBoots': tex = factory.texSpeedBoots
        elif powerupType == 'champ': tex = factory.texChamp
        elif powerupType == 'troll': tex = factory.texTroll
        elif powerupType == 'spazColor': tex = factory.texSpazColor
        elif powerupType == 'character': tex = factory.texCharacter
        elif powerupType == 'invisible': tex = factory.texInvisible
        else: raise Exception("invalid powerupType: "+str(powerupType))

        if len(position) != 3: raise Exception("expected 3 floats for position")
        
        self.node = bs.newNode(
            'prop',
            delegate=self,
            attrs={'body':'box',
                   'position':position,
                   'model':factory.model,
                   'lightModel':factory.modelSimple,
                   'shadowSize':0.5,
                   'colorTexture':tex,
                   'reflection':'powerup',
                   'reflectionScale':[1.0],
                   'materials':(factory.powerupMaterial,
                                bs.getSharedObject('objectMaterial'))})
        prefixAnim = {0: (1, 0, 0), 250: (1, 1, 0), 250 * 2: (0, 1, 0), 250 * 3: (0, 1, 1), 250 * 4: (1, 0, 1),
                      250 * 5: (0, 0, 1), 250 * 6: (1, 0, 0)}
        color = (0,0,1)
                   
        if fire.powerupName:
            m = bs.newNode('math', owner=self.node, attrs={'input1': (0, 0.7, 0), 'operation': 'add'})
            self.node.connectAttr('position', m, 'input2')
            self.nodeText = bs.newNode('text',
                                       owner=self.node,
                                       attrs={'text': powerupType,
                                              'inWorld': True,
                                              'shadow': 1.0,
                                              'flatness': 1.0,
                                              'color': color,
                                              'scale': 0.0,
                                              'hAlign': 'center'})
            m.connectAttr('output', self.nodeText, 'position')
            bs.animate(self.nodeText, 'scale', {0: 0, 140: 0.016, 200: 0.01})
            bs.animateArray(self.nodeText,'color',3,{0:(0,0,2),500:(0,2,0),1000:(2,0,0),1500:(2,2,0),2000:(2,0,2),2500:(0,1,6),3000:(1,2,0)},True)
            bs.emitBGDynamics(position=self.nodeText.position, velocity=self.node.position, count=75, scale=1.0, spread=1.3, chunkType='spark')
                                
        if fire.powerupShield:
            self.nodeShield = bs.newNode('shield', owner=self.node, attrs={'color': color,
                                                                           'position': (
                                                                               self.node.position[0],
                                                                               self.node.position[1],
                                                                               self.node.position[2] + 0.5),
                                                                           'radius': 1.2})
            self.node.connectAttr('position', self.nodeShield, 'position')
            bsUtils.animateArray(self.nodeShield, 'color', 3, prefixAnim, True)
            
        if fire.discoLights:
            self.nodeLight = bs.newNode('light',
                                        attrs={'position': self.node.position,
                                               'color': color,
                                               'radius': 0.25, #0.4 will make it nice and bright
                                               'volumeIntensityScale': 0.5})
            self.node.connectAttr('position', self.nodeLight, 'position') 
            bsUtils.animateArray(self.nodeLight, 'color', 3, prefixAnim, True)
            bs.animate(self.nodeLight, "intensity", {0:1.0, 1000:1.8, 2000:1.0}, loop = True)
            bs.gameTimer(8000,self.nodeLight.delete)  

        # animate in..
        curve = bs.animate(self.node,"modelScale",{0:0,140:1.6,200:1})
        bs.gameTimer(200,curve.delete)

        if expire:
            bs.gameTimer(defaultPowerupInterval-2500,
                         bs.WeakCall(self._startFlashing))
            bs.gameTimer(defaultPowerupInterval-1000,
                         bs.WeakCall(self.handleMessage, bs.DieMessage()))

    @classmethod
    def getFactory(cls):
        """
        Returns a shared bs.PowerupFactory object, creating it if necessary.
        """
        activity = bs.getActivity()
        if activity is None: raise Exception("no current activity")
        try: return activity._sharedPowerupFactory
        except Exception:
            f = activity._sharedPowerupFactory = PowerupFactory()
            return f
            
    def _startFlashing(self):
        if self.node.exists(): self.node.flashing = True
        
    def handleMessage(self, msg):
        self._handleMessageSanityCheck()

        if isinstance(msg, PowerupAcceptMessage):
            factory = self.getFactory()
            if self.powerupType == 'health':
                bs.playSound(factory.healthPowerupSound, 3,
                             position=self.node.position)
            bs.playSound(factory.powerupSound, 3, position=self.node.position)
            self._powersGiven = True
            self.handleMessage(bs.DieMessage())

        elif isinstance(msg, _TouchedMessage):
            if not self._powersGiven:
                node = bs.getCollisionInfo("opposingNode")
                if node is not None and node.exists():
                    if self.powerupType == "sloMo":
                        bs.getSharedObject('globals').slowMotion = bs.getSharedObject('globals').slowMotion == False
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())
                        bsUtils.PopupText("SloMo",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()
                    elif self.powerupType == "TNT":
                        p = node.positionForward
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())
                        bs.Bomb((p[0]+0.43,p[1]+4,p[2]-0.25),velocity=(0,-6,0),bombType = 'tnt').autoRetain()  
                        bsUtils.PopupText("TNT",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()
                    elif self.powerupType == "strongICE":
                        p = node.positionForward
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())    
                        bs.Bomb((p[0]+0.43,p[1]+4,p[2]-0.25),velocity=(0,-6,0),bombType = 'ice').autoRetain()  
                        bs.Bomb((p[0]+0.43,p[1]+4,p[2]-0.25),velocity=(0,-6,0),bombType = 'ice').autoRetain() 
                        bs.Bomb((p[0]+0.43,p[1]+4,p[2]-0.25),velocity=(0,-6,0),bombType = 'ice').autoRetain()     
                        bsUtils.PopupText("ICY",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()
                    elif self.powerupType == "speedBoots":
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())            
            	        node.hockey = True         
                        bsUtils.PopupText("Speed away",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()
                    elif self.powerupType == "invisible":
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())      
                        node.name = ' '
                        node.style = 'agent'
                        node.headModel = None
                        node.torsoModel = None
                        node.pelvisModel = None
                        node.upperArmModel = None
                        node.foreArmModel = None
                        node.handModel = None
                        node.upperLegModel = None
                        node.lowerLegModel = None
                        node.toesModel = None      
                        bsUtils.PopupText("Invisible",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()                        
                    elif self.powerupType == "character":
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())      
                        testingEvent = 0

                        event = random.randint(1,6) if testingEvent == 0 else testingEvent
                        print 'Patron And Oore282 <3: ' + str(event) 

                        if event in [1]:                        
                            node.colorTexture = bs.getTexture('frostyColor')
                            node.colorMaskTexture = bs.getTexture('frostyColorMask')
                            node.headModel = bs.getModel('frostyHead')
                            node.upperArmModel = bs.getModel('kronkUpperArm')
                            node.torsoModel = bs.getModel('frostyTorso')
                            node.pelvisModel = bs.getModel('frostyPelvis')
                            node.foreArmModel = bs.getModel('frostyForeArm')
                            node.handModel = bs.getModel('frostyHand')
                            node.upperLegModel = bs.getModel('frostyUpperLeg')
                            node.lowerLegModel = bs.getModel('frostyLowerLeg')
                            node.toesModel = bs.getModel('frostyToes')
                            node.style = 'frosty'       
                            bsUtils.PopupText("Frosty The Snowman",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain() 
                        elif event in [2]:         
                            node.colorTexture = bs.getTexture('santaColor')
                            node.colorMaskTexture = bs.getTexture('santaColorMask')      
                            node.headModel = bs.getModel('santaHead')
                            node.upperArmModel = bs.getModel('santaUpperArm')
                            node.torsoModel = bs.getModel('santaTorso')
                            node.pelvisModel = bs.getModel('kronkPelvis')
                            node.foreArmModel = bs.getModel('santaForeArm')
                            node.handModel = bs.getModel('santaHand')
                            node.upperLegModel = bs.getModel('santaUpperLeg')
                            node.lowerLegModel = bs.getModel('santaLowerLeg')
                            node.toesModel = bs.getModel('santaToes')
                            node.style = 'santa'
                            bsUtils.PopupText("SANTA",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()    
                        elif event in [3]:           
                            node.colorTexture = bs.getTexture('wizardColor')
                            node.colorMaskTexture = bs.getTexture('wizardColorMask')                
                            node.headModel = bs.getModel('wizardHead')
                            node.upperArmModel = bs.getModel('wizardUpperArm')
                            node.torsoModel = bs.getModel('wizardTorso')
                            node.pelvisModel = bs.getModel('wizardPelvis')
                            node.foreArmModel = bs.getModel('wizardForeArm')
                            node.handModel = bs.getModel('wizardHand')
                            node.upperLegModel = bs.getModel('wizardUpperLeg')
                            node.lowerLegModel = bs.getModel('wizardLowerLeg')
                            node.toesModel = bs.getModel('wizardToes')
                            node.style = 'wizard'
                            bsUtils.PopupText("EVIL SCEPTER WIZARD MAN",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()   
                        elif event in [4]:           
                            node.colorTexture = bs.getTexture('pixieColor')
                            node.colorMaskTexture = bs.getTexture('pixieColorMask')                
                            node.headModel = bs.getModel('pixieHead')
                            node.upperArmModel = bs.getModel('pixieUpperArm')
                            node.torsoModel = bs.getModel('pixieTorso')
                            node.pelvisModel = bs.getModel('pixiePelvis')
                            node.foreArmModel = bs.getModel('pixieForeArm')
                            node.handModel = bs.getModel('pixieHand')
                            node.upperLegModel = bs.getModel('pixieUpperLeg')
                            node.lowerLegModel = bs.getModel('pixieLowerLeg')
                            node.toesModel = bs.getModel('pixieToes')
                            node.style = 'pixie'
                            bsUtils.PopupText("PIXIEL-ATED",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()   
                        elif event in [5]:           
                            node.colorTexture = bs.getTexture('cyborgColor')
                            node.colorMaskTexture = bs.getTexture('cyborgColorMask')                
                            node.headModel = bs.getModel('cyborgHead')
                            node.upperArmModel = bs.getModel('cyborgUpperArm')
                            node.torsoModel = bs.getModel('cyborgTorso')
                            node.pelvisModel = bs.getModel('cyborgPelvis')
                            node.foreArmModel = bs.getModel('cyborgForeArm')
                            node.handModel = bs.getModel('cyborgHand')
                            node.upperLegModel = bs.getModel('cyborgUpperLeg')
                            node.lowerLegModel = bs.getModel('cyborgLowerLeg')
                            node.toesModel = bs.getModel('cyborgToes')
                            node.style = 'cyborg'
                            bsUtils.PopupText("The Robo",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()    
                        elif event in [6]:    
                            node.colorTexture = bs.getTexture('ninjaColor')
                            node.colorMaskTexture = bs.getTexture('ninjaColorMask')                
                            node.headModel = bs.getModel('ninjaHead')
                            node.upperArmModel = bs.getModel('ninjaUpperArm')
                            node.torsoModel = bs.getModel('ninjaTorso')
                            node.pelvisModel = bs.getModel('ninjaPelvis')
                            node.foreArmModel = bs.getModel('ninjaForeArm')
                            node.handModel = bs.getModel('ninjaHand')
                            node.upperLegModel = bs.getModel('ninjaUpperLeg')
                            node.lowerLegModel = bs.getModel('ninjaLowerLeg')
                            node.toesModel = bs.getModel('ninjaToes')
                            node.style = 'ninja'
                            node.nameColor = (0,0,0)
                            node.color = (0,0,0)
                            node.highlight = (0,0,0)
                            bsUtils.PopupText("PC||Modder",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()                            
                    elif self.powerupType == "spazColor":
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())            
                        node.color = ((0+random.random()*6.5),(0+random.random()*6.5),(0+random.random()*6.5))
                        node.highlight = ((0+random.random()*6.5),(0+random.random()*6.5),(0+random.random()*6.5))  
                        node.nameColor = ((0+random.random()*1.5),(0+random.random()*1.5),(0+random.random()*1.5))       
                        node.name += random.choice(['\nTHE BOSS','\nNOOB','\nPRO','\nKill Me','\nNooby'])  
                        bsUtils.PopupText("PC||Modder",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()         
                    elif self.powerupType == "troll":
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())            
                        node.handleMessage(bs.FreezeMessage())      
                        node.handleMessage(bs.FreezeMessage())      
                        node.handleMessage(bs.PowerupMessage(powerupType='curse'))
                        bsUtils.PopupText("TRoLL",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()
                    elif self.powerupType == "champ":
                        self._powersGiven = True
                        self.handleMessage(bs.DieMessage())            
                        node.handleMessage(bs.PowerupMessage(powerupType = 'punch'))
                        node.handleMessage(bs.PowerupMessage(powerupType = 'shield'))
                        bsUtils.PopupText("Champ",color=(1,2,1),scale=1.5,position=self.node.position).autoRetain()
                    else:
                        node.handleMessage(PowerupMessage(self.powerupType, sourceNode=self.node))

        elif isinstance(msg, bs.DieMessage):
            if self.node.exists():
                if (msg.immediate):
                    self.node.delete()
                else:
                    curve = bs.animate(self.node, "modelScale", {0:1,100:0})
                    bs.gameTimer(100, self.node.delete)
                    bs.gameTimer(100,self.nodeLight.delete)

        elif isinstance(msg ,bs.OutOfBoundsMessage):
            self.handleMessage(bs.DieMessage())

        elif isinstance(msg, bs.HitMessage):
            # dont die on punches (thats annoying)
            if msg.hitType != 'punch':
                self.handleMessage(bs.DieMessage())
        else:
            bs.Actor.handleMessage(self, msg)
            
#enjoy this my friends. Do give some credit and have a great day. :) its open sourced as well

bsPowerup.PowerupFactory = PowerupFactory
bsPowerup.Powerup = Powerup
bsPowerup.getDefaultPowerupDistribution = getDefaultPowerupDistribution
bsPowerup._TouchedMessage = _TouchedMessage