# linkedin_post_comments_analyzer
LinkedIn Post Comments Analyzer
Improvements:
1) click cli added
2) image file profile gathering
3) email crawler from post comments


The CLI Format:
    Analyze linkedin post comments infile and returns excel with processed information and image profiles
    $ python linkedin_comment_analyzer.py analyze infile imageoutdir timedate --debug=no
        infile      -file with the post comments
        imageoutdir -dir to store the profile images [subdir images]
        timedate    -prefix to store the processed excel file [subdir comments]
        debug       -option to analyze the post comments file and not getting image profiles from url

Work Steps to get the file with the post comments:

1- Expand all comments and replies from linkedin post,
    by clicking all "Show previous comments" until all comments are visible
2- Expand all comment replies by clicking all "Load previous replies" until all replies are visible
3- press f12 in your browser and select all comments with parent div it must be like this example:-
```
<div id="ember1482" class="feed-base-comments-list feed-base-comments-list--expanded ember-view">
<!---->
<!---->
      <article>
      <article>
      <article>

      ....

      <article>
 <div>
```

4- right click on that div and then press "Edit As HTML" and copy all contents
5- save these contents in a text file for example Comments.html and make sure that encoding is UTF-8
6- Excute python linkedin_comment_analyzer.py analyze infile imageoutdir timepath --debug='no' where 
"infile" is the file (path and name) saved in the previous step

Based on prvious work from:
https://github.com/rozester/LinkedInCommentAnalyzer/blob/master/linkedin-comments-grabber.py
LinkedIn Comments Analyzer
Copyright 2017 Amr Salama
Twitter: @amr_salama3
Github: rozester/LinkedInCommentAnalyzer
MIT License
