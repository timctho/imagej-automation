function run(f1, f2, out_dir)
{
    print("")
    print("Open file " + f1)
    open(f1)
    print("Open file " + f2)
    open(f2)
    imageCalculator("Subtract create", File.getName(f2), File.getName(f1))
    saveAs("Tiff", out_dir + "/Result-" + File.getName(f2))
}

arg = getArgument()
list = split(arg, " ")
run(list[0], list[1], list[2])