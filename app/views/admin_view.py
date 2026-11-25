from html import escape

from app.views.auth_view import _page


def render_admin_dashboard(counts: dict[str, int], users: list[dict], user: dict) -> str:
    stats = "".join(
        f"<li><strong>{count}</strong> {escape(table.replace('_', ' ').title())}</li>"
        for table, count in counts.items()
    )
    rows = "".join(
        f"""<tr><td>{item['id']}</td><td>{escape(item['name'])}</td><td>{escape(item['email'])}</td>
        <td>{escape(item['role'])}</td><td>
        <form class="inline-form" method="post" action="/admin/users/{item['id']}/role">
        <select name="role"><option value="user" {"selected" if item['role'] == 'user' else ""}>user</option>
        <option value="admin" {"selected" if item['role'] == 'admin' else ""}>admin</option></select>
        <button type="submit">Rolü kaydet</button></form>
        <form class="inline-form" method="post" action="/admin/users/{item['id']}/delete">
        <button class="danger" type="submit">Sil</button></form></td></tr>"""
        for item in users
    ) or '<tr><td colspan="5">Kullanıcı yok.</td></tr>'
    body = f"""<h1>Admin Paneli</h1><ul>{stats}</ul>
      <p><a href="/announcements">Duyuruları yönet</a> ·
      <a href="/admin/job-postings">İş ilanlarını yönet</a> ·
      <a href="/api/swagger">API dokümantasyonu</a></p>
      <h2>Kullanıcılar ve roller</h2><table><tr><th>#</th><th>Ad</th><th>E-posta</th><th>Rol</th><th>İşlem</th></tr>{rows}</table>"""
    return _page("Admin Paneli", body, user)


def render_admin_job_postings(postings: list[dict], user: dict) -> str:
    rows = "".join(
        f"""<tr><td>{posting['id']}</td><td>{escape(posting['title'])}</td><td>{escape(posting['company'])}</td>
        <td>{'Aktif' if posting['is_active'] else 'Pasif'}</td><td>
        <form class="inline-form" method="post" action="/admin/job-postings/{posting['id']}/active">
        <input type="hidden" name="is_active" value="{'false' if posting['is_active'] else 'true'}">
        <button type="submit">{'Pasifleştir' if posting['is_active'] else 'Etkinleştir'}</button></form>
        <form class="inline-form" method="post" action="/admin/job-postings/{posting['id']}/delete">
        <button class="danger" type="submit">Sil</button></form></td></tr>"""
        for posting in postings
    ) or '<tr><td colspan="5">İlan yok.</td></tr>'
    options = "".join(
        f'<option value="{kind}">{kind.replace("_", " ").title()}</option>'
        for kind in ("full_time", "part_time", "internship", "contract")
    )
    body = f"""<p><a href="/admin">← Admin Paneli</a></p><h1>İş İlanlarını Yönet</h1>
      <table><tr><th>#</th><th>Başlık</th><th>Şirket</th><th>Durum</th><th>İşlem</th></tr>{rows}</table>
      <h2>Admin ilanı ekle</h2><form method="post" action="/admin/job-postings">
      <label>Başlık</label><input name="title" maxlength="120" required>
      <label>Şirket</label><input name="company" maxlength="150" required>
      <label>Konum</label><input name="location">
      <label>İstihdam türü</label><select name="employment_type">{options}</select>
      <label>Açıklama</label><textarea name="description"></textarea>
      <button type="submit">İlan oluştur</button></form>"""
    return _page("İş İlanlarını Yönet", body, user)
