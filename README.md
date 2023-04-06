<div align="center">

# ACMReminder

一款可查询与订阅牛客/CF竞赛的插件

<a href="https://pypi.python.org/pypi/nonebot-plugin-acm-reminder">
    <img src="https://img.shields.io/pypi/dm/nonebot-plugin-acm-reminder?style=for-the-badge" alt="Download">
</a>

</div>

## 安装

```
pip install nonebot-plugin-acm-reminder
nb plugin install nonebot-plugin-acm-reminder
```

## 配置项

* 拉取竞赛列表的更新时间(分钟)
```
update_time = 720

proxies = "" 
#可为Proxy or URL
```

## 用法

```
/ := [命令起始符]
. := [命令分隔符]

/contest.list 拉取竞赛列表
/contest.update 更新竞赛列表
```

## TODO

- [x] 获取竞赛信息并形成列表
- [x] 支持CodeForces平台
- [x] 支持牛客平台
- [ ] 订阅指定竞赛，并提醒
- [ ] 可通过指令获取竞赛链接
- [ ] 支持力扣平台