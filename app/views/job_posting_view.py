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
    .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }
    .badge-active { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }
    .badge-closed { background: rgba(248, 113, 113, 0.2); color: #f87171; }
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
  {render_nav("/job-postings")}
  <div class="wrap">
    {body}
  </div>
</body>
</html>"""


def render_job_posting_list(postings: list[dict], users: list[dict] | None = None) -> str:
    rows = "".join(
        f"""<tr>
          <td><a href="/job-postings/{p['id']}">{p['id']}</a></td>
          <td><strong>{p['title']}</strong></td>
          <td>{p['company']}</td>
          <td>{p['location']}</td>
          <td>{p['employment_type']}</td>
          <td><span class="badge {'badge-active' if p['is_active'] else 'badge-closed'}">{'Active' if p['is_active'] else 'Closed'}</span></td>
          <td>{p['deadline'] or '-'}</td>
          <td>
            <a href="/job-postings/{p['id']}">View</a> |
            <a href="/job-postings/{p['id']}/edit">Edit</a>
            <form action="/job-postings/{p['id']}/delete" method="POST" class="inline-form" onsubmit="return confirm('Delete this job posting?');">
              <button class="danger" style="padding: 2px 8px; font-size: 12px;">Delete</button>
            </form>
          </td>
        </tr>"""
        for p in postings
    ) or '<tr><td colspan="8" style="color: #94a3b8; text-align: center;">No job postings found.</td></tr>'

    user_options = '<option value="">-- None (Department Posting) --</option>'
    if users:
        user_options += "".join(f'<option value="{u["id"]}">{u["name"]} ({u["email"]})</option>' for u in users)

    body = f"""
      <h1>Job Postings</h1>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Title</th>
            <th>Company</th>
            <th>Location</th>
            <th>Type</th>
            <th>Status</th>
            <th>Deadline</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>

      <h2>Create New Job Posting</h2>
      <form action="/job-postings" method="POST">
        <label>Title</label>
        <input name="title" required placeholder="e.g. Junior Data Analyst" />

        <label>Company</label>
        <input name="company" required placeholder="e.g. Acme Corp" />

        <label>Location</label>
        <input name="location" required placeholder="e.g. Istanbul or Remote" />

        <label>Employment Type</label>
        <select name="employment_type" required>
          <option value="full_time">Full Time</option>
          <option value="part_time">Part Time</option>
          <option value="internship">Internship</option>
          <option value="contract">Contract</option>
        </select>

        <label>Description</label>
        <textarea name="description" required placeholder="Describe responsibilities and requirements..."></textarea>

        <label>Application URL (optional)</label>
        <input name="application_url" type="url" placeholder="https://..." />

        <label>Deadline (optional)</label>
        <input name="deadline" type="date" />

        <label>Posted by User (optional)</label>
        <input name="posted_by_user_id" type="number" placeholder="User ID (leave empty if department)" />

        <button type="submit" style="margin-top: 8px;">Create Job Posting</button>
      </form>
    """
    return _page("Job Postings - Alumni Tracking", body)


def render_job_posting_detail(posting: dict, applications: list[dict] | None = None) -> str:
    app_rows = ""
    if applications:
        app_rows = "".join(
            f"""<tr>
              <td><a href="/applications/{a['id']}">{a['id']}</a></td>
              <td>User #{a['user_id']}</td>
              <td><span class="badge badge-active">{a['status']}</span></td>
              <td>{a.get('cover_letter') or '-'}</td>
              <td>{a.get('created_at', '')}</td>
            </tr>"""
            for a in applications
        )
    else:
        app_rows = '<tr><td colspan="5" style="color: #94a3b8; text-align: center;">No applications submitted yet.</td></tr>'

    body = f"""
      <p><a href="/job-postings">&larr; Back to Job Postings</a></p>
      <h1>{posting['title']}</h1>
      <dl>
        <dt>Company</dt><dd>{posting['company']}</dd>
        <dt>Location</dt><dd>{posting['location']}</dd>
        <dt>Employment Type</dt><dd>{posting['employment_type']}</dd>
        <dt>Status</dt><dd><span class="badge {'badge-active' if posting['is_active'] else 'badge-closed'}">{'Active' if posting['is_active'] else 'Closed'}</span></dd>
        <dt>Deadline</dt><dd>{posting['deadline'] or 'No deadline'}</dd>
        <dt>Application URL</dt><dd>{f'<a href="{posting["application_url"]}" target="_blank">{posting["application_url"]}</a>' if posting.get('application_url') else 'Direct application below'}</dd>
        <dt>Posted By User ID</dt><dd>{posting['posted_by_user_id'] or 'Department'}</dd>
        <dt>Created At</dt><dd>{posting.get('created_at', '-')}</dd>
        <dt>Description</dt><dd style="white-space: pre-wrap;">{posting['description']}</dd>
      </dl>

      <form class="actions">
        <a href="/job-postings/{posting['id']}/edit"><button type="button">Edit Posting</button></a>
        <form action="/job-postings/{posting['id']}/delete" method="POST" class="inline-form" onsubmit="return confirm('Are you sure you want to delete this posting?');">
          <button class="danger">Delete Posting</button>
        </form>
      </form>

      <h2>Apply to this Job</h2>
      <form action="/applications" method="POST" style="margin-bottom: 32px;">
        <input type="hidden" name="job_posting_id" value="{posting['id']}" />
        <label>Your User ID</label>
        <input name="user_id" type="number" required placeholder="Enter your registered User ID" />
        <label>Cover Letter (optional)</label>
        <textarea name="cover_letter" placeholder="Why are you a good fit for this position?"></textarea>
        <button type="submit">Submit Application</button>
      </form>

      <h2>Applicants ({len(applications) if applications else 0})</h2>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Applicant</th>
            <th>Status</th>
            <th>Cover Letter</th>
            <th>Applied At</th>
          </tr>
        </thead>
        <tbody>{app_rows}</tbody>
      </table>
    """
    return _page(f"{posting['title']} - Alumni Tracking", body)


def render_job_posting_edit_form(posting: dict) -> str:
    emp_types = ["full_time", "part_time", "internship", "contract"]
    type_options = "".join(
        f'<option value="{t}" {"selected" if t == posting["employment_type"] else ""}>{t.replace("_", " ").title()}</option>'
        for t in emp_types
    )

    body = f"""
      <p><a href="/job-postings/{posting['id']}">&larr; Cancel</a></p>
      <h1>Edit Job Posting #{posting['id']}</h1>
      <form action="/job-postings/{posting['id']}/edit" method="POST">
        <label>Title</label>
        <input name="title" value="{posting['title']}" required />

        <label>Company</label>
        <input name="company" value="{posting['company']}" required />

        <label>Location</label>
        <input name="location" value="{posting['location']}" required />

        <label>Employment Type</label>
        <select name="employment_type" required>
          {type_options}
        </select>

        <label>Description</label>
        <textarea name="description" required>{posting['description']}</textarea>

        <label>Application URL</label>
        <input name="application_url" type="url" value="{posting.get('application_url') or ''}" />

        <label>Deadline</label>
        <input name="deadline" type="date" value="{posting.get('deadline') or ''}" />

        <label>Is Active?</label>
        <select name="is_active">
          <option value="true" {"selected" if posting['is_active'] else ""}>Active</option>
          <option value="false" {"selected" if not posting['is_active'] else ""}>Closed</option>
        </select>

        <label>Posted By User ID</label>
        <input name="posted_by_user_id" type="number" value="{posting['posted_by_user_id'] or ''}" />

        <button type="submit" style="margin-top: 8px;">Save Changes</button>
      </form>
    """
    return _page(f"Edit {posting['title']} - Alumni Tracking", body)
