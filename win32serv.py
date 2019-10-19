import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import main as main_app
import sys


class CameraAppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "DDONG CAM Monitor"
    _svc_display_name_ = "DDONG CAM Monitor Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        self.main()

    def main(self):
        main_app.app.run(host='0.0.0.0',port=5000, threaded=True)


if __name__ == '__main__':
    #win32serviceutil.HandleCommandLine(AppServerSvc)
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(CameraAppServerSvc)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(CameraAppServerSvc)
    
