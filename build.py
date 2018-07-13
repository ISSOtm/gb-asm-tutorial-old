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
def generate_navigation(structure, current_id, is_root=True):
    is_current = False

    if structure["leaf"]:
        opening_class = ""

        if structure["id"] == current_id:
            is_current = True
            opening_class = " class=\"current\""
        
        lines = ["<a href=\"{}.html\"{}>{}</a>\n".format(structure["id"], opening_class, structure["title"])]
    
    else:
        # Generate link to section index
        is_current, lines = generate_navigation(structure["index"], current_id, False)

        # Generate lists for sub-sections
        sub_lines = []
        for sub_struct in structure["subpages"]:
            sub_lines.append("<li>\n")

            _is_current, _sub_lines = generate_navigation(sub_struct, current_id, False)
            is_current |= _is_current

            sub_lines.extend([ "    " + line for line in _sub_lines ])
            sub_lines.append("</li>\n")

        # Prepare attrs for expanding shenanigans
        opening_attr = ""
        if is_current and not is_root: # Do not "expand all" by default
            opening_attr = " checked"
        section_id = structure["index"]["id"]
        
        lines.append("<input type=\"checkbox\" id=\"" + section_id + "-navcheckbox\"" + opening_attr + ">\n")
        lines.append("<label for=\"" + section_id + "-navcheckbox\"></label>\n")
        lines.append("<ol>\n")
        
        lines.extend([ "    " + line for line in sub_lines ])
        lines.append("</ol>\n")
    
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
            HTML_snips["prev_next"] = [ "<link rel=\"{}\" href=\"{}.html\" />\n".format(*pair) for pair in links[structure["id"]].items() ]
            previous_next = {"prev": "Previous", "next": "Next"}
            HTML_snips["previous_next_pages"] = [ "<br /><a href=\"{}.html\">{}: {}</a>\n".format(pair[1], previous_next[pair[0]], get_structure(pair[1])["title"]) for pair in links[structure["id"]].items() ]
        else:
            HTML_snips["prev_next"] = []
            HTML_snips["previous_next_pages"] = []
        with open("src/{}.html".format(structure["id"]), "rt", encoding = "utf8") as content_file:
            HTML_snips["content"] = content_file.readlines()

        out_lines = []
        for line in template:
            match = include_re.match(line)
            if match:
                snip = HTML_snips.get(match.group("id"), None)
                if snip == None:
                    raise IndexError("Unknown snippet name: {}".format(match.group("id")))

                pre_mode = False
                for line in snip:
                    last_line = False
                    if len(re.findall("(<pre>|</pre>)", line, re.IGNORECASE)) % 2 == 1:
                        pre_mode = not pre_mode
                        if not pre_mode:
                            last_line = True
                    
                    if not pre_mode and not last_line:
                        line = match.group("whitespace") + line

                    out_lines.append(line)
                out_lines.append("\n") # The snip doesn't have a trailing newline, enforce it
            
            else:
                out_lines.append(line)

        with open("docs/{}.html".format(structure["id"]), "wt", encoding = "utf8") as out_file:
            out_file.writelines(out_lines)

print("Building links...")
links = build_links(site_structure)[0]

print("Generating pages...")
generate_page(site_structure, links)
