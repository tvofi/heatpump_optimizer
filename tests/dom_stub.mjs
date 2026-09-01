// The shared DOM stub for the Node-based card harnesses (issue #101).
//
// tests/card.mjs grew this stub one shim at a time, and
// tests/setup_qa_render.mjs carried a verbatim copy of an EARLIER
// revision -- a dormant file whose whole value is being right when
// someone reaches for it, drifting with every extension. One module
// now owns the stub; both harnesses build it against their own
// `document` (the stub's focus/blur track the active element on the
// host's document, not a module-global).
//
// `getBoundingClientRect` is the constant the real-browser lane exists
// to escape: 900x400 for every element. Geometry assertions live in
// tests/card_browser.mjs; this stub is for structure, wiring and
// behaviour that a real browser cannot check cheaply.
// `makeDomStub(domRef)` takes a holder object the host fills with its
// own `document` once that exists: the classes are needed to BUILD the
// document (its head and body are Nodes), and focus/blur need the
// document afterwards -- a ref breaks the circle.
export function makeDomStub(domRef) {
  const VOID_TAGS = new Set(["br","hr","img","input","meta","link","source","path","rect","line","circle","use"]);

  function parseHtml(html, mk) {
    const root = [];
    const stack = [];
    const push = (node) => {
      if (stack.length) stack[stack.length - 1].appendChild(node);
      else root.push(node);
    };
    const re = /<\/?([a-zA-Z][\w-]*)((?:\s+[^>]*?)?)(\/?)>|([^<]+)/g;
    let m;
    while ((m = re.exec(html)) !== null) {
      const [, tag, attrsRaw, selfClose, text] = m;
      if (text !== undefined) {
        const trimmed = text.replace(/\s+/g, " ");
        if (trimmed.trim() && stack.length) {
          stack[stack.length - 1]._text += trimmed;
        }
        continue;
      }
      if (m[0][1] === "/") {
        // Closing tag. Tolerate mismatches rather than throwing: the point is to
        // find elements, not to validate markup.
        for (let i = stack.length - 1; i >= 0; i--) {
          if (stack[i].tagName === tag.toUpperCase()) { stack.length = i; break; }
        }
        continue;
      }
      const node = mk(tag);
      for (const a of attrsRaw.matchAll(/([\w:-]+)\s*=\s*"([^"]*)"/g)) {
        const [, name, value] = a;
        if (name === "class") value.split(/\s+/).filter(Boolean).forEach((c) => node.classList.add(c));
        else if (name.startsWith("data-")) node.dataset[name.slice(5).replace(/-(\w)/g, (x, c) => c.toUpperCase())] = value;
        node.setAttribute(name, value);
      }
      // A bare `selected` on an <option> is what a browser reports as the
      // enclosing <select>'s value; the card's day selector and the entity
      // picker both read it back through `.value`.
      if (tag.toLowerCase() === "option" && /(^|\s)selected(\s|$)/.test(attrsRaw)
          && stack.length && stack[stack.length - 1].tagName === "SELECT") {
        stack[stack.length - 1].value = node.value === undefined ? "" : node.value;
      }
      push(node);
      if (!selfClose && !VOID_TAGS.has(tag.toLowerCase())) stack.push(node);
    }
    return root;
  }

  class Node {
    constructor(tag){ this.tagName=(tag||"").toUpperCase(); this.children=[]; this.style={};
      this._html=""; this._text=""; this._listeners={}; this.dataset={}; this.classList={
        _s:new Set(), add(...c){c.forEach(x=>this._s.add(x));},
        remove(...c){c.forEach(x=>this._s.delete(x));},
        toggle(c,f){ f===undefined? (this._s.has(c)?this._s.delete(c):this._s.add(c)) : (f?this._s.add(c):this._s.delete(c)); },
        contains(c){return this._s.has(c);} };
    }
    set innerHTML(v){
      this._html=String(v);
      this.children = [];
      for (const child of parseHtml(this._html, (t) => new Node(t))) this.appendChild(child);
    }
    get innerHTML(){ return this._html; }
    set textContent(v){ this._text = String(v); }
    get textContent(){
      return this._text + this.children.map((c) => c.textContent).join("");
    }
    set className(v){
      this.classList._s = new Set(String(v).split(/\s+/).filter(Boolean));
    }
    get className(){ return [...this.classList._s].join(" "); }
    appendChild(c){ this.children.push(c); c.parentNode = this; return c; }
    removeChild(c){
      this.children=this.children.filter(x=>x!==c);
      if (c) c.parentNode = null;
    }
    setAttribute(k,v){ this[k]=v; }
    getAttribute(k){ return this[k]; }
    addEventListener(t,f){ (this._listeners[t] ||= []).push(f); }
    removeEventListener(){}
    // No bubbling: the card and its editor only ever listen on the element the
    // event is dispatched on, so a local delivery is faithful enough.
    dispatchEvent(ev){ ev.target = ev.target || this;
      (this._listeners[ev.type]||[]).slice().forEach((f)=>f(ev)); return true; }
    querySelector(sel){ return this._find(sel); }
    querySelectorAll(sel){ const out=[]; this._findAll(sel,out); return out; }
    _find(sel){ const a=[]; this._findAll(sel,a); return a[0]||null; }
    _findAll(sel,out){
      // Descendant selectors: the card scopes its chart lookups with
      // ".chartwrap svg", because the header's expand icon is an <svg> too.
      const sp = sel.indexOf(" ");
      if (sp > 0) {
        const head = sel.slice(0, sp).trim();
        const rest = sel.slice(sp + 1).trim();
        const hosts = [];
        this._findAll(head, hosts);
        for (const h of hosts) h._findAll(rest, out);
        return;
      }
      for(const c of this.children){
        if (matches(c, sel)) out.push(c);
        c._findAll(sel,out);
      }
    }
    attachShadow(){ this.shadowRoot=new Node("shadow-root"); return this.shadowRoot; }
    getBoundingClientRect(){ return {width:900,height:400,left:0,top:0}; }
    // Focus is tracked, not simulated: the card restores focus after
    // render-destroying keyboard actions, and the assertion is simply "who
    // received the last .focus() call".
    focus(){ domRef.document.activeElement = this; }
    // ...and gives it up again. The card takes focus off a setup row that a
    // pointer gesture left holding it (item F), which is only observable if
    // the stub models letting go as well as taking hold.
    blur(){ const d = domRef.document;
      if (d.activeElement === this) d.activeElement = d.body; }
  }

  // Selector support: a tag name, a class, an attribute, or a tag+attribute
  // pair, which covers everything the card actually queries for.
  function matches(node, sel) {
    const attr = sel.match(/^([\w-]*)\[([\w-]+)(?:="([^"]*)")?\]$/);
    if (attr) {
      const [, tag, name, value] = attr;
      if (tag && node.tagName !== tag.toUpperCase()) return false;
      const actual = node.getAttribute(name);
      if (actual === undefined || actual === null) return false;
      return value === undefined || String(actual) === value;
    }
    if (sel.startsWith(".")) return node.classList.contains(sel.slice(1));
    return node.tagName === sel.toUpperCase();
  }

  class HTMLElement extends Node { constructor(){ super("div"); } }

  return { VOID_TAGS, parseHtml, Node, matches, HTMLElement };
}
