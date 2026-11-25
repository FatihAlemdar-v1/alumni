from html import escape

from app.views.auth_view import _page


def render_alumni_directory(users: list[dict], current_user: dict | None = None) -> str:
    rows = "".join(
        f"<tr><td>{escape(user['name'])}</td><td>{user['graduation_year']}</td>"
        f"<td>{escape(user['department'])}</td></tr>"
        for user in users
    ) or '<tr><td colspan="3">Henüz mezun kaydı bulunmuyor.</td></tr>'
    body = f"""<h1>Mezunlar</h1>
    <table><tr><th>Ad soyad</th><th>Mezuniyet yılı</th><th>Bölüm</th></tr>{rows}</table>"""
    return _page("Mezunlar", body, current_user)
