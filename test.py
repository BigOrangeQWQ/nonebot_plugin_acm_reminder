from nonebot import init, load_plugin

init(driver="~none")
valid = load_plugin("nonebot_plugin_acm_reminder")
if not valid:
    exit(1)
else:
    exit(0)