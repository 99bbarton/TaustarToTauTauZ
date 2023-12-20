#A namespace for colors and palettes for plots

from ROOT import gStyle, TCanvas, TF2
from array import array
import sys

colors = {
    "line" : [2, 4, 6, 7, 415, 32, 36, 634],
    "stack" : [595, 602, 434, 411, 426, 419, 597, 414, 402, 797, 626, 634, 610, 618, 619],
    "cool" : [884, 874, 881, 876, 890, 855, 852, 867, 835, 844, 419, 413],
    "line_cool" : [884, 881, 852, 876, 419],
    "warm" : [635, 633, 626, 904, 616],
    "line_warm" : [636, 633, 619, 613, 802]

}

#Print the names of the palettes in colors
def printPalettes():
    print("Available palettes are: ")
    print(colors.keys())

def getPalettes():
    return colors.keys()

#Draw the colors in palette, palette
def showPalette(palette):
    if palette not in colors.keys():
        print("ERROR: Palette of the name " + palette + " was not found")
        return -1
    
    pal = colors[palette]

    gStyle.SetPalette(len(pal), array("i",pal))
    canv = TCanvas("canv", "Palette Testing", 800, 600)
    f1 = TF2("f1","y",0, 1 ,1,10)
    f1.Draw("colz")

    resp = raw_input("Hit enter to close...")
    return 0


#Return the color at index num from the palette specfied by palette
def getColor(palette, num):
    if palette not in colors.keys():
        print("ERROR: Palette of the name " + palette + " was not found")
        return 1
    pal = colors[palette]
    if num >= len(pal):
        print("ERROR: Palette does not have " + str(num + 1) + " colors.")
        return 1
    
    return pal[num]


#Return the list of colors corresponding to the name palette
def getPalette(palette):
    if palette not in colors.keys():
        print("ERROR: Palette of the name " + palette + " was not found")
        return []
    else:
        return colors[palette]
    
if __name__ == "__main__":
    if len(sys.argv) == 2:
        showPalette(sys.argv[1])
    else:
        print("USAGE: python Colors.py <paletteName>")