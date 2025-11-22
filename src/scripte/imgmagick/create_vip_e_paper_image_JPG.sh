#!/usr/bin/bash

OUT="/home/sna/src/twitch/src/scripte/imgmagick/vip_epaper.jpg"
SIZE="384x184"
FONT="/usr/share/fonts/OTF/MonaspaceKrypton-Regular.otf"
FONT1="/usr/share/fonts/OTF/MonaspaceKrypton-Bold.otf"
NAME=$1
BGIMAGE=$2

echo "$1"
echo "$2"

magick -size "$SIZE" xc:white \
  \( "$BGIMAGE" -resize 180x180 -gravity center -compose over \)  -composite \
  \
  \( -size "$SIZE" -gravity center \
     -fill "#000000" -font "$FONT1" caption:$NAME \) -composite \
  \
  -colorspace sRGB \
  -strip \
  -quality 92 \
  "$OUT"

echo "image created: $OUT"
