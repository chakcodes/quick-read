# General-purpose expandable reader

Use `scripts/render_reader.py` to render content after its overview has been written, its accuracy checked, and its language selected. The script only validates, safely escapes, and renders the input; it does not summarize, translate, or infer a language.

Each section shows its condensed overview by default. Its complete body expands directly below it, and multiple sections can remain open at once. Full-text mode displays all complete bodies in sequence without repeating the overviews. Returning to overview mode restores the previous expansion state. Without JavaScript, native section expansion still works and the mode buttons remain hidden.

## Input JSON

The input must be UTF-8 JSON with the following fields:

| Field | Requirement |
| --- | --- |
| `title` | A nonempty title in the selected output language |
| `language` | A BCP 47 language tag for the document and shared controls, such as `en`, `zh-Hans`, `zh-Hant`, or `ar` |
| `notice` | A nonempty notice, in the appropriate language, explaining that the overview is a condensed rewrite and the complete body can be expanded |
| `labels` | All six nonempty control labels are required: `overview`, `full`, `expand`, `collapse`, `body`, and `source`. The script supplies no default language. |
| `sections` | A nonempty array in the original source order |
| `direction` | Optional: `auto` (default), `ltr`, or `rtl` |
| `byline` | Optional attribution that preserves the actual author's identity; omit it when no author is given |
| `source_url` | An optional HTTP(S) source link; script URLs, credentials, and whitespace are not accepted |

Each item in `sections` contains:

| Field | Requirement |
| --- | --- |
| `overview` | A nonempty condensed rewrite that preserves the source's narrative perspective and main logic |
| `body` | The nonempty complete body, preserving words, punctuation, line breaks, and indentation |
| `heading` | An optional navigation heading; defaults to an empty string |
| `language` | An optional section language; inherits the document language by default. Set it per section for sources containing multiple languages. |
| `overview_language` | An optional language for the overview and its navigation heading; takes precedence over the section's `language`, which in turn inherits the document's `language` |
| `body_language` | An optional language for the complete body; takes precedence over the section's `language`, which in turn inherits the document's `language` |
| `direction` | Optional: `auto` (default), `ltr`, or `rtl` |

Language tags do not translate content. All visible text comes from the input. Apply the skill's language rules before filling in the JSON. Choose an accurate `labels.body` label for the content, such as "Complete original text," "Complete text," or "Complete translation," in the appropriate language. A Traditional Chinese source requires a Traditional Chinese overview and labels unless translation is explicitly requested. Example labels are `概覽`, `全文`, `展開原文`, `收起`, `完整原文`, and `原文來源`. If the user asks in Chinese but provides English material, the controls and overview still use English.

For example, if the user explicitly requests a Spanish overview while retaining the English original, set the document and controls to `language: "es"` and the relevant section to `overview_language: "es"` and `body_language: "en"`. Keep the original English in the body. The overview and body receive separate language tags rather than sharing an inaccurate `lang` attribute.

Example for an English source:

```json
{
  "title": "Retry behavior",
  "language": "en",
  "notice": "Condensed overview. Expand each section for the complete text.",
  "labels": {
    "overview": "Overview",
    "full": "Full text",
    "expand": "Read complete text",
    "collapse": "Collapse",
    "body": "Complete text",
    "source": "Source"
  },
  "sections": [
    {
      "heading": "Retry only after a timeout",
      "overview": "We retry once after a timeout, but never after a rejected request.",
      "body": "We wait for the response. If the request times out, we retry once.\nIf the server rejects the request, we stop without retrying."
    }
  ]
}
```

## Generation and display

Save the prepared JSON in a directory allowed for the current task. Replace the paths in this command:

```bash
python3 <skill-dir>/scripts/render_reader.py <input.json> <preview.html>
```

The default output is an HTML fragment. Save inline previews in a persistent directory that the current task can read and write, and display them through a rendering mechanism confirmed to work in the environment. If `visualize` is available, follow its rendering requirements when using the generated fragment. Add `--standalone` only when a standalone page is needed:

```bash
python3 <skill-dir>/scripts/render_reader.py <input.json> <reader.html> --standalone
```

The destination's parent directory must already exist. Existing files are not overwritten by default; add `--force` when intentionally updating your own preview. Input and output must not point to the same file. The script rejects symbolic links as output paths and does not create extra files or make network requests.

Inline fragments have a 1 MB limit. Exceeding it produces an error without truncating the body. Use a standalone document or divide the content into multiple readers at complete semantic boundaries.

## Content handling and validation limits

- This template renders the body as **plain text**, preserving line breaks, indentation, symbols, and code text. It does not parse Markdown, mathematical notation, or HTML. Input tags appear as text and are not executed.
- For rich Markdown tables, formulas, or specialized code formatting, use a native Markdown folding or rendering mechanism confirmed to work in the environment, or provide the complete source file with its formatting preserved. Do not silently damage the source formatting or write an incomplete Markdown parser as a workaround.
- Nonempty-string validation does not trim input whitespace. Null characters and invalid Unicode that HTML cannot preserve produce explicit errors.
- Compare the generated complete body with the source, paying particular attention to whitespace, punctuation, code, and paragraph order. In the actual rendering environment, verify the default collapsed state, individual section expansion, simultaneous expansion of multiple sections, and full-text mode switching.
- Format validation does not establish that the overview preserves meaning, that the language selection is correct, or that the host supports the interactions. Verify each of these separately.
