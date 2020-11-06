import re
import sys
import logging

from collections import namedtuple, defaultdict

if sys.version_info.major == 3:
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser


class Tree:
    def __init__(self, serialized_tree, saved_views, with_completed=False):
        self.root_nodes = []
        self.calendar = defaultdict(list)
        self.available_nodes = {}
        self.tags = defaultdict(set)
        self.mentions = defaultdict(set)
        self.with_completed = with_completed
        for serialized_node in serialized_tree:
            root_node = self.add_node(serialized_node, path="Home")
            if root_node is not None:
                self.root_nodes.append(root_node)

        self.starred_nodes, self.starred_searches = self.load_starred_nodes(saved_views)

    @property
    def nodes(self):
        return self.available_nodes.values()

    def load_starred_nodes(self, saved_views):
        starred_nodes, starred_searches = [], []
        for item in saved_views:
            projectId = item["zoomedProject"]["projectid"]
            node_id = Node.shorten_id(projectId)
            if not (node_id in self.available_nodes or node_id == "None"):
                continue
            node = (
                self.available_nodes[Node.shorten_id(node_id)]
                if node_id != "None"
                else None
            )
            if item["searchQuery"]:
                starred_searches.append(Search(node, item["searchQuery"]))
            else:
                node_id = item["zoomedProject"]["projectid"]
                starred_nodes.append(self.available_nodes[Node.shorten_id(node_id)])

        return starred_nodes, starred_searches

    def __getitem__(self, node_id):
        return self.available_nodes[node_id]

    def add_node(self, serialized_node, path=""):
        try:
            node = Node(self, path, **serialized_node)
            if not self.with_completed and node.is_completed:
                return
            for tag in node.tags:
                self.tags[tag].add(node.short_id)
            for mention in node.mentions:
                self.mentions[mention].add(node.short_id)
            self.available_nodes[node.short_id] = node

            for serialized_child in serialized_node.get("ch", []):
                child_node = self.add_node(
                    serialized_child, path="%s > %s" % (path, node.text)
                )
                if child_node is not None:
                    node.add_child(child_node)

            return node
        except MirrorException:
            return


Search = namedtuple("Search", ["node", "query"])


class MirrorException(Exception):
    pass

class NodeParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a":
            link = attrs.get("href")
            self.links.append(link)

    def handle_data(self, data):
        self.text.append(data)
    
    def feed(self, *args, **kwargs):
        self.links = []
        self.text = []
        HTMLParser.feed(self, *args, **kwargs)
        text = str.join("", self.text)
        tags = re.findall("(?:^|\s)(#[\w]?[\w_-]+)", text)
        mentions = re.findall("(?:^|\s)(@[\w]?[\w_-]+)", text)
        return text, tags, mentions, self.links

def mirrored(method):
    def wrapper(self, *args, **kwargs):
        if self.is_mirror_root:
            return method(self.original_node, *args, **kwargs)
        return method(self, *args, **kwargs)

    return wrapper


class Node:
    parser = NodeParser()
    def __init__(self, tree, path, **kwargs):
        self._name = kwargs["nm"]
        self._text, self._tags, self._mentions, self._links = self.parser.feed(self._name)
        self.path = path
        self.id = kwargs["id"]
        self.metadatas = kwargs.get("metadata", {})
        self._note = kwargs.get("no")
        self.completed_time = kwargs.get("cp")
        self.tree = tree
        self._children = []

    @property
    @mirrored
    def name(self):
        return self._name

    @property
    @mirrored
    def text(self):
        return self._text
    
    @property
    @mirrored
    def note(self):
        return self._note

    @property
    @mirrored
    def short_id(self):
        return self.shorten_id(self.id)

    @staticmethod
    def shorten_id(node_id):
        if node_id is None:
            return None
        return node_id.split("-")[-1]

    @property
    @mirrored
    def is_completed(self):
        return self.completed_time is not None

    @property
    @mirrored
    def is_uncompleted(self):
        return self.completed_time is None

    @mirrored
    def add_child(self, child):
        self._children.append(child)

    @property
    @mirrored
    def website_url(self):
        return "https://workflowy.com/#/{}".format(self.short_id)

    @property
    @mirrored
    def desktop_url(self):
        return "workflowy://workflowy.com/#/{}".format(self.short_id)

    @property
    def is_mirror(self):
        return "mirror" in self.metadatas and not self._name

    @property
    def is_mirror_root(self):
        if not self.is_mirror:
            return False
        return "isMirrorRoot" in self.metadatas["mirror"]

    @property
    def original_node(self):
        original_id = self.metadatas["mirror"]["originalId"]
        if not self.is_mirror_root or original_id not in self.tree.available_nodes:
            raise MirrorException
        return self.tree[self.shorten_id(original_id)]

    @property
    @mirrored
    def children(self):
        return [child for child in self._children]

    @property
    @mirrored
    def has_link(self):
        return len(self._links) != 0

    @property
    @mirrored
    def tags(self):
        return self._tags

    @property
    @mirrored
    def mentions(self):
        return self._mentions

    @property
    @mirrored
    def embed_link(self):
        return self._links[0] if self.has_link else None

    def __hash__(self):
        return hash(self.id)

    @property
    @mirrored
    def has_inner_link(self):
        return "workflowy.com/#/" in self.embed_link
