<div align="center">
# ACM Reminder

一款可查询与订阅牛客/CF竞赛的插件
<a href="https://pypi.python.org/pypi/nonebot-plugin-orangedice">
    <img src="https://img.shields.io/pypi/dm/nonebot-plugin-orangedice?style=for-the-badge" alt="Download">
</a>

</div>

## 安装

```
pip install nonebot-plugin-acm-reminder
nb plugin install nonebot-plugin-acm-reminder
```

## 配置项

* 拉取竞赛列表的更新时间
```
update_time = 360
```

## 用法

```
/ := [命令起始符]
. := [命令分隔符]

/contest.list 拉取竞赛列表
```

## TODO

- [ ] 订阅指定竞赛，并提醒
- [x] 获取竞赛信息并形成列表
- [ ] 可通过指令获取竞赛链接
- [ ] 支持洛谷平台
- [x] 支持CodeForces平台
- [ ] 支持力扣平台
- [x] 支持牛客平台