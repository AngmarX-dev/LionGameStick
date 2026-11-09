# 006 — تحلیل تکرار payloadهای ELF در stack گرافیکی

- **تاریخ:** 2026-11-09
- **هدف:** بررسی دقیق‌تر باینری‌های گرافیکی پس از inventory واقعی GitHub Actions و شناسایی payloadهای ELF یکسان با نام‌های کتابخانه‌ای متفاوت.
- **شاخهٔ کاری فنی:** `recovery/05-rockchip-graphics-audit`
- **شاخهٔ گزارش:** `main`
- **Commit فنی نهایی این مرحله:** `1353eca546d52c0e7b032d64e67f53a39a5c5d4c`

## وضعیت اولیه و منبع داده

Workflow اجراشده روی commit `2acc91511396f460ffec07a74a64e497456e1b5c` با موفقیت inventory اولیه را تولید کرد. Artifact آن شامل 182 مسیر گرافیکی/نمایشی بود.

- 61 فایل ELF شناسایی شد.
- 121 فایل غیر ELF در محدودهٔ جست‌وجوی نام‌ها ثبت شد.
- تمام ELFهای شناسایی‌شده در این inventory از نوع `ELF32 / ARM` بودند.
- وجود ELF32/ARM به‌تنهایی ABI کامل، hard-float بودن، نسخهٔ libc یا سازگاری با SoC را اثبات نمی‌کند.

## یافته‌های اصلی

اسکریپت جدید `scripts/analyze-elf-duplicates.py` CSV را می‌خواند و فایل‌های ELF با SHA-256 یکسان را گروه‌بندی می‌کند. در artifact اجرای نهایی، شش گروه تکرار شناسایی شد:

| گروه | تعداد مسیر | اندازه | SHA-256 |
|---|---:|---:|---|
| Mali / EGL / GLES / GBM | 28 | 929,956 B | `d0b9599caa87baf1343b314e3b25ad1dbf9d33e3f75d17ceb43ab82a40057329` |
| MiniGUI | 6 | 1,248,260 B | `1ef180c0b2efcea4ba8771f03f77141c04fa7ca7d0c0fb0d0044dfb0528679a5` |
| libdrm | 6 | 46,680 B | `42574fc656e4b8e234533465e244e16b3115d8a0b344e8469738747eb55a742b` |
| libdrm_rockchip | 6 | 9,448 B | `64b27acc6a74f5ddc0179d7425958815600eceea58ddf5a5ea963bde934ce886` |
| libglapi | 6 | 152,980 B | `a01a58fdf2f7efc80f3992163ab2dad313f69863adbb323a439036446fd50bbf` |
| libkms | 6 | 9,464 B | `3f130688c25b613115569162fadd69bc52edd03efba980d7fe73a08f7248ae1c` |

مهم‌ترین مورد، گروه 28‌تایی با payload یکسان است که نام‌هایی مانند `libEGL.so`، `libGLESv2.so`، `libMali.so`، `libMaliOpenCL.so` و `libgbm.so` را در هر دو مسیر `usr/lib` و `usr/lib32` پوشش می‌دهد. همهٔ این نام‌ها به یک محتوای ELF32/ARM با اندازهٔ 929,956 بایت اشاره می‌کنند.

این وضعیت **بسیار مشکوک و نیازمند بررسی مستقیم** است؛ اما هنوز نمی‌توان نتیجه گرفت که فایل‌ها قطعاً خراب‌اند. احتمال دارد snapshot یا بسته‌بندی اولیه عمداً یک blob مشترک ایجاد کرده باشد، ولی این موضوع برای کتابخانه‌هایی با نقش‌های متفاوت غیرعادی است و باید با SONAME، symbol table، ARM attributes، build-id و نسخهٔ منبع تطبیق داده شود.

گروه‌های MiniGUI، libdrm، libdrm_rockchip، libglapi و libkms نیز بین نام‌های نسخه‌ای و مسیرهای lib/lib32 محتوای یکسان دارند. این مورد می‌تواند ناشی از روش بسته‌بندی یا کپی فایل‌ها باشد؛ سازگاری آن هنوز تأیید نشده است.

## تغییرات فنی

- افزوده شد: `scripts/analyze-elf-duplicates.py`
- افزوده شد: `tests/test_analyze_elf_duplicates.py`
- به‌روزرسانی شد: `.github/workflows/graphics-stack-audit.yml`
- Workflow اکنون inventory CSV و گزارش JSON گروه‌های تکراری را به‌صورت artifact منتشر می‌کند.
- یک خطای newline در تولید JSON توسط تست CI شناسایی و اصلاح شد؛ اجرای commit اصلاحی موفق بود.

## تست‌ها و CI

- **Run ID:** `42690757892`
- **Commit بررسی‌شده:** `1353eca546d52c0e7b032d64e67f53a39a5c5d4c`
- **نتیجه:** موفق
- Python syntax compilation: موفق
- fixture tests: موفق، شامل دو تست
- CLI help: موفق
- inventory واقعی مخزن: موفق
- تحلیل گروه‌های تکراری ELF: موفق
- آپلود artifact: موفق
- **Artifact:** `graphics-stack-audit`، شامل `graphics-stack-audit.csv` و `elf-duplicate-audit.json`

[مشاهده اجرای GitHub Actions](https://github.com/AngmarX-dev/LionGameStick/actions/runs/42690757892)

## Build و بررسی سخت‌افزار

- Firmware build: اجرا نشد؛ در این مرحله فقط ابزارهای read-only ممیزی تغییر کردند و build system یا firmware source تغییر نکرد.
- بررسی روی GameStick واقعی: انجام نشد.
- اجرای هیچ‌یک از ELFهای هدف روی میزبان یا دستگاه انجام نشد.
- هیچ باینری runtime حذف، جایگزین یا بازنویسی نشد.

## محدودیت‌ها و مرحلهٔ بعد

گزارش CSV فقط ELF header و DT_NEEDED را استخراج کرده است؛ برای تصمیم دربارهٔ بازیابی باینری‌ها هنوز این موارد لازم‌اند:

1. بررسی مستقیم `readelf -d -n -A -Ws` برای SONAME، build-id، ARM attributes و symbol exports.
2. مقایسهٔ خروجی با نسخهٔ شناخته‌شدهٔ همان BSP/SDK و SoC دقیق دستگاه.
3. بررسی معماری dynamic loader و libc مورد استفادهٔ rootfs.
4. بررسی symlinkها و modeهای فایل در بستهٔ اصلی و مقایسه با snapshot معتبر.
5. تهیهٔ نسخهٔ پشتیبان و hash قبل از هرگونه restore؛ جایگزینی فقط پس از اثبات تطابق ABI.

**نتیجه:** شش گروه payload تکراری ثبت شده‌اند؛ گروه Mali/EGL/GLES/GBM با 28 مسیر اولویت بالای بررسی دارد. هیچ ادعای قطعی دربارهٔ خرابی یا سازگاری و هیچ تغییر مخرب روی باینری‌ها انجام نشده است.
