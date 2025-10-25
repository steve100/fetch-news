rem delete the last news file 
del top_news.html /q
rem python top_news_aggregator.py --include-world --include-us --include-ai --ai-first --max 20 --format html --output-file top_news.html

rem python3 top_news_aggregator.py --include-world --include-us --include-ai --format html --output-file top_news.html --also-stdout
python top_news_aggregator.py --include-world --include-us --include-ai --all-formats


rem set filepath slash direction for web urls
set p=%cd%
set p=%p:\=/%
echo %p%

rem call filefox -- mine is on the path
rem any html render will work

rem firefox
rem "C:\Program Files\Mozilla Firefox\firefox.exe" %p%/top_news.html

rem chrome
rem "C:\Program Files\Google\Chrome\Application\chrome.exe" %p%/top_news.html

rem Edge
"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" %p%/top_news.html
