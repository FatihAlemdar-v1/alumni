# Alumni Connect UI/UX Design Architecture

> This project-specific design system is informed by the plain-text design-system approach described in [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md). The reference is used for structure and consistency, not as a source of copied site designs.

## Product and Design Principles

- **Reconnect first:** Make the alumni directory, career opportunities, and announcements easy to discover.
- **Editorial, not corporate stock:** Use warm surfaces, considered typography, generous spacing, and restrained color.
- **Useful before decorative:** Every card, badge, and call to action should clarify information or provide a next step.
- **Consistent across CRUD pages:** Lists, detail views, and forms share navigation, spacing, controls, and status patterns.
- **Mobile-first:** Prioritize readable content and reachable actions on narrow screens, then enhance layouts for larger viewports.

## Design Tokens

| Token | Value | Application |
| --- | --- | --- |
| `color.ink` | `#1a252f` | Primary text, navigation, and dark call-to-action surfaces. |
| `color.accent` | `#e67e22` | Primary actions, highlights, links, and focus indicators. |
| `color.paper` | `#f7f5f0` | Main application canvas. |
| `color.surface` | `#ffffff` | Cards, forms, and elevated content. |
| `color.muted` | `#64727c` | Supporting copy and metadata. |
| `color.line` | `#e7e2d9` | Dividers, borders, and table rules. |
| `color.success` | `#49675b` | Positive and secondary community accents. |
| `font.heading` | Merriweather, Georgia, serif | Page titles and editorial section headings. |
| `font.body` | Inter, Segoe UI, sans-serif | Body text, navigation, forms, and tables. |
| `radius.card` | `12px` | Cards, panels, and grouped content. |
| `radius.control` | `8px` | Buttons, inputs, and compact interactive controls. |

Use the tokens consistently rather than introducing one-off colors. Dark navy may be used for a high-emphasis panel, but long-form text and data tables should remain on light, readable surfaces.

## Layout and Responsive Behavior

- Use a centered content container with a maximum width near `1120px` and comfortable side gutters.
- Build page sections with CSS Grid or Flexbox; avoid fixed-width layouts.
- At tablet widths, collapse multi-column hero and content layouts to a single column.
- At phone widths, stack card grids and form controls; allow navigation links to wrap without horizontal scrolling.
- Keep primary actions visible and comfortably tappable; retain clear separation between destructive and ordinary actions.
- Respect `prefers-reduced-motion` and avoid motion as the only feedback mechanism.

## Shared Components

1. **Site navigation:** Brand mark and name, links to the main web sections, and an API documentation link. Indicate the current section accessibly.
2. **Primary and secondary buttons:** Orange filled primary action; neutral outlined secondary action. Destructive actions use a distinct warning treatment and require confirmation when data will be removed.
3. **Cards:** White surface, subtle border, restrained shadow on hover, clear heading, short supporting copy, and a visible destination or action.
4. **Forms:** Persistent labels, required/optional wording, native input types, visible validation feedback, and grouped submit/cancel actions.
5. **Status badges:** Pair concise text with a distinguishable treatment; never communicate application status by color alone.
6. **Tables and lists:** Use readable column labels and row actions on desktop. On narrow screens, prioritize essential fields and avoid forcing page-wide horizontal scroll.
7. **Empty and error states:** Explain what is missing and provide a meaningful next action. The 404 page links back to the home page.

## Page-by-Page Design

The page designs below map to the existing server-rendered routes. They describe the intended layout and behavior; dynamic records and counts must come from the application rather than invented sample data.

| Page | Route | Structure and key interactions |
| --- | --- | --- |
| Home | `GET /` | Warm editorial hero with a clear alumni-network message and links to the directory and jobs. Follow with community entry cards for graduates, jobs, and announcements. Keep artwork decorative and avoid fabricated statistics. |
| About | `GET /about` | Narrow reading column, concise project introduction, key project facts in a responsive card grid, and a chronological project timeline. End with a home link. |
| Alumni directory | `GET /users` | Page title and clear add-user form paired with a scannable directory table. Show name, email, graduation year, department, and row actions. Provide an explicit empty state. |
| Create alumni record | `POST /users` | Inline form on the directory page. Require name, email, graduation year, and department; preserve entered values and show validation feedback if the submission fails. |
| Alumni profile | `GET /users/{user_id}` | Profile-style detail card with the graduate's name as the focal point and email, graduation year, and department as labeled facts. Offer edit and return-to-directory actions. |
| Edit alumni profile | `GET, POST /users/{user_id}/edit` | Pre-filled, labeled form with validation feedback, a clear save action, and a cancel link to the profile. |
| Announcements | `GET /announcements` | Community bulletin list with title, author, publication date, and a clear detail action. Place the create form after or beside the list, collapsing to one column on mobile. |
| Announcement detail | `GET /announcements/{announcement_id}` | Editorial reading view with title, author/date metadata, readable long-form content, and edit/back links. |
| Edit announcement | `GET, POST /announcements/{announcement_id}/edit` | Pre-filled title, content, and author fields. Keep the primary save action distinct from the cancel/back link. |
| Job board | `GET /job-postings` | Job cards or a responsive table showing title, company, optional location, employment type, status, and deadline. Put the posting form in a clearly separated section. |
| Job detail | `GET /job-postings/{posting_id}` | Position title and company lead the page. Group location, employment type, deadline, and application details; include an application form and applicant list where appropriate. |
| Edit job posting | `GET, POST /job-postings/{posting_id}/edit` | Pre-filled posting form, optional location and description, clear active/closed status control, and separate save/cancel actions. |
| Applications | `GET /applications` | Application tracking table with applicant, job, status, and submission date. Include a clearly labeled application form and a useful empty state. |
| Application detail | `GET /applications/{application_id}` | Show applicant, linked job, cover letter, submitted/updated dates, and a textual status badge. Put status update and withdrawal actions in separate groups. |
| Not found | Any unmatched web route | Branded 404 message with a single, prominent route back to the home page. API routes return the documented JSON error contract instead. |
| API documentation | `GET /docs` or `/api/swagger` | Use FastAPI's Swagger UI for endpoint discovery and request testing; preserve its native interaction and accessibility patterns. |

### Home Page Composition

1. **Header:** Alumni Connect mark, primary section links, and a high-emphasis link to API documentation.
2. **Hero:** Alumni-network headline, one short value proposition, and directory/jobs calls to action. A small abstract connection illustration supports, but does not compete with, the message.
3. **Community summary:** A concise statement of the product's three areas: alumni profiles, career opportunities, and announcements.
4. **Discovery cards:** Three equal-priority links to the directory, job board, and announcements.
5. **Closing call to action and footer:** Repeat a single useful next step and provide project/API links.

## Interaction, Accessibility, and Content Rules

- Use semantic landmarks, a single page-level heading, descriptive link labels, and correctly associated form labels.
- Keep keyboard focus visible and maintain sensible tab order.
- Ensure text and controls meet WCAG AA contrast expectations where practical.
- Use `aria-hidden` only for decorative visuals; provide alternative text for meaningful images.
- Use text labels for statuses and validation messages; color is supplemental.
- Confirm destructive actions and avoid presenting a destructive button as the primary action.
- Render user-supplied content safely and preserve line breaks only in content areas designed for them.
- Use Turkish for user-facing page copy; keep code comments and docstrings in English.

## Design Reference

The [VoltAgent/awesome-design-md collection](https://github.com/VoltAgent/awesome-design-md) describes `DESIGN.md` as a portable, human- and agent-readable source of design tokens, patterns, and rules. This document applies that format to Alumni Connect's existing routes, visual identity, and responsive needs.
