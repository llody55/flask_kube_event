'''
Author: 745719408@qq.com 745719408@qq.com
Date: 2023-10-24 15:20:40
LastEditors: 745719408@qq.com 745719408@qq.com
LastEditTime: 2023-10-26 10:37:36
FilePath: \K8S\组件包\公网IP部署K8S\钉钉事件通知\flask_kube_event\app.py
Description: 基于flask的事件获取脚本
'''
from flask import Flask, jsonify
from email.policy import default
from unicodedata import name
from kubernetes import client,config
import  yaml,pymysql,json
import threading
import time
import requests
import pytz
from datetime import datetime, timedelta

app = Flask(__name__)

# 初始化事件数据
event_data = []

# 在全局变量中维护事件计数器
event_counter = 0

# # 配置 Kubernetes 客户端
# config.load_incluster_config()  # 如果在集群内部运行，请使用此选项
# 企业微信 Webhook URL
webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="

conn = pymysql.connect(
    host='',
    user='',
    db='',
    passwd='',
    port=3306,
    autocommit=True

)

cursor = conn.cursor()
sql1 = "SELECT content FROM myapp_auth WHERE token=8456061014422884;"
cursor.execute(sql1)
res = cursor.fetchall()

# 从数据库中获取 kubeconfig 数据
kubeconfig_tuple = res[0]

# 解包元组并将 kubeconfig 数据转换为字符串
kubeconfig_str = kubeconfig_tuple[0]

# 将 kubeconfig 字符串解析为 Python 字典
kubeconfig_dict = yaml.safe_load(kubeconfig_str)

# 使用 config.kube_config.load_kube_config 加载 kubeconfig 数据
config.kube_config.load_kube_config_from_dict(kubeconfig_dict)

def get_events_thread():
    while True:
        v1 = client.CoreV1Api()
        
        # 获取当前时间，带有 UTC 时区信息
        current_time = datetime.now(pytz.utc)
        # 计算5分钟前的时间戳
        five_minutes_ago = current_time - timedelta(minutes=5)
        
        events = v1.list_event_for_all_namespaces()
        warning_events = []

        for event in events.items:
            #print("事件信息:",event)
            # 检查是否为 Warning 事件并时间戳是否在5分钟内
            if event.type == "Warning" and event.last_timestamp >= five_minutes_ago:
                warning_events.append(event)
        
        # 按时间戳逆序排序 Warning 事件
        warning_events.sort(key=lambda x: x.last_timestamp, reverse=True)
        
        # 增加事件计数
        global event_counter
        event_counter += len(warning_events)
        
        # 处理 Warning 事件并推送到企业微信
        push_events_to_wechat(warning_events)
        
        time.sleep(5)  # 暂停5秒再次获取事件

# 获取所有事件，并用json打印出来
# def get_events_thread():
#     global event_data  # 声明全局变量
#     while True:
#         v1 = client.CoreV1Api()
#         # 计算5分钟前的时间戳
#         five_minutes_ago = datetime.now() - timedelta(minutes=5)

#         events = v1.list_event_for_all_namespaces()
#         event_list = []
#         for event in events.items:
#             #print(event)
#             event_data = {
#                 "namespace": event.metadata.namespace,
#                 "name": event.metadata.name,
#                 "reason": event.reason,
#                 "message": event.message,
#                 "timestamp": event.last_timestamp,
#                 "type": event.type,
#             }
#             event_list.append(event_data)
        
#         # 更新事件数据
#         event_data = event_list
#         time.sleep(5)  # 暂停5秒再次获取事件

def push_events_to_wechat(events):
    for event in events:
        # 添加一个8小时的时差
        event_time = event.last_timestamp + timedelta(hours=8)
        message = f"事件时间: {event_time}\n" \
                  f"事件节点: {event.source.host}\n" \
                  f"事件命名空间: {event.metadata.namespace}\n" \
                  f"事件Pod: {event.involved_object.name}\n" \
                  f"事件级别: {event.type}\n" \
                  f"事件原因: {event.reason}\n" \
                  f"事件消息: {event.message}"

        data = {
            "msgtype": "text",
            "text": {
                "content": message
            }
        }

        response = requests.post(webhook_url, json=data)
        if response.status_code == 200:
            print("事件信息已成功推送到企业微信")
        else:
            print("事件信息推送失败")

# 启动获取事件信息的线程
event_thread = threading.Thread(target=get_events_thread)
event_thread.daemon = True
event_thread.start()

@app.route('/events', methods=['GET'])
def get_events():
    global event_counter
    return jsonify({
        "event_info": event_data,
        "event_count": event_counter
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


