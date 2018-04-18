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

def generate_page(structure, links):
    global site_structure
    global include_re

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
        with open("src/{}.html".format(structure["id"]), "rt") as content_file:
            HTML_snips["content"] = content_file.readlines()

        out_lines = []
        for line in template:
            match = include_re.match(line)
            if match:
                for line in HTML_snips.get(match.group("id"), []):
                    out_lines.append(match.group("whitespace") + line)
            
            else:
                out_lines.append(line)

        with open("docs/{}.html".format(structure["id"]), "wt") as out_file:
            out_file.writelines(out_lines)

print("Building links...")
links = build_links(site_structure)[0]

print("Generating pages...")
generate_page(site_structure, links)
