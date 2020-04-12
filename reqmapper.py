#!/bin/python

import os, sys, argparse
from requirements import Parser












rootDir="sources"
filename="requirements"






reqs={}
chapters=[]

categories={ "U":"user", "B": "business", "S": "system" }

def checkSensitivity(v):
    s = float(v)
    if s < 0.0 or s> 1.0:
        raise argparse.ArgumentTypeError("%s should be a decimal value between 0 and 1" % v)

    return s


parser = argparse.ArgumentParser()
parser.add_argument("-i", "--independent", default=False, action="store_true", help="Produce two separate maps, one for topdown the other for bottomup. Requirements are always the same, but the two maps provide topdown and bottomup traceability between them")
parser.add_argument("-d", "--directory", default=rootDir, action="store", help="The folder containing the sources for the requirements, in xls/xlsx Excel spreadsheets")
parser.add_argument("-f", "--filename", default=filename, action="store", help="The filename to use for the rendered XMind map(s) (default: %s.xmind)" % filename)
parser.add_argument("-p", "--no_orphans", default=False, action="store_true", help="Do not show issues such as orphaned and non-linked requirements")
parser.add_argument("-n", "--no_folded", default=False, action="store_true", help="Do not render all topics as folded")
parser.add_argument("-k", "--semantic", default=False, action="store_true", help="Check requirements for duplicates and other issues")
parser.add_argument("-v", "--verbose", default=False, action="store_true", help="Print additional information when parsing and rendering requirements")
parser.add_argument("-S", "--strict", default=False, action="store_true", help="Be less permissive when parsing requirements. By default, the parser will try to work around issues in the parsing using sensible defaults (es.: assume that Difficulty is Low if the actual value is illegal).")
parser.add_argument("-s", "--minScore", default=0.8, action="store", type=checkSensitivity, help="Minimum semantic similarity score to be used (defaults to 0.0). Can be used to increase the amount of results reported when performing semantic checks on requirements")
parser.add_argument("-m", "--maxScore", default=1.0, action="store", type=checkSensitivity, help="Maximum semantic similarity score to be used (defaults to 1.0). Can be used to limit the amount of results reported when performing semantic checks on the requirements.")

args = parser.parse_args()

semantic=args.semantic
minScore=args.minScore
maxScore=args.maxScore
verbose=args.verbose
strict=args.strict
independent=args.independent
filename=args.filename

for root, dirs, files in os.walk(args.directory):
    for f in files:
        if f.endswith("xlsx"):
            category = "unknown"
            if f[0] in categories.keys():
                category = categories[f[0]]

            print("Parsing file %s for category %s" % (f, category))
            p = Parser( category, os.path.join(root, f), strict, verbose)
            (c, r, alerts) = p.parse()

            for k, i in r.items():
                if k in reqs.keys():
                    print("WARNING: requirement %s from file %s has a duplicate ID" % (i.getID(), f))

            reqs.update(r)
            chapters.extend(c)

print("%d total requirements parsed\n" % len(reqs))



if not semantic:

    if not independent:
        from requirements import UnifiedRenderer

        r = UnifiedRenderer(chapters, reqs, renderFolded=(not args.no_folded), verbose=verbose)
        fname = "%s.xmind" % filename
        r.render( fname )

        print("Rendered to %s" % fname)

    else:
        from requirements import TopDownRenderer, BottomUpRenderer

        fname = "%s-topdown.xmind" % filename
        r = TopDownRenderer(chapters, reqs, renderOrphans=(not args.no_orphans), renderFolded=(not args.no_folded), verbose=verbose)
        r.render(fname )

        fname2 = "%s-bottomup.xmind" % filename
        r = BottomUpRenderer(chapters, reqs, renderOrphans=(not args.no_orphans), renderFolded=(not args.no_folded), verbose=verbose)
        r.render( fname2)

        print("Rendered to files %s and %s." % (fname, fname2))

else:
    from requirements.checker import SemanticChecker

    print("Running a semantic scan on the requirements to identify potential duplicates.")
    checker = SemanticChecker(reqs, minScore=minScore, maxScore=maxScore)
    (sims, ranges) = checker.check()

    print("\nSimilarity ranges (every requirements is checked against all the others):")
    for i in sorted(ranges):
        v = ranges[i]
        print("Percentile %s: %d matches" % (i, v))
        #print("%d requirements checks scored between %d and %d" % (ranges[i], i, (i+1)))

    print("\n")

    checker.prettyPrint(sims)

