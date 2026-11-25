from html import escape

from app.views.auth_view import _page


def render_job_postings(postings: list[dict], user: dict | None = None) -> str:
    rows = "".join(
        f"""<tr><td><a href="/job-postings/{posting['id']}">{escape(posting['title'])}</a></td>
        <td>{escape(posting['company'])}</td><td>{escape(posting.get('location') or '—')}</td>
        <td>{escape(posting['employment_type'].replace('_', ' ').title())}</td>
        <td>{escape(posting.get('deadline') or '—')}</td></tr>"""
        for posting in postings
    ) or '<tr><td colspan="5">Şu anda açık iş ilanı bulunmuyor.</td></tr>'
    return _page(
        "İş İlanları",
        f"""<h1>İş İlanları</h1><table><tr><th>Pozisyon</th><th>Şirket</th><th>Konum</th>
        <th>Tür</th><th>Son başvuru</th></tr>{rows}</table>""",
        user,
    )


def render_job_posting_detail(posting: dict, user: dict | None = None) -> str:
    apply_action = (
        f"""<form method="post" action="/my-applications">
        <input type="hidden" name="job_posting_id" value="{posting['id']}">
        <label>Ön yazı</label><textarea name="cover_letter"></textarea>
        <button type="submit">Başvur</button></form>"""
        if user
        else '<p><a href="/login">Başvurmak için giriş yapın</a></p>'
    )
    body = f"""<p><a href="/job-postings">← Tüm ilanlar</a></p>
        <h1>{escape(posting['title'])}</h1><h2>{escape(posting['company'])}</h2>
        <dl><dt>Konum</dt><dd>{escape(posting.get('location') or 'Belirtilmedi')}</dd>
        <dt>İstihdam türü</dt><dd>{escape(posting['employment_type'].replace('_', ' ').title())}</dd>
        <dt>Son başvuru</dt><dd>{escape(posting.get('deadline') or 'Belirtilmedi')}</dd></dl>
        <p style="white-space:pre-wrap">{escape(posting.get('description') or '')}</p>
        {apply_action}"""
    return _page(posting["title"], body, user)
