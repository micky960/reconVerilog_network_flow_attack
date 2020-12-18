import argparse
import os, sys
import re

class inputNode:

    def __init__(self, line):
        self.line = ""
        self.name = ""
        self.drives = ""
        self.line = line
        self.__parseInput(self.line)

    def __parseInput(self, line):
        self.name = re.split("\+\+\+ INPUT", line)[0]
        self.name = re.split("-", self.name)[1].strip()

    def getName(self):
        return self.name

class outputNode:

    def __init__(self, line):
        self.line = ""
        self.name = ""
        self.driver = ""
        self.line = line
        self.__parseOutput(self.line)

    def __parseOutput(self, line):
        temp = re.split("\+\+\+ OUTPUT", line)
        self.name = re.split("-", temp[0])[1].strip()
        temp = re.split(":", temp[1])
        self.driver = re.sub("[|]", "", temp[2].strip())
        cellOPPinName = re.split(",", self.driver)
        opPinSet = set()
        opPinSet.add(cellOPPinName[1].strip())
        if cellOPPinName[0].strip() in cellOPPin:
            cellOPPin[cellOPPinName[0].strip()].add(cellOPPinName[1].strip())
        else:
            cellOPPin[cellOPPinName[0].strip()] = opPinSet

    def getDriver(self):
        return self.driver

    def getName(self):
        return self.name

class cellNode:

    def __init__(self, line):
        self.cellName = ""
        self.cellType = ""
        self.cellIP = list()
        self.cellOP = ""
        temp = re.split("\|", line)
        self.cellName = re.sub("[-]", "", re.split("\+\+\+", temp[0])[0].strip()).strip()
        self.cellType = re.split("\+\+\+", temp[0])[1].strip()
        for i in range(1, len(temp)-1):
            p = re.split(":", temp[i])
            self.cellIP.append(p[0].strip()+", "+p[-1].strip())
            cellOPPinName = re.split(",", p[-1])
            opPinSet = set()
            opPinSet.add(cellOPPinName[1].strip())
            if cellOPPinName[0].strip() in cellOPPin:
                cellOPPin[cellOPPinName[0].strip()].add(cellOPPinName[1].strip())
            else:
                cellOPPin[cellOPPinName[0].strip()] = opPinSet

    def getName(self):
            return self.cellName

    def getType(self):
            return self.cellType

    def getPinDriver(self):
        return self.cellIP

def constructVerilog(name, inputs, outputs, cells, fo):

    fo.write("module "+name+"_mod(\n")
    for i in inputs:
        fo.write(i.getName()+",")

    for i in range(0, len(outputs)-1):
        fo.write(outputs[i].getName()+",")
    fo.write(outputs[-1].getName()+");\n\n\n")
            
    fo.write("input ")
    for i in range(0, len(inputs)-1):
        fo.write(inputs[i].getName()+",")

    fo.write(inputs[-1].getName()+";\n\n\n")

    fo.write("output ")
    for i in range(0, len(outputs)-1):
        fo.write(outputs[i].getName()+",")
    fo.write(outputs[-1].getName()+";\n\n\n")

    for c in cells:
        fo.write(c.getType()+" ")
        fo.write(c.getName()+" ")
        fo.write("(")
        try:
            cur  = list(cellOPPin[c.getName()])
            for i in range(0, len(cur)-1):
                fo.write("."+cur[i]+"("+cur[i]+"_"+c.getName()+"), ")
            fo.write("."+cur[-1]+"("+cur[-1]+"_"+c.getName()+"), ")
        except KeyError as e:
            #fo.write("), ")
            print((repr(e)))

        pins = c.getPinDriver()
        for i in range(0, len(pins)-1):
            temp = re.split(",", pins[i])
            if "Primary" in pins[i]:
                fo.write("."+temp[0].strip()+"("+temp[1].strip()+"), ")
            else:
                fo.write("."+temp[0].strip()+"("+temp[2].strip()+"_"+temp[1].strip()+"), ")
        temp = re.split(",", pins[-1])
        if "Primary" in pins[-1]:
            fo.write("."+temp[0].strip()+"("+temp[1].strip()+"));\n")
        else:
            fo.write("."+temp[0].strip()+"("+temp[2].strip()+"_"+temp[1].strip()+"));\n")
        
    for o in outputs:
        temp = re.split(",", o.driver)
        if "Primary" in o.getDriver():
            fo.write("assign "+o.name+" = "+temp[0].strip()+";\n")
        else:
            fo.write("assign "+o.name+" = "+temp[1].strip()+"_"+temp[0].strip()+";\n")

    fo.write("\nendmodule ")

def main(name, inputFile, outputFile):

    global cellOPPin
    cellOPPin = dict()

    fo = open(outputFile, 'w')

    with open(inputFile) as fi:
        content = fi.readlines()

    content = content[2:]
    inputs = list()
    outputs = list()
    cells = list()
   
    for c in content:
        if 'INPUT' in c:
            inputs.append(inputNode(c))
        elif 'OUTPUT' in c:
            outputs.append(outputNode(c))
        else:
            cells.append(cellNode(c))

    constructVerilog(name, inputs, outputs, cells, fo)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Reconstruct verilog from network flow output')
    parser.add_argument('--name', help='Name of module')
    parser.add_argument('--input', help='Path for input file')
    parser.add_argument('--output', help='Path for output file')

    args = parser.parse_args()

    main(args.name, args.input, args.output)
