"""
Based on:
https://github.com/rozester/LinkedInCommentAnalyzer/blob/master/linkedin-comments-grabber.py
LinkedIn Comments Analyzer
Copyright 2017 Amr Salama
Twitter: @amr_salama3
Github: rozester/LinkedInCommentAnalyzer
MIT License

LinkedIn Post Comments Analyzer
Improvements:
1) click cli added
2) image file profile gathering
3) email crawler from post comments


THE CLI Format:
    Analyze linkedin postcomments infile and returns excel with processed information and image profiles
    $ python linkedin_comment_analyzer.py analyze infile imageoutdir timedate --debug=no
        infile      -file with the post comments
        imageoutdir -dir to store the profile images [subdir images]
        timedate    -prefix to store the processed excel file [subdir comments]
        debug       -option to analyze the post comments file and not getting image profiles from url

Work Steps to get the file with the post comments:-
1- Expand all comments and replies from linkedin post,
    by clicking all "Show previous comments" until all comments are visible
2- Expand all comment replies by clicking all "Load previous replies" until all replies are visible
3- press f12 in your browser and select all comments with parent div it must be like this example:-
<div id="ember1482" class="feed-base-comments-list feed-base-comments-list--expanded ember-view"><!---->
<!---->
      <article>
      <article>
      <article>

      ....

      <article>
<div>
4- right click on that div and then press "Edit As HTML" and copy all contents
5- save these contents in a text file for example Comments.html and make sure that encoding is UTF-8
Enjoy Data Science :)
"""
import click
import pandas as pd
from bs4 import BeautifulSoup

import requests

import progressbar
import re


from pathlib import Path


# Data Cleansing Phase
def paragraph_cleaning(p):
    # Normal Comment
    if (p.span and p.span.span):
        return p.span.span.string.replace('\n', '').strip()

    # # mention comment
    #    elif (p.span and p.span.a):
    #        return p.span.a.string.replace('\n','').strip()
    #    elif (p.a.span):
    #        return p.a.span.string.replace('\n','').strip()
    #    # url comment
    #    elif (cmnt.find('p').a):
    #        return cmnt.find('p').a.string.replace('\n','').strip()
    #    return p

    # Complicated Comment
    p_body = ""
    for cmnt in p.children:
        if (cmnt.string):
            p_body = p_body + cmnt.string
        else:
            p_body = p_body + " " + cmnt.a.string
    return p_body


def get_likes(comment):
    # likes exists
    likes = comment.find('button',
                         #class_="feed-base-comment-social-bar__likes-count Sans-13px-black-55% hoverable-link-text")
                         class_="feed-shared-comment-social-bar__likes-count Sans-13px-black-55% hoverable-link-text")

    if (likes):
        return likes.span.string.split(" ")[0]
    return 0


def get_replies(comment):
    # replies exists
    replies = comment.find('button',
                           #class_="feed-base-comment-social-bar__comments-count Sans-13px-black-55% hoverable-link-text")
                           class_="feed-shared-comment-social-bar__comments-count Sans-13px-black-55% hoverable-link-text")



    if (replies):
        return replies.span.string.split(" ")[0]
    return 0



def get_image(url,images_path,debug):

    urlfile = url.split('/')[5]+'.jpg'
    if (debug == 'yes'):
        return urlfile #debug
    with open(Path(images_path,urlfile), "wb") as f:
        f.write(requests.get(url).content)


    return urlfile



