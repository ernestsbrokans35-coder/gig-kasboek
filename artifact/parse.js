/* Invoice reading: Gmail raw message -> PDF bytes -> text -> numbers. Pure functions, no page state. */
const Inv = (() => {
  const num = s => parseFloat(String(s).replace(/\./g, '').replace(',', '.'));
  const r2 = n => Math.round(n * 100) / 100;
  function b64ToBytes(b64) {
    const bin = atob(b64.replace(/-/g, '+').replace(/_/g, '/').replace(/[^A-Za-z0-9+/=]/g, ''));
    const out = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
    return out;
  }
  function pdfFromRaw(raw) {
    const bytes = b64ToBytes(raw);
    let s = '';
    for (let i = 0; i < bytes.length; i += 8192) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 8192));
    const m = /Content-(?:Type:\s*application\/pdf|Disposition:[^\r\n]*\.pdf)[\s\S]*?\r?\n\r?\n([A-Za-z0-9+\/=\r\n]+)/i.exec(s);
    if (!m) return null;
    const pdf = b64ToBytes(m[1]);
    return pdf.length > 4 && pdf[0] === 0x25 && pdf[1] === 0x50 ? pdf : null;
  }
  async function pdfText(bytes, pdfjsLib) {
    const doc = await pdfjsLib.getDocument({ data: bytes.slice() }).promise;
    const out = [];
    for (let p = 1; p <= doc.numPages; p++) {
      const tc = await (await doc.getPage(p)).getTextContent();
      out.push(tc.items.map(i => i.str).join('\n'));
    }
    return out.join('\n');
  }
  function parse(text) {
    const flat = text.replace(/\s+/g, ' ').trim();
    const number = (/Factuurnummer:\s*([\d-]+)/.exec(flat) || [])[1] || null;
    const d = /Uitgiftedatum:\s*(\d{2})-(\d{2})-(\d{4})/.exec(flat);
    const issued = d ? `${d[3]}-${d[2]}-${d[1]}` : null;
    const a = flat.indexOf('Bedrag ');
    const b = flat.indexOf('IBAN nummer');
    let sec = a >= 0 && b > a ? flat.slice(a + 7, b) : '';
    sec = sec.replace(/Beschrijving Aantal Eenheidsprijs Belasting Bedrag/g, ' ').replace(/Pagina \d+ van \d+/g, ' ').replace(/\s+/g, ' ').trim();
    const lines = [];
    const re = /(.*?) (\d+(?:[.,]\d+)?) € ([\d.,]+) (?:(\d+) ?% )?€ ([\d.,]+)(?= |$)/g;
    let m, venue = '';
    while ((m = re.exec(sec))) {
      const desc = m[1].trim();
      const base = { qty: num(m[2]), rate: num(m[3]), vatRate: m[4] ? Number(m[4]) : 0, amount: num(m[5]) };
      const s = /^(.*?)\s*(\d{2})-(\d{2})-(\d{4}), (\d{2}:\d{2})u - (\d{2}:\d{2})u,?\s*(.*?)\s*(?:\d+ ?%)?$/.exec(desc);
      if (s) {
        if (s[1].trim()) venue = s[1].trim();
        lines.push({ kind: 'shift', venue, date: `${s[4]}-${s[3]}-${s[2]}`, start: s[5], end: s[6], what: s[7].trim(), ...base });
      } else {
        lines.push({ kind: 'extra', venue, what: desc, ...base });
      }
    }
    const hours = r2(lines.filter(l => l.kind === 'shift').reduce((t, l) => t + l.qty, 0));
    const subtotal = r2(lines.reduce((t, l) => t + l.amount, 0));
    const tm = /openstaande bedrag van € ([\d.,]+)/.exec(flat);
    const total = tm ? num(tm[1]) : subtotal;
    const vat = r2(total - subtotal);
    const expectVat = r2(lines.reduce((t, l) => t + l.amount * l.vatRate / 100, 0));
    let check = !number || !issued || !lines.length || !tm || vat < -0.005 || Math.abs(vat - expectVat) > 0.05;
    const blk = /Te betalen bedrag: ([\d.,]+) € ([\d.,]+)/.exec(flat);
    if (blk && (Math.abs(num(blk[1]) - hours) > 0.02 || Math.abs(num(blk[2]) - subtotal) > 0.02)) check = true;
    return { number, issued, hours, subtotal, vat, total, lines, check };
  }
  return { pdfFromRaw, pdfText, parse, r2 };
})();
