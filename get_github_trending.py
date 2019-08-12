# -*- coding: utf-8 -*-
# @Author: S_W_K 

import requests
from lxml import etree

url='https://github.com/trending?since=daily'
response=requests.get(url)
html=etree.HTML(response.text)

repo_names=html.xpath('/html/body/div[4]/main/div[3]/div/div[2]/article//h1/a')
repo_names=[''.join(name.xpath('./text()')).strip() for name in repo_names]

# urls
repo_dirs=html.xpath('/html/body/div[4]/main/div[3]/div/div[2]/article//h1/a/@href')
prefix='https://github.com'
repo_urls=[prefix+name for name in repo_dirs]

# introductions
repo_intros=html.xpath('/html/body/div[4]/main/div[3]/div/div[2]/article//p')
repo_intros=[''.join(intro.xpath('./text()')) for intro in repo_intros]
repo_intros=[intro.strip() for intro in repo_intros]

cnt=1
with open('Blog/source/trending/index.md','w') as f:
    front_matter='---\ntitle: Trending\ncomments: false\nno_toc: true\n---\n'
    f.write(front_matter)
    f.write('\n')
    f.write('> Scraped from [GitHub](https://github.com/trending?since=daily), auto-deployed with [Travis Ci](https://travis-ci.org/).')
    f.write('\n\n')

    for n,u,i in zip(repo_names,repo_urls,repo_intros):
        term=str('%d. [%s](%s)\n%s')%(cnt,n,u,i)
        cnt+=1
        f.write(term)
        f.write('\n')
