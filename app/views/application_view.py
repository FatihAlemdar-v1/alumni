from app.views.layout import NAV_STYLE, render_nav

PAGE_STYLE = """
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
           background: #0b1120; color: #e2e8f0; margin: 0; padding: 40px 24px; }
    .wrap { max-width: 860px; margin: 0 auto; }
    h1 { margin-bottom: 24px; }
    h2 { margin-top: 36px; margin-bottom: 16px; font-size: 18px; color: #38bdf8; }
    a { color: #38bdf8; text-decoration: none; }
    a:hover { text-decoration: underline; }
    table { width: 100%; border-collapse: collapse; margin-bottom: 32px; }
    th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid #24314f; font-size: 14px; }
    th { color: #94a3b8; font-weight: 600; }
    form { display: grid; gap: 10px; max-width: 480px; }
    .inline-form { display: inline; margin: 0; }
    label { font-size: 13px; color: #94a3b8; }
    input, select, textarea { padding: 8px 10px; border-radius: 6px; border: 1px solid #24314f;
                              background: #151f38; color: #e2e8f0; font-family: inherit; font-size: 14px; }
    textarea { min-height: 80px; resize: vertical; }
    button { padding: 6px 12px; border-radius: 8px; border: none;
             background: linear-gradient(120deg, #38bdf8, #a78bfa); color: #0b1120;
             font-weight: 600; cursor: pointer; }
    form.actions { display: flex; gap: 8px; max-width: none; }
    .danger { background: #f87171; color: #0b1120; }
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; text-transform: uppercase; }
    .badge-submitted { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }
    .badge-under_review { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .badge-interview { background: rgba(167, 139, 250, 0.2); color: #a78bfa; }
    .badge-accepted { background: rgba(52, 211, 153, 0.2); color: #34d399; }
    .badge-rejected { background: rgba(248, 113, 113, 0.2); color: #f87171; }
    .badge-withdrawn { background: rgba(100, 116, 139, 0.2); color: #64748b; }
    dl { display: grid; grid-template-columns: 180px 1fr; gap: 10px 16px; margin-bottom: 24px; }
    dt { color: #94a3b8; font-size: 13px; }
  </style>
"""


def _page(title: str, body: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>
  {PAGE_STYLE}
  {NAV_STYLE}
</head>
<body>
  {render_nav("/applications")}
  <div class="wrap">
    {body}
  </div>
</body>
</html>"""


def render_application_list(applications: list[dict]) -> str:
    rows = "".join(
        f"""<tr>
          <td><a href="/applications/{a['id']}">{a['id']}</a></td>
          <td><a href="/users/{a['user_id']}">User #{a['user_id']}</a></td>
          <td><a href="/job-postings/{a['job_posting_id']}">Posting #{a['job_posting_id']}</a></td>
          <td><span class="badge badge-{a['status']}">{a['status']}</span></td>
          <td>{a.get('created_at', '-')}</td>
          <td>
            <a href="/applications/{a['id']}">Details</a>
            <form action="/applications/{a['id']}/delete" method="POST" class="inline-form" onsubmit="return confirm('Withdraw/Delete this application?');">
              <button class="danger" style="padding: 2px 8px; font-size: 12px;">Withdraw</button>
            </form>
          </td>
        </tr>"""
        for a in applications
    ) or '<tr><td colspan="6" style="color: #94a3b8; text-align: center;">No applications found.</td></tr>'

    body = f"""
      <h1>Job Applications</h1>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Applicant</th>
            <th>Job Posting</th>
            <th>Status</th>
            <th>Applied At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>

      <h2>Submit a New Application</h2>
      <form action="/applications" method="POST">
        <label>User ID (Applicant)</label>
        <input name="user_id" type="number" required placeholder="e.g. 1" />

        <label>Job Posting ID</label>
        <input name="job_posting_id" type="number" required placeholder="e.g. 1" />

        <label>Cover Letter (optional)</label>
        <textarea name="cover_letter" placeholder="State your motivation..."></textarea>

        <button type="submit" style="margin-top: 8px;">Submit Application</button>
      </form>
    """
    return _page("Applications - Alumni Tracking", body)


def render_application_detail(application: dict) -> str:
    status_options = [
        "submitted",
        "under_review",
        "interview",
        "accepted",
        "rejected",
        "withdrawn",
    ]
    options_html = "".join(
        f'<option value="{s}" {"selected" if s == application["status"] else ""}>{s.replace("_", " ").title()}</option>'
        for s in status_options
    )

    body = f"""
      <p><a href="/applications">&larr; Back to Applications</a></p>
      <h1>Application #{application['id']}</h1>
      <dl>
        <dt>Applicant</dt><dd><a href="/users/{application['user_id']}">User #{application['user_id']}</a></dd>
        <dt>Job Posting</dt><dd><a href="/job-postings/{application['job_posting_id']}">Posting #{application['job_posting_id']}</a></dd>
        <dt>Current Status</dt><dd><span class="badge badge-{application['status']}">{application['status']}</span></dd>
        <dt>Applied At</dt><dd>{application.get('created_at', '-')}</dd>
        <dt>Updated At</dt><dd>{application.get('updated_at', '-')}</dd>
        <dt>Cover Letter</dt><dd style="white-space: pre-wrap;">{application.get('cover_letter') or '<em>No cover letter provided.</em>'}</dd>
      </dl>

      <h2>Update Application Status</h2>
      <form action="/applications/{application['id']}/status" method="POST" style="margin-bottom: 24px;">
        <label>New Status</label>
        <select name="status">
          {options_html}
        </select>
        <button type="submit" style="margin-top: 6px;">Update Status</button>
      </form>

      <form action="/applications/{application['id']}/delete" method="POST" onsubmit="return confirm('Withdraw/Delete this application?');">
        <button class="danger">Withdraw Application</button>
      </form>
    """
    return _page(f"Application #{application['id']} - Alumni Tracking", body)
