"use strict";

// ── State ────────────────────────────────────────────────────────────────────
let ROOT_SCHEMA = null;   // for $ref resolution
let MODE = "config";       // "config" | "coordinates"
let CURRENT_SIZE = null;   // coordinate size when MODE === "coordinates"
let FORM_GET = null;       // () => assembled values object
let BOOLEANS_ONLY = false; // coordinates: only show boolean/enum leaves
let SELECTED_SPORTS = new Set(); // current sport_ids selection (drives team pickers)
let LAST_SCHEMA = null;    // last rendered schema (for reactive re-render)
let LAST_SOURCE = null;    // last rendered source label

// ── Helpers ──────────────────────────────────────────────────────────────────
function humanize(key) {
  return String(key).replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
}

// Field/section caption: prefer an explicit schema title, else humanize the key.
function caption(key, schema) {
  return (schema && schema.title) || humanize(key);
}

function resolveRef(ref) {
  // "#/$defs/team" -> ROOT_SCHEMA.$defs.team
  const parts = ref.replace(/^#\//, "").split("/");
  let node = ROOT_SCHEMA;
  for (const p of parts) node = node?.[p];
  return node || {};
}

function deref(schema) {
  if (!schema || typeof schema !== "object") return schema || {};
  if (schema.$ref) {
    const target = resolveRef(schema.$ref);
    // sibling keys (default, description) win over the referenced ones
    const { $ref, ...rest } = schema;
    return { ...target, ...rest };
  }
  return schema;
}

function el(tag, attrs = {}, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (k === "class") e.className = v;
    else if (k === "html") e.innerHTML = v;
    else if (v !== null && v !== undefined) e.setAttribute(k, v);
  }
  for (const c of children) if (c != null) e.append(c);
  return e;
}

function descEl(schema) {
  return schema.description ? el("div", { class: "desc" }, schema.description) : null;
}

// Determine if a (deref'd) schema is a "boolean-ish" leaf we show in booleansOnly mode.
function isSimpleToggle(schema) {
  return schema.type === "boolean" || Array.isArray(schema.enum);
}

// ── Node renderer: returns { el, get } ───────────────────────────────────────
function renderNode(rawSchema, value, key) {
  const schema = deref(rawSchema);

  // Hidden / const-enforced fields: keep an existing value or a const, render
  // nothing. If neither is present, emit nothing (e.g. the x-schema mirror of
  // $schema, which is carried through by renderObject's passthrough instead).
  if (schema["x-hidden"] || ("const" in schema)) {
    const fixed = value !== undefined ? value
      : ("const" in schema ? schema.const : undefined);
    return { el: null, get: () => fixed };
  }

  // Anything with declared properties is a structured object. Typeless nodes
  // whose value/default is a plain object (e.g. "matrix": { default: {} }) are
  // freeform — renderObject serialises them through a JSON textarea.
  const looksObject = !schema.type && !schema.enum && !schema.oneOf &&
    ((value && typeof value === "object" && !Array.isArray(value)) ||
     (schema.default && typeof schema.default === "object" && !Array.isArray(schema.default)));
  if (schema.properties || schema.type === "object" || looksObject) {
    return renderObject(schema, value, key);
  }

  if (schema.type === "array") return renderArray(schema, value, key);
  if (schema.type === "boolean") return renderBoolean(schema, value, key);
  if (Array.isArray(schema.enum)) return renderEnum(schema, value, key);
  if (schema.type === "number" || schema.type === "integer") return renderNumber(schema, value, key);
  if (schema.oneOf) return renderOneOf(schema, value, key);
  // strings & fallback
  return renderString(schema, value, key);
}

function fieldWrap(labelText, schema, control) {
  return el("div", { class: "field" },
    el("label", { class: "field-label" }, labelText),
    descEl(schema),
    control,
  );
}

