# 📰 Top News Aggregator


## A program that  will Fetch and merge headlines from multiple public RSS feeds
```
Output is formatted in .html, .csv, .json and optional Markdown Language.
```
## Quick Overview

- A Simple Python based News Aggrator and should run on any system supporting a Modern Python3. Tested Python 3.13.9
  https://www.bbc.com/news/articles/cr7m2pd3810o
- The program Uses Modules feedparser beautifulsoup4
- Optionally you may create a Python Environment  (* reccommended)
- The batch file is Microsoft Windows centric
- Last tested:  python top_news_aggregator.py --all-formats
  Other formats were tested earlier but not with the new --all-formats option.  They were not removed. 



## 🚀 Quick Start

- Make sure Python3 is installed
  python3 --version
- Install the requiremeents
  pip3 install -r requirements  
- Edit and modify run-news.bat as desired
- Run the new program
  run-news.bat


## ⚙️ Features

- Pulls from trusted RSS sources:
  - **AI/Technology:** Google News (AI topic), NYT Tech, BBC Tech, Reuters Tech
  - **World:** BBC World, NYT, Reuters World, Google News Top Stories
  - **U.S.:** BBC US & Canada, NYT U.S., Reuters Domestic, Google News Nation
- Deduplicates articles automatically.
- Outputs in **Markdown** or **HTML**.
- AI/Tech stories appear first by default.
- Optionally disable AI-first or quiet stdout output.
- Works on macOS, Linux, and Windows.

---

## 🧩 Requirements

Python 3.9+ and the following packages:

```
pip install feedparser beautifulsoup4
```

## 🧠 Basic Usage

### Markdown output (to terminal)
python top_news_aggregator.py --include-world --include-us --include-ai --format markdown

### HTML output (saved to file)
python top_news_aggregator.py --include-world --include-us --include-ai --format html --output-file 

### Default AI-first order

- AI/Tech stories are shown first automatically.

## ⚙️ Options
```
--all-formats  -- what I am using now. creates .html .csv .json and .md files
These are untested now.  See run-news.bat

--include-world	Include global news (BBC, NYT, Google, Reuters).
--include-us	Include U.S.-focused news feeds.
--include-ai	Include AI/Tech feeds.
--max <N>	Limit total stories (default: 20, max: 50).
--format <markdown|html>	Output format (default: markdown).
--output-file <path>	Save output to a file (no stdout by default).
--also-stdout	Print to stdout even when writing to a file.
--quiet	Suppress stdout entirely.
--no-ai-first	Disable AI/Tech-first ordering.
--markdown-file <path>	Deprecated alias for --output-file (markdown only).
```

## 🧭 Examples
### ALL outputs (.html, .json, .csv, .md)
```
python top_news_aggregator.py --include-world --include-us --include-ai --all-formats
```

### Disable AI-first
```
python top_news_aggregator.py --include-world --include-us --include-ai --no-ai-first --format html --output-file top_news.html
```
### Markdown output
```
python top_news_aggregator.py --include-world --include-us --include-ai --format markdown
```
### Quiet mode
```
python top_news_aggregator.py --include-ai --format html --output-file top_ai.html --quiet
```

### Write all three files with default base (top_news.*) in current folder:
```
python top_news_aggregator.py --include-world --include-us --include-ai --all-formats
```

### Write all three using a custom base via --output-file:
```
python top_news_aggregator.py --include-world --include-us --include-ai --all-formats --output-file "C:\Users\Steve\projects\fetch-news\morning_report.html"
 Creates: morning_report.html, morning_report.json, morning_report.csv
```

```
## Also print Markdown to stdout at the same time:

python top_news_aggregator.py --include-world --include-us --include-ai --all-formats --also-stdout
```

## Generate only one format
```
python top_news_aggregator.py --include-world --include-us --include-ai --format csv --output-file to
```


## 📜 License
### MIT License — freely usable and modifiable.
