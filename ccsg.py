import os
import argparse
import markdown
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ---------- STEP 1 ----------
def init_site(site_name):
    if os.path.exists(site_name):
        print("❌ Site already exists")
        return

    os.makedirs(os.path.join(site_name, "content"))

    with open(os.path.join(site_name, "content", "index.md"), "w") as f:
        f.write("# Home\n\nWelcome to your new static site!")

    print(f"✅ Site '{site_name}' initialized")

# ---------- STEP 2 ----------
def create_theme(theme_name):
    themes_path = os.path.join(os.getcwd(), "themes")
    theme_path = os.path.join(themes_path, theme_name)

    if os.path.exists(theme_path):
        print("❌ Theme already exists")
        return

    os.makedirs(theme_path)

    with open(os.path.join(theme_path, "index.html"), "w") as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
  <title>{{ Title }}</title>
</head>
<body>
  {{ Content }}
</body>
</html>
""")

    print(f"✅ Theme '{theme_name}' created")

# ---------- STEP 3 ----------
def create_page(page_name):
    content_path = os.path.join(os.getcwd(), "content")

    if not os.path.exists(content_path):
        print("❌ content directory not found")
        return

    page_file = os.path.join(content_path, f"{page_name}.md")

    if os.path.exists(page_file):
        print("❌ Page already exists")
        return

    with open(page_file, "w") as f:
        f.write(f"# {page_name.capitalize()}\n\nWrite your content here.")

    print(f"✅ Page '{page_name}' created")

# ---------- STEP 4 ----------
def build_site():
    content_dir = os.path.join(os.getcwd(), "content")
    themes_dir = os.path.join(os.getcwd(), "themes")
    public_dir = os.path.join(os.getcwd(), "public")

    theme_name = os.listdir(themes_dir)[0]
    template_path = os.path.join(themes_dir, theme_name, "index.html")

    with open(template_path, "r") as f:
        template = f.read()

    os.makedirs(public_dir, exist_ok=True)

    for file in os.listdir(content_dir):
        if file.endswith(".md"):
            with open(os.path.join(content_dir, file), "r") as f:
                md_text = f.read()

            title = "Untitled"
            for line in md_text.splitlines():
                if line.startswith("# "):
                    title = line.replace("# ", "")
                    break

            html_content = markdown.markdown(md_text)
            final_html = template.replace("{{ Title }}", title)
            final_html = final_html.replace("{{ Content }}", html_content)

            output_file = file.replace(".md", ".html")
            with open(os.path.join(public_dir, output_file), "w") as f:
                f.write(final_html)

    print("🔄 Site rebuilt")

# ---------- STEP 5 ----------
class RebuildHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith((".md", ".html")):
            build_site()

def serve_site():
    build_site()

    observer = Observer()
    observer.schedule(RebuildHandler(), path="content", recursive=True)
    observer.schedule(RebuildHandler(), path="themes", recursive=True)
    observer.start()

    os.chdir("public")
    server = HTTPServer(("0.0.0.0", 8000), SimpleHTTPRequestHandler)

    print("🚀 Serving at http://localhost:8000")
    print("👀 Watching for changes... (Ctrl+C to stop)")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 Server stopped")

    observer.join()

# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="CCSG - Custom Static Site Generator")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build")
    subparsers.add_parser("serve")

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("name")

    new_parser = subparsers.add_parser("new")
    new_subparsers = new_parser.add_subparsers(dest="new_command")

    theme_parser = new_subparsers.add_parser("theme")
    theme_parser.add_argument("name")

    page_parser = new_subparsers.add_parser("page")
    page_parser.add_argument("name")

    args = parser.parse_args()

    if args.command == "init":
        init_site(args.name)
    elif args.command == "new" and args.new_command == "theme":
        create_theme(args.name)
    elif args.command == "new" and args.new_command == "page":
        create_page(args.name)
    elif args.command == "build":
        build_site()
    elif args.command == "serve":
        serve_site()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