// ── Object ───────────────────────────────────────────────────────────────────
function renderObject(schema, value, key) {
  value = value && typeof value === "object" ? value : {};

  // Freeform objects (matrix, plugins) have no declared properties — preserve
  // their content verbatim via a JSON textarea so we never clobber plugin config.
  if (!schema.properties) {
    const ta = el("textarea", { rows: 6, style: "width:100%;font-family:monospace" });
    ta.value = JSON.stringify(value, null, 2);
    const ctrl = fieldWrap(humanize(key || "value"), schema, ta);
    return {
      el: ctrl,
      get: () => { try { return JSON.parse(ta.value); } catch { return value; } },
    };
  }

  const getters = {};
  const body = el("div");
  let entries = Object.entries(schema.properties);
  // At the form root, surface the league selector first for a cohesive flow:
  // pick leagues, then everything below (incl. team pickers) reflects them.
  if (!key) {
    entries = entries.slice().sort(([a], [b]) =>
      (a === "sport_ids" ? -1 : 0) - (b === "sport_ids" ? -1 : 0));
  }
  for (const [propKey, propSchema] of entries) {
    const ds = deref(propSchema);
    if (BOOLEANS_ONLY && ds.type !== "object" && ds.type !== "array" && !isSimpleToggle(ds)) continue;
    const child = renderNode(propSchema, value[propKey], propKey);
    getters[propKey] = child.get;
    if (child.el) body.append(child.el);
  }

  const get = () => {
    // Carry through keys present in the input but not declared as properties
    // (e.g. "$schema", matched via patternProperties) so they survive a save.
    const out = {};
    for (const k of Object.keys(value)) {
      if (!schema.properties[k]) out[k] = value[k];
    }
    for (const [k, g] of Object.entries(getters)) {
      const v = g();
      if (v !== undefined) out[k] = v;
    }
    return out;
  };

  if (!key) return { el: body, get }; // root: no fieldset wrapper
  const fs = el("fieldset", {}, el("legend", {}, caption(key, schema)), descEl(schema), body);
  return { el: fs, get };
}

// ── Boolean ──────────────────────────────────────────────────────────────────
function renderBoolean(schema, value, key) {
  const cb = el("input", { type: "checkbox" });
  cb.checked = value !== undefined ? !!value : !!schema.default;
  const row = el("div", { class: "field" },
    el("div", { class: "checkrow" }, cb, el("label", {}, caption(key, schema))),
    descEl(schema),
  );
  return { el: row, get: () => cb.checked };
}

// ── Enum (single select) ─────────────────────────────────────────────────────
function renderEnum(schema, value, key) {
  const sel = el("select");
  const labels = schema["meta:enum"] || {};
  const cur = value !== undefined ? value : schema.default;
  // If the field is unset and has no default, offer a blank so we don't inject
  // an unintended value (a native <select> would otherwise pick the first option).
  if (cur === undefined) sel.append(el("option", { value: "" }, "(unset)"));
  for (const opt of schema.enum) {
    sel.append(el("option", { value: String(opt) }, labels[String(opt)] || String(opt)));
  }
  sel.value = cur !== undefined ? String(cur) : "";
  const coerce = v => (schema.type === "number" || schema.type === "integer") ? Number(v) : v;
  return {
    el: fieldWrap(caption(key, schema), schema, sel),
    get: () => sel.value === "" ? undefined : coerce(sel.value),
  };
}

// ── Number ───────────────────────────────────────────────────────────────────
function renderNumber(schema, value, key) {
  const cur = value !== undefined ? value : schema.default;

  // Slider when explicitly marked x-format:"range" (needs min + max).
  if (schema["x-format"] === "range" && schema.minimum !== undefined && schema.maximum !== undefined) {
    const inp = el("input", { type: "range" });
    inp.min = schema.minimum;
    inp.max = schema.maximum;
    inp.step = schema["x-step"] || (schema.type === "integer" ? 1 : 1);
    if (cur !== undefined) inp.value = cur;
    const readout = el("span", { class: "range-val" }, String(cur !== undefined ? cur : schema.minimum));
    inp.oninput = () => { readout.textContent = inp.value; };
    const wrap = el("div", { class: "range-wrap" }, inp, readout);
    return {
      el: fieldWrap(caption(key, schema), schema, wrap),
      get: () => inp.value === "" ? undefined : Number(inp.value),
    };
  }

  const inp = el("input", { type: "number" });
  if (schema.minimum !== undefined) inp.min = schema.minimum;
  if (schema.maximum !== undefined) inp.max = schema.maximum;
  inp.step = schema.type === "integer" ? "1" : "any";
  if (cur !== undefined) inp.value = cur;
  return {
    el: fieldWrap(caption(key, schema), schema, inp),
    get: () => inp.value === "" ? undefined : Number(inp.value),
  };
}

