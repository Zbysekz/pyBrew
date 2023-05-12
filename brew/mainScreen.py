import pygame
import pathlib
from GUIObjects import Value, Label, InputField, Checkbox, Button
import datetime
from parameters import Parameters

rootPath = str(pathlib.Path(__file__).parent.absolute())

# defines
TEXT_COLOR = (44, 180, 232)
RED_COLOR = (232, 56, 44)
ORANGE_COLOR = (232, 150, 44)


class cMainScreen:
    def __init__(self, screenManager, pyScreen):
        self.objects = {}
        self.pyScreen = pyScreen
        self.screenManager = screenManager

        Value.default_color = TEXT_COLOR  # sets default for all values

        self.perShiftOrPerOperator = True

        self.tmrBlink = 0
        self.warningFlip = False

        offset_y = 25
        x = 38
        y = 0
        # inside
        # self.objects['valTemperature1'] = Value(screen=self.pyScreen, position=(x, y), units='°C', decimals=1)

        y += offset_y
        self.objects['label1'] = Label(screen=self.pyScreen, position=(14, 4), text='Brew', size=28)

        offset_y = 40
        x = 17
        y = 50
        self.objects['hlt_value'] = Value(screen=self.pyScreen, position=(x, y - 5), title='HLT     ', units='°C',
                                          size=60, decimals=1)
        self.objects['hlt_setpoint'] = InputField(screen=self.pyScreen, pos=(x + 500, y), size=40)
        self.objects['hlt_PID'] = Checkbox(screen=self.pyScreen, caption='PID', pos=(x + 670, y), size=40)
        self.objects['hlt_on'] = Checkbox(screen=self.pyScreen, caption='ON', pos=(x + 800, y), size=40)
        self.objects['hlt_out1'] = Checkbox(screen=self.pyScreen, caption='', pos=(x + 900, y))
        self.objects['hlt_out2'] = Checkbox(screen=self.pyScreen, caption='', pos=(x + 940, y))
        self.objects['hlt_out3'] = Checkbox(screen=self.pyScreen, caption='', pos=(x + 980, y))

        y = y + offset_y
        self.objects['rvk_value'] = Value(screen=self.pyScreen, position=(x, y - 5), title='RMUT    ', units='°C',
                                          size=60, decimals=1)
        self.objects['rvk_setpoint'] = InputField(screen=self.pyScreen, pos=(x + 500, y), size=40)
        self.objects['rvk_PID'] = Checkbox(screen=self.pyScreen, caption='PID', pos=(x + 670, y), size=40)
        self.objects['rvk_on'] = Checkbox(screen=self.pyScreen, caption='ON', pos=(x + 800, y), size=40)
        self.objects['rvk_out1'] = Checkbox(screen=self.pyScreen, caption='', pos=(x + 900, y))
        self.objects['rvk_out2'] = Checkbox(screen=self.pyScreen, caption='', pos=(x + 940, y))
        self.objects['rvk_out3'] = Checkbox(screen=self.pyScreen, caption='', pos=(x + 980, y))

        y = y + offset_y
        self.objects['scz_value'] = Value(screen=self.pyScreen, position=(x, y - 5), title='SCEZ    ', units='°C',
                                          size=60, decimals=1)
        y = y + offset_y
        self.objects['error_value'] = Value(screen=self.pyScreen, position=(x, y - 5), title='ERR    ', units='',
                                            size=60, decimals=0)

        # automat
        x = 50
        y = 300
        offset_x = 150
        self.objects['labelCol1'] = Label(screen=self.pyScreen, position=(x, y), text='SP', size=25)
        self.objects['labelCol2'] = Label(screen=self.pyScreen, position=(x + offset_x, y), text='Gradient', size=25)
        self.objects['labelCol3'] = Label(screen=self.pyScreen, position=(x + offset_x*2, y), text='Time', size=25)
        self.objects['labelCol4'] = Label(screen=self.pyScreen, position=(x + offset_x*3, y), text='Remaining', size=25)
        y += offset_y
        for i in range(5):
            self.objects['aut_setpoint'+str(i)] = InputField(screen=self.pyScreen, pos=(x , y), size=40, units='°C', decimals = 1)
            self.objects['aut_grad'+str(i)] = InputField(screen=self.pyScreen, pos=(x + offset_x, y), size=40, units='%')
            self.objects['aut_time' + str(i)] = InputField(screen=self.pyScreen, pos=(x + offset_x*2, y), size=40, units='min')
            self.objects['aut_remTime' + str(i)] = Value(screen=self.pyScreen, position=(x + offset_x*3, y), title='', units='min', size=40, decimals=0)

            y += offset_y
            Parameters.makePersistent(self.objects, 'aut_setpoint'+str(i), 'value')
            Parameters.makePersistent(self.objects, 'aut_grad' + str(i), 'value')
            Parameters.makePersistent(self.objects, 'aut_time' + str(i), 'value')

        self.objects['chk_aut_man'] = Checkbox(screen=self.pyScreen, caption='Automat / Manual', pos=(x + 940, 300))
        self.objects['btnResetStateMachine'] = Button(manager=self.screenManager, screen=self.pyScreen, caption="Reset",
                                         callback=self.screenManager.ResetStateMachine,  pos=(x + 940, 350))

        self.objects['avg_grad'] = Value(screen=self.pyScreen, position=(x+700, 200), title='AVG gradient  ', units='°C/min',
                                          size=40, decimals=1)

        self.objects['label_SP_reached'] = Label(screen=self.pyScreen, position=(600, 400), text='SP reached', size=25)

        Parameters.makePersistent(self.objects, 'hlt_setpoint', 'value')
        Parameters.makePersistent(self.objects, 'rvk_setpoint', 'value')


    def animate(self):
        for name, obj in self.objects.items():
            if hasattr(obj, 'animate'):
                obj.animate()

        if self.tmrBlink > 2:
            self.warningFlip = not self.warningFlip
            self.tmrBlink = 0
        else:
            self.tmrBlink = self.tmrBlink + 1

    def draw(self):
        for name, obj in self.objects.items():
            obj.draw()

        data = self.screenManager.dataContainer
        if data.get('errorFlags') or data.get('commFail'):
            pygame.draw.rect(self.pyScreen, (255, 0, 0), (0, 0, self.pyScreen.get_width(), self.pyScreen.get_height()), 6)

        for i in range(5):
            cond = i == data.get('stateMachine_status') and data.get('stateMachine_on')
            self.objects['aut_setpoint' + str(i)].frameColor = (0, 255, 0) if cond else (0, 0, 255)
            self.objects['aut_grad' + str(i)].frameColor = (0, 255, 0) if cond else (
            0, 0, 255)
            self.objects['aut_time' + str(i)].frameColor = (0, 255, 0) if cond else (
            0, 0, 255)

    def drawBackground(self):
        img = pygame.image.load(rootPath + "/graphics/background.png").convert()
        rect = img.get_rect()
        self.pyScreen.blit(img, rect)

    def updateValues(self):

        data = self.screenManager.dataContainer
        # CONTAINER -> VISUAL DATA
        self.objects['label1'].text = datetime.datetime.now().strftime('%H:%M  %d.%m.%Y')

        self.objects['hlt_value'].value = data.get('hlt_value')
        self.objects['rvk_value'].value = data.get('rvk_value')
        self.objects['scz_value'].value = data.get('scz_value')
        self.objects['error_value'].value = data.get('errorFlags')
        self.objects['rvk_out1'].checked = (data.get('outputs') & (1 << 0)) != 0
        self.objects['rvk_out2'].checked = (data.get('outputs') & (1 << 1)) != 0
        self.objects['rvk_out3'].checked = (data.get('outputs') & (1 << 2)) != 0

        self.objects['hlt_out1'].checked = (data.get('outputs') & (1 << 3)) != 0
        self.objects['hlt_out2'].checked = (data.get('outputs') & (1 << 4)) != 0
        self.objects['hlt_out3'].checked = (data.get('outputs') & (1 << 5)) != 0

        self.objects['avg_grad'].value = data['avg_grad']

        if data['sp_reached']:
            self.objects['label_SP_reached'].color = (255, 0, 0)
        else:
            self.objects['label_SP_reached'].color = (100, 100, 100)
        # INPUT FIELDS -> CONTAINER
        data['hlt_setpoint'] = self.objects['hlt_setpoint'].value
        data['hlt_on'] = self.objects['hlt_on'].checked
        data['hlt_PID'] = self.objects['hlt_PID'].checked
        data['stateMachine_on'] = self.objects['chk_aut_man'].checked

        if data['stateMachine_on']:
            self.objects['rvk_setpoint'].value = data['rvk_setpoint']
            self.objects['rvk_on'].checked = data['rvk_on']
            self.objects['rvk_PID'].checked = data['rvk_PID']
        else:
            data['rvk_setpoint'] = self.objects['rvk_setpoint'].value
            data['rvk_on'] = self.objects['rvk_on'].checked
            data['rvk_PID'] = self.objects['rvk_PID'].checked

        for i in range(5):
            data['aut_setpoint'+str(i)] = self.objects['aut_setpoint' + str(i)].value
            data['aut_grad' + str(i)] = self.objects['aut_grad' + str(i)].value
            data['aut_time' + str(i)] = self.objects['aut_time' + str(i)].value
            self.objects['aut_remTime' + str(i)].value = data['aut_remTime' + str(i)]

        self.objects['rvk_setpoint'].units = '°C' if data['rvk_PID'] else '%'
        self.objects['hlt_setpoint'].units = '°C' if data['hlt_PID'] else '%'

    def mouseClick(self, event):
        pass
