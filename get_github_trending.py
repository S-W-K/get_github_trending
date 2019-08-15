# -*- coding: utf-8 -*-
# @Author: S_W_K 

import requests
from lxml import etree
from fake_useragent import UserAgent

urls=['https://github.com/trending/python?since=daily',
'https://github.com/trending?since=daily']
directories=['Python Projects','All Projects']

with open('Blog/source/trending/index.md','w') as f:
    front_matter='---\ntitle: Trending\ncomments: false\n---\n'
    f.write(front_matter)
    f.write('\n')
    f.write('> Scraped from [GitHub](https://github.com/trending?since=daily), auto-deployed with [Travis Ci](https://travis-ci.org/).')
    f.write('\n')
    for url,dir_ in zip(urls,directories):
        user_agent=UserAgent().random

        response=requests.get(url,headers={'User-Agent':user_agent})
        html=etree.HTML(response.text)

        f.write('\n')
        f.write('### %s\n'%dir_)
        repo_infos=html.xpath('/html/body/div[4]/main/div[3]/div/div[2]/article')
        cnt=1
        for info in repo_infos:
            # names
            name=info.xpath('.//h1/a/text()')
            name=''.join(name).strip()

            # urls
            repo_url=info.xpath('.//h1/a/@href')[0]
            prefix='https://github.com'
            repo_url=prefix+repo_url

            # description
            description=info.xpath('.//p/text()')
            description=''.join(description).strip()
            if len(description)==0:
                description='No description'

            term=str('%d. [%s](%s)\n%s')%(cnt,name,repo_url,description)
            cnt+=1
            f.write(term)
            f.write('\n')
