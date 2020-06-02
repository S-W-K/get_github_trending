# -*- coding: utf-8 -*-
# @Author: S_W_K

import requests
from requests.adapters import HTTPAdapter
from lxml import etree
from fake_useragent import UserAgent


UA = UserAgent()


def retry_get_none(func):
    # wrapper of get_infos(), if get_infos() fails more than three times,
    # break the loop and return infos as None
    def wrapper(*args, **kw):
        infos = func(*args, **kw)

        retry_cnt = 0
        while len(infos) == 0:
            if retry_cnt == 3:
                infos = None
                break
            infos = func(*args, **kw)
            retry_cnt += 1
        return infos
    return wrapper


@retry_get_none
def get_infos(url, xpath):
    with requests.Session() as session:
        session.mount('https://', HTTPAdapter(max_retries=3))
        response = session.get(
            url, headers={'User-Agent': UA.random}, timeout=5)
    html = etree.HTML(response.text)
    infos = html.xpath(xpath)
    return infos


def scrape_github(since_when, language=''):
    url = 'https://github.com/trending/%s?since=%s' % (language, since_when)
    repo_infos = get_infos(
        url, '/html/body/div[4]/main/div[3]/div/div[2]/article')

    for info in repo_infos:
        repo_url = info.xpath('.//h1/a/@href')[0]
        repo_name = repo_url[1:]
        prefix = 'https://github.com'
        repo_url = prefix+repo_url

        repo_description = info.xpath('string(./p)').strip()
        if len(repo_description) == 0:
            repo_description = 'No repo_description'

        yield repo_name, repo_url, repo_description


def scrape_medium():
    url = 'https://medium.com/topic/popular'
    with requests.Session() as session:
        session.mount('https://', HTTPAdapter(max_retries=3))
        response = session.get(
            url, headers={'User-Agent': UA.random}, timeout=5)

    article_titles = []
    article_urls = []
    article_descriptions = []

    the_first = get_infos(
        url, '//*[@id="root"]/div/div[4]/div/div/div[1]/div[3]/div/div[3]/div')
    if the_first == None:
        return None
    the_first = the_first[0]

    first_title = the_first.xpath('string(./h1/a)')
    first_url = the_first.xpath('./h1/a/@href')[0]
    if first_url[:5] != 'https':
        first_url = 'https://medium.com'+first_url
    first_descrp = the_first.xpath('string(./div/h3/a)').strip()
    article_titles.append(first_title)
    article_urls.append(first_url)
    article_descriptions.append(first_descrp)

    the_rest = get_infos(
        url, '//*[@id="root"]/div/div[4]/div/div/div[1]/div[4]/div[1]/section')
    for r in the_rest:
        r_title = r.xpath('string(./div/section/div[1]/div[1]/div[1]/h3/a)')
        r_url = r.xpath('./div/section/div[1]/div[1]/div[1]/h3/a/@href')[0]
        if r_url[:5] != 'https':
            r_url = 'https://medium.com'+r_url
        r_descrp = r.xpath(
            'string(./div/section/div[1]/div[1]/div[1]/div/h3/a)').strip()
        article_titles.append(r_title)
        article_urls.append(r_url)
        article_descriptions.append(r_descrp)

    return article_titles, article_urls, article_descriptions


if __name__ == '__main__':
    with open('Blog/source/trending/index.md', 'w') as f:
        # front_matter and beginning
        front_matter = '---\ntitle: Trending\ncomments: false\nno_toc: true\n---\n'
        f.write(front_matter)
        f.write('\n')
        f.write(
            '> Scraped from [GitHub](https://github.com/trending), [Medium](https://medium.com/topic/popular)\n')
        f.write('Auto-deployed with [Travis Ci](https://travis-ci.org/)')
        f.write('\n\n')

        f.write('{% tabs TAB %}\n')

        # ------------------ GitHub Tab ------------------------------------
        f.write('<!-- tab GitHub -->\n')

        # ---------- GitHub Subtab ---------------
        f.write('{% subtabs GitHub Tab%}\n')
        # daily
        f.write('<!-- tab Daily -->\n')
        repo_infos = scrape_github('daily')
        # if crawler can't get any info, print modify request
        try:
            for index, (name, url, descp) in enumerate(repo_infos):
                f.write('%d. [**%s**](%s)\n' % (index+1, name, url))
                f.write('%s\n' % descp)
        except TypeError:
            f.write(
                'The crawler crashed, please contact the administrator to modify.\n')
        f.write('<!-- endtab -->\n')

        # weekly
        f.write('<!-- tab Weekly -->\n')
        repo_infos = scrape_github('weekly')
        # if crawler can't get any info, print modify request
        try:
            for index, (name, url, descp) in enumerate(repo_infos):
                f.write('%d. [**%s**](%s)\n' % (index+1, name, url))
                f.write('%s\n' % descp)
        except TypeError:
            f.write(
                'The crawler crashed, please contact the administrator to modify.\n')
        f.write('<!-- endtab -->\n')

        # monthly
        f.write('<!-- tab Monthly -->\n')
        repo_infos = scrape_github('monthly')
        # if crawler can't get any info, print modify request
        try:
            for index, (name, url, descp) in enumerate(repo_infos):
                f.write('%d. [**%s**](%s)\n' % (index+1, name, url))
                f.write('%s\n' % descp)
        except TypeError:
            f.write(
                'The crawler crashed, please contact the administrator to modify.\n')
        f.write('<!-- endtab -->\n')

        f.write('{% endsubtabs %}\n')
        # ---------- <EOF> GitHub Subtab ---------------
        f.write('<!-- endtab -->\n')
        # ------------------ <EOF> GitHub Tab ------------------------------------

        # ------------------ Medium Tab ------------------------------------
        f.write('<!-- tab Medium -->\n')

        # if crawler can't get any info, print modify request
        try:
            titles, urls, descrps = scrape_medium()
            for index, (title, url, descrp) in enumerate(zip(titles, urls, descrps)):
                f.write('%d. [**%s**](%s)\n' % (index+1, title, url))
                f.write('%s\n' % descrp)
        except TypeError:
            f.write(
                'The crawler crashed, please contact the administrator to modify.\n')
        f.write('<!-- endtab -->\n')
        # ------------------ <EOF> Medium Tab ------------------------------------

        f.write('{% endtabs %}\n')
