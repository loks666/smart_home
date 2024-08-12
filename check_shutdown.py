import win32serviceutil
import win32service
import win32event
import servicemanager
import requests
from datetime import datetime


class StartupShutdownMonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "开关机监控服务"  # 服务名称
    _svc_display_name_ = "系统开关机监控服务"  # 服务显示名称
    _svc_description_ = "监控系统启动和关机，并发送微信消息。"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.isrunning = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.isrunning = False

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, "")
        )
        self.send_startup_message()
        self.main()

    def send_wechat_message(self, message):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=d2e8a0eb-64e9-473f-9827-17b727071386'
        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print("消息发送成功")
        else:
            print(f"消息发送失败，状态码: {response.status_code}, 响应: {response.text}")

    def send_startup_message(self):
        # 在服务启动时发送开机消息
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        startup_message = f"{current_time} 电脑已开机"
        self.send_wechat_message(startup_message)

    def main(self):
        # 监控关机
        while self.isrunning:
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if rc == win32event.WAIT_OBJECT_0:
                # 系统正在关闭或服务停止，发送关机消息
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                shutdown_message = f"{current_time} 电脑正在关机，请查看原因"
                self.send_wechat_message(shutdown_message)
                break


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(StartupShutdownMonitorService)
