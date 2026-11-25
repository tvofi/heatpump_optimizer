class Window {
  constructor() { this.rows = []; this.seen = new Set(); }
  absorb(r) {
    this.rows.push(r);
    this.seen.add(r.k);
    const floor = Date.now() - 48 * 3600e3;
    while (this.rows.length && this.rows[0].t < floor) this.rows.shift();
    this.seen.delete(r.old);
  }
}
