import os
import subprocess
from datetime import datetime

# The external drive is now the git repo itself
REPO_DIR = "/Volumes/Untitled/myfavoriteascii"

ASCII_ART = r"""    __________________________________________________
   /                                                  \
   |   WELCOME TO MY FAVORITE ASCII & FILE ARCHIVE    |
   \__________________________________________________/

       _~~-_
      ( (`\
       \   \  __   _
        >   \/  \_/ \
       /   /       \
       \   \_/ \_/\_/
        \___/"""

def get_file_size_string(file_path):
    if os.path.isdir(file_path):
        return "-"
    size_bytes = os.path.getsize(file_path)
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"

def generate_html_for_directory(current_dir):
    file_rows = ""
    is_root = (os.path.abspath(current_dir) == os.path.abspath(REPO_DIR))

    if not is_root:
        file_rows += f"""        <tr>
            <td><a href="../index.html">📁 .. (Parent Directory)</a></td>
            <td>Folder</td>
            <td>-</td>
            <td>-</td>
        </tr>\n"""

    all_items = sorted(os.listdir(current_dir))
    for item in all_items:
        # Skip hidden files, git metadata, python script, and index files
        if item.startswith(".") or item == "index.html" or item == ".git" or item == "sync_site.py":
            continue

        full_path = os.path.join(current_dir, item)
        is_dir = os.path.isdir(full_path)
        mtime = os.path.getmtime(full_path)
        date_str = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")

        if is_dir:
            icon = "📁"
            file_type = "Folder"
            size_str = "-"
            size_bytes = 0
            display_link = f'<a href="{item}/index.html">{icon} {item}/</a>'
            preview_html = "-"
        else:
            size_bytes = os.path.getsize(full_path)
            size_str = get_file_size_string(full_path)
            ext = os.path.splitext(item)[1].lower().replace(".", "")

            if ext in ["png", "jpg", "jpeg", "gif", "webp"]:
                icon = "🖼️"
                file_type = f"{ext.upper()} Image"
                preview_html = f'<br><img src="{item}" class="thumb" loading="lazy">'
            elif ext in ["mp3", "wav", "ogg"]:
                icon = "🎵"
                file_type = f"{ext.upper()} Audio"
                preview_html = f'<br><audio controls preload="none"><source src="{item}"></audio>'
            else:
                icon = "📄"
                file_type = f"{ext.upper()} File" if ext else "Binary"
                preview_html = "-"

            display_link = f'<a href="{item}">{icon} {item}</a>{preview_html}'

        file_rows += f"""        <tr data-name="{item.lower()}" data-type="{file_type.lower()}" data-size="{size_bytes}" data-date="{mtime}">
            <td>{display_link}</td>
            <td>{file_type}</td>
            <td>{size_str}</td>
            <td>{date_str}</td>
        </tr>\n"""

    rel_path = os.path.relpath(current_dir, REPO_DIR)
    title_suffix = f" / {rel_path}" if rel_path != "." else ""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>myfavoriteascii.com{title_suffix}</title>
    <style>
        body {{ background-color: #c0c0c0; color: #000000; font-family: monospace; margin: 20px; }}
        a {{ color: #0000ff; text-decoration: underline; }}
        a:visited {{ color: #800080; }}
        table {{ width: 100%; border-collapse: collapse; background-color: #ffffff; }}
        th, td {{ border: 1px solid #808080; padding: 8px; text-align: left; vertical-align: middle; }}
        th {{ background-color: #d4d0c8; cursor: pointer; user-select: none; }}
        th:hover {{ background-color: #b1aeb5; }}
        .thumb {{ max-width: 120px; max-height: 90px; border: 1px solid #000; margin-top: 5px; display: block; }}
        audio {{ height: 30px; margin-top: 5px; }}
    </style>
</head>
<body>

    <pre>{ASCII_ART}</pre>

    <hr>
    <h2>// ARCHIVE{title_suffix.upper()}</h2>
    <p><i>Click table headers to sort. Click links to download or browse.</i></p>
    <hr>

    <table id="fileTable">
        <thead>
            <tr>
                <th onclick="sortTable(0)">Filename ↕</th>
                <th onclick="sortTable(1)">Type ↕</th>
                <th onclick="sortTable(2)">Size ↕</th>
                <th onclick="sortTable(3)">Date Added ↕</th>
            </tr>
        </thead>
        <tbody>
{file_rows}
        </tbody>
    </table>

    <br><br>
    <hr>
    <address>Interactive retro archive. Powered by Python & client-side JS.</address>

    <script>
    function sortTable(n) {{
        var table, rows, switching, i, x, y, shouldSwitch, dir, switchcount = 0;
        table = document.getElementById("fileTable");
        switching = true;
        dir = "asc";
        while (switching) {{
            switching = false;
            rows = table.rows;
            for (i = 1; i < (rows.length - 1); i++) {{
                shouldSwitch = false;
                let xVal = rows[i].getAttribute(n === 0 ? "data-name" : n === 1 ? "data-type" : n === 2 ? "data-size" : "data-date");
                let yVal = rows[i + 1].getAttribute(n === 0 ? "data-name" : n === 1 ? "data-type" : n === 2 ? "data-size" : "data-date");

                if (n === 2 || n === 3) {{
                    xVal = parseFloat(xVal);
                    yVal = parseFloat(yVal);
                }}

                if (dir == "asc") {{
                    if (xVal > yVal) {{ shouldSwitch = true; break; }}
                }} else if (dir == "desc") {{
                    if (xVal < yVal) {{ shouldSwitch = true; break; }}
                }}
            }}
            if (shouldSwitch) {{
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;
            }} else {{
                if (switchcount == 0 && dir == "asc") {{
                    dir = "desc";
                    switching = true;
                }}
            }}
        }}
    }}
    </script>
</body>
</html>
"""
    target_index = os.path.join(current_dir, "index.html")
    with open(target_index, "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    if not os.path.exists(REPO_DIR):
        print(f"[!] Volume not found: {REPO_DIR}.")
        return

    os.chdir(REPO_DIR)
    print("[*] Generating index.html files for all folders...")
    for root, dirs, files in os.walk(REPO_DIR):
        if ".git" in root:
            continue
        generate_html_for_directory(root)

    status_result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not status_result.stdout.strip():
        print("[*] No changes detected. Everything is up to date.")
        return

    print("[*] Changes detected. Committing and pushing straight to GitHub...")
    subprocess.run(["git", "add", "-A"], check=True)

    commit_msg = f"Archive update: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
    if push_result.returncode == 0:
        print("[+] Successfully updated and pushed live!")
    else:
        print(f"[!] Push failed: {push_result.stderr}")

if __name__ == "__main__":
    main()
