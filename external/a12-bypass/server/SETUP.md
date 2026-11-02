# Server Backend Setup

## Directory Structure

```
/var/www/html/
├── public/
│   ├── index.php       (Main Logic)
│   └── cache/          (Publicly accessible storage)
├── templates/
│   ├── bl_structure.sql
│   └── downloads_structure.sql
├── assets/
│   └── Maker/          (Device Configuration Files)
├── logs/
└── cron/
    └── cleanup.php
```

## Installation Steps

1.  **Upload**: Upload the entire contents of the `server` directory to your web host.
2.  **Web Root**: Point your web server (Nginx/Apache) document root to the `public` folder.
3.  **Permissions**: Ensure the `public/cache` and `logs` directories are writable by the web server:
    ```bash
    chmod -R 777 public/cache logs
    ```

## Validation (Auto-Generated)

Because you used the automated `package_builder.sh`, the following complex tasks have been completed for you:

* **Database Templates**: `downloads_structure.sql` has been successfully reconstructed and placed in `templates/`.
* **Asset Migration**: The `Maker` folder has been automatically extracted from your backup and placed in `assets/Maker/`.

**You do not need to manually copy or rename any files.**

## Maintenance

Set up a cron job to run every minute to clean up old payload files:
```bash
* * * * * php /path/to/server/cron/cleanup.php
```
