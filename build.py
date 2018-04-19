#!/usr/bin/python3

import json
import re


# Read the tutorial's structure 
with open("structure.json", "rt") as f:
    site_structure = json.load(f)


# Perform common operations

with open("template.html", "rt") as template_file:
    template = template_file.readlines()

include_re = re.compile("(?P<whitespace>\s+)#include\s+(?P<id>\w+)", re.IGNORECASE)


"""
Generates the navigation HTML for a given page
"""
def generate_navigation(structure, current_id):
    is_current = False

    if structure["leaf"]:
        opening_class = ""

        if structure["id"] == current_id:
            is_current = True
            opening_class = " class=\"current\""
        
        lines = ["<a href=\"{}.html\"{}>{}</a>".format(structure["id"], opening_class, structure["title"])]
    
    else:
        is_current, lines = generate_navigation(structure["index"], current_id)

        sub_lines = []
        for sub_struct in structure["subpages"]:
            sub_lines.append("<li>")

            _is_current, _sub_lines = generate_navigation(sub_struct, current_id)
            is_current |= _is_current

            sub_lines.extend(_sub_lines)
            sub_lines.append("</li>")
        
        if is_current:
            lines.append("<ol class=\"current\">")
        else:
            lines.append("<ol>")
        
        lines.extend(sub_lines)
        lines.append("</ol>")
    
    return is_current, lines


# Generate the pages

def build_links(structure, links = {}, prev = None):
    if structure["leaf"]:
        this_id = structure["id"]
        if prev != None:
            links[prev]["next"] = this_id
            links[this_id] = {"prev": prev}
        else:
            links[this_id] = {}
        prev = this_id
    
    else:
        links, prev = build_links(structure["index"], links, prev)
        for sub_struct in structure["subpages"]:
            links, prev = build_links(sub_struct, links, prev)

    return links, prev

def get_structure(page_id, structure=site_structure):
    if structure["leaf"]:
        if structure["id"] == page_id:
            return structure
        else:
            return None
    
    else:
        struct = get_structure(page_id, structure["index"])
        if struct != None:
            return struct
        
        for sub_struct in structure["subpages"]:
            struct = get_structure(page_id, sub_struct)
            if struct != None:
                return struct
        
        return None

def generate_page(structure, links):
    global site_structure
    global include_re
    global template

    if not structure["leaf"]:
        generate_page(structure["index"], links)
        for sub_struct in structure["subpages"] + structure.get("special_pages", []):
            generate_page(sub_struct, links)
    
    else:
        print("Generating page {}.html, \"{}\"...".format(structure["id"], structure["title"]))

        HTML_snips = {}
        HTML_snips["navigation"] = generate_navigation(site_structure, structure["id"])[1]
        HTML_snips["title"] = [ structure["title"] ]
        page_links = links.get(structure["id"])
        if page_links != None:
            HTML_snips["prev_next"] = [ "<link rel=\"{}\" href=\"{}.html\" />".format(*pair) for pair in links[structure["id"]].items() ]
            previous_next = {"prev": "Previous", "next": "Next"}
            HTML_snips["previous_next_pages"] = [ "<br /><a href=\"{}.html\">{}: {}</a>".format(pair[1], previous_next[pair[0]], get_structure(pair[1])["title"]) for pair in links[structure["id"]].items() ]
        else:
            HTML_snips["prev_next"] = []
            HTML_snips["previous_next_pages"] = []
        with open("src/{}.html".format(structure["id"]), "rt") as content_file:
            HTML_snips["content"] = content_file.readlines()

        out_lines = []
        for line in template:
            match = include_re.match(line)
            if match:
                snip = HTML_snips.get(match.group("id"), None)
                if snip == None:
                    raise IndexError("Unknown snippet name: {}".format(match.group("id")))

                for line in snip:
                    out_lines.append(match.group("whitespace") + line)
                out_lines.append("\n") # The snip doesn't have a trailing newline, enforce it
            
            else:
                out_lines.append(line)

        with open("docs/{}.html".format(structure["id"]), "wt") as out_file:
            out_file.writelines(out_lines)

print("Building links...")
links = build_links(site_structure)[0]

print("Generating pages...")
generate_page(site_structure, links)
