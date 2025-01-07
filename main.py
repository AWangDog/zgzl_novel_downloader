from bs4 import BeautifulSoup
import requests, re, time

DEBUG = False

class info:
    class Error:
        def Function(function , info: str, *args):
            """函数报错

            Args:
                function (function): 函数
                info (str): 错误信息
            """
            print(f'Error-function: [{function}]; ARGS: [{args}]; Info: [{info}]')
    class Info:
        def Function(function , info: str, *args):
            """函数信息

            Args:
                function (function): 函数
                info (str): 信息
            """
            print(f'Info-function: [{function}]; ARGS: [{args}]; Info: [{info}]')

def get_web_html(url: str, debug = False) -> str: # 获取网页HTML
    """获取网页HTML

    Args:
        url (str): 网页网址
        debug (bool, optional): debug模式. Defaults to False.

    Returns:
        str: 返回的HTML
    """
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'
        if response.status_code!= 200:
            if debug is True or DEBUG is True:
                info.Error.Function(get_web_html, response.status_code, url)
            return None
        return response.text
    except Exception as e:
        if debug is True or DEBUG is True:
            info.Error.Function(get_web_html, e, url)
        return None

def get_novel_html(novel_url: str) -> str: # 获取小说主页
    """获取小说主页

    Args:
        novel_url (str): 小说主页URL

    Returns:
        str: 小说主页html
    """
    novel_test = None
    while novel_test is None:
        novel_test = get_web_html(novel_url)
        if novel_test is None:
            print('获取小说主页错误, 重试中...')
            time.sleep(3)
    return novel_test
    
def get_chapter_list(novel_test: str, debug = False) -> dict: # 获取章节列表
    """获取章节列表

    Args:
        novel_test (str): 小说主页
        debug (bool, optional): debug模式. Defaults to False.

    Returns:
        dict: 章节字典
    """

    try:
        soup = BeautifulSoup(novel_test, 'html.parser')
        ul_tags = soup.find_all('ul', class_='p2')
        second_ul = ul_tags[1]
        chapter_list = {}
        for url in second_ul.find_all('a'):
            chapter_url = f"{DOMAIN}{url['href']}"
            chapter_name = url.text
            chapter_list[chapter_name] = chapter_url
        return chapter_list
    except Exception as e:
        if debug is True or DEBUG is True:
            info.Error.Function(get_chapter_list, e, novel_test)
        return None
    
def get_novel_title(novel_test: str, debug = False) -> str: # 获取小说名
    """获取小说名

    Args:
        novel_test (str): 小说主页
        debug (bool, optional): debug模式. Defaults to False.

    Returns:
        str: 小说名
    """
    try:
        soup = BeautifulSoup(novel_test, 'html.parser')
        title = soup.find('div', class_ = 'catalog1').find('h1').text
        return title
    except Exception as e:
        if debug is True or DEBUG is True:
            info.Error.Function(get_novel_title, e, novel_test)
        return None

def get_page(page_text: str, debug = False) -> tuple[str, str, str]: # 获取页面文本
    """获取页面文本

    Args:
        page_text (str): 页面HTML
        debug (bool, optional): debug模式. Defaults to False.

    Returns:
        tuple[str, str, str]: 章节标题, 章节正文, 下一页URL
    """
    try:
        soup = BeautifulSoup(page_text, 'html.parser')
        try:
            next_page = soup.find('a', class_ = 'p4')['href']
        except:
            next_page = None
        next_page = f"{DOMAIN}{next_page}"
        title = soup.find('div', class_ = 'nr_function').find('h1').text
        title = clear_title(title)
        text = soup.find('div', id = 'novelcontent', class_ = 'novelcontent')
        text = text.get_text(strip = True, separator = '\n')
        text = clear_text(text)
        return title, text, next_page
    except Exception as e:
        if debug is True or DEBUG is True:
            info.Error.Function(get_page, e, page_text)
        return None

def clear_text(text: str) -> str: # 清理小说正文
    """清理小说正文

    Args:
        text (str): 原文本

    Returns:
        str: 清理后的文本
    """
    text = text.replace('《关闭小说畅读模式体验更好》\n', '')
    text = text.replace('\n内容未完，下一页继续阅读', '')
    text = re.sub(r"\n【本章阅读完毕，更多请搜索.*;.* 阅读更多精彩小说】", "", text)
    return text

def clear_title(title: str) -> str: # 清理小说标题
    """清理小说标题

    Args:
        title (str): 原标题

    Returns:
        str: 清理后的标题
    """
    title = re.sub(r"\s*\([^)]*\)$", "", title)
    return title

NOVEL_URL = 'https://m.zgzl.net/info_5s6/'
DOMAIN = NOVEL_URL[:NOVEL_URL.find('/', NOVEL_URL.find('//') + 2)]
print('获取小说主页中...')
NOVEL_HTML = get_novel_html(NOVEL_URL)
print('小说主页获取成功/ 开始获取章节列表...')
CHAPTER_LIST = get_chapter_list(NOVEL_HTML)
print('章节列表获取成功/ 开始获取小说名...')
NOVEL_TITLE = get_novel_title(NOVEL_HTML)
CHAPTER_NUM = len(CHAPTER_LIST) - 1
LATEST_CHAPTER = list(CHAPTER_LIST.values())[0]
print(f'小说名: {NOVEL_TITLE}, 开始下载第1/{CHAPTER_NUM}章: {list(CHAPTER_LIST.keys())[0]}')

def main(debug = False):
    over = False
    next_page = LATEST_CHAPTER
    page_title = ''
    chapter = 0
    page_num = 0
    num = 0
    with open(f'{NOVEL_TITLE}.txt', 'w', encoding='utf-8') as f:
        while over is False:
            if next_page == NOVEL_URL:
                over = True
                break
            page_html = None
            while page_html is None:
                page_html = get_web_html(next_page)
                if page_html is None:
                    if DEBUG is True or debug is True:
                        info.Error.Function(main, f'Error - 章节: {page_title}, 第{page_num}页获取失败, 重试中')
                    else:
                        print(f'Error - 章节: {page_title}, 第{page_num}页获取失败, 重试中')
                    time.sleep(3)
            page = get_page(page_html)
            if page_title == '':
                page_title = page[0]
                chapter += 1
                f.write(page_title + '\n')
            elif page_title != page[0]:
                page_title = page[0]
                page_num = 0
                chapter += 1
                f.write('\n' + page_title + '\n')
            f.write(page[1] + '\n')
            next_page = page[2]
            num += 1
            page_num += 1
            print(f'Info - 第{chapter}/{CHAPTER_NUM}章: {page_title}, 第{page_num}页, 总第{num}页')
    print(f'下载完成, 共{chapter}/{CHAPTER_NUM}章, {num}页')

if __name__ == '__main__':
    main()