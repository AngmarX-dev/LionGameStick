# LionGameStick Development Reports

این پوشه تاریخچهٔ ممیزی و بازیابی فایل‌های باینری پروژه را نگه می‌دارد. گزارش‌ها در `main` ثبت می‌شوند؛ ابزارها و تغییرات فنی هر مرحله فقط در یک شاخهٔ کاری مستقل انجام می‌شوند.

| گزارش | شاخهٔ کاری | موضوع |
|---|---|---|
| [001-binary-recovery-audit.md](001-binary-recovery-audit.md) | `recovery/01-git-history-archive` | بازیابی آرشیو اصلی از Git history و تطبیق فایل‌های استخراج‌شده |
| [002-verified-extraction.md](002-verified-extraction.md) | `recovery/02-verified-extraction` | استخراج مرحله‌ای، بررسی integrity و جلوگیری از overwrite |
| [003-repack-rootfs.md](003-repack-rootfs.md) | `recovery/03-repack-rootfs` | ساخت آرشیو پشتیبان از root filesystem |
| [004-arm-binary-audit.md](004-arm-binary-audit.md) | `recovery/04-arm-binary-audit` | ممیزی معماری ARM، ELF و وابستگی کتابخانه‌ها |
| [005-rockchip-graphics-stack-audit.md](005-rockchip-graphics-stack-audit.md) | `recovery/05-rockchip-graphics-audit` | ممیزی اولیه stack گرافیکی و ساخت ابزار inventory |
| [006-elf-duplicate-payload-analysis.md](006-elf-duplicate-payload-analysis.md) | `recovery/05-rockchip-graphics-audit` | تحلیل تکرار payloadهای ELF و شناسایی نامزدهای مشکوک |
| [007-complete-binary-and-elf-audit.md](007-complete-binary-and-elf-audit.md) | `recovery/05-rockchip-graphics-audit` | inventory جامع 769 فایل binary-like و تحلیل عمیق 591 فایل ELF |
| [008-udevadm-arm-recovery-candidate.md](008-udevadm-arm-recovery-candidate.md) | `recovery/05-rockchip-graphics-audit` | ردیابی udevadm ناسازگار و نگهداری نامزد ARM در مسیر ایزوله |
| [009-udevadm-candidate-compatibility.md](009-udevadm-candidate-compatibility.md) | `recovery/05-rockchip-graphics-audit` | تطبیق نسخهٔ eudev، ABI، وابستگی‌ها و مسیر PATH در زمان boot |

## تاریخچه

- 2026-11-09: بازیابی آرشیو اصلی و ایجاد روش‌های استخراج و بسته‌بندی غیرمخرب.
- 2026-11-09: ایجاد ابزار ممیزی ABI و ممیزی تخصصی stack گرافیکی.
- 2026-11-09: تحلیل گروه‌های hash یکسان ELF؛ شش گروه تکراری شناسایی شد.
- 2026-11-09: ممیزی جامع کل مخزن؛ 769 فایل binary-like شناسایی و 591 فایل ELF تحلیل شد.
- 2026-11-09: یافتن نامزد ARM برای `sbin/udevadm` و نگهداری آن در `recovery-candidates/` بدون تغییر runtime.
- 2026-11-10: ارزیابی استاتیک نامزد ARM؛ نسخهٔ eudev 3.2.7 و وابستگی‌های آن با daemon هم‌راستا هستند، اما PATH مؤثر init و رفتار واقعی هنوز باید روی target آزمایش شود.
- سیاست محافظه‌کارانه: هیچ باینری صرفاً بر اساس نام فایل یا حدس دربارهٔ مدل SoC جایگزین نمی‌شود.
