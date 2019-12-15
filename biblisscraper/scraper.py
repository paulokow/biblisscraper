import requests
from datetime import datetime
from lxml import html
from urllib.parse import urljoin

def get_frame_src(session, baseurl, url, framename):
    result = session.get(urljoin(baseurl, url))
    return extract_frame_src(framename, result)


def extract_frame_src(framename, result):
    tree = html.fromstring(result.text)
    return list(set(tree.xpath("//frameset//frame[@name='{}']/@src".format(framename))))[0]

def scrap_biblis_book_lents(account_config: dir):
    with requests.Session() as session:
        # all requests through session now have User-Agent header set
        session.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}

        starturl = 'https://biblis.de/FOR/lissy/lissy.ly?pg=bnrlogin'

        topframeurl = get_frame_src(session, starturl, starturl, 'topeframe')
        rightframeurl = get_frame_src(session, starturl, topframeurl, 'toprighteframe')

        rightframe = session.get(urljoin(starturl, rightframeurl))
        tree = html.fromstring(rightframe.text)

        inputs = list(set(tree.xpath("//form//input[@value]/@name")))
        formparams = dict([(i, str(list(set(tree.xpath("//form//input[@name='{}']/@value".format(i))))[0])) for i in inputs])
        formposturl = str(list(set(tree.xpath("//form[@name='form1']/@action")))[0])
        formparams["bnr"] = account_config["user"]
        formparams["gd"] = account_config["password"]

        loggedin = session.post(urljoin(starturl, formposturl), data=formparams)
        topframeurl = extract_frame_src('topframe', loggedin)
        toplefturl = get_frame_src(session, starturl, topframeurl, 'topleftframe')

        menu = session.get(urljoin(starturl, toplefturl))
        tree = html.fromstring(menu.text)
        itemlisturl = list(tree.xpath("//td//a[img/@alt='Entliehene Medien anzeigen']/@href"))[0]

        tmp = session.get(urljoin(starturl, itemlisturl))
        tree = html.fromstring(tmp.text)
        script = list(tree.xpath("//head/script"))[0].text

        leftmarker = 'window.location.replace("'
        leftcuturl = script[script.find(leftmarker)+len(leftmarker):]
        listurl = leftcuturl[:leftcuturl.find('"')]
        tmp = session.get(urljoin(starturl, listurl))

        tree = html.fromstring(tmp.text)

        rows = list(tree.xpath('//table/tr[td]'))
        itemslist = [
            {
                "account": account_config,
                "name": item.xpath('td[4]')[0].text.replace('\u200b',''),
                "date": datetime.strptime(item.xpath('td[5]')[0].text.replace('\u200b',''), '%d.%m.%Y').date(),
                "remarks": item.xpath('td[6]')[0].text.replace('\u200b','').replace('---',''),
            } for item in rows]

        return itemslist

