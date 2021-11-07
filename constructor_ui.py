
### ### ### ### ### ## ### ### ### ###
### ### ### BUILT-IN LIBRARIES ### ###
### ### ### ### ### ## ### ### ### ###
import logging
from time import sleep

from numpy import reciprocal

from PyQt5.QtGui import QImage

### ### ### ### ## ## ## ### ### ###
### ### ### CUSTOM LIBRARIES ### ###
### ### ### ### ## ## ## ### ### ###
import libs

from stdo import stdo
from structure_ui import Structure_UI, init_and_run_UI, init_UI
from structure_camera import Camera_Object, CAMERA_FLAGS
from structure_threading import Thread_Object
from structure_data import Structure_Buffer

from qt_tools import numpy_To_QT_Image_Converter, QT_Scene_Add_Item_To_Background

# CONFIGURATIONS
MAX_SUBWINDOW = 2


def baumer_api_test(camera_object, delay=7, exposure_time=40000, acquisition_framerate_enable=True, acquisition_framerate=25):
    print("API Test waiting for ", delay, " sec...")
    sleep(delay)
    print("API Test is starting...")
    camera_object.api_Baumer_Camera_Is_Colorfull()
    camera_object.api_Baumer_Camera_Configurations(
            exposure_time=exposure_time, 
            acquisition_framerate_enable=acquisition_framerate_enable, 
            acquisition_framerate=acquisition_framerate, 
        )

### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### CAMERA UI CONFIGURATIONS ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###
class Ui_Camera_API_Main(Structure_UI):
    logger_level = logging.INFO
    
    def __init__(self, *args, obj=None, logger_level=logging.INFO, **kwargs):
        super(Ui_Camera_API_Main, self).__init__(*args, **kwargs)

        ### ### ### ### ###
        ### Constractor ###
        ### ### ### ### ###
        self.logger_level = logger_level

        ### ### ### ### ###
        ### ### Init ### ##
        ### ### ### ### ###
        self.init()
        
    ### ### ## ### ###
    ### OVERWRITES ###
    ### ### ## ### ###
    
    def init(self):
        self.configure_Other_Settings()

    def configure_Other_Settings(self):
        self.action_Settings_Page.triggered.connect(
            self.action_Settings_Page_Triggered
        )
        self.action_Add_Camera.triggered.connect(
            self.action_Add_Camera_Triggered
        )

    ### ### ## ### ###
    ### ### ## ### ###
    ### ### ## ### ###

    ### ### ### ## ### ###
    ### MDI SUB WINDOW ###
    ### ### ### ## ### ###
    """
    def destroy_Sub_Window_Overwrite(self, sub_window):
        self.mdiArea_Camera_Area.removeSubWindow(sub_window)
        self.action_Add_Camera.setEnabled(True) \
            if len(self.mdiArea_Camera_Area.subWindowList()) < MAX_SUBWINDOW \
            else self.action_Add_Camera.setEnabled(False)
    """

    def action_Add_Camera_Triggered(self):
        if len(self.mdiArea_Camera_Area.subWindowList()) < MAX_SUBWINDOW:
            #self.action_Add_Camera.setEnabled(True)
            self.create_Sub_Window(
                parent=self, 
                mdiArea=self.mdiArea_Camera_Area, 
                UI_Class=Ui_Camera_API_Developer, 
                title="Camera", 
                UI_File_Path="camera_api_developer_UI.ui"
            ).show()
            self.mdiArea_Camera_Area.tileSubWindows()
        """
        else:
            self.action_Add_Camera.setEnabled(False)
        """

    ### ### ### ## ### ###
    ### ### ### ## ### ###
    ### ### ### ## ### ###

    def action_Settings_Page_Triggered(self):
        app_Ui_Settings_Page, ui_Settings_Page = init_UI(
            Ui_Settings,
            UI_File_Path="Settings_UI.ui",
            is_Maximized=False
        )
        ui_Settings_Page.setWindowTitle("Settings")
        ui_Settings_Page.show()
        self.garbage_Collector_Add([app_Ui_Settings_Page, ui_Settings_Page])
        """
        ui_Settings_Page = Structure_UI(
            UI_File_Path="Ui_Settings_Page.ui"
        )
        ui_Settings_Page.show()
        self.garbage_Collector_Add(ui_Settings_Page)
        """
    
### ### ### ### ### ### ## ### ### ### ### ### ###
### ### ### SETTINGS UI CONFIGURATIONS ### ### ###
### ### ### ### ### ### ## ### ### ### ### ### ###

