from html import escape

from app.views.layout import NAV_STYLE, render_nav
from app.views.user_view import PAGE_STYLE


def _page(title: str, body: str, user: dict | None = None) -> str:
    return f"""<!DOCTYPE html>
<html lang="tr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>{PAGE_STYLE}{NAV_STYLE}</head><body>
{render_nav("", user)}<main class="wrap">{body}</main></body></html>"""


def render_auth_form(
    register: bool, error: str | None = None, next_url: str = "/"
) -> str:
    if register:
        fields = """
      <label>Ad</label><input name="first_name" maxlength="50" required autocomplete="given-name">
      <label>Soyad</label><input name="last_name" maxlength="50" required autocomplete="family-name">
      <label>E-posta</label><input type="email" name="email" maxlength="255" required autocomplete="email">
      <label>Mezuniyet yılı</label><input type="number" name="graduation_year" min="1950" max="2100" required>
      <label>Bölüm</label><input name="department" maxlength="100" required>
      <label>Şifre (en az 10 karakter)</label><input type="password" name="password" minlength="10" maxlength="72" required autocomplete="new-password">"""
        action, title, button = "/register", "Kayıt Ol", "Hesap oluştur"
    else:
        fields = f"""
      <label>E-posta</label><input type="email" name="email" required autocomplete="email">
      <label>Şifre</label><input type="password" name="password" required autocomplete="current-password">
      <input type="hidden" name="next" value="{escape(next_url)}">"""
        action, title, button = "/login", "Giriş Yap", "Giriş yap"
    message = f'<p role="alert" style="color:#f87171">{escape(error)}</p>' if error else ""
    body = f"""<h1>{title}</h1>{message}<form method="post" action="{action}">{fields}
      <button type="submit">{button}</button></form>"""
    return _page(title, body)


def render_profile(user: dict, error: str | None = None, saved: bool = False) -> str:
    message = '<p>Profil güncellendi.</p>' if saved else ""
    if error:
        message = f'<p role="alert" style="color:#f87171">{escape(error)}</p>'
    body = f"""<h1>Profilim</h1>{message}
      <form method="post" action="/profile">
      <label>Ad soyad</label><input name="name" maxlength="100" value="{escape(str(user['name']))}" required>
      <label>E-posta</label><input type="email" name="email" maxlength="255" value="{escape(str(user['email']))}" required>
      <label>Mezuniyet yılı</label><input type="number" name="graduation_year" min="1950" max="2100" value="{user['graduation_year']}" required>
      <label>Bölüm</label><input name="department" maxlength="100" value="{escape(str(user['department']))}" required>
      <button type="submit">Kaydet</button></form>"""
    return _page("Profilim", body, user)


def render_my_applications(applications: list[dict], user: dict) -> str:
    rows = "".join(
        f"""<tr><td>{item['id']}</td><td>{item['job_posting_id']}</td><td>{escape(item['status'])}</td>
        <td><form method="post" action="/my-applications/{item['id']}/delete">
        <button class="danger" type="submit">Başvuruyu geri çek</button></form></td></tr>"""
        for item in applications
    ) or '<tr><td colspan="4">Henüz başvurunuz yok.</td></tr>'
    body = f"""<h1>Başvurularım</h1><table><tr><th>#</th><th>İlan</th><th>Durum</th><th></th></tr>{rows}</table>
      <h2>İlana başvur</h2><form method="post" action="/my-applications">
      <label>İlan numarası</label><input type="number" name="job_posting_id" min="1" required>
      <label>Ön yazı</label><textarea name="cover_letter"></textarea><button type="submit">Başvur</button></form>"""
    return _page("Başvurularım", body, user)


def render_my_job_postings(postings: list[dict], user: dict) -> str:
    rows = "".join(
        f"""<tr><td>{posting['id']}</td><td>{escape(posting['title'])}</td><td>{escape(posting['company'])}</td>
        <td><form method="post" action="/my-job-postings/{posting['id']}/delete">
        <button class="danger" type="submit">Sil</button></form></td></tr>"""
        for posting in postings
    ) or '<tr><td colspan="4">Henüz ilan oluşturmadınız.</td></tr>'
    options = "".join(
        f'<option value="{kind}">{kind.replace("_", " ").title()}</option>'
        for kind in ("full_time", "part_time", "internship", "contract")
    )
    body = f"""<h1>Oluşturduğum İlanlar</h1><table><tr><th>#</th><th>Başlık</th><th>Şirket</th><th></th></tr>{rows}</table>
      <h2>Yeni ilan</h2><form method="post" action="/my-job-postings">
      <label>Başlık</label><input name="title" maxlength="120" required>
      <label>Şirket</label><input name="company" maxlength="150" required>
      <label>Konum</label><input name="location">
      <label>İstihdam türü</label><select name="employment_type">{options}</select>
      <label>Açıklama</label><textarea name="description"></textarea><button type="submit">İlan oluştur</button></form>"""
    return _page("Oluşturduğum İlanlar", body, user)
