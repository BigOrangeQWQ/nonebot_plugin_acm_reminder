from json import loads
from time import strptime, mktime, struct_time
from html import unescape
from typing import Any, Dict, Literal, Optional, TypedDict, List, Union
from httpx import AsyncClient, Response
from httpx._types import URLTypes, ProxiesTypes
from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag

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
        r: Response = await client.get(url)
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
    datatable: Union[Tag,NavigableString,None] = soup.find('div', class_='datatable')  # 获取到数据表
    if not isinstance(datatable,Tag):
        return contest_data

    # 解析竞赛信息
    contest_list: ResultSet[Any] = datatable.find_all("tr") 
    for contest in contest_list:
        cdata: ResultSet[Any] = contest.find_all("td")
        if cdata:
            cwriters: List[str] = [i.string for i in cdata[1].find_all("a")] #获得主办方
            ctime: float = mktime(strptime(cdata[2].find("span").string, "%b/%d/%Y %H:%M")) #获得开始时间戳
            ctime+=5*60*60
            try:
                clength: struct_time = strptime(str(cdata[3].string).strip("\n").strip(), "%H:%M")
            except:
                clength: struct_time = strptime(str(cdata[3].string).strip("\n").strip(), "%H:%M:%S")
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
    find_item: Union[Tag,NavigableString,None] = soup.find('div', class_='platform-mod js-current')
    if not isinstance(find_item, Tag):
        return contest_data
    datatable: ResultSet = find_item.find_all('div', class_='platform-item js-item')
    for contest in datatable:
        cdata: Dict[str, Any] = loads(unescape(contest.get("data-json")))
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
