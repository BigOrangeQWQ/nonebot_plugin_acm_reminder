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

async def update():
    global contest_data
    contest_data.clear()
    contest_data.extend(html_parse_cf(await req_get("https://codeforces.com/contests")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13")))
    print(contest_list)

@scheduler.scheduled_job('interval', minutes=plugin_config.update_time, id="update_contest")
async def update_contest():
    await update()

@get_driver().on_startup
async def startup():
    await update()

@contest_list.handle()
async def get_list(event: MessageEvent):
    msg = ''
    click = 1
    for contest in contest_data:
        click+=1
        time = datetime.utcfromtimestamp(contest["time"]).strftime("%Y-%m-%d %H:%M")
        writes = ",".join(filter(None,contest["writes"])) if len(contest["writes"]) < 5 else ",".join(filter(None,contest["writes"][:5])) + "..."
        msg += "——————\n" \
            f"名称：{contest['name']}\n" \
            f"平台：{contest['platform']}\n" \
            f"主办：{writes}\n" \
            f"开时：{time}\n" \
            f"时长: {contest['length']/60} h\n"
        await contest_list.send(msg)