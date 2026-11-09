# LionGameStick Development Reports

این پوشه تاریخچهٔ ممیزی و بازیابی فایل‌های باینری پروژه را نگه می‌دارد. گزارش‌ها در `main` ثبت می‌شوند؛ ابزارها و تغییرات فنی هر مرحله فقط در یک شاخهٔ کاری مستقل انجام می‌شوند.

| گزارش | شاخهٔ کاری | موضوع |
|---|---|---|
| [001-binary-recovery-audit.md](001-binary-recovery-audit.md) | `recovery/01-git-history-archive` | بازیابی آرشیو اصلی از Git history و تطبیق فایل‌های استخراج‌شده |
| [002-verified-extraction.md](002-verified-extraction.md) | `recovery/02-verified-extraction` | استخراج مرحله‌ای، بررسی integrity و جلوگیری از overwrite |
| [003-repack-rootfs.md](003-repack-rootfs.md) | `recovery/03-repack-rootfs` | ساخت آرشیو پشتیبان از root filesystem |
| [004-arm-binary-audit.md](004-arm-binary-audit.md) | `recovery/04-arm-binary-audit` | ممیزی معماری ARM، ELF و وابستگی کتابخانه‌ها |
| [005-rockchip-graphics-stack-audit.md](005-rockchip-graphics-stack-audit.md) | `recovery/05-rockchip-graphics-audit` | ممیزی stack گرافیکی Rockchip و افزودن اعتبارسنجی GitHub Actions |

## تاریخچه

- 2026-11-09: بازیابی آرشیو اصلی و ایجاد روش‌های استخراج و بسته‌بندی غیرمخرب.
- 2026-11-09: ایجاد ابزار ممیزی ABI و ممیزی تخصصی stack گرافیکی.
- 2026-11-09: افزودن تست fixture و workflow اعتبارسنجی برای مرحلهٔ پنجم؛ اجرای واقعی workflow هنوز از GitHub تأیید نشده است.
- سیاست محافظه‌کارانه: هیچ باینری صرفاً بر اساس نام فایل یا حدس دربارهٔ مدل SoC جایگزین نمی‌شود.
