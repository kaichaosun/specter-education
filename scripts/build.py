import subprocess
import os
import markdown
import datetime
import yaml

from create_index import website

def load_content():
  with open('content.yaml', 'r') as content:
    try:
      content = yaml.safe_load(content)
    except yaml.YAMLError as exc:
      print(f"issues with parsing content.yaml: {exc}")
      exit(1)
    return content


def process_guide(content, guide):
  ''' processes one guide at a time '''
  guide_markdown="# Table of Contents \n\n[TOC]\n\n"
  pure_html = ""
  for section in content["guides"][guide]["content"]:
    section_file=""
    if os.path.isdir(f"content/{section}") and os.path.isfile(f"content/{section}/description.md"):
      section_file = f"content/{section}/description.md"
    elif os.path.isfile(f"content/{section}.md"):
      section_file = f"content/{section}.md"
    else:
      print(f"ERROR: Could not find section: {section}")
      exit(1)

    with open(section_file, "r", encoding="utf-8") as section_file:
      guide_markdown = guide_markdown + section_file.read() + "\n\n"
      
  guide_html = markdown.markdown(guide_markdown,extensions=['toc','tables'])
  # https://python-markdown.github.io/reference/#the-basics


  hash = subprocess.check_output(["git","rev-parse","HEAD"]).decode("utf-8")[:10]
  date = datetime.datetime.now().strftime("%Y-%m-%d")

  html=f'''
  <html>
  <head>
  <link rel="stylesheet" href="mystyle.css">
  </head>
  <body>
      <article id="cover">
        <h1>{content["guides"][guide]["title"]}</h1>
        <address>
          Cryptoadvance
          https://specter.solutions
        </address>
        <address>
          v0.2 - {hash}
          {date}
        </address>
      </article>
  {guide_html}
  </body>
  <html>
  '''
  filename = content["guides"][guide]["filename"]
  with open(f"build/{filename}.html","w", encoding="utf-8") as html_file:
      html_file.write(html)

  # late import because:
  # https://github.com/Python-Markdown/markdown/issues/950
  from weasyprint import HTML
  
  HTML(f'./build/{filename}.html').write_pdf(f'./build/{filename}.pdf')


if __name__ == "__main__":
  content = load_content()
  for key, value in content["guides"].items():
    print(f"Creating Guide {key}")
    process_guide(content,key)
  website(content)