// ── String ───────────────────────────────────────────────────────────────────
function renderString(schema, value, key) {
  const inp = el("input", { type: "text" });
  const cur = value !== undefined ? value : schema.default;
  if (cur !== undefined) inp.value = cur;
  return { el: fieldWrap(caption(key, schema), schema, inp), get: () => inp.value };
}

// ── oneOf ────────────────────────────────────────────────────────────────────
function renderOneOf(schema, value, key) {
  const branches = (schema.oneOf || []).map(deref);

  // Toggle + date picker (e.g. demo_date: false | "YYYY-MM-DD").
  const falseBranch = branches.find(b => b.const === false || b.type === "boolean");
  const strBranch = branches.find(b => b.type === "string");
  if (falseBranch && strBranch) {
    // Only a non-empty string (the date) counts as enabled; false/0/"" are off.
    const enabled = typeof value === "string" && value.length > 0;
    const cb = el("input", { type: "checkbox" });
    cb.checked = enabled;
    const date = el("input", { type: "date", style: "margin-top:6px" });
    if (enabled) date.value = value;
    const sync = () => { date.disabled = !cb.checked; };
    cb.onchange = sync; sync();
    const wrap = el("div", {},
      el("div", { class: "checkrow" }, cb, el("label", {}, "Enabled")),
      date);
    return {
      el: fieldWrap(caption(key, schema), schema, wrap),
      get: () => cb.checked ? (date.value || false) : false,
    };
  }

  const arrayBranch = branches.find(b => b.type === "array");

  // Number-or-list (e.g. with_priority: [0,1,2] | 0). Comma-separated input.
  if (arrayBranch) {
    const items = deref(arrayBranch.items || {});
    const numeric = items.type === "number" || items.type === "integer";
    const inp = el("input", { type: "text", placeholder: "e.g. 0 or 0,1,2" });
    inp.value = Array.isArray(value) ? value.join(",") : (value !== undefined ? String(value) : "");
    return {
      el: fieldWrap(caption(key, schema), schema, inp),
      get: () => {
        const parts = inp.value.split(",").map(s => s.trim()).filter(Boolean)
          .map(s => numeric ? Number(s) : s);
        if (parts.length === 0) return undefined;
        return parts.length === 1 ? parts[0] : parts;
      },
    };
  }

  // Scalar oneOf (e.g. demo_date: false | "YYYY-MM-DD"). Empty/"false" -> false.
  const inp = el("input", { type: "text", placeholder: "false" });
  if (value !== undefined && value !== false) inp.value = value;
  return {
    el: fieldWrap(caption(key, schema), schema, inp),
    get: () => {
      const t = inp.value.trim();
      if (t === "" || t.toLowerCase() === "false") return false;
      if (/^-?\d+(\.\d+)?$/.test(t)) return Number(t);
      return t;
    },
  };
}

// ── Array ────────────────────────────────────────────────────────────────────
function renderArray(schema, value, key) {
  const items = deref(schema.items || {});

  // choices: array of enum values (teams, divisions, sport_ids, weekdays)
  if (Array.isArray(items.enum)) return renderChoices(schema, items, value, key);

  // array of objects: the rotation "screens" editor
  if (items.type === "object" || items.anyOf) return renderObjectArray(schema, items, value, key);

  // array of scalars (e.g. with_priority as a list): comma-separated text
  return renderScalarArray(schema, value, key);
}

// True when this choices array is a team picker (its options are the MLB team enum).
function isTeamPicker(itemsEnum) {
  const t = ROOT_SCHEMA && ROOT_SCHEMA.$defs && ROOT_SCHEMA.$defs.team && ROOT_SCHEMA.$defs.team.enum;
  return t && itemsEnum.length === t.length && itemsEnum.every((v, i) => v === t[i]);
}

