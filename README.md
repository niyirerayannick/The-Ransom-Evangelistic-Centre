# The Ransom Evangelistic Centre - Django Platform

A modern newspaper/publishing platform for Gashugi Yves / The Ransom Evangelistic Centre, built with Django 5, Tailwind CSS, HTMX/Alpine.js, and SQLite (development).

## Features

- **Multilingual**: English (`/en/`), French (`/fr/`), Kinyarwanda (`/rw/`) via `django-modeltranslation`
- **News Management**: Posts, categories, tags, featured posts, breaking news, scheduled publishing
- **Pages**: Dynamic pages (About, History, What We Do, Contact)
- **Media Hub**: Photo galleries, video embeds, media library
- **Comments**: Reader comments with approval workflow
- **Newsletter**: Subscriber management
- **Accounts**: Custom user roles (Admin, Editor, Author)
- **Search**: Full-text search across posts and pages
- **SEO**: SEO titles, meta descriptions, clean URLs, sitemap-ready
- **Responsive**: Tailwind CSS, mobile-first design
- **WordPress Import**: Management command to import from existing WP database

## Quick Start

```bash
# Clone and enter the project
cd "The Ransom Evangelistic Centre"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit http://localhost:8000/en/ for the site, http://localhost:8000/admin/ for admin.

## WordPress Import

To import content from your existing WordPress MySQL database:

```bash
python manage.py import_wordpress --db-name=wordpress_db --db-user=root --db-password=pass --db-host=localhost
```

Optional flags:
- `--uploads-dir=/path/to/wp-content/uploads` - migrate images
- `--table-prefix=wp_` - custom table prefix (default: wp_)
- `--dry-run` - preview without importing

## Project Structure

```
The Ransom Evangelistic Centre/
├── django_project/       # Project settings, URLs, wsgi
├── apps/
│   ├── core/            # Site settings, menus, sliders, home sections
│   ├── news/            # Posts, categories, tags, views
│   ├── pages/           # Dynamic pages
│   ├── mediahub/        # Galleries, videos, media files
│   ├── comments/        # Reader comments
│   ├── newsletter/      # Email subscribers
│   ├── accounts/        # Custom user model with roles
│   └── search/          # Site search
├── templates/           # HTML templates (Tailwind CSS)
├── static/              # Static assets (CSS input)
├── media/               # User uploads
└── manage.py
```

## Deployment (Coolify)

See [DEPLOYMENT_COOLIFY.md](DEPLOYMENT_COOLIFY.md) for production deployment with persistent SQLite and media volumes.

## Languages

Content is translatable into English, French, and Kinyarwanda. To add/edit translations:
1. Update `LANGUAGES` in settings.py
2. Create/update translation files: `django-admin makemessages -l fr -l rw`
3. Translate strings in `locale/` directories
4. Compile: `django-admin compilemessages`