def get_email (comentario):
    email = ''

    #email = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", ' '.join(comentario), re.I))
    if type(comentario) is str:
        email = list(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", comentario, re.I))
    else:
        email = list(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+", ' '.join(comentario), re.I))
    return email


def obfuscate_list(*name):
    processed = []
    for cadena in name:
        lista = []
        for item in cadena:
            lista.append(obfuscate_string(item))

        processed.extend(lista)
    return processed

def obfuscate_string(*name):

    processed = ''
    email = False

    for cadena in name:
        words = cadena.split()
        if len(words) == 1: words = cadena.split('@');email = True
        obf_words = []
        for word in words:
            if len(word)>3:
                obfuscated = word[:3] +word[3:-1].translate("*" * 256)
            else:
                obfuscated = word.translate("*" * 256)[:]
            obf_words.append(obfuscated)

        if (email): processed = '@'.join(obf_words)
        else: processed = ' '.join(obf_words)


    return processed



i = 0


# Fill Dataframe with comments and replies
def add_comment(parent, comment, output_comments_df,images_path,debug):
    global i
    profile_image = ''
    file_image = ''
    try:
        profile_image = comment.a.div.div.div.attrs.get('style').replace('background-image: url("', '').replace('");', '')
        if profile_image:
            file_image = get_image(profile_image,images_path,debug)

    except Exception as e:
        pass #sin imagen cargada
    try:

            #file_image = ''
        profile_comment = comment.find('p').text #paragraph_cleaning(comment.find('p'))
        if profile_comment:
            email = get_email(profile_comment)

        profile_name = comment.find('span',
                             #class_="feed-base-shared-item__name Sans-13px-black-70%-semibold").
                             class_=" feed-shared-post-meta__name Sans-15px-black-85%-semibold").text.replace('\n', '').strip()

        profile_job = comment.find('span',
                             class_="feed-shared-post-meta__headline Sans-13px-black-55%").text.replace('\n', '').strip()

        publish_time = comment.find('time',class_="feed-shared-comment-item__timestamp Sans-13px-black-55%").text.replace('\n', '').strip()

        obfuscated_name = obfuscate_string(profile_name)
        obfuscated_email = obfuscate_list(email)
        output_comments_df.loc[i] = \
            [
                i + 1,
                parent,
                publish_time,
                comment.a.attrs.get('href'),
                profile_name,
                profile_job,
                #comment.img.attrs.get('src'),
                profile_image,
                file_image,
                email,
                profile_comment,
                get_likes(comment),
                get_replies(comment),
                obfuscated_name,
                obfuscated_email
            ]



        i = i + 1
    except Exception as e:
        pass
    return i


# Get all replies
def add_comment_replies(parent, comment, output_comments_df,images_path,debug):
    if (comment.article):
        for cmnt in comment.find_all("article"):
            add_comment(parent, cmnt, output_comments_df,images_path,debug)





def parse_comments(html_doc,images_path,debug,timedate_path, click = click):



    if debug =='yes':
        click.echo("Images profiles will NOT be downloaded")
    else:
        click.echo("Images profiles will be downloaded to:"+images_path)

    # Parse html file
    soup = BeautifulSoup(html_doc, 'html.parser')

    # Select all comments and replies html tags
    comments = soup.div.find_all("article", recursive=True)

    # Prepare Dataframe for loading all comments and replies inside it
    output_comments_df = pd.DataFrame(columns=['CommentID', 'ParentID', 'Time', 'LinkedIn ID', 'Name', 'Job', 'Photo','PhotoFile','Email',
                                               'Comment', 'Likes', 'Replies','OfusName', 'Ofusmail'])

    click.echo("Post comments readed. Processing "+str(len(comments))+" comments")

    bar = progressbar.ProgressBar(maxval=len(comments), \
                                  widgets=[progressbar.Bar('#', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()


    processed = 0
    # the main iterator for all comments and replies
    for cmnt in comments:
        cmnt_id = add_comment(0, cmnt, output_comments_df, images_path,debug)
        add_comment_replies(cmnt_id, cmnt, output_comments_df,images_path,debug)
        processed += 1
        bar.update(processed)

    bar.finish()

    # Fixing Data Types
    output_comments_df['CommentID'] = output_comments_df['CommentID'].astype(int)
    output_comments_df['ParentID'] = output_comments_df['ParentID'].astype(int)
    output_comments_df['Likes'] = output_comments_df['Likes'].astype(int)
    output_comments_df['Replies'] = output_comments_df['Replies'].astype(int)

    #timedate_path = datetime.now().strftime('%Y%m%d-%H%M%S') #retrieves as input argument
    # Exporting to Excel file
    processed_file_path = Path(Path(images_path).parents[1],'comments',timedate_path+'-'+'post_processed.xlsx')
    writer = pd.ExcelWriter(processed_file_path)
    #writer = pd.ExcelWriter(timedate_path + '-' + 'output.xlsx')
    #https://stackoverflow.com/questions/42306755/how-to-remove-illegal-characters-so-a-dataframe-can-write-to-excel
    output_comments_df = output_comments_df.applymap(lambda x: x.encode('unicode_escape').
                                   decode('utf-8') if isinstance(x, str) else x)


    output_comments_df.to_excel(writer, 'Sheet1') #getting openpyxl.utils.exceptions.IllegalCharacterError

    writer.save()

    click.echo("Parsing post comments ended, stored in file:" + processed_file_path.name)
    return processed_file_path.name


@click.group()
def cli():
    """
    Analyze linkedin postcomments infile and returns excel with processed information and image profiles
    $ python linkedin_comment_analyzer.py analyze infile imageoutdir timedate --debug=no
        infile      -file with the post comments
        imageoutdir -dir to store the profile images [subdir images]
        timedate    -prefix to store the processed excel file [subdir comments]
        debug       -option to analyze the post comments file and not getting image profiles from url
    """
    pass

@cli.command()
@click.argument('infile', required=1, nargs=1, type=click.File('r', encoding='utf8'))
@click.argument('imageoutdir', required=1, nargs=1, type=click.Path(exists=True))
@click.argument('timedate', required=1, nargs=1, type=click.STRING)
@click.option('--debug', default='no', type=click.Choice(['yes', 'no']), help='Debugging the post comments file and not getting image profiles')
def analyze(infile, imageoutdir,timedate,debug):
    """
    Analyze the infile html post comments with specified arguments
    """
    pass
    #file = open(str(infile), 'r', encoding='utf8')
    #html_doc = file.read()
    #file.close()
    click.echo("Post comments html DOWNLOADED file to analyze:" + infile.name)
    html_doc = infile.read()
    infile.close()

    processed_file_path = parse_comments(html_doc, imageoutdir, debug, timedate)


#cli.add_command(analyze)

if __name__ == '__main__':
    cli()