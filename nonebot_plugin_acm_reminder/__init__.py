from datetime import datetime
from email.mime import application
from turtle import home
from typing import List
from nonebot.adapters import Event
from nonebot.plugin import on_command, PluginMetadata
from nonebot import get_driver, logger, require, get_plugin_config


from .config import Config
from .data_source import ContestType, html_parse_at, req_get, html_parse_cf, html_parse_nc

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
require("nonebot_plugin_alconna")
from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_alconna import UniMessage, on_alconna


__plugin_meta__ = PluginMetadata(
    name="ACMReminder",
    description="订阅牛客/CF/AT平台的比赛信息",
    usage=
    "/contest.list 获取所有/CF/牛客/AT平台的比赛信息\n"
    "/contest.subscribe 订阅CF/牛客/AT平台的比赛信息\n"
    "/contest.update 手动更新比赛信息\n",
    supported_adapters=None,
    config=Config,
    type="application",
    homepage="https://github.com/BigOrangeQWQ/nonebot_plugin_acm_reminder",
    )

contest_list = on_command(("contest", "list"), aliases={"比赛列表"}, priority=5)
contest_update = on_command(("contest", "update"),
                            aliases={"更新比赛"}, priority=5)
contest_subscribe = on_command(
    ("contest", "subscribe"), aliases={"订阅比赛"}, priority=5)

driver = get_driver()
contest_data: List[ContestType] = []
plugin_config: Config = get_plugin_config(Config)


async def update():
    """
    更新比赛信息
    """
    contest_data.clear()
    contest_data.extend(html_parse_cf(await req_get("https://codeforces.com/contests")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=14")))
    contest_data.extend(html_parse_at(await req_get("https://atcoder.jp")))

@scheduler.scheduled_job('interval', minutes=plugin_config.update_time, id="update_contest")
async def update_contest():
    try:
        await update()
    except Exception as e:
        logger.warning("拉取竞赛信息更新失败!")
        logger.warning(e)


@driver.on_startup
async def startup():
    try:
        await update()
    except Exception as e:
        logger.warning("拉取竞赛信息更新失败!")
        logger.warning(e)
    # 防止因为网络问题导致机器人启动失败


@contest_update.handle()
async def update_handle(event: Event):
    try:
        await update()
    except Exception as e:
        logger.warning("拉取竞赛信息更新失败!")
        logger.warning(e)
        await contest_update.finish("更新失败")
    await contest_update.finish("更新成功")


@contest_list.handle()
async def get_list(event: Event):
    msg = '<div align="center">\n <h1> 近期竞赛 </h1> \n</div>'
    # contest_data.sort()
    for contest in contest_data:
        time = datetime.fromtimestamp(
            contest["time"]).strftime("%Y-%m-%d %H:%M")
        writes = ",".join(filter(None, contest["writes"])) if len(
            contest["writes"]) < 5 else ",".join(filter(None, contest["writes"][:5])) + "..."
        msg += f"## {contest['name']}\n" \
            f"* 竞赛平台  **{contest['platform']}**\n" \
            f"* 举办人员 {writes}\n" \
            f"* 开始时间 **{time}**\n" \
            f"* 竞赛时长 **{contest['length']/60}h**\n"
    await UniMessage.image(raw=await md_to_pic(msg)).send()
