from datetime import datetime
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.plugin import on_command, PluginMetadata
from nonebot import get_driver,require

from .config import Config
from .data_source import ContestType, req_get, html_parse_cf, html_parse_nc


__plugin_meta__ = PluginMetadata(
                                name="ACMReminder",
                                description="订阅牛客/CF平台的比赛信息",
                                usage="/contest.list [all/cf/nc] 获取所有/CF/牛客平台的比赛信息"
                                    "/contest.subscribe [cf/nc]-[id] 订阅CF/牛客平台的比赛信息")


contest_list = on_command(("contest","list"), aliases={"比赛列表"}, priority=5)
contest_subscribe = on_command(("contest","subscribe"), aliases={"订阅比赛"}, priority=5)
plugin_config: Config = Config.parse_obj(get_driver().config)
contest_data: list[ContestType] = []

require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler
@scheduler.scheduled_job('interval', minutes=plugin_config.update_time)
async def update_contest():
    """更新比赛信息"""
    global contest_data
    contest_data.clear()
    contest_data.extend(html_parse_cf(await req_get("https://codeforces.com/contests")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13")))

@contest_list.handle()
async def get_list(event: MessageEvent):
    msg = ''
    click = 1
    if contest_data:
        await contest_list.finish("比赛列表为空，请稍后再试")
    for contest in contest_data:
        click+=1
        time = datetime.utcfromtimestamp(contest["time"]).strftime("%Y-%m-%d %H:%M")
        writes = ",".join(contest["writes"]) if len(contest["writes"]) < 5 else ",".join(contest["writes"][:5]) + "..."
        msg += "——————" \
            f"比赛名称：{contest['name']}" \
            f"比赛平台：{contest['platform']}" \
            f"比赛主办：{writes}" \
            f"开赛时间：{time}" \
            f"比赛时长: {contest['length']/60}/h" \
            f"比赛ID：{contest['id']}" \
            f"比赛链接：还没写" 
        if(click%5==0):
            await contest_list.send(msg)
            msg = ''
    if msg:
        await contest_list.finish(msg)