# 📰 Top News Aggregator

### Main Concern
``` 
    News stories were not what I expected.
    Can this be improved?
```

### First I tried a prompt:
   Works fine in gemini and Fails due to licencing in ChatGPT
   Gemini suggested using Markdown language for the prompt.
   ```
Please fetch the top news stories from `https://news.google.com/`.

Your response must follow these specific instructions:

* **Format:** A bulleted list.
* **Quantity:** Please provide under 20 top stories.
* **Content:** For each story in the list, you must provide:
    1.  A single-line summary.
    2.  The direct source link for the article.
   ```

### Second ChatGPT suggested a prompt
   I won't include it here.  

### Third ChatGPT suggested a Python3 program

    This is interesting because now it doesn't use an LLM or any Tokens! 
    
    Version 1:  
      Through Vibe coding: simple program that listed news in a markdown.
      Time: About 30 minutes
    
    Version 2:  A new program creates .json, .csv, and .html. 
      Time: About 2.5 hrs more.  
      Errata:
                            There was also a feature explosion 
                            Due to my needs, I didn't remove them.
                            At the end ChatGPT suggested more robustness.  
    
    Version 3:  Database
    
                Proposed:   Create a Python3 program to load a database.
                            PostgreSQL prefered.  SQL lite possible
                Thoughts:   News can change rapidly.  
                            What does "top 10 stories really mean ?  
                            Can we look at it for trends ?
                            How can we remove duplicates ?
                            Should we remove dups from run to run ?
