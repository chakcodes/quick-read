---
name: quick-read
description: "Turn long texts or complete answers into concise overviews shown by default, with the full text expandable by section. Use for overview reading, progressive disclosure, and reducing the reading burden of long answers while preserving the source. Keep the source language, narrative perspective, and main logic; change languages only when explicitly requested."
---

# Quick Read

Make the overview a coherent, condensed text that can be read on its own, with complete content available on expansion. Adapt to literature, explanations, technical answers, instructions, and arguments instead of imposing one genre's style on every source.

## Establish the complete content

- For an existing article, file, or link, obtain the complete text to be processed and confirm its source and order before condensing it. If only an excerpt is available, do not claim to have the full text or reconstruct an "original" from a summary.
- For a newly generated answer, first develop the complete answer needed to address the user's question, then organize the overview and expansion layers. Label the expanded layer "Full text" rather than implying an external original source. Localize this label according to the language rules below.
- Segment by complete units of meaning. Usually keep the original paragraphs; closely related adjacent paragraphs may be grouped when useful, while retaining their internal paragraph breaks and original order. Do not split mechanically by a fixed paragraph count or text length.
- For existing content, preserve all words, punctuation, writing variants, citations, data, and code in the expanded layer. Web navigation and invisible layout markers may be removed; formatting changes must not become textual rewrites. Apply explicit editing or translation requests only within their requested scope.

## Language rules

1. **An explicitly requested target language takes precedence, within the requested scope.** If only the overview should change languages, translate the overview and its associated headings and controls while keeping the full text in the source language. If the entire output should change languages, translate both the overview and the complete text, label the latter as a translation, retain its source attribution, and do not call it a verbatim original.
2. **Without an explicit language request, inherit the source language and writing variant.** An English source gets an English overview; a Traditional Chinese source gets a Traditional Chinese overview. A question asked in Chinese does not by itself authorize translating English material or converting Traditional Chinese to Simplified Chinese. The English language of these skill instructions does not set the output language.
3. Apply the same language choice to titles, notices, buttons, and expansion labels. For multilingual material, inherit each section's language; use the document's dominant language for shared controls, or the first substantive section's language when none dominates. Preserve code, symbols, proper names, and necessary terminology rather than changing them merely for language uniformity.
4. When generating a new answer without an external source, use the user's explicitly requested language; otherwise inherit the language and writing variant of their current request.

## Condense while preserving perspective and logic

- **Rewrite concisely instead of stitching together excerpts.** Reorganize each section's key meaning into tighter prose so the overviews form a coherent text that stands on its own. Headings, keywords, opening sentences, and selected striking quotations do not substitute for an overview.
- **Inherit the narrative perspective.** Keep "I" when the source uses "I", continue addressing "you" when the source does, and retain third person where appropriate. Do not add outside commentary such as "the author argues" or "readers can see" unless it already appears in the source or the user requests external analysis.
- Preserve speakers, quotation attribution, narrative timing, and the limits of what was known. Distinguish feelings at the time from later reflection; do not present later knowledge as something already known then or invent a person's inner thoughts.
- Preserve the main causal links, contrasts, sequence, prerequisites, negations, exceptions, and uncertainty. Conditions that affect a conclusion must appear in the overview rather than being hidden entirely in the expanded text. In technical content, also retain numbers, units, and step dependencies that affect actions or judgments.
- Retain the original attitude and emotional intensity. Do not turn possibilities into certainties, reduce complex experiences to a single judgment, or add advice or conclusions absent from the source. Provide additional interpretation only when needed by the user, clearly separated from the overview.
- Do not impose a compression ratio. Remove repetition and secondary elaboration while retaining the concrete information needed for understanding. Condensing is not completely lossless; the full text preserves the details and original expression.

## Default reading experience

- Show only the coherent, condensed overview by default. Each overview section independently expands its corresponding full text directly below it; allow multiple sections to remain open.
- Use a simple single-column reading order. Headings may aid navigation but must not replace the overview. Do not add card grids, scores, complex navigation, or nested disclosure levels to ordinary reading.
- Provide an "Overview / Full text" switch, localized to the chosen language. Full-text mode displays the complete text continuously in its original order without repeating the overview. Returning to overview mode preserves the previously expanded sections.
- Briefly identify the overview as a condensed rewrite in the content's language. Keep accessible source references when available, and distinguish translations from originals and generated answers from external source text.
- Preserve the content and readable structure of code, tables, formulas, images, and links. Do not remove them to fit a particular template.

## Choose an available presentation method

Prefer an interactive presentation confirmed to work in the current environment. The skill defines content rules; disclosure requires a working renderer.

- **Inline interactive previews:** If `visualize` is available, follow its instructions to generate and display an HTML fragment in a durable directory writable by the current conversation. Read the [rendering contract](references/rendering.md) first; reuse this skill's `scripts/render_reader.py` and `assets/reader.html` instead of rebuilding disclosure behavior. The script handles presentation and safe escaping only; it does not condense or translate content.
- **Markdown environments with confirmed HTML disclosure support:** Use native `<details>/<summary>`, with the overview as the always-visible summary and the full text as the expanded content. Do not put the tags inside a code block and claim they are interactive.
- **Standalone HTML delivery:** Use the same script with `--standalone` to generate a readable HTML document.
- **No disclosure support:** Present clearly corresponding overview and full-text sections in order, with a brief note that this format does not support click-to-expand. Do not imitate interactive buttons or omit the full text.

The template preserves body text, line breaks, and indentation as plain text; it does not parse Markdown. When rich formatting is needed, use an appropriate renderer available in the environment while following this skill's content and language rules.

## Check before delivery

- Compare each overview with its full text for perspective, timing, core causality, qualifications, numbers, negations, and uncertainty. Confirm that it is a condensed rewrite rather than an extract.
- Check that the overview, headings, notices, and controls follow the requested or inherited language and writing variant. Validate multilingual content and explicit translation requests within their specified scope.
- For existing text that was not requested to be rewritten, compare the complete content, paragraph order, and source section by section to catch omissions or unintended translation. Code and tables are part of the full text too.
- Check the initial overview, individual expansion and collapse, full-text switching, keyboard operation, and narrow-screen readability. When only text changes and the interaction is unchanged, do not repeat the entire UI test suite.
