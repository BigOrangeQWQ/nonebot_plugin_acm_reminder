from json import loads
from time import strptime, mktime
from html import unescape
from typing import Literal, Optional, TypedDict, List, Dict
from httpx import AsyncClient
from httpx._types import URLTypes, ProxiesTypes
from bs4 import BeautifulSoup, ResultSet

class ContestType(TypedDict):
    id: int  # 竞赛ID
    name: str  # 竞赛名称
    writes: List[str]  # 竞赛主办方
    length: int  # 竞赛时长 [分钟]
    time: float  # 竞赛开始时间戳
    platform: Literal["Codeforces", "Nowcoder"]  # 竞赛平台


async def req_get(url: URLTypes, proxies: Optional[ProxiesTypes] = None) -> str:
    """
    生成一个异步的GET请求

    Args:
        url (URLTypes): 对应的URL

    Returns:
        str: URL对应的HTML
    """
    async with AsyncClient(proxies=proxies) as client:
        r = await client.get(url)
    return r.content.decode("utf-8")

def html_parse_cf(content: str) -> List[ContestType]:
    """
    处理Codeforces的竞赛列表

    Args:
        content (str): HTML

    Returns:
        list: 竞赛列表
    """
    contest_data: List[ContestType] = []
    
    soup = BeautifulSoup(content, 'html.parser')
    datatable = soup.find('div', class_='datatable')  # 获取到数据表
    if datatable is None:
        return contest_data

    # 解析竞赛信息
    contest_list = datatable.find_all("tr")  # type: ignore
    for contest in contest_list:
        cdata = contest.find_all("td")
        if cdata:
            cwriters = [i.string for i in cdata[1].find_all("a")] #获得主办方
            ctime = mktime(strptime(cdata[2].find("span").string, "%b/%d/%Y %H:%M")) #获得开始时间戳
            ctime+=5*60*60
            clength = strptime(str(cdata[3].string).strip("\n").strip(), "%H:%M")
            contest_data.append({"name": str(cdata[0].string).strip("\n").strip(), 
                                "writes": cwriters, 
                                "time": ctime, 
                                "length": clength.tm_hour * 60 + clength.tm_min, 
                                "platform": "Codeforces", 
                                "id": contest.get("data-contestid")})
    return contest_data

def html_parse_nc(content: str) -> List[ContestType]:
    """
    处理牛客的竞赛列表 

    Args:
        content (str): HTML

    Returns:
        list: 竞赛列表
    """
    contest_data: List[ContestType] = []
    soup = BeautifulSoup(content, 'html.parser')
    datatable: ResultSet = soup.find('div', class_='platform-mod js-current').find_all('div', class_='platform-item js-item') #type: ignore
    for contest in datatable:
        cdata = loads(unescape(contest.get("data-json")))
        if cdata:
            contest_data.append({"name": cdata["contestName"], 
                                "writes": [cdata["settingInfo"]["organizerName"]], 
                                "time":  cdata["contestStartTime"] / 1000, 
                                "length": cdata["contestDuration"] / 1000 / 60, 
                                "platform": "Nowcoder", 
                                "id": cdata["contestId"]})
    return contest_data

# import asyncio

# async def update():
#     """
#     更新比赛信息
#     """
    
#     a = html_parse_cf(await req_get("https://codeforces.com/contests"))
#     b = html_parse_nc(await req_get("https://ac.nowcoder.com/acm/contest/vip-index?topCategoryFilter=14"))
#     print(a,b)
    
# asyncio.run(update())
