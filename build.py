#!/usr/bin/env python3

import json
import re


"""
Generate the navigation HTML for a given page
"""
def generate_navigation(structure, current_id, is_root=True):
    is_current = False

    # If leaf, generate a link to that page
    if structure["leaf"]:
        # Decide if link points to current page
        opening_class = ""
        if structure["id"] == current_id:
            is_current = True
            opening_class = " class=\"current\""

        # Generate exactly 1 line
        lines = [f"<a href=\"{structure['id']}.html\"{opening_class}>{structure['title']}</a>\n"]

    # If not leaf, generate the HTML recursively
    else:
        # Generate link to section index (should be a leaf, normally)
        is_current, lines = generate_navigation(structure["index"], current_id, False)

        # Generate lists for sub-sections
        # This has to be done first to know if we are "current" (for Expand)
        sub_lines = []
        for sub_struct in structure["subpages"]:
            # Generate navigation for the sub-section, inheriting "current" status
            # Note that the root element will always be marked as current
            _is_current, _sub_lines = generate_navigation(sub_struct, current_id, False)
            is_current |= _is_current

            # Insert list elem (including indenting, I know it's stupid but the output looks nicer = better debugging)
            sub_lines.append("<li>\n")
            sub_lines.extend([ f"    {line}" for line in _sub_lines ])
            sub_lines.append("</li>\n")

        # Prepare attrs for expanding shenanigans
        opening_attr = ""
        if is_current and not is_root: # Prevent checking "Expand all" by default
            opening_attr = " checked"
        section_id = structure["index"]["id"]

        # Generate "Expand" elems (the checkbox holds the state, the label serves as the interactor)
        lines.append(f"<input type=\"checkbox\" id=\"{section_id}-navcheckbox\"{opening_attr}>\n")
        lines.append(f"<label for=\"{section_id}-navcheckbox\"></label>\n")
        lines.append("<ol>\n")

        # Add sub-sections (& index)
        lines.extend([ f"    {line}" for line in sub_lines ])
        lines.append("</ol>\n")

    return is_current, lines

"""
Generate a double-linked "list" of all page IDs (using a left-child depth-first search of the tree)
Empty connections are omitted entirely so as to not be iterated over
"""
def build_links(structure, links = {}, prev = None):
    # Leaves are registered into the list
    if structure["leaf"]:
        this_id = structure["id"]
        # If there was a previous element, register as its next, and register it as our prev
        if prev != None:
            links[prev]["next"] = this_id
            links[this_id] = {"prev": prev}
        # Otherwise hope that we'll get a "next" connection
        else:
            links[this_id] = {}
        # Register as the next element's previous one
        prev = this_id

    # Non-leaves register their children recursively
    else:
        links, prev = build_links(structure["index"], links, prev)
        for sub_struct in structure["subpages"]:
            links, prev = build_links(sub_struct, links, prev)

    return links, prev

"""
Return the struct's leaf with the given ID, or None if none exists
"""
def get_structure(page_id, structure):
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

"""
Generate all pages in a structure recursively
"""
def generate_pages(structure, site_structure, links, template, include_re):

    # Non-leaves generate their children
    if not structure["leaf"]:
        generate_pages(structure["index"], site_structure, links, template, include_re)
        for sub_struct in structure["subpages"] + structure.get("special_pages", []):
            generate_pages(sub_struct, site_structure, links, template, include_re)

    # Leaves actually generate the page
    else:
        print(f"Generating page {structure['id']}.html, \"{structure['title']}\"...")

        # First, generate the "snips" that will be inserted into the template
        HTML_snips = {}
        # They're hardcoded, which might be a problem (but I doubt it)
        HTML_snips["navigation"] = generate_navigation(site_structure, structure["id"])[1] # Navbar's list
        HTML_snips["title"] = [ f"{structure['title']} - GB ASM tutorial" ] # <title> content
        HTML_snips["heading"] = [ structure["title"] ] # <h1> content
        # "prev" and "next" pages; useful for prefetching, apparently
        # Also "Previous" and "Next" pages, useful for user navigation this time
        page_links = links.get(structure["id"])
        if page_links != None:
            HTML_snips["prev_next"] = [ f"<link rel=\"{pair[0]}\" href=\"{pair[1]}.html\" />\n" for pair in links[structure["id"]].items() ]
            previous_next = {"prev": "Previous", "next": "Next"}
            HTML_snips["previous_next_pages"] = [ f"<br /><a href=\"{pair[1]}.html\">{previous_next[pair[0]]}: {get_structure(pair[1], site_structure)['title']}</a>\n" for pair in links[structure["id"]].items() ]
        else:
            HTML_snips["prev_next"] = []
            HTML_snips["previous_next_pages"] = []
        # Actual page content
        with open(f"src/{structure['id']}.html", "rt", encoding = "utf8") as content_file:
            HTML_snips["content"] = content_file.readlines()

        # Now generate the final HTML
        out_lines = []
        for line in template:
            # Check if the line should trigger snippet insertion
            match = include_re.match(line)
            if match:
                snip = HTML_snips.get(match.group("id"), None)
                if snip == None:
                    raise IndexError(f"Unknown snippet name: {match.group('id')}")

                # Insert all snippet lines with leading whitespace (looks more "pro" :p); however, <pre> blocks should *not* be indented
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
                # Snips don't have a trailing newline, enforce it
                out_lines.append("\n")

            # If not a snippet, just copy the line
            else:
                out_lines.append(line)

        # Finally, write the output (buffer everything to preserve pages if an error occurs)
        with open(f"docs/{structure['id']}.html", "wt", encoding = "utf8") as out_file:
            out_file.writelines(out_lines)


if __name__ == "__main__":
    # Perform common operations

    # Read the tutorial's structure
    with open("structure.json", "rt") as f:
        site_structure = json.load(f)

    # Read template HTML file
    with open("template.html", "rt") as template_file:
        template = template_file.readlines()

    # Compile regex that detects & parses `#include` lines
    include_re = re.compile("(?P<whitespace>\s+)#include\s+(?P<id>\w+)", re.IGNORECASE)


    # Generate the pages

    print("Building links...")
    links = build_links(site_structure)[0]

    print("Generating pages...")
    generate_pages(site_structure, site_structure, links, template, include_re) # site_structure argument is duplicated due to the recursive call; it would also allow generating only a subset of all pages if there ever was a point to that
