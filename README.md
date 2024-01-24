# google_search_spider

## Introduction

It is just a little python-script to fulfill the needs of my professor after I found that most google-search spider on github didn't run well or out of date.

It runs well on my/my friends/my parents' compluter. Also runs well on my Linux & Windows. So I think it has few bugs. If any questions, plz contact me by email  :)

## Usage

### Quick Start

1. Replace `todo` in `google_spider.py` as your **quesion** and then run it. You will see a Firefox/Chrome launched. 
   1. It will scroll over and over again automatically until reaches the max results count of Google (about 500) till it is finished.
   2. It will then spider all results into `data/` folder. Note that it just contains [webtitle, weburl] of all results. It also logs the progress in `data/`.
2. Replace `todo` as your **file names** (got in step 1) in `result_filter.py` and run it if you want to remove duplicate results.
3. Replace `todo` as your **file names** (got in step 1/2) in `web_text_visitor.py`. You will see `web_text.txt` generated in `data/`. It is the whole-text-result of this project.

## Change Log

### latest update: 2024/1/4

Add `README.md` when I found someone stared this project. It is the FIRST START I've got! I've never thought that someone would start it, so I replace Chinese comments into English to facilitate and welcome the public.

Rushly, I didn't check if there were any imperfect errors such as translation errors and spelling mistakes after making the changes. Welcome to modify any code if you want.


## Bugs Possible

### Environments

No specific environments are needed (I think?), so I didn't generate a `requiremnts.txt`. If you meet env questions, you can try creating a new env of `python=3.11`, and simply run several `pip install <packages used in this project>`.

### Drive not found

Maybe because your computer doesn't have a FireFox webdriver. 