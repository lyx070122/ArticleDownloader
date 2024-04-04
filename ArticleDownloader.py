import requests
from bs4 import BeautifulSoup
from urllib import parse
#import time
from contextlib import closing
import re
from rich.progress import Progress
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    TransferSpeedColumn
)


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
}
url_xmol = "https://www.x-mol.com/zd?option="
url_scidl = "https://sci.bban.top/pdf/"
url_scihub = "https://www.sci-hub.wf/"
url_bing = "https://cn.bing.com/search?q="

process = {
    "color": "[red]",
    "content": (
        "初始化",
        "调用x-mol",
        "解析原文献链接",
        "获取文献标题",
        "调用sci-hub",
    )
}


def down_load(file_url: str, file_path: str):
    # start_time = time.time()  # 文件开始下载时的时间
    with closing(requests.get(file_url, stream=True, headers=headers)) as response:
        chunk_size = 1024  # 单次请求最大值
        content_size = int(response.headers.get("Content-Length"))  # 内容体总大小
        data_count = 0
        description = "[red]Downloading"
        progress = Progress(
            "   [progress.description]{task.description}",
            # SpinnerColumn(finished_text="[green]√"),
            BarColumn(),
            # "[progress.percentage]{task.percentage:>3.2f}%",
            DownloadColumn(),
            TransferSpeedColumn(),
            "[yellow]已用时间:",
            TimeElapsedColumn(),
            "[cyan]预计剩余时间:",
            TimeRemainingColumn()
        )
        task = progress.add_task(description, total=content_size)
        with progress:
            with open(file_path, "wb") as file:
                for data in response.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    data_count = data_count + len(data)
                    #now_jd = (data_count / content_size) * 100
                    #speed = data_count / 1024 / (time.time() - start_time)
                    progress.update(
                        task, description=description, completed=data_count)
                    # print("\r 文件下载进度：%d%%(%d/%d) 文件下载速度：%dKB/s - %s"
                    #      % (now_jd, data_count, content_size, speed, file_path), end=" ")


def jump_process(iniurl: str):
    if iniurl.startswith("http://xlink.rsc.org/"):
        return requests.get(url=iniurl.replace("http", "https"), headers=headers, allow_redirects=False).headers.get("Location")

    return iniurl


def test(t):
    with open("t.html", "w", encoding="utf-8") as f:
        f.write(t)


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    return new_title


def main():
    s = input("[Progress] input data > ")
    with Progress("[progress.description]{task.description}", BarColumn(), "{task.completed}/{task.total}") as progress:

        task = progress.add_task(
            process["color"]+process["content"][0], total=len(process["content"])-1)
        #s = "Acc. Chem. Res. 2009, 42, 1, 183–191"
        progress.update(task, completed=1,
                        description=process["color"]+process["content"][1])
        r = requests.get(url=url_xmol + parse.quote(s), headers=headers)

        progress.update(task, completed=2,
                        description=process["color"]+process["content"][2])
        # print(r.headers.get("Location"))
        # with open('t.html', 'r', encoding='utf-8') as f:
        xmolpage = BeautifulSoup(r.text, 'lxml')

        tar = xmolpage.find_all("input")[1]["value"]
        #
        # print(jump_process(tar))
        tar = jump_process(tar)
        # print(tar)
        progress.update(task, completed=3,
                        description=process["color"]+process["content"][3])
        b = requests.get(url=url_scihub + tar, headers=headers)
        # with open('test.html', 'w', encoding='utf-8') as f:
        #    f.write(b.text)
        scihubpage = BeautifulSoup(b.text, 'lxml')
        title = str(scihubpage.find_all("title")[0]).split(" | ")
        #print(title[1], tar)
        doi = title[-1][:-8]
        # print(doi)
        fileUrl = url_scidl + doi + ".pdf"  # 文件链接
        # print(fileUrl)
        filePath = validateTitle(title[1]) + ".pdf"  # 文件路径
        progress.update(task, completed=4,
                        description=process["color"]+process["content"][4])
    down_load(fileUrl, filePath)


if __name__ == '__main__':
    main()
