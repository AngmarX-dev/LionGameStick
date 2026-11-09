# 007 — ممیزی جامع باینری‌ها و تحلیل عمیق ELF

- تاریخ: 2026-11-09
- هدف: شناسایی فایل‌های باینری در کل مخزن، تشخیص قالب واقعی، استخراج ABI و وابستگی ELF و یافتن فایل‌های مشکوک به معماری اشتباه.
- شاخهٔ فنی: `recovery/05-rockchip-graphics-audit`
- commit فنی: `4b8353a5e287b7738804d6f672689cfa8ed3ab2c`
- شاخهٔ گزارش: `main`

## وضعیت اولیه و مسئله

ممیزی قبلی فقط روی مسیرهای مرتبط با گرافیک تمرکز داشت. برای بررسی کامل‌تر، یک اسکنر read-only اضافه شد که تمام فایل‌های repository را از نظر signature، نوع فایل، اندازه و SHA256 بررسی می‌کند و برای ELFها از GNU readelf استفاده می‌کند. هیچ فایل اجرایی هدف اجرا نشد و هیچ runtime binary تغییر نکرد.

## فایل‌های بررسی‌شده و تغییرات

افزوده شد:
- `scripts/audit-all-binaries.py`: شناسایی فایل‌های binary-like در کل درخت، طبقه‌بندی Magic Bytes، محاسبه SHA256، استخراج metadata با `readelf -h -l -d -n -A -Ws` و نمونه‌ای محدود از رشته‌های ASCII.
- `tests/test_audit_all_binaries.py`: تست fixture برای ELF، ZIP، باینری ناشناخته، symlink و حذف فایل متنی معمولی از inventory.
- `.github/workflows/graphics-stack-audit.yml`: اجرای اسکن جامع و انتشار artifact شامل CSV و JSON.

ابزارهای قبلی graphics audit و duplicate ELF analysis نیز در workflow اجرا شدند.

## نتایج اسکن کل مخزن

Workflow روی commit فنی فوق اجرا شد و خروجی واقعی آن:

| طبقه‌بندی | تعداد |
|---|---:|
| ELF | 591 |
| باینری با signature ناشناخته | 148 |
| GIF | 12 |
| PNG | 1 |
| فایل خالی | 11 |
| فایل دارای پسوند shared-library ولی بدون ELF magic | 2 |
| فایل دارای پسوند binary | 4 |
| **مجموع ورودی‌های binary-like** | **769** |

148 مورد ناشناخته به معنی خرابی نیستند. بررسی پسوندها و مسیرها نشان می‌دهد بخش عمده شامل cursorهای CUR، تصاویر BMP/ICO، فونت‌های TTF، فایل‌های terminfo، cache و منابع MiniGUI است. چهار فایل `.bin` شناسایی‌شده نیز منابع فونت MiniGUI هستند. دو فایل `libgcc_s.so` باید جداگانه به‌عنوان linker script یا فایل متنی بررسی شوند؛ صرف پسوند، ELF بودن را ثابت نمی‌کند.

## نتایج تحلیل ELF

هر 591 فایل ELF با readelf قابل‌خواندن بود:

| ویژگی | نتیجه |
|---|---:|
| ELF32 / ARM | 590 |
| ELF64 / x86-64 | 1 |
| نوع executable | 318 |
| نوع shared object | 272 |
| PIE executable | 1 |
| دارای SONAME | 270 |
| دارای Build ID | 31 |
| دارای ARM interpreter | 326 |
| دارای x86-64 interpreter | 1 |

مشخصات ARM:
- 560 فایل دارای attributes با CPU name برابر Cortex-A7، معماری ARMv7-A و FP VFPv4 هستند.
- 30 فایل ARMv7-A با FP VFPv3 و CPU name برابر 7-A گزارش شده‌اند.
- 590 فایل ARM از نوع ELF32 و little-endian هستند.
- بخش عمده executableهای ARM از interpreter برابر `/lib/ld-linux-armhf.so.3` استفاده می‌کنند.

### یافتهٔ پرریسک: sbin/udevadm

فایل `sbin/udevadm` تنها ELF خارج از معماری ARM در inventory است:
- ELF64، x86-64، little-endian
- interpreter: `/lib64/ld-linux-x86-64.so.2`
- وابستگی‌ها: `libm.so.6`، `libsystemd-shared-261.so` و `libc.so.6`
- Build ID: `cd454fe47ffb3b554940652351b3df4513f4e197`

