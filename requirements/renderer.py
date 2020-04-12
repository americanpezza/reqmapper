import os
from xmind import XMindDocument
from xmind.document import SHAPE_RECTANGLE, SHAPE_ROUND_RECTANGLE, SHAPE_ELLIPSIS
from requirements import Attribute

import config






class AttributeNotRenderable(Exception):
    pass

class AttributeRenderer:
    markers = config.getAttributeMarkers()

    def __init__(self, attr):
        if not attr.isValid():
            raise AttributeNotRenderable("Attribute '%s' with value '%s' is not valid" % (attr.getName(), attr.getValue()))

        self.attribute = attr

    def isValid(self):
        return (self.attribute.getName() in AttributeRenderer.markers.keys()) and (self.attribute.getOrder() <= len(AttributeRenderer.markers[self.attribute.getName()]) )

    def render(self):
        order = self.attribute.getOrder()

        return AttributeRenderer.markers[self.attribute.getName()][order]

class Renderer:
    def __init__(self, chapters, requirements, doc=None, renderOrphans=True, renderFolded=True, maxDepth=999, verbose=False):
        self.requirements = requirements
        self.verbose = verbose
        self.chapters = chapters
        self.maxDepth = maxDepth
        self.xmindDoc = doc
        if self.xmindDoc is None:
            self.xmindDoc = XMindDocument.create(u"ReqTrees", u"text")

        self.levelsProgression = ['system', 'user', 'business']

        self._renderOrphans = renderOrphans
        self.renderFolded = renderFolded

        self.topicStyle = {}
        if doc is None:
            self.topicStyle['unknown'] = Renderer.setupStyle(self.xmindDoc, "unknown")
            self.topicStyle['business'] = Renderer.setupStyle(self.xmindDoc, "business")
            self.topicStyle['user'] = Renderer.setupStyle(self.xmindDoc, "user")
            self.topicStyle['system'] = Renderer.setupStyle(self.xmindDoc, "system")
        else:
            self.topicStyle = self.xmindDoc.get_styles()

        self.issues = []

    @staticmethod
    def setupStyle(xmindDoc, what):
        style = config.getMapStyle(what)
        return xmindDoc.create_topic_style( style['fill'], styleid=what, shape=style['shape'], line_color=style['lineColor'], line_width=style['lineWidth'])

    def setStyle(self, requirement, topic):
        style = 'unknown'
        if requirement.getCategory() in self.topicStyle.keys():
            style = requirement.getCategory()
        else:
            print("WARNING: Unknown category: %s" % requirement.getCategory())

        topic.set_style( self.topicStyle[ style ] )

    def setupSheet(self, rootSheet, rootTopic):
        pass

    def render(self, filename, sheet=None):
        rootSheet = sheet
        if rootSheet is None:
            rootSheet = self.xmindDoc.get_first_sheet()

        rootTopic = rootSheet.get_root_topic()

        cat = self.setupSheet(rootSheet, rootTopic)
        self.renderContent(rootSheet, cat )

        if self._renderOrphans:
            self.renderOrphans(rootTopic)
            self.renderNoLinks(rootTopic)

        if sheet is None:
            self.xmindDoc.save(filename)

    def renderContent(self, rootSheet, category ):
        self.attributeIssues = {}
        rootTopic = rootSheet.get_root_topic()

        for chapter in self.chapters:
            if chapter['category'] == category and len(chapter['reqs']) > 0:
                newTopic = rootTopic.add_subtopic(chapter['name'], folded=True)
                newTopic.set_style(self.topicStyle[category])

                children = self.sortLinks(chapter['reqs'])
                for reqID in children:
                    self.renderTopic(None, newTopic, reqID )

    def renderOrphans(self, rootTopic):
        for cat in self.levelsProgression[:-1]: # skip the business requirements
            orphans = []
            for key, req in self.requirements.items():
                if req.getCategory() == cat:
                    found = False
                    for key2, req2 in self.requirements.items():
                        for link in self.getNextLevel(req2):
                            if link == req.getID():
                                found = True
                                break

                        if found:
                            break

                    if not found and (key not in orphans):
                        orphans.append(key)

            if len(orphans) > 0:
                topic = rootTopic.add_subtopic("Orphaned %s Requirements" % cat )
                for key in orphans:
                    req = self.requirements[key]
                    self.createTopic(topic, req)

    def renderNoLinks(self, rootTopic):
        for cat in self.levelsProgression[1:]:   # skip the system requirements
            orphans = []
            for key, req in self.requirements.items():
                if req.getCategory() == cat and len(req.getLinks()) == 0:
                    orphans.append(key)

            if len(orphans) > 0:
                topic = rootTopic.add_subtopic("%s Requirements without links" % cat )
                for key in orphans:
                    req = self.requirements[key]
                    self.createTopic(topic, req)

    def createTopic(self, root, requirement):
        newTopic = root.add_subtopic(requirement.getText(), folded=self.renderFolded)
        self.setStyle(requirement, newTopic)

        note = ("%s\n%s" % (requirement.getID(), requirement.getFullText()))
        newTopic.set_note(note)

        for a in requirement.getAttributes():
            renderer = AttributeRenderer(a)
            if renderer.isValid():
                newTopic.add_marker(renderer.render())
            else:
                if a.getValue() is not None and len(a.getValue()) > 1 and requirement.getID() not in self.attributeIssues.keys():
                    msg = "WARNING: unknown attribute value ('%s') for '%s' in requirement %s" % (a.getValue(), a.getName(), requirement.getID())
                    self.attributeIssues[requirement.getID()] = msg
                    if self.verbose:
                        print(msg)

        return newTopic

    # sort the links attributed to a requirement.
    # use the 3 attributes priority, risk and difficulty
    def sortLinks(self, reqList):
        reqs = []
        for l in reqList:
          r = self.getLinkedRequirement(l)
          if r is not None:
              reqs.append(r)

        def reqOrder(req):
            order = []
            attrs = req.getAttributes()
            for attributeOrder in ['Priority', 'Risk', 'Difficulty']:
                for attribute in attrs:
                    if attribute.getName() == attributeOrder:
                       order.append( attribute.getOrder() )
                       break

            return order

        reqs.sort(key=reqOrder)
        return [x.getID() for x in reqs]

    def renderTopic(self, root, rootTopic, link ):
        linked = self.getLinkedRequirement(link)
        valid = (linked is not None )  # do we have valid links (consdiering the asymmetry between business and system)?

        if valid:
            newTopic = self.createTopic(rootTopic, linked)
            children = self.sortLinks(self.getNextLevel(linked))
            for l in children:
                self.renderTopic(linked, newTopic, l)

    def getNextLevel(self, requirement):
        pass

    def getLinkedRequirement(self, link):
        req = None
        if link in self.requirements.keys():
            req = self.requirements[link]

        return req

