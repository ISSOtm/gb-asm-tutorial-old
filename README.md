# gb-asm-tutorial

An online Game Boy assembly programming tutorial, hosted at https://eldred.fr/gb-asm-tutorial.

## Structure

The `docs` folder is what is served publicly. (Note: GitHub Pages only considers the `master` branch's `docs` folder.)

The `src` folder contains all "source" HTML files, sorted by language. (This hierarchy is **not** preserved in the `docs` folder due to historical reasons). Each of those files contains a page's "main content" (ie. not the navigation, header, etc. HTML; this is taken care of by the build script)

Files in the root of the repo are for converting the pages only (plus this README for obvious reasons).

## Building

To convert files from the `src` folder to `docs`, run `build.py`. Python 3 is required.

### Missing pages

If a page isn't present in a given language, a fallback will be generated offering to read it in another language. This is intended for pages that haven't been translated yet.

## `properties.json`

This file is read by `build.py` to determine what pages to convert.

### `structure` attribute

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
