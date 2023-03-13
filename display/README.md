# Inky Impression 7.3" (7 colour ePaper/E Ink HAT)

> An extra large 7.3" (800 x 480 pixel) 7 colour E Ink® display for Raspberry Pi.

There's a new ePaper screen in town, and it's a whopper! Like the ones on our other Inky Impressions, this XL 7.3" display is **super crisp, low power** and looks great from a variety of viewing angles. These seven colour screens are our absolute favourites, with **high pixel density** and **bright vivid colours**, perfect for showing off gorgeous dithered images (we've put a lot of effort into our dithering code and we hope you love it).

We've enhanced this fancy display by adding:

- The appropriate hardware to plug in a Raspberry Pi so it sits tidily behind the display. If your Pi has a 40 pin header attached, you won't need to do any soldering.
- Four side mounted buttons that are accessible if you've got the panel mounted on a wall or whatnot.
- Cutting edge ray tracing technology (in the form of some snazzy PCB art) 🐟 

Electronic paper displays only consume power whilst they're refreshing, so they're a good choice for projects like home automation dashboards and electronic photo frames that need to be always on. This one takes **around 40 seconds** to refresh, so is best suited to projects that don't require constant screen updates.

## Features

- 7.3" EPD display (800 x 480 pixels)
  -E Ink Gallery Palette® ePaper
  - ACeP (Advanced Color ePaper) 7-color with black, white, red, green, blue, yellow, orange.
  - Ultra wide viewing angles
  - Ultra low power consumption
  - Dot pitch – 0.2 x 0.2mm
- Four side mounted buttons
- 40-pin extension header included to boost height for full-size Raspberry Pi.
- Standoffs included to securely attach to your Pi
- I2C pins broken out for adding breakouts
- Compatible with all 40-pin header Raspberry Pi computers
- [Python library](https://github.com/pimoroni/inky)
- [Schematic](https://cdn.shopify.com/s/files/1/0174/1800/files/inky_impression_73_schematic.pdf?v=1677856907)
- Comes fully assembled

Multi-colour EPD displays use electrophoresis to pull coloured particles up and down on the display. The coloured particles reflect light, unlike most display types, meaning that they're visible under bright lights.

Everything comes fully-assembled and there's no soldering required (as long as your Raspberry Pi has a 40 pin header attached). The display is securely stuck down to the Inky Impression PCB and connected via a ribbon cable. Just pop Inky Impression on your Pi and run our installer to get everything set up!

We've also broken out the I2C pins on the back of Inky Impression, letting you connect additional devices like [breakouts](https://shop.pimoroni.com/collections/breakout-garden) and show their data right on the display.

Inky Impression will work with any version of the Pi that has a 40 pin header, including Zero variants. If you want to use it with a Raspberry Pi 400, you'll probably also want to pick up a [GPIO extender cable](https://shop.pimoroni.com/collections/breakout-garden) (unless you're into using screens at a highly unusual angle).

## Software

Our [Python library](https://github.com/pimoroni/inky) takes the stress out of displaying text and images on Inky Impression, and we've put together some special [examples](https://github.com/pimoroni/inky/tree/master/examples/7color) to show off Inky Impression's capabilities. We've provided a one-line-installer for the Python library too, to make installation a little more straightforward:

```bash
$ curl https://get.pimoroni.com/inky | bash
```

## Notes

- **The Inky Impression display is made from glass so it's pretty fragile. Be careful not to drop it or press too hard on it, or it will crack. When fitting it to your Pi, grip at the edges of the board rather than pressing on top of the screen.**
- ePaper displays work best when refreshed at an ambient room temperature (**between 15 and 35°**). If the screen is cold you might find that the colours are less vibrant.
- Due to the size of this panel and the esoteric practices surrounding suspending coloured particles in goo, there is some expected **variation in colour density towards the corners**. This is most noticeable when displaying block colours - green and orange in particular become less saturated towards the corners of the panel. We've noticed that the corners can also sometimes can have a pink tinge when displaying full white.
- Overall display dimensions: 170.2 x 111.2mm (W x H)
- Usable area dimensions: 160 x 96 mm (W x H)
