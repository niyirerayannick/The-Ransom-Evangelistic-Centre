# Coolify Deployment Guide — The Ransom Evangelistic Centre

Deploy with your **existing local SQLite database and media**. Do not re-import WordPress data or run seed commands on production.

## What production uses

| Resource | Container path | Host persistent path (Coolify) |
|----------|----------------|--------------------------------|
| SQLite database | `/app/data/db.sqlite3` | `/data/yvesgashugi/data` |
| Uploaded media | `/app/media/` | `/data/yvesgashugi/media` |
| Collected static | `/app/staticfiles/` | (ephemeral — rebuilt on each deploy) |

Production startup runs **only**:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn django_project.wsgi:application --bind 0.0.0.0:8000
```

It does **not** run `seed_homepage`, `import_wordpress_data`, `seed_donation_data`, `seed_counsellor_data`, or any other seed/import commands.

---

## A. On your local computer

1. Stop the development server.
2. Apply migrations locally:

   ```bash
   python manage.py migrate
   ```

3. Confirm your data exists:

   ```bash
   python manage.py shell
   ```

   ```python
   from apps.news.models import Post
   from apps.pages.models import Page
   Post.objects.count()
   Page.objects.count()
   ```

4. Note your local files:
   - `db.sqlite3` (project root)
   - `media/` (project root — all subfolders)

---

## B. Copy local database and media (required)

**Coolify does not copy your local database automatically.** You must upload it once (and again whenever you want to refresh production from local).

If the server already started with an **empty** database, replace it:

1. Stop the Coolify application (or scale to 0).
2. Delete the empty file on the server: `/data/yvesgashugi/data/db.sqlite3`
3. Upload your local copy (steps below).
4. Redeploy / restart.

### Option 1 — PowerShell script (Windows)

From the project root, after `python manage.py migrate`:

```powershell
.\scripts\push_production_data.ps1 -Server "root@YOUR_SERVER_IP"
```

Replace `YOUR_SERVER_IP` with your Coolify server address.

### Option 2 — Manual `scp`

```bash
# On your PC (Git Bash or WSL), from the project folder:
python manage.py migrate

scp db.sqlite3 root@YOUR_SERVER_IP:/data/yvesgashugi/data/db.sqlite3
scp -r media/* root@YOUR_SERVER_IP:/data/yvesgashugi/media/
```

### Option 3 — Coolify / SSH file manager

Upload directly on the server:

- `db.sqlite3` → `/data/yvesgashugi/data/db.sqlite3`
- `media/*` → `/data/yvesgashugi/media/`

**Important:** The file must be named exactly `db.sqlite3` and sit inside the folder mounted to `/app/data`.

---

## C. On the server — create folders

```bash
sudo mkdir -p /data/yvesgashugi/data
sudo mkdir -p /data/yvesgashugi/media
sudo chown -R 1000:1000 /data/yvesgashugi
```

Upload:

- `db.sqlite3` → `/data/yvesgashugi/data/db.sqlite3`
- `media/*` → `/data/yvesgashugi/media/`

---

## D. In Coolify

1. Create a new application from your Git repository.
2. Build pack: **Dockerfile**.
3. Expose port **8000**.
4. Add **persistent storage** (bind mounts):

   | Host path | Container path |
   |-----------|------------------|
   | `/data/yvesgashugi/data` | `/app/data` |
   | `/data/yvesgashugi/media` | `/app/media` |

5. Ensure the database file is at `/data/yvesgashugi/data/db.sqlite3` **before** the first deploy (or immediately after creating volumes).

---

## E. Environment variables in Coolify

```env
DEBUG=False
SECRET_KEY=strong-secret-key-here
ALLOWED_HOSTS=yvesgashugi.org,www.yvesgashugi.org
CSRF_TRUSTED_ORIGINS=https://yvesgashugi.org,https://www.yvesgashugi.org
SQLITE_DB_PATH=/app/data/db.sqlite3
MEDIA_ROOT=/app/media
STATIC_ROOT=/app/staticfiles
MAINTENANCE_MODE=True
```

Replace domain and `SECRET_KEY` with your real values.

**Maintenance mode:** While `MAINTENANCE_MODE=True`, public visitors see the coming-soon page. Dashboard and admin remain available.

---

## F. Deploy

Push your code (with `Dockerfile` and `start.sh`), then deploy in Coolify.

Check container logs. If the database was not uploaded or mounted, startup **stops** with:

```
ERROR: SQLite database not found at /app/data/db.sqlite3
```

Upload your local `db.sqlite3`, confirm the volume mount, then redeploy.

---

## G. Verify after deploy

- [ ] `https://your-domain.com/dashboard/login/` — login works
- [ ] `https://your-domain.com/admin/` — Django admin works
- [ ] Public homepage shows **coming soon** (503) while maintenance is on
- [ ] Dashboard shows existing posts, pages, team, donations, counsellors
- [ ] Media images load (e.g. post thumbnails, team photos)
- [ ] `/health/` returns `ok`

Quick shell check (Coolify terminal or `docker exec`):

```bash
python manage.py shell -c "from apps.news.models import Post; print(Post.objects.count())"
```

The count should match your local database.

---

## H. Launch the public website

When you are ready to go live:

1. In Coolify, set `MAINTENANCE_MODE=False`
2. In **Dashboard → Site Settings → Maintenance**, turn maintenance **OFF**
3. Redeploy or restart the container

The live site will use the same database and media — no re-import needed.

---

## Troubleshooting

| Problem | Likely cause | Fix |
|---------|----------------|-----|
| Empty site / no posts | Database not mounted | Check volume `/data/yvesgashugi/data` → `/app/data` and file exists |
| Broken images | Media not mounted | Check volume `/data/yvesgashugi/media` → `/app/media` |
| 400 Bad Request | `ALLOWED_HOSTS` | Add your domain |
| CSRF error on login | `CSRF_TRUSTED_ORIGINS` | Add `https://your-domain.com` |
| Static CSS missing | `collectstatic` failed | Check logs; ensure `STATIC_ROOT=/app/staticfiles` |
| Demo/seed data appeared | Seed command ran manually | Do not run seed/import commands on production |

---

## Local development (unchanged)

Without environment variables, Django uses:

- `db.sqlite3` in the project root
- `media/` in the project root
- `DEBUG=True` by default

Legacy env names still work: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_DB_PATH`.
