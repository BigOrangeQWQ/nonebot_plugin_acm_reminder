from datetime import datetime
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment, Message
from nonebot.plugin import on_command, PluginMetadata
from nonebot.params import CommandArg
from nonebot import get_driver, require, logger

require("nonebot_plugin_apscheduler")
require("nonebot_plugin_htmlrender")
from nonebot_plugin_apscheduler import scheduler
from nonebot_plugin_htmlrender import md_to_pic

from .data_source import ContestType, req_get, html_parse_cf, html_parse_nc
from .config import Config

__plugin_meta__ = PluginMetadata(
    name="ACMReminder",
    description="订阅牛客/CF平台的比赛信息",
    usage="/contest.list 获取所有/CF/牛客平台的比赛信息"
    "/contest.subscribe 订阅CF/牛客平台的比赛信息")

contest_list = on_command(("contest", "list"), aliases={"比赛列表"}, priority=5)
contest_subscribe = on_command(
    ("contest", "subscribe"), aliases={"订阅比赛"}, priority=5)

driver = get_driver()
contest_data: list[ContestType] = []
plugin_config: Config = Config.parse_obj(driver.config)


async def update():
    """
    更新比赛信息
    """
    global contest_data
    contest_data.clear()
    contest_data.extend(html_parse_cf(await req_get("https://codeforces.com/contests")))
    contest_data.extend(html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=13")))


@scheduler.scheduled_job('interval', minutes=plugin_config.update_time, id="update_contest")
async def update_contest():
    try:
        await update()
    except Exception as e:
        logger.warning("ACMReminder拉取竞赛数据失败")
        logger.warning("请检查网络连接或者稍后重试")
        logger.warning(e)

@driver.on_startup
async def startup():
    try:
        await update()
    except Exception as e:
        logger.warning("ACMReminder拉取竞赛数据失败")
        logger.warning("请检查网络连接或者稍后重试")
        logger.warning(e)
    # 防止因为网络问题导致机器人启动失败


@contest_list.handle()
async def get_list(event: MessageEvent, args: Message = CommandArg()):
    msg = '<div align="center">\n <h1> 近期竞赛 </h1> \n</div>'
    for contest in contest_data:
        time = datetime.utcfromtimestamp(
            contest["time"]).strftime("%Y-%m-%d %H:%M")
        writes = ",".join(filter(None, contest["writes"])) if len(
            contest["writes"]) < 5 else ",".join(filter(None, contest["writes"][:5])) + "..."
        msg += f"## {contest['name']}\n" \
            f"* 竞赛平台  **{contest['platform']}**\n" \
            f"* 举办人员 {writes}\n" \
            f"* 开始时间 **{time}**\n" \
            f"* 竞赛时长 **{contest['length']/60}h**\n"
    await contest_list.finish(MessageSegment.image(await md_to_pic(msg)))