در مقابل، `sbin/udevd` و سایر executableهای بررسی‌شده در مسیرهای سیستم ARM هستند. بنابراین `sbin/udevadm` یک ناسازگاری معماری قطعی نسبت به rootfs مبتنی بر ARM است و در محیط ARM معمولی قابل اجرا نخواهد بود. هنوز مشخص نیست این فایل عمداً برای ابزار host نگه داشته شده یا اشتباهاً وارد rootfs شده است؛ پیش از حذف یا جایگزینی باید تاریخچه Git، نحوهٔ فراخوانی آن و نسخهٔ معتبر ARM بررسی شود.

## بررسی تکرار payloadها

شش گروه محتوای ELF یکسان مجدداً تأیید شدند:
- Mali/EGL/GLES/GBM: 28 مسیر، 14 نام پایه، 929,956 بایت.
- MiniGUI: 6 مسیر، 3 نام پایه، 1,248,260 بایت.
- libdrm: 6 مسیر، 3 نام پایه، 46,680 بایت.
- libdrm_rockchip: 6 مسیر، 3 نام پایه، 9,448 بایت.
- libglapi: 6 مسیر، 3 نام پایه، 152,980 بایت.
- libkms: 6 مسیر، 3 نام پایه، 9,464 بایت.

برای نمونه، تمام 28 نام Mali/EGL/GLES/GBM یک ELF32/ARM با این مشخصات هستند:
- SONAME: `libmali.so.1`
- Build ID: `f56d0ce5a4ff4d39df6963e01a0a84d8a0905c25`
- ARMv7-A، VFPv3، hard-float VFP argument convention
- DT_NEEDED: `libpthread.so.0`، `libm.so.6`، `libdl.so.2`، `librt.so.1`، `libc.so.6` و `ld-linux-armhf.so.3`

این خروجی نشان می‌دهد نام‌های مختلف در واقع نسخه‌های هم‌محتوای همان payload با SONAME یکسان هستند؛ می‌تواند ناشی از روش packaging یا aliasهای کپی‌شدهٔ BSP باشد و به‌تنهایی خرابی را ثابت نمی‌کند. تطبیق با BSP اصلی Rockchip و ساختار symlink مورد انتظار همچنان لازم است.

## تست‌ها و CI

GitHub Actions:
- Run ID: `42693762124`
- نتیجه: `completed / success`
- URL: https://github.com/AngmarX-dev/LionGameStick/actions/runs/42693762124
- سه تست unit اجرا و موفق شدند.
- py_compile برای هر سه اسکریپت موفق بود.
- هر سه CLI help اجرا شدند.
- inventory گرافیکی: 182 ورودی.
- inventory جامع: 769 ورودی binary-like و 591 ELF عمیقاً تحلیل‌شده.
- artifact با نام `complete-binary-analysis` و شناسهٔ `13708048282` بارگذاری شد؛ شامل چهار فایل CSV/JSON است.

## Build و سخت‌افزار

- Firmware build: اجرا نشد؛ این مرحله ابزار ممیزی است و build system/toolchain کامل هدف در این اجرای CI فراهم نبود.
- اجرای ELFهای ARM: انجام نشد؛ اجرای باینری هدف روی runner x86-64 ایمن و معتبر نیست.
- Hardware verification روی GameStick: انجام نشد.
- هیچ باینری runtime جایگزین، حذف یا ویرایش نشد.

## محدودیت‌ها و گام بعدی

1. بررسی تاریخچهٔ Git و منابع BSP برای `sbin/udevadm` و پیدا کردن نسخهٔ ARM سازگار؛ تا آن زمان فایل دست‌نخورده بماند.
2. مقایسهٔ dependency closure همهٔ executableها و shared objectها با کتابخانه‌ها و dynamic loader موجود در rootfs.
3. بررسی دقیق‌تر فایل‌های linker script با پسوند `.so` و فایل‌های ناشناختهٔ بدون پسوند.
4. مقایسهٔ Build ID، SONAME، symbols و ARM attributes با SDK/BSP رسمی همان SoC و نسخهٔ firmware.
5. بازیابی فقط پس از اثبات معماری، ABI، نسخه و وابستگی؛ ابتدا در مسیر آزمایشی و همراه backup.

این گزارش یافته‌های استاتیک را مستند می‌کند؛ هیچ نتیجه‌ای دربارهٔ عملکرد واقعی GPU یا سازگاری قطعی با مدل مشخص Rockchip ادعا نمی‌شود.
