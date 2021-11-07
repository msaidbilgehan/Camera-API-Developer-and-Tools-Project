import libs
from structure_ui import init_and_run_UI
from constructor_ui import Ui_Camera_API_Main


if __name__ == "__main__":
    app, ui = init_and_run_UI(
        "Camera Developer UI",
        Ui_Camera_API_Main,
        UI_File_Path="camera_api_developer_MDI_UI.ui"
    )
