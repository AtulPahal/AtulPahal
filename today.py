import os
import requests

def github_request(url, token, accept="application/vnd.github+json"):
    headers = {
        "Authorization": f"token {token}",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def fetch_github_stats(username, token):
    # 1. Fetch repositories and followers
    user_url = f"https://api.github.com/users/{username}"
    user_data = github_request(user_url, token)
    public_repos = user_data.get("public_repos", 0)
    followers = user_data.get("followers", 0)
    
    # 2. Total up all repository stars (handling pagination)
    total_stars = 0
    page = 1
    while True:
        repos_url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        repos_data = github_request(repos_url, token)
        if not repos_data or not isinstance(repos_data, list):
            break
        for repo in repos_data:
            total_stars += repo.get("stargazers_count", 0)
        if len(repos_data) < 100:
            break
        page += 1
            
    # 3. Fetch total commit contributions across all repositories
    search_url = f"https://api.github.com/search/commits?q=author:{username}"
    search_data = github_request(search_url, token)
    total_commits = search_data.get("total_count", 0)
    
    return {
        "repos": public_repos,
        "followers": followers,
        "stars": total_stars,
        "commits": total_commits
    }
def generate_svg(stats, theme="dark"):
    if theme == "dark":
        bg = "#1a1b26"       # Tokyonight Dark Background
        text = "#a9b1d6"     # Foreground Text
        accent = "#7aa2f7"   # Command Blue
        green = "#9ece6a"    # Success Green
        yellow = "#e0af68"   # Info Yellow
        border = "#24283b"   # Element Border
    else:
        bg = "#ffffff"       # Clean Light Background
        text = "#373b41"
        accent = "#0066cc"
        green = "#28a745"
        yellow = "#b58900"
        border = "#e1e4e8"

    # Arch Linux stylized ASCII logo grid
    ascii_art = [
        "   /\\       ",
        "  /  \\      ",
        " /\\   \\     ",
        "/__\\   \\    ",
        "    \\   \\   ",
        "     \\___\\  "
    ]
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="600" height="300" viewBox="0 0 600 300">
    <style>
        .terminal {{ font-family: monospace; font-size: 14px; fill: {text}; white-space: pre; }}
        .title {{ fill: {accent}; font-weight: bold; }}
        .accent {{ fill: {accent}; }}
        .green {{ fill: {green}; }}
        .yellow {{ fill: {yellow}; }}
        .border {{ stroke: {border}; fill: {bg}; stroke-width: 2; rx: 8; }}
    </style>
    
    <rect class="border" width="598" height="298" x="1" y="1" />
    
    <!-- Decorative Terminal Window Control Buttons -->
    <circle cx="20" cy="20" r="6" fill="#ff5f56" />
    <circle cx="40" cy="20" r="6" fill="#ffbd2e" />
    <circle cx="60" cy="20" r="6" fill="#27c93f" />
    
    <g class="terminal" transform="translate(30, 60)" xml:space="preserve">
        <!-- ASCII Grid column -->
        <text x="0" y="20" class="accent">{ascii_art[0]}</text>
        <text x="0" y="40" class="accent">{ascii_art[1]}</text>
        <text x="0" y="60" class="accent">{ascii_art[2]}</text>
        <text x="0" y="80" class="accent">{ascii_art[3]}</text>
        <text x="0" y="100" class="accent">{ascii_art[4]}</text>
        <text x="0" y="120" class="accent">{ascii_art[5]}</text>
        
        <!-- System Metric Specs column -->
        <text x="160" y="20"><tspan class="title">atul</tspan>@<tspan class="title">arch-box</tspan></text>
        <text x="160" y="35" fill="{border}">-------------------</text>
        
        <text x="160" y="55"><tspan class="green">OS</tspan>: Arch Linux x86_64</text>
        <text x="160" y="75"><tspan class="green">Host</tspan>: Apple M2 MacBook Air</text>
        <text x="160" y="95"><tspan class="green">Kernel</tspan>: Linux 6.x-zen</text>
        <text x="160" y="115"><tspan class="green">Shell</tspan>: zsh + Hyprland</text>
        <text x="160" y="135"><tspan class="green">Editor</tspan>: Neovim (LazyVim)</text>
        
        <!-- Live GitHub statistics payload -->
        <text x="160" y="170" class="yellow" font-weight="bold">[GitHub Metrics]</text>
        <text x="160" y="190"><tspan class="accent">Repositories</tspan>: {stats['repos']}</text>
        <text x="160" y="210"><tspan class="accent">Total Commits</tspan>: {stats['commits']}</text>
        <text x="160" y="230"><tspan class="accent">Stars Earned </tspan>: {stats['stars']} | <tspan class="accent">Followers</tspan>: {stats['followers']}</text>
    </g>
</svg>
"""

def main():
    token = (os.environ.get("ACCESS_TOKEN", "").strip() or 
             os.environ.get("GITHUB_TOKEN", "").strip())
    username = os.environ.get("USER_NAME", "").strip() or "AtulPahal"
    
    if not token:
        print("Error: Missing ACCESS_TOKEN or GITHUB_TOKEN environment variable.")
        import sys
        sys.exit(1)
        
    try:
        stats = fetch_github_stats(username, token)
        
        with open("dark_mode.svg", "w") as f:
            f.write(generate_svg(stats, "dark"))
            
        with open("light_mode.svg", "w") as f:
            f.write(generate_svg(stats, "light"))
            
        print("Profile graphics generated cleanly.")
    except Exception as e:
        print(f"Execution failure: {e}")
        import sys
        sys.exit(1)
if __name__ == "__main__":
    main()
