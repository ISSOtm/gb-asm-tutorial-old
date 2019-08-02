# gb-asm-tutorial

An online Game Boy assembly programming tutorial, hosted at https://eldred.fr/gb-asm-tutorial.


## Building

The "output" is located in the `docs` folder, which is what is served publicly. (Note: GitHub Pages only considers the `master` branch's `docs` folder.)

The `.html` files in that folder's root are **auto-generated** (and thus shouldn't be edited manually). To re-generate them, run the `build.py` Python script. (May not work with Python 2).


The page's contents are located in the `src` folder. They are inserted into the `template.html` file, alongside a few other generated HTML snippets. The structure of the tutorial is contained within the `structure.json` file.


## The structure

Each element MUST contain a `leaf` boolean attribute. If that attribute is `true`, then it is a leaf; otherwise it's not.

A leaf MUST contain the following attributes:
<dl>
    <dt><code>id</code></dt><dd>The page's ID; `.html` is appended to it to get the source and destination HTML page</dd>
    <dt><code>title</code></dt><dd>The page's displayed name</dd>
</dl>

A non-leaf MUST contain the following attributes:
<dl>
    <dt><code>index</code></dt><dd>The ID of the page that serves as the subtree/section's index</dd>
    <dt><code>subpages</code></dt><dd>The list of subpages that this section contains. May contain non-leaves.</dd>
</dl>
A non-leaf MAY contain the following attributes:
<dl>
    <dt><code>special_pages</code></dt><dd>A list of subpages that should not be present in the tree, but still be generated nonetheless.</dd>
</dl>
