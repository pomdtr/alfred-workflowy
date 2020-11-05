import argparse
import sys
from datetime import datetime

from workflow import MATCH_ALL, MATCH_ALLCHARS, PasswordNotFound, Workflow3
from workflow.background import run_in_background
from workflowy_api.transport import Transport
from workflowy_api.tree import daterange
from update import get_tree

def coalesce(args, default=None):
    return next((a for a in args if a is not None), default)

def get_node_icon(node):
    if node.is_completed:
        return "img/completed.png"
    if node.children:
        if node.is_mirror:
            return "img/mirrored_folder.png"
        return "img/folder.png"
    if node.is_mirror:
        return "img/mirrored_node.png"
    if node.has_link:
        if node.has_inner_link:
            return "img/inner_link.png"
        return "img/link.png"
    if node.note:
        return "img/note.png"
    return "img/node.png"





def create_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument("query", nargs="*")
    parser.add_argument("--hierarchical", action="store_true")
    parser.add_argument("--starred", action="store_true")
    parser.add_argument("--only-links", action="store_true")
    parser.add_argument("--with-completed", action="store_true")
    parser.add_argument("--mentions", action="store_true")
    parser.add_argument("--tags", action="store_true")
    parser.add_argument("--node", action="store_true")
    parser.add_argument("--dates", action="store_true")
    parser.add_argument("--range", nargs="+")
    parser.add_argument("--login")
    parser.add_argument("--code")
    parser.add_argument("--password")
    parser.add_argument("--logout", action="store_true")

    return parser


def login(wf, username, password, code):
    session_id = Transport.login(username, password, code)
    wf.logger.debug(session_id)
    wf.save_password("session_id", session_id)


def logout(wf):
    wf.delete_password("session_id")
    print("Logout successful")


def main(wf):
    parser = create_parser()
    args = parser.parse_args(sys.argv[1].split())
    if args.login:
        login(wf, args.login, password=args.password, code=args.code)
        print("Login Successfull")
        return 0

    if args.logout:
        logout(wf)
        return 0

    try:
        session_id = wf.get_password("session_id")
        wf.setvar("session_id", session_id)
    except PasswordNotFound:  # API key has not yet been set
        wf.add_item(
            "No API key set.",
            "Please use wlogin to set your Workflowy API key.",
            valid=False,
            icon="img/bug.png",
        )
        wf.send_feedback()
        return 0

    def wrapper():
        return get_tree(session_id)

    tree, tree_with_completed, transaction_id = wf.cached_data(
        "workflowy_tree", None, max_age = 0
    )
    if not wf.cached_data_fresh('workflowy_tree', max_age=15):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)
    
    if args.with_completed:
        tree = tree_with_completed

    wf.setvar("transaction_id", transaction_id)


    query = " ".join(args.query)
    if len(args.query) < 2 and args.tags or args.mentions:
        options_dict = tree.tags if args.tags else tree.mentions
        if len(args.query) != 1 or args.query[0] not in options_dict:
            options_dict = wf.filter(query, options_dict)
            for option in options_dict:
                wf.add_item(
                    title=option,
                    icon="img/tag.png" if args.tags else "img/mention.png",
                    autocomplete="%s " % option,
                )
            if len(options_dict) == 0:
                wf.add_item(
                    "No results !",
                    "Hit Enter to clear your search",
                    valid=False,
                    autocomplete="",
                    icon="img/info.png",
                )
            wf.send_feedback()
            return 0

    if args.hierarchical:
        nodes = tree.root_nodes
    elif args.starred:
        nodes = tree.starred_nodes
    elif args.only_links:
        nodes = [node for node in tree.nodes if node.has_link]
    else:
        nodes = tree.nodes

    if args.dates:
        nodes = get_scheduled_nodes(tree, *args.range)

    autocomplete = ""
    if len(args.query) > 0:
        i = 0
        if len(args.query) == 1 and args.mentions or args.tags:
            node_ids = (
                tree.tags[args.query[0]] if args.tags else tree.mentions[args.query[0]]
            )
            nodes = [tree.available_nodes[node_id] for node_id in node_ids]
            autocomplete = "%s " % args.query[0]
            i += 1
        while i < len(args.query) and args.query[i] in tree.available_nodes:
            node = tree.available_nodes[args.query[i]]
            autocomplete = "%s%s " % (autocomplete, node.short_id)
            nodes = node.children
            i += 1
            query = " ".join(args.query[i:])

    nodes = wf.filter(
        query, nodes, key=lambda node: node.name, match_on=MATCH_ALL ^ MATCH_ALLCHARS
    )

    for node in nodes:
        if args.node:
            add_simple_node_item(wf, node, autocomplete)
        else:
            add_node_item(wf, node, autocomplete, sortable=not args.hierarchical)

    if args.starred:
        for search in tree.starred_searches:
            add_search_item(search)

    if len(nodes) + len(tree.starred_searches) == 0:
        wf.add_item(
            "No results !",
            "Hit Enter to clear your search",
            valid=False,
            autocomplete="",
            icon="img/info.png",
        )

    wf.send_feedback()

