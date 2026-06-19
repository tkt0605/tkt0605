import os
import argparse
from shutil import rmtree
from urllib.parse import urljoin

import mistune
import frontmatter
from bs4 import BeautifulSoup, element
from jinja2 import Environment, FileSystemLoader, select_autoescape

first_name = "Takato"
last_name = "Komada"
name = f"{first_name} {last_name}"
domain = "localhost"  # TODO: カスタムドメインに変更
url = f"https://{domain}"

parser = argparse.ArgumentParser(description="Build the website")
parser.add_argument("--output", help="Output directory", default="dist")
parser.add_argument("--no-clean", action="store_true")
args = parser.parse_args()

script_path = os.path.dirname(os.path.realpath(__file__))

env = Environment(
    loader=FileSystemLoader(os.path.join(script_path, "..", "templates")),
    autoescape=select_autoescape(["html"]),
)

if not args.no_clean:
    for root, dirs, files in os.walk(args.output):
        for file in files:
            if file == "index.css":
                continue
            os.remove(os.path.join(root, file))
        for dir in dirs:
            rmtree(os.path.join(root, dir))


def write_output(content, *path):
    for i in range(len(path) - 1):
        dir_path = os.path.join(args.output, *path[: i + 1])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
    with open(os.path.join(args.output, *path), "w", encoding="utf-8") as f:
        f.write(content)


def bs(content):
    return BeautifulSoup(content, "html.parser")


def img_tag_rule(img_tag: element.Tag):
    if not img_tag.has_attr("decoding"):
        img_tag["decoding"] = "async"
    if not img_tag.has_attr("loading"):
        img_tag["loading"] = "lazy"


def render_template(template_name, **context):
    template = env.get_template(template_name)
    rendered = template.render(**context)
    soup = bs(rendered)
    for img_tag in soup.find_all("img"):
        img_tag_rule(img_tag)
    return soup


make_html = mistune.create_markdown(
    escape=False,
    plugins=["strikethrough", "footnotes", "table"],
)


def get_post(folder, file):
    obj = frontmatter.load(f"posts/{folder}/{file}")
    obj.content = make_html(obj.content)
    obj["slug"] = file.replace(".md", "")
    obj["href"] = f"/{folder}/{obj['slug']}"
    if "order" not in obj:
        obj["order"] = 0
    return obj


def og_tags(data: dict):
    tags = []
    for key, value in data.items():
        tags.append(f'<meta property="og:{key}" content="{value}">')
    if "description" in data:
        tags.append(f'<meta name="description" content="{data["description"]}">')
    return tags


def load_content(path):
    obj = frontmatter.load(path)
    obj.content = make_html(obj.content)
    return obj


# posts/ 以下のフォルダを自動検出してビルド
post_folders = [f for f in os.listdir("posts") if os.path.isdir(f"posts/{f}")]
lists = {}

for folder in post_folders:
    files = [f for f in os.listdir(f"posts/{folder}") if f.endswith(".md")]
    posts = [get_post(folder, f) for f in files]
    posts = sorted(posts, key=lambda x: x["order"])

    page_template = env.get_template(f"posts/{folder}/page.html")
    list_template = env.get_template(f"posts/{folder}/list.html")

    for post in posts:
        rendered = page_template.render(post=post, title=f"{name} | {post['title']}", name=name)
        soup = bs(rendered)
        seo = og_tags({
            "url": urljoin(url, f"/{folder}/{post['slug']}"),
            "title": f"{name} | {post['title']}",
            "description": post.get("summary", ""),
            "type": "website",
        })
        for item in seo:
            soup.head.append(bs(item))
        write_output(soup.encode_contents().decode("utf-8"), folder, f"{post['slug']}.html")

    lists[folder] = list_template.render(posts=posts)

# index.html
seo_common = {
    "url": url,
    "title": name,
    "description": f"{name}'s personal website",
    "type": "profile",
}
whoami = load_content("content/information/whoami.md")
hobby = load_content("content/mylist/hobby.md")
experience = load_content("content/experience/experience.md")
project = load_content("content/projects/project.md")
index_soup = render_template("index.html", lists=lists, name=name, title=name, whoami=whoami, hobby=hobby, experience=experience, project=project)
for item in og_tags(seo_common):
    index_soup.head.append(bs(item))
write_output(index_soup.encode_contents().decode("utf-8"), "index.html")

print("Build complete.")
