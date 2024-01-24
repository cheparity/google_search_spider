# google_search_spider

## Introduction

It is just a little python-script to fulfill the needs of my professor after I found that most google-search spider on github didn't run well or out of date.

It runs well on my/my friends/my parents' compluter. Also runs well on my Linux & Windows. So I think it has few bugs. If any questions, plz contact me by email  :)

## Quick Start

0. Create a new data folder, at the same level as the application folder. Or you may meet strange errors.
1. Replace `todo` in `google_spider.py` as your **quesion** and then run it. You will see a Firefox/Chrome launched. 
   1. It will scroll over and over again automatically until reaches the max results count of Google (about 500).
   2. It will then spider all results into `data/` folder. Note that it just contains [webtitle, weburl] of all results as `results_of_<your qeustion>.csv`. It also logs the progress in `data/progress_*.csv`.
2. Replace `todo` as your **file names** (got in step 1) in `result_filter.py` and run it if you want to remove duplicate results. It will replace old files got in step 1. You can backup them if you don't want them to be replaced.
3. Replace `todo` as your **file names** (got in step 1/2) in `web_text_visitor.py`. You will see `web_text.txt` finally generated in `data/`. It is the whole-text-result of this project.

## Change Log

### latest update: 2024/1/4

Add `README.md` when I found someone stared this project. It is the FIRST START I've got! I've never thought that someone would start it, so I replace Chinese comments into English to facilitate and welcome the public.

Rushly, I didn't check if there were any imperfect errors such as translation errors and spelling mistakes after making the changes. Welcome to modify any code if you want.


## Bugs Possible

### Environments

No specific environments are needed (I think?), so I didn't generate a `requiremnts.txt`. If you meet env questions, you can try creating a new env of `python=3.11`, and simply run several `pip install <packages used in this project>`.

### Drive not found

Maybe because your computer doesn't have a FireFox webdriver. You can try to replace the 1st todo in `google_search_spider` to change a Chrome Driver. If you run it on linux, you might need to download the Firefox/Chrome Driver additionally. Worsely, if you use Linux without GUI, you might need to add the `--headless` option in `tools.py`.