function renderChoices(schema, items, value, key) {
  const selected = new Set((value || schema.default || []).map(String));
  const labels = items["meta:enum"] || {};
  const isNum = items.type === "number" || items.type === "integer";

  // Team pickers gain the International/WBC national teams when the
  // International league (sportId 51) is selected (or a WBC team is already set).
  let options = items.enum.slice();
  if (isTeamPicker(items.enum)) {
    const wbc = (ROOT_SCHEMA.$defs.wbc_team && ROOT_SCHEMA.$defs.wbc_team.enum) || [];
    const showWbc = SELECTED_SPORTS.has(51);
    for (const w of wbc) {
      if ((showWbc || selected.has(String(w))) && !options.includes(w)) options.push(w);
    }
  }

  const grid = el("div", { class: "choices" });
  const boxes = [];
  for (const opt of options) {
    const cb = el("input", { type: "checkbox", value: String(opt) });
    cb.checked = selected.has(String(opt));
    boxes.push([cb, opt]);
    grid.append(el("label", {}, cb, el("span", {}, labels[String(opt)] || String(opt))));
  }

  // The league selector drives the team pickers; re-render reactively on change.
  if (key === "sport_ids") {
    for (const [cb] of boxes) {
      cb.onchange = () => {
        SELECTED_SPORTS = new Set(
          boxes.filter(([c]) => c.checked).map(([, opt]) => Number(opt)));
        rerenderConfig();
      };
    }
  }

  return {
    el: fieldWrap(caption(key, schema), schema, grid),
    get: () => boxes.filter(([cb]) => cb.checked).map(([, opt]) => isNum ? Number(opt) : opt),
  };
}

function renderScalarArray(schema, value, key) {
  const inp = el("input", { type: "text", placeholder: "comma,separated" });
  inp.value = (value || schema.default || []).join(",");
  const numeric = deref(schema.items || {}).type === "number";
  return {
    el: fieldWrap(caption(key, schema), schema, inp),
    get: () => inp.value.split(",").map(s => s.trim()).filter(Boolean).map(s => numeric ? Number(s) : s),
  };
}

// rotation.screens — array of discriminated objects
function renderObjectArray(schema, items, value, key) {
  const variants = items.anyOf ? items.anyOf.map(deref) : [items];
  const discriminator = items["x-discriminator"] || "kind";
  const container = el("div", { class: "screens" });
  const list = el("div");
  const rowGetters = [];

  function variantFor(rowValue) {
    const kind = rowValue?.[discriminator];
    return variants.find(v => deref(v.properties?.[discriminator] || {}).const === kind)
      || variants.find(v => !("const" in deref(v.properties?.[discriminator] || {})))  // plugin (free kind)
      || variants[0];
  }

  function addRow(rowValue) {
    const variant = variantFor(rowValue);
    const inner = renderObject(variant, rowValue, ""); // no legend
    const title = variant.title || humanize(rowValue?.[discriminator] || "screen");
    const remove = el("button", { type: "button", class: "btn-remove" }, "Remove");
    const row = el("div", { class: "screen-row" },
      el("div", { class: "row-head" }, el("strong", {}, title), remove),
      inner.el,
    );
    const entry = { row, get: inner.get };
    rowGetters.push(entry);
    remove.onclick = () => {
      list.removeChild(row);
      const i = rowGetters.indexOf(entry);
      if (i >= 0) rowGetters.splice(i, 1);
    };
    list.append(row);
  }

  (value || schema.default || []).forEach(addRow);

  // "Add" control: a dropdown of variant titles + button
  const addSel = el("select", { style: "width:auto" });
  variants.forEach((v, i) => addSel.append(el("option", { value: String(i) }, v.title || `Option ${i + 1}`)));
  const addBtn = el("button", { type: "button", class: "btn-add" }, "+ Add");
  addBtn.onclick = () => {
    const v = variants[Number(addSel.value)];
    const seed = {};
    const dk = deref(v.properties?.[discriminator] || {});
    if ("const" in dk) seed[discriminator] = dk.const;
    else if (dk.default) seed[discriminator] = dk.default;
    addRow(seed);
  };

  container.append(list, el("div", { class: "row-head" }, addSel, addBtn));
  return {
    el: el("fieldset", {}, el("legend", {}, caption(key, schema)), descEl(schema), container),
    get: () => rowGetters.map(e => e.get()),
  };
}

