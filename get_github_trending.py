# -*- coding: utf-8 -*-
# @Author: S_W_K

import requests
from requests.adapters import HTTPAdapter
from lxml import etree
from fake_useragent import UserAgent


session = requests.Session()
session.mount('https://', HTTPAdapter(max_retries=3))
UA = UserAgent()


def scrape_github(since_when, language=''):
    url = 'https://github.com/trending/%s?since=%s' % (language, since_when)
    user_agent = UA.random

    response = session.get(url, headers={'User-Agent': user_agent}, timeout=5)
    html = etree.HTML(response.text)

    repo_infos = html.xpath('/html/body/div[4]/main/div[3]/div/div[2]/article')
    for info in repo_infos:
        repo_name = info.xpath('string(.//h1/a)').strip()

        repo_url = info.xpath('.//h1/a/@href')[0]
        prefix = 'https://github.com'
        repo_url = prefix+repo_url

        repo_description = info.xpath('string(./p)').strip()
        if len(repo_description) == 0:
            repo_description = 'No repo_description'

        yield repo_name, repo_url, repo_description


def scrape_medium():
    url = 'https://medium.com/topic/popular'
    response = session.get(url, headers={'User-Agent': UA.random}, timeout=5)
    html = etree.HTML(response.text)

    article_titles = []
    article_urls = []
    article_descriptions = []

    the_first = html.xpath(
        '//*[@id="root"]/div/div[3]/div/div/div[1]/div[2]/div/div[3]/div')[0]
    first_title = the_first.xpath('string(./h1/a)')
    first_url = the_first.xpath('./h1/a/@href')[0]
    first_url = 'https://medium.com'+first_url
    first_descrp = the_first.xpath('string(./div/p/a)').strip()
    article_titles.append(first_title)
    article_urls.append(first_url)
    article_descriptions.append(first_descrp)

    the_rest = html.xpath(
        '//*[@id="root"]/div/div[3]/div/div/div[1]/div[3]/div[1]//section/div/section/div[1]/div[1]/div[1]')
    for r in the_rest:
        r_title = r.xpath('string(./h3/a)')
        r_url = r.xpath('./h3/a/@href')[0]
        r_descrp = r.xpath('string(./div/p/a)').strip()
        article_titles.append(r_title)
        article_urls.append(r_url)
        article_descriptions.append(r_descrp)

    return article_titles, article_urls, article_descriptions


if __name__ == '__main__':
    with open('Blog/source/trending/index.md','w') as f:
        # front_matter and beginning
        front_matter = '---\ntitle: Trending\ncomments: false\nno_toc: true\n---\n'
        f.write(front_matter)
        f.write('\n')
        f.write(
            '> Scraped from [GitHub](https://github.com/trending), [Medium](https://medium.com/topic/popular)\n')
        f.write('auto-deployed with [Travis Ci](https://travis-ci.org/)')
        f.write('\n\n')

        f.write('{% tabs TAB %}\n')

        # ------------------ GitHub Tab ------------------------------------
        f.write('<!-- tab GitHub -->\n')

        # ---------- GitHub Subtab ---------------
        f.write('{% subtabs GitHub Tab%}\n')
        # daily
        f.write('<!-- tab Daily -->\n')
        repo_infos = scrape_github('daily')
        for index, (name, url, descp) in enumerate(repo_infos):
            f.write('%d. [**%s**](%s)\n' % (index+1, name, url))
            f.write('%s\n' % descp)
        f.write('<!-- endtab -->\n')

        # weekly
        f.write('<!-- tab Weekly -->\n')
        repo_infos = scrape_github('weekly')
        for index, (name, url, descp) in enumerate(repo_infos):
            f.write('%d. [**%s**](%s)\n' % (index+1, name, url))
            f.write('%s\n' % descp)
        f.write('<!-- endtab -->\n')

        # monthly
        f.write('<!-- tab Monthly -->\n')
        repo_infos = scrape_github('monthly')
        for index, (name, url, descp) in enumerate(repo_infos):
            f.write('%d. [**%s**](%s)\n' % (index+1, name, url))
            f.write('%s\n' % descp)
        f.write('<!-- endtab -->\n')

        f.write('{% endsubtabs %}\n')
        # ---------- <EOF> GitHub Subtab ---------------
        f.write('<!-- endtab -->')
        # ------------------ <EOF> GitHub Tab ------------------------------------

        # ------------------ Medium Tab ------------------------------------
        f.write('<!-- tab Medium -->\n')
        titles, urls, descrps = scrape_medium()
        for index, (title, url, descrp) in enumerate(zip(titles, urls, descrps)):
            f.write('%d. [**%s**](%s)\n' % (index+1, title, url))
            f.write('%s\n' % descrp)
        f.write('<!-- endtab -->\n')
        # ------------------ <EOF> Medium Tab ------------------------------------

        f.write('{% endtabs %}\n')
