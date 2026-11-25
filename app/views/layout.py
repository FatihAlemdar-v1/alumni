NAV_STYLE = """
  <style>
    nav { display: flex; align-items: center; justify-content: space-between;
          max-width: 1080px; margin: 0 auto 40px; }
    .brand { display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 18px; }
    .brand-mark { width: 32px; height: 32px; border-radius: 9px;
                  background: linear-gradient(135deg, #38bdf8, #a78bfa);
                  display: flex; align-items: center; justify-content: center;
                  font-size: 15px; font-weight: 800; color: #0b1120; }
    nav .nav-links { display: flex; gap: 28px; font-size: 14px; }
    nav .nav-links a { color: #94a3b8; text-decoration: none; transition: color 0.15s ease; }
    nav .nav-links a:hover, nav .nav-links a.active { color: #e2e8f0; }
    nav .nav-links form { display: inline; margin: 0; }
    nav .nav-links button { border: 0; background: transparent; color: #94a3b8;
                            font: inherit; cursor: pointer; }
    @media (max-width: 720px) {
      nav { flex-direction: column; gap: 14px; }
      nav .nav-links { gap: 16px; font-size: 13px; flex-wrap: wrap; justify-content: center; }
    }
  </style>
"""


def render_nav_links(active: str, user: dict | None = None) -> str:
    active_attr = ' class="active"'
    nav_links = [
        ("/", "Home"),
        ("/about", "About"),
        ("/alumni", "Mezunlar"),
        ("/announcements", "Announcements"),
        ("/job-postings", "Job Postings"),
        ("/docs", "API Docs"),
    ]
    if user:
        nav_links.extend(
            [
                ("/profile", "Profilim"),
                ("/my-applications", "Başvurularım"),
                ("/my-job-postings", "İlanlarım"),
            ]
        )
        if user.get("role") == "admin":
            nav_links.append(("/admin", "Admin Paneli"))
        links = "".join(
            f'<a href="{href}"{active_attr if href == active else ""}>{label}</a>'
            for href, label in nav_links
        )
        links += '<form class="inline-form" method="post" action="/logout"><button type="submit">Logout</button></form>'
    else:
        nav_links.extend([("/login", "Login"), ("/register", "Register")])
        links = "".join(
            f'<a href="{href}"{active_attr if href == active else ""}>{label}</a>'
            for href, label in nav_links
        )
    return links


def render_nav(active: str, user: dict | None = None) -> str:
    links = render_nav_links(active, user)
    return f"""
  <nav>
    <div class="brand"><span class="brand-mark">AT</span>Alumni Tracking</div>
    <div class="nav-links">{links}</div>
  </nav>"""