// ── Page wiring ──────────────────────────────────────────────────────────────
async function loadConfig() {
  MODE = "config";
  const data = await (await fetch("/api/schema/config")).json();
  ROOT_SCHEMA = data.schema;
  BOOLEANS_ONLY = false;
  renderForm(data);
}

async function loadCoordinates(size) {
  MODE = "coordinates";
  CURRENT_SIZE = size;
  const data = await (await fetch(`/api/schema/coordinates/${size}`)).json();
  ROOT_SCHEMA = data.schema;
  BOOLEANS_ONLY = !!data.booleansOnly;
  renderForm(data);
}

function renderForm(data) {
  LAST_SCHEMA = data.schema;
  LAST_SOURCE = data.source;
  // Seed the league selection so team pickers render correctly on first paint.
  if (MODE === "config") {
    SELECTED_SPORTS = new Set((data.values && data.values.sport_ids) || [1]);
  }
  renderFormWith(data.values);
}

function renderFormWith(values) {
  const form = document.getElementById("form");
  form.innerHTML = "";
  document.getElementById("source").textContent =
    LAST_SOURCE ? `editing: ${LAST_SOURCE}` : "(new file)";
  const root = renderNode(LAST_SCHEMA, values, "");
  FORM_GET = root.get;
  if (root.el) form.append(root.el);
}

// Re-render the config form in place, preserving current edits and scroll.
// Used when toggling leagues so team pickers update reactively.
function rerenderConfig() {
  const values = FORM_GET ? FORM_GET() : {};
  const y = window.scrollY;
  renderFormWith(values);
  window.scrollTo(0, y);
}

function showStatus(msg, ok) {
  const s = document.getElementById("status");
  s.hidden = false;
  s.className = "status " + (ok ? "ok" : "err");
  s.textContent = msg;
}

async function save() {
  if (!FORM_GET) return;
  const values = FORM_GET();
  const url = MODE === "config" ? "/api/save/config" : `/api/save/coordinates/${CURRENT_SIZE}`;
  try {
    const res = await (await fetch(url, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(values),
    })).json();
    if (res.ok) {
      const c = res.changes || {};
      showStatus(`Saved ${res.written}${res.backup ? ` (backup: ${res.backup})` : ""}` +
        ` — +${c.added || 0} / −${c.deleted || 0} keys reconciled.`, true);
    } else {
      showStatus("Save failed: " + (res.error || "unknown error"), false);
    }
    return res.ok;
  } catch (e) {
    showStatus("Save failed: " + e.message, false);
    return false;
  }
}

async function setupService() {
  const svc = await (await fetch("/api/service")).json();
  const btn = document.getElementById("restart");
  const note = document.getElementById("restart-note");
  if (svc.detected) {
    btn.hidden = false;
    btn.onclick = async () => {
      if (!(await save())) return;
      const r = await (await fetch("/api/restart", { method: "POST" })).json();
      showStatus(r.ok ? `Saved and restarted ${r.restarted}.` : "Restart failed: " + r.error, r.ok);
    };
  } else {
    note.hidden = false;
    note.textContent = "No scoreboard service detected on this machine — save here, then restart your scoreboard manually to apply.";
  }
}

async function setupCoordPicker() {
  const { sizes } = await (await fetch("/api/coordinates")).json();
  const sel = document.getElementById("coord-size");
  sel.innerHTML = "";
  sizes.forEach(s => sel.append(el("option", { value: s }, s)));
  sel.onchange = () => loadCoordinates(sel.value);
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      const isCoord = tab.dataset.tab === "coordinates";
      document.getElementById("coord-picker").hidden = !isCoord;
      if (isCoord) {
        const sel = document.getElementById("coord-size");
        if (sel.value) loadCoordinates(sel.value);
      } else {
        loadConfig();
      }
    };
  });
}

document.getElementById("save").onclick = save;
document.getElementById("reload").onclick = () =>
  MODE === "config" ? loadConfig() : loadCoordinates(CURRENT_SIZE);

setupTabs();
setupCoordPicker();
setupService();
loadConfig();