def get_scheduled_nodes(tree, start, end=None):
    if end is not None:
        node_ids = set()
        start = datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")
        for date in daterange(start, end, end_included=True):
            node_ids.update(tree.calendar[date.strftime("%Y-%m-%d")])
    else:
        node_ids = tree.calendar[start]
    return [tree.available_nodes[node_id] for node_id in node_ids]

def add_simple_node_item(wf, node, autocomplete, sortable=True):
    wf.add_item(
        title=node.text or "Empty",
        subtitle=node.path,
        uid=node.id if sortable else None,
        valid=True,
        arg=node.id,
        icon=get_node_icon(node),
        autocomplete="%s%s " % (autocomplete, node.short_id)
        if node.children
        else None,
        copytext=coalesce([node.note, node.embed_link, node.name]),
        largetext=coalesce([node.note, node.name]),
        quicklookurl=node.embed_link,
    )

def add_node_item(wf, node, autocomplete, sortable=True):
    it = wf.add_item(
        title=node.text or "Empty",
        subtitle=node.path,
        uid=node.id if sortable else None,
        valid=True,
        arg=node.website_url,
        icon=get_node_icon(node),
        autocomplete="%s%s " % (autocomplete, node.short_id)
        if node.children
        else None,
        copytext=coalesce([node.note, node.embed_link, node.name]),
        largetext=coalesce([node.note, node.name]),
        quicklookurl=node.embed_link,
    )

    it.setvar("node_name", node.name)
    it.setvar("node_note", node.note)
    it.setvar("node_id", node.id)
    it.setvar("node_desktop_url", node.desktop_url)
    it.setvar("node_website_url", node.website_url)
    it.setvar("node_embed_url", node.embed_link)
    it.setvar("node_is_completed", int(node.is_completed))

    it.add_modifier(
        "cmd",
        arg=node.desktop_url,
        subtitle="Open in Desktop App",
        valid=True,
    )

    it.add_modifier(
        "alt",
        arg=node.id,
        subtitle="Create child node",
        valid=True,
    )

    if node.embed_link:
        it.add_modifier(
            "shift",
            arg=node.embed_link,
            subtitle="Open Embed Link: %s" % node.embed_link,
            valid=True,
        )
        if node.has_inner_link:
            inner_link_desktop = node.embed_link.replace("https://", "workflowy://")
            it.add_modifier(
                "cmd+shift",
                arg=inner_link_desktop,
                subtitle="Open Inner Link in Desktop",
                valid=True,
            )

def add_search_item(wf, search):
    if search.node is None:
        website_url = "https://workflowy.com#?q={}".format(search.query)
        desktop_url = "workflowy://workflowy.com/#?q={}".format(search.query)
        subtitle = "Home"

    else:
        website_url = "https://workflowy.com/#/{}?q={}".format(
            search.node.short_id, search.query
        )
        desktop_url = "workflowy://workflowy.com/#/{}?q={}".format(
            search.node.short_id, search.query
        )
        subtitle = search.node.name
    it = wf.add_item(
        title="Starred Search: {}".format(search.query),
        subtitle=subtitle,
        arg=website_url,
        valid=True,
        icon="img/search.png",
    )
    it.setvar("node_desktop_url", desktop_url)
    it.setvar("node_website_url", website_url)
    it.add_modifier(
        "cmd",
        arg=desktop_url,
        subtitle="Search in Desktop App",
        valid=True,
    )

if __name__ == "__main__":
    wf = Workflow3()
    sys.exit(wf.run(main))
