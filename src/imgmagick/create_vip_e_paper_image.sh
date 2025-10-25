#!/usr/bin/env bash
# magick -background none -fill "#ff52fc" -size 384x184 canvas:none "(" bg.png -resize 150x150 ")" -geometry +5+5 -composite -font "/usr/share/fonts/OTF/MonaspaceKrypton-Regular.otf"  -density 280 -gravity southeast -annotate +0+0 "legomen68" text.png 
#
# magick -size 3x1 xc:"#333333" xc:"#EEEEEE" xc:"#888888" +append palette.png
# magick text.png -colorspace Gray -contrast-stretch 0x10% -posterize 4 -dither None  -remap palette.png output.png
#
OUT="text.png"
SIZE="384x184"
FONT="/usr/share/fonts/OTF/MonaspaceKrypton-Regular.otf"
FONT1="/usr/share/fonts/OTF/MonaspaceKrypton-Bold.otf"
FONT2="/usr/share/fonts/OTF/MonaspaceKrypton-Bold.otf"
BGIMAGE="bg.png"

magick -background none -size "$SIZE" canvas:white \
  \( "$BGIMAGE" -resize 150x150 \) -geometry +5+5 -composite \
  \
  -fill "#ff52fc" -font "$FONT2" -pointsize 36 -density 100 \
  -gravity southeast -annotate +0+0 "legomen68" \
  \
  -fill "#000000" -font "$FONT2" -pointsize 36 -density 40 \
  -gravity northwest -annotate +170+20 "FiSHiNG VIP!!!" \
  \
  -fill "#000000" -font "$FONT1" -pointsize 36 -density 80 \
  -gravity center -annotate +60+0 "<>< VIP" \
  \
  "$OUT"

echo "image created:  $OUT"

