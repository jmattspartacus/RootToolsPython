import ROOT
import ctypes

def root_line_style_to_pyplot(root_line_style: int) -> str:
  #kSolid      = 1
  #kDashed     = 2
  #kDotted     = 3
  #kDashDotted = 4
  ret_vals = [
    "-"
    "solid",    # Solid line
    "dashed",   # Dashed line
    "dotted",    # Dotted line
    "dashdot",   # Dash-dotted line
    ("."),  # Dots (Matplotlib doesn't support directly)
    ("-,"), # Long dashes (approximate)
    (":,"), # Dotted-dash
    ("-."), # Alternate dash-dot
    ("--"), # Similar to dashed
    ":",    # Similar to dotted
    "-",    # Default to solid
  ]
  if root_line_style > 0 and root_line_style < len(ret_vals):
    return ret_vals[root_line_style]
  else:
    return ret_vals[0]

def root_line_color_to_pyplot(root_line_color: int) -> str:
  #kWhite  = 0,   kBlack  = 1,   kGray    = 920,  kRed    = 632,  kGreen  = 416,
  #kBlue   = 600, kYellow = 400, kMagenta = 616,  kCyan   = 432,  kOrange = 800,
  #kSpring = 820, kTeal   = 840, kAzure   =  860, kViolet = 880,  kPink   = 900
  pixel_num = ROOT.TColor.Number2Pixel(root_line_color)
  red   = ctypes.c_int(0)
  green = ctypes.c_int(0)
  blue  = ctypes.c_int(0)
  pixel_num = ROOT.TColor.Pixel2RGB(pixel_num, red, green, blue)
  return "#{:02x}{:02x}{:02x}".format(red.value, green.value, blue.value)