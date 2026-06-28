import os
import argparse
from shutil import rmtree, copytree, copy2
from urllib.parse import urljoin

import mistune
import frontmatter
from bs4 import BeautifulSoup, element
from jinja2 import Environment, FileSystemLoader, select_autoescape, TemplateNotFound

first_name = "Takato"
last_name = "Komada"
name = f"{first_name} {last_name}"
domain = "tkt0605.me"
url = f"https://{domain}"

parser = argparse.ArgumentParser(description="Build the website")
parser.add_argument("--output", help="Output directory", default="dist")
parser.add_argument("--no-clean", action="store_true")
args = parser.parse_args()

script_path = os.path.dirname(os.path.realpath(__file__))
root_path = os.path.normpath(os.path.join(script_path, ".."))

if not os.path.isabs(args.output):
    args.output = os.path.join(root_path, args.output)

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
    obj = frontmatter.load(os.path.join(root_path, "posts", folder, file))
    obj.content = make_html(obj.content)
    obj["slug"] = file.replace(".md", "")
    obj["href"] = f"/{folder}/{obj['slug']}"
    if "order" not in obj:
        obj["order"] = 0
    if "pin" not in obj:
        obj["pin"] = False
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
posts_dir = os.path.join(root_path, "posts")
post_folders = [f for f in os.listdir(posts_dir) if os.path.isdir(os.path.join(posts_dir, f))]
lists = {}
posts_by_folder = {}

for folder in post_folders:
    files = [f for f in os.listdir(os.path.join(posts_dir, folder)) if f.endswith(".md")]
    posts = [get_post(folder, f) for f in files]
    posts = sorted(posts, key=lambda x: (not x["pin"], x["order"]))

    try:
        page_template = env.get_template(f"posts/{folder}/page.html")
    except TemplateNotFound:
        page_template = None
    list_template = env.get_template(f"posts/{folder}/list.html")

    if page_template:
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

    posts_by_folder[folder] = posts
    lists[folder] = list_template.render(posts=posts)
    list_page_rendered = env.get_template("posts/list_page.html").render(
        posts=posts,
        folder_title=folder,
        list_html=lists[folder],
        title=f"{name} | {folder}",
        name=name
    )
    list_page_soup=bs(list_page_rendered)
    seo=og_tags({
        "url": urljoin(url, f"/{folder}/"),
        "title": f"{name} | {folder}",
        "type": "website",
    })
    for item in seo:
        list_page_soup.head.append(bs(item))
    write_output(list_page_soup.encode_contents().decode("utf-8"), folder, "index.html")
# index.html
seo_common = {
    "url": url,
    "title": name,
    "description": f"{name}'s personal website",
    "type": "profile",
}
whoami = load_content(os.path.join(root_path, "content/information/whoami.md"))
hobby = load_content(os.path.join(root_path, "content/mylist/hobby.md"))
experience = load_content(os.path.join(root_path, "content/experience/experience.md"))
index_soup = render_template("index.html", lists=lists, name=name, title=name, whoami=whoami, hobby=hobby, experience=experience, projects=posts_by_folder.get("projects", []))
for item in og_tags(seo_common):
    index_soup.head.append(bs(item))
write_output(index_soup.encode_contents().decode("utf-8"), "index.html")

# public/の静的アセットを出力Directotryにコピー
public_dir = os.path.join(script_path, "..", "public")
if os.path.isdir(public_dir):
    for entry in os.listdir(public_dir):
        src_p = os.path.join(public_dir, entry)
        dst_p = os.path.join(args.output, entry)
        if os.path.isdir(src_p):
            copytree(src_p, dst_p, dirs_exist_ok=True)
        else:
            copy2(src_p, dst_p)
    print("Copied public/ into output.")
print("Build complete.")