class Ui_Settings(Structure_UI):

    UI_File_Path = ""
    themes_list = {
        "default": "default.qss"
    }

    def __init__(self, *args, obj=None, **kwargs):
        super(Ui_Settings, self).__init__(*args, **kwargs)
        """
        self.UI_File_Path = UI_File_Path
        self.load_UI(self, self.UI_File_Path)
        # self.configure_Button_Connections()
        """

        self.init()
        
    ### ### ## ### ###
    ### OVERWRITES ###
    ### ### ## ### ###
    
    def init(self):
        self.themes_list = self.load_themes_to_combobox(
            self.comboBox_theme_chooser,
            "themes"
        )
        self.configure_Other_Settings()

    def configure_Other_Settings(self):
        self.comboBox_theme_chooser.currentIndexChanged.connect(
            self.comboBox_theme_chooser_currentIndexChanged
        )
        self.pushButton_theme_chooser_refresher.clicked.connect(
            lambda: self.pushButton_theme_chooser_refresher_Clicked(
                self.comboBox_theme_chooser
            )
        )

    ### ### ## ### ###
    ### ### ## ### ###
    ### ### ## ### ###
    
    ### ### ### ### ###
    ## Theme Chooser ##
    ### ### ### ### ### 

    def comboBox_theme_chooser_currentIndexChanged(self):
        self.set_Style_Sheet_Globally(
            self.themes_list[self.comboBox_theme_chooser.currentText(
            )] if self.comboBox_theme_chooser.currentText() in self.themes_list else ""
        )

    def pushButton_theme_chooser_refresher_Clicked(self, comboBox):
        self.themes_list = self.load_themes_to_combobox(
            comboBox,
            "themes",
            True
        )

    ### ### ## ### ###
    ### ### ## ### ###
    ### ### ## ### ###

### ### ### ### ### ### ## ### ### ### ### ### ###
### ### ### ### ### ### ## ### ### ### ### ### ###
### ### ### ### ### ### ## ### ### ### ### ### ###

### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### CAMERA UI CONFIGURATIONS ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###


