import requests
from datetime import datetime


def send_wechat_message(message):
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


if __name__ == "__main__":
    # 获取当前时间并格式化为 年-月-日 时:分:秒
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # 生成消息内容
    message = f"{current_time} 电脑正在关机,请查看原因"
    # 发送消息到微信
    send_wechat_message(message)