class BottomUpRenderer(Renderer):
    def setupSheet(self, rootSheet, rootTopic):
        rootSheet.set_title(u"BottomUp" )
        rootTopic.set_title(u"BottomUp Requirements tree" )

        return self.levelsProgression[0]

    def getNextLevel(self, requirement):
        links = []
        for i in range(0, len(self.levelsProgression)):
            if requirement.getCategory() == self.levelsProgression[i] and i< (len(self.levelsProgression) - 1):
                category = self.levelsProgression[i+1]
                for reqID, req in self.requirements.items():
                    if req.getCategory() == category and requirement.getID() in req.getLinks():
                        links.append(reqID)

        return links

class TopDownRenderer(Renderer):
    def setupSheet(self, rootSheet, rootTopic):
        rootSheet.set_title(u"TopDown" )
        rootTopic.set_title(u"TopDown Requirements tree" )

        return self.levelsProgression[-1]

    def getNextLevel(self, requirement):
        return requirement.getLinks()

class UnifiedRenderer:
    def __init__(self, chapters, requirements, renderFolded=True, maxDepth=999, verbose=False):
        self.xmindDoc = XMindDocument.create(u"ReqTrees", u"text")
        self.topicStyle = {}

        self.topicStyle['unknown'] = Renderer.setupStyle(self.xmindDoc, "unknown")
        self.topicStyle['business'] = Renderer.setupStyle(self.xmindDoc, "business")
        self.topicStyle['user'] = Renderer.setupStyle(self.xmindDoc, "user")
        self.topicStyle['system'] = Renderer.setupStyle(self.xmindDoc, "system")

        self.topdown = TopDownRenderer(chapters, requirements, doc=self.xmindDoc, renderOrphans=False, renderFolded=True, maxDepth=maxDepth, verbose=verbose)
        self.bottomup = BottomUpRenderer(chapters, requirements, doc=self.xmindDoc, renderOrphans=False, renderFolded=True, maxDepth=maxDepth, verbose=verbose)

    def render(self, filename ):

        # topdown is the first sheet
        sheet = self.xmindDoc.get_first_sheet()
        self.topdown.render(None, sheet=sheet )

        # bottomup is the first sheet
        newsheet = self.xmindDoc.create_sheet(u"ReqTrees", u"text")
        self.bottomup.render(None, sheet=newsheet)

        # now render orphans
        newsheet = self.xmindDoc.create_sheet(u"Issues", u"Issues")
        root = newsheet.get_root_topic()
        self.topdown.renderOrphans(root)
        self.topdown.renderNoLinks(root)

        # add a legend. the XMind legend creation does not seem to work properly anymore, so we create a dedicated sheet with all info
        newsheet = self.xmindDoc.create_sheet(u"Conventions", u"Conventions")
        root = newsheet.get_root_topic()
        self.renderLegend(root)

        # save our precious work!
        self.xmindDoc.save(filename)

    def renderLegend(self, root):
        # render topic styles legend
        rootTypes = root.add_subtopic("Requirement types", folded=False)

        for name, style in self.topicStyle.items():
            if name != "unknown":
                t = rootTypes.add_subtopic("%s Requirements" % name)
                t.set_style(style)

        # render markers legend
        rootMarkers = root.add_subtopic("Requirement attributes", folded=False)

        attributeMappings = config.getAttributeMappings()
        attributeTypes = attributeMappings.keys()

        for markerType in attributeTypes:
            generic = Attribute.getDescription(markerType)
            rootType = rootMarkers.add_subtopic(markerType, folded=True)
            rootType.set_note(generic)

            #levels = AttributeRenderer.getAttributeMapping(markerType)
            #levels = config.getAttributeMapping(markerType)
            for levelname, levelvalue in attributeMappings[markerType].items():
                descr = "indicates %s" % levelname
                m = rootType.add_subtopic(descr)
                m.add_marker(levelvalue)

        # render orphans + nolinks
        rootIssues = root.add_subtopic("Requirements Issues", folded=False)
        orphans = rootIssues.add_subtopic("Orphans: requirements that are not linked by any other requirement")
        orphans.set_style(self.topicStyle['unknown'])
        orphans.set_note("If a user requirement is not linked by any business requirement, this implies that this user requirement has no foundation in any business need and thus should not be implemented. If a system requirement is not linked by any user requirement, this implies that this system requirement is not related to any user feature, and thus may not be needed at all")

        nolinks = rootIssues.add_subtopic("NoLinks: requirements that do not link to any other requirement")
        nolinks.set_style(self.topicStyle['unknown'])
        nolinks.set_note("If a business requirement is not linked to any other requirement, the conclusion is that the requirement is NOT going to be implemented. In other words, any business requirement that is not linked to other (user) requirement results in a need that will not be addressed by the project. This situation should be avoided as much as possible: each business requirement is expected to have at least one link.\n If a user requirement has no link to any system requirement, this implies that, while there is a business need that was converted into a user requirement, this will not be implemented. This situation should be avoided as much as possible: each user requirement is expected to be linked to at least one system requirement.")

        # render traceability
        rootTrace = root.add_subtopic("Requirements traceability", folded=False)
        orphans = rootTrace.add_subtopic("TopDown: from business requirements down to system requirements traceability")
        orphans.set_style(self.topicStyle['unknown'])

        nolinks = rootTrace.add_subtopic("BottmUp: from system requirements up to business requirements traceability")
        nolinks.set_style(self.topicStyle['unknown'])

