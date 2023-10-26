# flask_kube_event

python连接kubernetes获取Warning事件并通过webhook向企业微信机器人推送消息

## 说明

> 这个脚本分为四个部分：
>
> 1、从数据库中查询出kubernetes apiserver的kubeconfig信息。
>
> 2、连接并获取当前5分钟内发生的事件信息。
>
> 3、通过webhook将消息推送给支持webhook的任何接收器，如：微信，钉钉等。
>
> 4、访问/events可以查看到当前发生中的事件信息，并做了一个简单统计。（PS：待优化扩展）

## 连接部分

### 本地部分

启用如下代码

```
# 配置 Kubernetes 客户端
config.load_incluster_config()  # 如果在集群内部运行，请使用此选项
```

注释如下代码

```
# 此部分代码用于解析数据库中的kubeconfig
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
```


## 运行方法

```
# 环境
python3.7.5+

# 安装依赖
pip install -r requirements.txt

# 运行
python3 app.py
```

## 效果
