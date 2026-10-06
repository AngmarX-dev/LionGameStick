#!/bin/sh -x
#FC		fceumm_libretro.so
#GB/GBA/GBC	mgba_libretro.so
#GG	/SMS	genesis_plus_gx_libretro.so
#MD		genesisplusgx_libretro.so
#N64		mupen64plus_libretro.so
#PS ONE		pcsx_rearmed_libretro.so
#SFC 		snes9x_libretro.so
#PCE		mednafen_pce_fast_libretro.so
#WSC		mednafen_wswan_libretro.so
#NDS		desmume2015_libretro.so
#ATARI2600		stella_libretro.so
#ATARI5200		atari800_libretro.so	
#ATARI7800		prosystem_libretro.so
#usr/lib/libretro

export XDG_CONFIG_HOME=/sdcard
export XDG_RUNTIME_DIR=/sdcard

GAME_PATH=
GAME_LIB=

export LC_ALL='zh_CN.utf8'

case "$1" in
  0)
    GAME_LIB=fbalpha2012_libretro.so
    ;;
  1)
    GAME_LIB=nestopia_libretro.so
    ;;
  2)
    GAME_LIB=daphne_libretro.so
    ;;
  3)
    GAME_LIB=fbalpha2012_libretro1.so
    ;;
  4)
    GAME_LIB=mame2003_libretro.so
    ;;
  5)
    GAME_LIB=genesisplusgx_libretro.so
    ;;
  6)
    GAME_LIB=snes9x_libretro.so
    ;;
  7)
    GAME_LIB=mgba_libretro.so
    ;;
  8)
    GAME_LIB=mupen64plus_libretro.so
    ;;
  9)
    GAME_LIB=pcsx_rearmed_libretro.so
    ;;
  10)
    GAME_LIB=mednafen_pce_fast_libretro.so
    ;;
  11)
    GAME_LIB=mednafen_wswan_libretro.so
    ;;
  12)
    GAME_LIB=desmume2015_libretro.so
    ;;
  13)
    GAME_LIB=genesis_plus_gx_libretro.so
    ;;
  14)
    GAME_LIB=fbalpha_libretro.so
    ;;
  15)
    GAME_LIB=stella_libretro.so
    ;;
  16)
    GAME_LIB=atari800_libretro.so
    ;;
	17)
    GAME_LIB=prosystem_libretro.so
    ;;
	18)
    GAME_LIB=mame2016_libretro.so
    ;;
	 19)
    GAME_LIB=snes9x_libretro_racing.so
    ;;
	 20)
    GAME_LIB=fbalpha_libretro_other.so
    ;;
 	 21)
    GAME_LIB=stella_libretro_other.so
    ;;
	  22)
    GAME_LIB=atari800_libretro_other.so
    ;;
        23)
    GAME_LIB=prosystem_libretro_other.so
    ;;
        24)
    GAME_LIB=mame2016_libretro_other.so
    ;;
         25)
    GAME_LIB=snes9x_libretro_other.so
    ;;
	 26)
    GAME_LIB=mame2003_libretro_other.so
    ;;


  *)
    echo "Have not game resources"
    return
    ;;
esac

/usr/bin/retroarch -y "12"\
    -c "$2"\
    -L /sdcard/retro_lib/$GAME_LIB "$3"
