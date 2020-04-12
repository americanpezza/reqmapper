import excel, xlrd
from .requirement import Requirement
import config





class Parser:
    def __init__(self, category, filename, strict, verbose=False):
        self.filename = filename
        self.category = category
        self.colNames = {}
        self.verbose = verbose
        self.strict = strict

    def getValue(self, row, value):
        result = None
        if value in self.colNames.keys() and (self.colNames[value] is not None):
            result = row[ self.colNames[value]].value

        return result

    def checkColName(self, rowValue, possibleValues):
        result = False
        sanitizedValue = str(rowValue).strip()
        for val in possibleValues:
            if sanitizedValue == val:
                result =True
                break

        return result

    def parseColNames(self, row):
        colNameProbes = config.getColNameProbes()
        for name, values in colNameProbes.items():
            for i in range(0, len(row)):
                if self.checkColName(row[i].value, values):
                    self.colNames[name] = i
                    break

        if self.verbose:
            print("The column indexes are: %s" % (str(self.colNames)))

    def parse(self):
        try:
            f=excel.OpenExcel(self.filename)
        except xlrd.biffh.XLRDError as e:
            print("WARNING: You may need to close Excel if you have it open")
            raise e

        sheet=f.read()
        reqs={}
        counter=0
        reqCounter=0
        nolinks = []
        duplicates=[]

        chapters = []
        currentChapter = { 'name': "Default", "category": self.category, 'reqs': []}

        # row #0 contains the headers
        for row in sheet.get_rows():
            # rows without a reqID are not requirements
            if counter == 0:
                self.parseColNames(row)
            else:
                reqID = self.getValue(row, "CodeName")
                if len(reqID) > 1:

                    attributes = {}
                    for name in self.colNames.keys():
                        val = self.getValue(row, name)
                        attributes[name] = val

                    essentialValues = attributes.keys()
                    if ("ID" not in essentialValues) or ("CodeName" not in essentialValues) or ("Requirement" not in essentialValues) or ("Link" not in essentialValues):
                        raise Exception("To parse requirements properly, all essential attributes ('ID', 'CodeName', 'Requirement' and 'Link') must be provided in each requirement, while these values were found in file %s: %s" % (self.filename, str(attributes)))

                    r = Requirement(self.category, self.strict, attributes)

                    # Some integrity checks
                    if len(r.getLinks()) == 0 and self.category != "system":
                        nolinks.append( str(r.getID()) )

                    if r.getID() in reqs.keys():
                        duplicates.append( str(r.getID()) )
                        if self.verbose:
                            print("WARNING: duplicate requirement ID.\n%s\n%s\n" % ( r, reqs[r.getID()]))

                    # let's add it finally!
                    reqs[r.getID()] = r
                    currentChapter['reqs'].append( str(r.getID()) )
                    reqCounter = reqCounter + 1
                else:
                    if len(currentChapter['reqs']) > 0:
                        chapters.append(currentChapter)
                    currentChapter = { "name": self.getValue(row, "Requirement"), "category":self.category, "reqs": []}

            counter = counter+1

        # close the last chapter
        if len(currentChapter['reqs']) > 0:
            chapters.append(currentChapter)

        print("Parsed %d (%s) requirements, %s requirement(s) had no links, %d requirement(s) had a duplicate ID" % (reqCounter, self.category, len(nolinks), len(duplicates), ))

        if self.verbose:
            if len(nolinks) > 0:
                print("The following requirements have no links: %s" % ", ".join(nolinks))

            if len(duplicates) > 0:
                print("The following requirements have duplicates: %s" % ", ".join(duplicates))

        print("")

        return (chapters, reqs, [nolinks, duplicates ])

