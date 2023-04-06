from datetime import datetime
from typing import List
from httpx import URL
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.plugin import on_command, PluginMetadata
from nonebot import get_driver, require


from .config import Config
from .data_source import ContestType, req_get, html_parse_cf, html_parse_nc

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_htmlrender import md_to_pic
from nonebot_plugin_apscheduler import scheduler


__plugin_meta__ = PluginMetadata(
    name="ACMReminder",
    description="订阅牛客/CF平台的比赛信息",
    usage=
    "/contest.list 获取所有/CF/牛客平台的比赛信息"
    "/contest.subscribe 订阅CF/牛客平台的比赛信息"
    "/contest.update 手动更新比赛信息")

contest_list = on_command(("contest", "list"), aliases={"比赛列表"}, priority=5)
contest_update = on_command(("contest", "update"),
                            aliases={"更新比赛"}, priority=5)
contest_subscribe = on_command(
    ("contest", "subscribe"), aliases={"订阅比赛"}, priority=5)

driver = get_driver()
contest_data: List[ContestType] = []
plugin_config: Config = Config.parse_obj(driver.config)


async def update():
    """
    更新比赛信息
    """
    contest_data.clear()
    contest_data.extend(html_parse_cf(await req_get("https://codeforces.com/contests")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=14")))


@scheduler.scheduled_job('interval', minutes=plugin_config.update_time, id="update_contest")
async def update_contest():
    await update()


@driver.on_startup
async def startup():
    await update()
    # 防止因为网络问题导致机器人启动失败


@contest_update.handle()
async def update_handle(event: MessageEvent):
    try:
        await update()
    except Exception as e:
        await contest_update.finish(MessageSegment.image(await md_to_pic(f"更新失败 {e}")))

    await contest_update.finish("更新成功")


@contest_list.handle()
async def get_list(event: MessageEvent):
    msg = '<div align="center">\n <h1> 近期竞赛 </h1> \n</div>'
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
    await contest_list.finish(MessageSegment.image(await md_to_pic(msg)))