class Ui_Camera_API_Developer(Structure_UI):
    logger_level = logging.INFO
    __camera_instance = None
    __Camera_Pack = list()
    __Camera_Pack_Structure = {
        "title": "",
        "camera_object": None,
        "thread_object": None,
        "buffer_object": None,
        "connected_UI_Frame": None
    }
    __Threads = dict()
    
    UI_File_Path = ""
    themes_list = {
        "default": "default.qss"
    }
    mdiArea = None
    is_Camera_Stream_Active = False
    mouse_Positions = dict()

    def __init__(self, *args, obj=None, logger_level=logging.INFO, **kwargs):
        super(Ui_Camera_API_Developer, self).__init__(*args, **kwargs)

        ### ### ### ### ###
        ### Constractor ###
        ### ### ### ### ###
        self.logger_level = logger_level
        
        ### ### ### ### ###
        ### ### Init ### ##
        ### ### ### ### ###
        self.init()

    ### ### ## ### ###
    ### OVERWRITES ###
    ### ### ## ### ###
    
    def init(self):
        self.configure_Other_Settings()
        self.init_Buffers()
        self.init_Threads()
        self.connect_Threads()
    
    def init_Buffers(self, *args, **kwargs):
        super(Ui_Camera_API_Developer, self).init_Buffers(*args, **kwargs)
        
        self.Buffer_Dict["graphicsView_Page_1_Camera"] = Structure_Buffer(
            max_limit=240
        )
    
    def init_QTimers(self, *args, **kwargs):
        super(Ui_Camera_API_Developer, self).init_QTimers(*args, **kwargs)
        
        """
        self.QTimer_Dict["graphicsView_Page_1_Camera_Buffer_Connector"] = self._qtimer_Create_And_Run(
            self,
            lambda: self.Buffer_Dict["graphicsView_Page_1_Camera"].append(self.__camera_instance.stream_Returner())
            ),
            100
        )
        """
        self.QTimer_Dict["graphicsView_Page_1_Camera_Renderer"] = self._qtimer_Create_And_Run(
            self,
            lambda: self.graphicsView_Renderer(
                self.graphicsView_Page_1_Camera,
                None if self.__camera_instance is None else self.__camera_instance.stream_Returner()
            ),
            100
        )
    
    def configure_Button_Connections(self):
        self.pushButton_Page_1_Connect_to_Camera.clicked.connect(
            lambda: self.connect_to_Camera(
                CAMERA_FLAGS.BASLER if self.comboBox_Camera_API_Selection.currentText() == "Basler" else 
                CAMERA_FLAGS.BAUMER if self.comboBox_Camera_API_Selection.currentText() == "Baumer" else 
                CAMERA_FLAGS.CV2
            )
        )
        self.pushButton_Page_1_Stream_Switch.clicked.connect(
            self.stream_Switch
        )
    
    def configure_Other_Settings(self):
        # Event Position Initializes
        self.mouse_Positions["mouseMove_graphicsView_Pos"] = None
        self.mouse_Positions["mouseMove_graphicsView_Pos_To_Scene"] = None
        
        self.init_qt_graphicsView(
            self.graphicsView_Page_1_Camera,
            mouseMoveEvent=self.mouseMove_Event_Handler_graphicsView
        )
        print("!!!graphicsView.mouseMoveEvent",
              self.graphicsView_Page_1_Camera.mouseMoveEvent)
        
        self.init_qt_graphicsView_Scene(
            self.graphicsView_Page_1_Camera,
        )
        self.spinBox_Exposure_Time.valueChanged.connect(
            lambda: self.dial_Exposure_Time.setValue(
                int(
                    float(
                        self.spinBox_Exposure_Time.value()
                    ) * 10000
                )
            )
        )
        
        self.dial_Exposure_Time.valueChanged.connect(
            lambda: self.spinBox_Exposure_Time.setValue(
                int(
                    self.dial_Exposure_Time.value() / 10000
                )
             )
        )
    
    def closeEvent(self, *args, **kwargs):
        super(Ui_Camera_API_Developer, self).closeEvent(*args, **kwargs)
        
        if self.mdiArea is not None:
            #self.Parent.destroy_Sub_Window_Overwrite(self)
            self.Parent.destroy_Sub_Window(self.mdiArea, self)
        
    ### ### ## ### ###
    ### ### ## ### ###
    ### ### ## ### ###
    
    ### ### ### ### ###
    ### THREAD APIs ###
    ### ### ### ### ###
    
    def init_Threads(self):
        return
        logger_level = logging.INFO
        self.__Threads["camera_Listener"] = Thread_Object(
            name="camera_Listener",
            delay=0.1,
            logger_level=logger_level,
            set_Deamon=True,
            run_number=1,
            quit_trigger=self.is_Quit_App
        )
        """
        ### ### ### ### ### ### ### #
        #  Camera Streamer Thread   #
        ### ### ### ### ### ### ### #
        self.__Threads["camera_Listener"] = Thread_Object(
            name="camera_Listener",
            delay=0.1,
            logger_level=logger_level,
            set_Deamon=True,
            run_number=1,
            quit_trigger=self.is_Quit_App
        )
        # self.__Threads["camera_Listener"].logger.disabled = True  # is_logger_disabled
        # self.__Threads["camera_Listener"].logger.propagate = not is_logger_disabled
        """

    def connect_Threads(self):
        return
        self.__Threads["camera_Listener"].init(
            params=[
                self.is_Quit_App
            ],
            task=self.camera_Listener
        )
        
    ### ### ### ### ###
    ### ### ### ### ###
    ### ### ### ### ###

    ### ### ### ### ###
    ### CAMERA APIs ###
    ### ### ### ### ###
    
    def connect_to_Camera(self, camera_flag):
        self.__camera_instance = self.get_Camera(camera_flag)
        """
        self.__camera_instance.stream_Connector(
            connection=self.(), 
            trigger_pause=self.is_Stream_Active,
            trigger_quit=self.is_Quit_App,
            number_of_snapshot=-1, 
            auto_pop=True, 
            pass_broken=True, 
            delay=0.001
        )
        """
        self.__camera_instance.stream_Start_Thread(
            trigger_pause=self.is_Stream_Active,
            trigger_quit=self.is_Quit_App,
            number_of_snapshot=-1,
            delay=0.001
        )
        """
        self.__camera_instance.stream_Start(
            trigger_pause=self.is_Stream_Active,
            trigger_quit=self.is_Quit_App,
            number_of_snapshot=-1,
            delay=0.001
        )
        """
    
    def camera_Listener(self):
        pass
        """
        if self.__camera_instance is not None and self.is_Camera_Stream_Active:
            self.__camera_instance.stream_Start(
                trigger_pause=self.is_Stream_Active,
                trigger_quit=self.is_Quit_App,
                number_of_snapshot=-1,
                delay=0.001
            )
        """
            
            
    
        """
        self.set_connector_snapshot(camera_object.snapshot)
        self.set_connection_camera_api(camera_object.api_Baumer_Camera_Configurations)
        """
        
    def get_Camera(self, camera_flag=CAMERA_FLAGS.CV2):
        # Engine Class Init Parameters
        return Camera_Object(
            camera_flag=camera_flag,
            auto_configure=True,
            trigger_quit=self.is_Quit_App,
            trigger_pause=self.is_Stream_Active,
            lock_until_done=False,
            acquisition_framerate=15,
            exposure_time=40000,
            max_buffer_limit=1,
            logger_level=self.logger_level
        )
    
    def is_Camera_Active(self):
        return False if self.__camera_instance is None else True
    
    def camera_Remove(self):
        self.__camera_instance.quit()
        return self.is_Camera_Stream_Active

    def is_Stream_Active(self):
        return self.is_Camera_Stream_Active
    
    def stream_Switch(self, bool=None):
        self.is_Camera_Stream_Active = (
            bool
            if bool is None else not self.is_Camera_Stream_Active
        )
        return self.is_Camera_Stream_Active
        
    ### ### ### ### ###
    ### ### ### ### ###
    ### ### ### ### ###
    
    ### ### ### ### ### ### ### ###
    ### ###  EVENT HANDLERS ### ###
    ### ### ### ### ### ### ### ###
    
    def mouseMove_Event_Handler_graphicsView(self, event):
        self.mouse_Positions["mouseMove_graphicsView_Pos"] = event.pos()
        self.mouse_Positions["mouseMove_graphicsView_Pos_To_Scene"] = self.graphicsView_Page_1_Camera.mapToScene(
            self.mouse_Positions["mouseMove_graphicsView_Pos"]
        )
        self.lcdNumber_Set(
            [
                self.lcdNumber_Pointer_X,
                self.lcdNumber_Pointer_Y
            ],
            [
                self.mouse_Positions["mouseMove_graphicsView_Pos_To_Scene"].x(),
                self.mouse_Positions["mouseMove_graphicsView_Pos_To_Scene"].y()
            ]
        )

        qt_color_red, qt_color_green, qt_color_blue = self.get_Color(
            QImage(
                # https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QGraphicsPixmapItem.html#PySide2.QtWidgets.PySide2.QtWidgets.QGraphicsPixmapItem.pixmap
                self.get_Background_Item(
                    self.graphicsView_Page_1_Camera
                ).pixmap()
            ),
            self.mouse_Positions["mouseMove_graphicsView_Pos_To_Scene"].x(),
            self.mouse_Positions["mouseMove_graphicsView_Pos_To_Scene"].y()
        )
        self.lcdNumber_Set(
            [
                self.lcdNumber_Pointer_Color_Red,
                self.lcdNumber_Pointer_Color_Green,
                self.lcdNumber_Pointer_Color_Blue,
                self.lcdNumber_Pointer_Color_Grayscale,
                self.lcdNumber_Pointer_Color_Grayscale_Inverted
            ],
            [
                qt_color_red, 
                qt_color_green, 
                qt_color_blue,
                int((qt_color_red + qt_color_green + qt_color_blue) / 3)
                if qt_color_red + qt_color_green + qt_color_blue != 0
                else 0,
                int(255 - (qt_color_red + qt_color_green + qt_color_blue) / 3)
                if qt_color_red + qt_color_green + qt_color_blue != 0
                else 0
            ]
        )
            
    ### ### ### ### ### ### ### ###
    ### ### ### ### ### ### ### ###
    ### ### ### ### ### ### ### ###

        
### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###
### ### ### ### ### ## ## ## ### ### ### ### ###

if __name__ == "__main__":
    # title, Class_UI, run=True, UI_File_Path= "test.ui", qss_File_Path = ""
    stdo(1, "Running {}...".format(__name__))
    """app, ui = init_and_run_UI(
        "Camera Developer UI",
        Ui_Camera_API_Main,
        UI_File_Path="camera_api_developer_MDI_UI.ui"
    )"""
    app, ui = init_and_run_UI(
        "Camera Developer UI",
        Ui_Camera_API_Developer,
        UI_File_Path="camera_api_developer_UI.ui"
    )
