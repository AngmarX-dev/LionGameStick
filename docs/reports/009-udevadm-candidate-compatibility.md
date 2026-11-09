# 009 — ارزیابی سازگاری نامزد ARM برای udevadm

- تاریخ: 2026-11-10
- هدف: بررسی تطابق نسخه، ABI، وابستگی‌ها و رابط فرمان نامزد ARM با daemon و اسکریپت راه‌اندازی udev.
- شاخهٔ فنی: `recovery/05-rockchip-graphics-audit`
- commit فنی: `acbe1fe090a6977882d4ba74486a503185ff8a57`
- شاخهٔ گزارش: `main`

## وضعیت اولیه

گزارش 008 یک نسخهٔ ARM از `udevadm` را از `usr/bin/udevadm` شناسایی و در مسیر ایزولهٔ `recovery-candidates/udevadm/sbin-udevadm.armhf` نگهداری کرد. فایل runtime در `sbin/udevadm` همچنان ELF64/x86-64 است.

## بررسی‌های انجام‌شده

فایل‌ها و مسیرهای زیر بررسی شدند:
- `sbin/udevadm`، `usr/bin/udevadm`، `sbin/udevd`
- `etc/init.d/S10udev`، `etc/init.d/rcS`، `etc/inittab`
- `etc/profile` و `etc/udev/udev.conf`
- درخت کتابخانه‌ها و dynamic loader در `lib/`، `lib32/`، `usr/lib/` و `usr/lib32/`

### تطبیق نسخه و رفتار

- رشته‌های داخلی نامزد ARM شامل `udev-3.2.7` است.
- رشته‌های daemon شامل `starting version 3.2.7` و `starting eudev-3.2.7` است.
- بنابراین شواهد قوی وجود دارد که نامزد و daemon به یک release از خانوادهٔ eudev تعلق دارند؛ با این حال manifest بسته یا provenance ساخت در مخزن پیدا نشد.
- اسکریپت `S10udev` از فرمان‌های `udevadm trigger`، `udevadm settle --timeout=30` و `udevadm control --stop-exec-queue` استفاده می‌کند. رشته‌ها و help داخلی نامزد ARM وجود زیر‌فرمان‌های trigger، settle و control و گزینه‌های مورد استفاده را نشان می‌دهند.
- این تطبیق استاتیک است و جایگزین smoke test اجرای واقعی نیست.

### ABI و dependency closure

- نامزد ARM از ELF32/ARM little-endian و interpreter برابر `/lib/ld-linux-armhf.so.3` استفاده می‌کند.
- DT_NEEDED ثبت‌شده: `libblkid.so.1`، `libuuid.so.1`، `libkmod.so.2`، `libz.so.1` و `libc.so.6`.
- کتابخانه‌های ARM متناظر و loader در rootfs وجود دارند؛ پس از نظر حضور فایل‌ها، dependency closure اولیه کامل به نظر می‌رسد. بارگذاری واقعی و symbol-version resolution روی target آزمایش نشده است.
- `sbin/udevd` نیز ARM و از خانوادهٔ eudev 3.2.7 است. در مقابل، `sbin/udevadm` فعلی x86-64 و وابسته به `libsystemd-shared-261.so` است؛ این تفاوت با daemon مبتنی بر eudev ناسازگاری روشن در خانوادهٔ بسته‌بندی را نشان می‌دهد.

### PATH و راه‌اندازی

- `S10udev`، daemon را با مسیر مطلق `/sbin/udevd` اجرا می‌کند اما `udevadm` را بدون مسیر کامل فراخوانی می‌کند.
- `/etc/profile` مقدار `/bin:/sbin:/usr/bin:/usr/sbin` را export می‌کند، ولی این فایل مربوط به login shell است.
- BusyBox init از `/etc/inittab`، اسکریپت `/etc/init.d/rcS` را اجرا می‌کند؛ در زنجیرهٔ بررسی‌شده PATH صریحی پیش از اجرای `S10udev` تنظیم نشده است.
- در نتیجه، resolve شدن `udevadm` به نسخهٔ `/usr/bin/udevadm` در boot هنوز اثبات نشده و باید مقدار PATH واقعی init روی دستگاه یا از تنظیمات دقیق BusyBox تعیین شود.

## تغییرات

در شاخهٔ فنی، فایل زیر اضافه شد:
- `recovery-candidates/udevadm/COMPATIBILITY.md`

این یادداشت نتیجهٔ ارزیابی و شروط لازم پیش از promotion را ثبت می‌کند. هیچ فایل runtime تغییر نکرد.

## تست‌ها و CI

- GitHub Actions Run ID: `42696627843`
- نتیجه: `completed / success`
- URL: https://github.com/AngmarX-dev/LionGameStick/actions/runs/42696627843
- نصب binutils، py_compile، تمام fixture tests، CLI help، inventory گرافیکی، inventory جامع ELF و artifact upload همگی موفق شدند.
- Artifact: `complete-binary-analysis`، شناسهٔ `13709840911`.

## Build و سخت‌افزار

- Firmware build: اجرا نشد؛ این مرحله ارزیابی استاتیک بوده و toolchain/build process کامل هدف در دسترس این workflow نبود.
- اجرای نامزد ARM: انجام نشد.
- آزمایش PATH، hotplug، ساخت device node و shutdown روی GameStick: انجام نشد.
- `sbin/udevadm` و سایر فایل‌های runtime دست‌نخورده باقی ماندند.

## نتیجه و گام بعدی

نامزد ARM از نظر معماری، ABI، dependency presence، رشتهٔ نسخه و فرمان‌های موردنیاز با daemon eudev 3.2.7 هم‌راستایی قوی دارد و اکنون یک candidate معتبرتر برای آزمایش محسوب می‌شود؛ اما هنوز مجوز جایگزینی runtime را ندارد.

گام بعدی باید تعیین PATH مؤثر BusyBox init و سپس اجرای smoke test در محیط target قابل‌بازیابی باشد. تنها پس از موفقیت این آزمون‌ها می‌توان دربارهٔ جایگزینی `sbin/udevadm` تصمیم گرفت.
