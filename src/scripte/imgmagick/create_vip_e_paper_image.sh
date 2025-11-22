#!/usr/bin/env bash
# magick -background none -fill "#ff52fc" -size 384x184 canvas:none "(" bg.png -resize 150x150 ")" -geometry +5+5 -composite -font "/usr/share/fonts/OTF/MonaspaceKrypton-Regular.otf"  -density 280 -gravity southeast -annotate +0+0 "legomen68" text.png 
#000000
# magick -size 3x1 xc:"#333333" xc:"#EEEEEE" xc:"#888888" +append palette.png
# magick text.png -colorspace Gray -contrast-stretch 0x10% -posterize 4 -dither None  -remap palette.png output.png
#
OUT="/home/sna/src/twitch/src/scripte/imgmagick/vip_epaper.jpg"
SIZE="384x184"
FONT="/usr/share/fonts/OTF/MonaspaceKrypton-Regular.otf"
FONT1="/usr/share/fonts/OTF/MonaspaceKrypton-Bold.otf"
NAME=$1
BGIMAGE=$2
echo "$1"
echo "$2"
magick -background none -size "$SIZE" canvas:white \
  \( "$BGIMAGE" -resize 180x180 -gravity center \) -composite \
  \
  \( -size "$SIZE"  -gravity center \
     -fill "#000000" -font "$FONT1" caption:$NAME \) -composite \
  \
  "$OUT"

echo "image created:  $OUT"

