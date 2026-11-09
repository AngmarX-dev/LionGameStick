# 008 — بررسی ناسازگاری udevadm و نگهداری نامزد ARM

- تاریخ: 2026-11-09
- هدف: ردیابی `sbin/udevadm` با معماری x86-64، یافتن نسخهٔ ARM موجود در rootfs، بررسی وابستگی‌ها و نگهداری نامزد بازیابی بدون تغییر runtime.
- شاخهٔ فنی: `recovery/05-rockchip-graphics-audit`
- commit نهایی فنی: `9efba8b22d72db8efb8f5fb3d3a2ce5f1a7bc7fa`
- شاخهٔ گزارش: `main`

## وضعیت اولیه

در ممیزی 007، `sbin/udevadm` یک ELF64/x86-64 شناسایی شد؛ در حالی که `sbin/udevd` و `usr/bin/udevadm` هر دو ELF32/ARM هستند. هدف این مرحله بررسی منشأ فایل، تشخیص نامزد جایگزین و حفظ نسخهٔ ARM در مسیری ایزوله بود.

## بررسی Git history

- تاریخچهٔ مسیر `sbin/udevadm` به commit انتقال rootfs به ریشهٔ مخزن در `5dbba210279c81b1d6c465ae39f691cee8254a8e` می‌رسد.
- در درخت commit والد، فایل اصلی در `extracted/GameStickLite/sbin/udevadm` وجود داشت.
- Git blob همان فایل در مسیر فعلی نیز `c16ba9d65d73056e518db07a8474ba01a28b9b7d` است.
- بنابراین فایل x86-64 در همان snapshot تاریخی rootfs وجود داشته و شواهدی از خرابی تصادفی جدید در commitهای اخیر پیدا نشد. علت ورود آن به rootfs هنوز معلوم نیست؛ ممکن است اشتباه بسته‌بندی در منبع اولیه باشد.

## تحلیل باینری‌ها

### فایل فعلی sbin/udevadm

- اندازه: 807,448 bytes
- SHA256: `d3f7aa5fbe40cbe1fa25e381464bdb1fec12acce9ad908bbddf7098bc86cd515`
- ELF64، x86-64، little-endian
- interpreter: `/lib64/ld-linux-x86-64.so.2`
- DT_NEEDED: `libm.so.6`, `libsystemd-shared-261.so`, `libc.so.6`
- Build ID: `cd454fe47ffb3b554940652351b3df4513f4e197`

### نامزد ARM موجود در usr/bin/udevadm

- اندازه: 227,684 bytes
- Git blob SHA: `7f6547d6a9cead8b46dd5962aeba2f1439cb97ca`
- SHA256: `54ddb7ddb7777c52dc43384262d7e8618dd4da67c267265f3486dee1028e6b29`
- ELF32، ARM، little-endian
- interpreter: `/lib/ld-linux-armhf.so.3`
- ARM attributes: Cortex-A7 / ARMv7-A / VFPv4 / VFP registers
- DT_NEEDED: `libblkid.so.1`, `libuuid.so.1`, `libkmod.so.2`, `libz.so.1`, `libc.so.6`, `ld-linux-armhf.so.3`

### تطبیق با udevd و کتابخانه‌ها

`sbin/udevd` نیز ARM32 با interpreter برابر `/lib/ld-linux-armhf.so.3` است و وابستگی‌های اصلی آن با نامزد ARM `udevadm` هم‌راستا هستند. کتابخانه‌های `libblkid.so.1`، `libuuid.so.1` و `libkmod.so.2` در rootfs وجود دارند و در inventory به‌عنوان ELFهای ARM شناسایی شده‌اند.

اسکریپت `etc/init.d/S10udev`، daemon را با مسیر صریح `/sbin/udevd` اجرا می‌کند، اما فرمان `udevadm` را بدون مسیر کامل فراخوانی می‌کند. بنابراین باید PATH واقعی محیط init و مسیر resolve شدن فرمان روی دستگاه بررسی شود. وجود نسخهٔ ARM در `/usr/bin` نامزد قوی برای مسیر اجرایی مورد استفاده است، ولی به‌تنهایی اثبات نمی‌کند که فایل x86-64 در `/sbin` هرگز فراخوانی نمی‌شود.

## نامزد بازیابی ایزوله

یک کپی Git-object از همان فایل ARM موجود در `usr/bin/udevadm` در مسیر زیر نگهداری شد:

`recovery-candidates/udevadm/sbin-udevadm.armhf`

همراه آن، `recovery-candidates/udevadm/README.md` مشخصات و محدودیت‌ها را ثبت می‌کند. این مسیر بخشی از runtime rootfs نیست و هیچ فایل اصلی جایگزین یا حذف نشده است.

## تست‌ها و CI

GitHub Actions:
- Run ID: `42694813336`
- نتیجه: `completed / success`
- URL: https://github.com/AngmarX-dev/LionGameStick/actions/runs/42694813336
- چهار تست unit موفق شدند؛ از جمله تست جدید که برابری byte-for-byte نامزد و `usr/bin/udevadm` و ELF32/little-endian/EM_ARM بودن آن را بررسی می‌کند.
- py_compile، CLI help، graphics inventory، inventory جامع و artifact upload موفق شدند.

یک اجرای اولیه با Run ID `42694726887` به دلیل اشتباه escaping در literal بایت‌های تست شکست خورد. خطا در تست اصلاح شد و اجرای بعدی روی commit نهایی موفق شد؛ workflow یا تستی حذف یا تضعیف نشد.

## Build و سخت‌افزار

- Firmware build: اجرا نشد.
- اجرای باینری ARM: انجام نشد.
- تست واقعی udev در GameStick: انجام نشد.
- فایل `sbin/udevadm` در runtime تغییر نکرد.
- نامزد ARM فقط در مسیر آزمایشی نگهداری شده است.

## نتیجه و گام بعدی

یک نامزد ARM واقعی و موجود در rootfs پیدا و در مسیر جداگانه ثبت شد. با وجود سازگاری معماری و وابستگی‌های ظاهری، جایگزینی هنوز تأیید نشده است؛ نسخهٔ دقیق udev، سازگاری رابط فرمان، ترتیب PATH و رفتار hotplug باید روی rootfs و سخت‌افزار هدف بررسی شوند.

گام بعدی: بررسی نسخه و provenance بسته‌های udev/systemd و وابستگی‌های runtime، بررسی مسیرهای PATH در init، سپس تحلیل فایل‌های x86-64 یا باینری‌های ناشناختهٔ دیگر برای کشف موارد مشابه.
