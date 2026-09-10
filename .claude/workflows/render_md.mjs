// Walk a markdown document the way a reader sees it, not the way the source
// looks. Used by the record job (#682): disposition documents are read as
// source by every other check, and the class of defect a seat does not notice
// is exactly a render that disagrees.
//
// markdown-it 14.1.0, vendored beside this file so the walk is offline. Tables
// are in its default preset. html and linkify stay off: we compare structure,
// not a browser DOM, and an autolinked URL is not a link whose text is `#NNN`.

import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const MarkdownIt = require('./vendor/markdown-it.min.js')

const md = new MarkdownIt({ html: false, linkify: false, typographer: false })

// A `#NNN` markdown link resolves iff the href is a GitHub issue or pull
// request for that same number. The citations class already does the path /
// symbol half for policy files; these two documents were outside that corpus
// on purpose and so a `#677` pointing at `/issues/999` was nobody's finding.
const ISSUE_HREF_RE = /^https:\/\/github\.com\/[^/]+\/[^/]+\/(?:issues|pull)\/(\d+)(?:$|[?#/])/

function stripQuote(line) {
  return line.replace(/^(?:\s{0,3}>\s?)+/, '')
}

function isPipeLine(line) {
  return /^\s{0,3}\|/.test(stripQuote(line))
}

// GFM cell count, not the rendered td count. markdown-it already truncates a
// five-cell row in a three-column table to three tokens, which is how a
// Delivery-status overflow sat in the source while every token walk agreed
// with the header.
function rowCells(line) {
  let s = stripQuote(line).replace(/^\s{0,3}/, '')
  if (!s.startsWith('|')) return 0
  const inner = s.replace(/^\|/, '').replace(/\|\s*$/, '')
  const parts = []
  let buf = ''
  for (let i = 0; i < inner.length; i++) {
    if (inner[i] === '\\' && inner[i + 1]) {
      buf += inner[i] + inner[i + 1]
      i += 1
      continue
    }
    if (inner[i] === '|') {
      parts.push(buf)
      buf = ''
      continue
    }
    buf += inner[i]
  }
  parts.push(buf)
  return parts.length
}

function isDelim(line) {
  let s = stripQuote(line).replace(/^\s{0,3}/, '')
  if (!s.startsWith('|')) return false
  const inner = s.replace(/^\|/, '').replace(/\|\s*$/, '')
  const parts = inner.split('|')
  return parts.length > 0 && parts.every((p) => /^\s*:?-+:?\s*$/.test(p))
}

function fenced(lines) {
  const out = Array(lines.length).fill(false)
  let fence = null
  for (let i = 0; i < lines.length; i++) {
    const m = /^( {0,3})(`{3,}|~{3,})/.exec(lines[i])
    if (fence) {
      out[i] = true
      if (m && m[2][0] === fence.ch && m[2].length >= fence.n) fence = null
      continue
    }
    if (m) {
      fence = { ch: m[2][0], n: m[2].length }
      out[i] = true
    }
  }
  return out
}

// Source `|…|` blocks that contain a delimiter row, outside fences. 0–3 spaces
// of indent, matching GFM: four spaces is a code block and not a table.
function sourceTableCount(text) {
  const lines = text.split('\n')
  const fence = fenced(lines)
  let n = 0
  let i = 0
  while (i < lines.length) {
    if (fence[i] || !isPipeLine(lines[i])) {
      i += 1
      continue
    }
    const start = i
    while (i < lines.length && !fence[i] && isPipeLine(lines[i])) i += 1
    if (lines.slice(start, i).some(isDelim)) n += 1
  }
  return n
}

function linkTextFindings(token) {
  const out = []
  if (!token.children) return out
  let href = null
  let buf = ''
  for (const c of token.children) {
    if (c.type === 'link_open') {
      href = c.attrGet('href') || ''
      buf = ''
      continue
    }
    if (c.type === 'text' && href != null) {
      buf += c.content
      continue
    }
    if (c.type === 'link_close' && href != null) {
      const m = /^#(\d+)$/.exec(buf)
      if (m) {
        const ok = ISSUE_HREF_RE.exec(href)
        if (!ok || ok[1] !== m[1]) {
          out.push({
            line: (token.map?.[0] ?? 0) + 1,
            message: `link text #${m[1]} does not resolve to a pull request or issue`,
          })
        }
      }
      href = null
    }
  }
  return out
}

// Pure over the text. findings carry a 1-based line so the caller can attach
// a path; counts are what the record job prints beside RECORD:/TABLES:/CAPS:.
export function inspectRender(text) {
  const lines = text.split('\n')
  const tokens = md.parse(text, {})
  const findings = []
  let tables = 0
  let rows = 0
  let lists = 0
  let items = 0
  const stack = []

  const walk = (ts) => {
    for (const t of ts) {
      if (t.type === 'table_open') tables += 1
      if (t.type === 'tr_open') rows += 1
      if (t.type === 'ordered_list_open') {
        lists += 1
        stack.push({ start: Number(t.attrGet('start') || 1), i: 0 })
      }
      if (t.type === 'ordered_list_close') stack.pop()
      if (t.type === 'list_item_open' && stack.length) {
        const top = stack[stack.length - 1]
        const rendered = top.start + top.i
        top.i += 1
        items += 1
        const src = Number(t.info)
        if (Number.isFinite(src) && src !== rendered) {
          findings.push({
            line: (t.map?.[0] ?? 0) + 1,
            message: `ordered-list source number ${src} renders as ordinal ${rendered}`,
          })
        }
      }
      if (t.type === 'inline') findings.push(...linkTextFindings(t))
      if (t.children) walk(t.children)
    }
  }
  walk(tokens)

  for (const t of tokens) {
    if (t.type !== 'table_open' || !t.map) continue
    const [a, b] = t.map
    const slice = lines.slice(a, b)
    const header = slice.find((l) => isPipeLine(l) && !isDelim(l))
    if (!header) continue
    const want = rowCells(header)
    for (let i = 0; i < slice.length; i++) {
      const l = slice[i]
      if (!isPipeLine(l) || isDelim(l)) continue
      const got = rowCells(l)
      if (got === want) continue
      findings.push({
        line: a + i + 1,
        message: `a rendered table row has a different cell count from its header (${got} cells, header ${want})`,
      })
    }
  }

  const sourceTables = sourceTableCount(text)
  if (sourceTables !== tables) {
    findings.push({
      line: 1,
      message: `rendered table count is ${tables}; the source has ${sourceTables} pipe-block(s) with a delimiter`,
    })
  }

  return { findings, tables, rows, lists, items }
}
