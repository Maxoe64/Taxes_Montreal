import { useState, useMemo, useCallback } from "react";

const ARRONDISSEMENTS = [
  { id: "ahuntsic_cartierville", label: "Ahuntsic-Cartierville", services: 0.0448, invest: 0.0303, fixe: 0 },
  { id: "anjou", label: "Anjou", services: 0.115, invest: 0.0649, fixe: 0 },
  { id: "cote_des_neiges_ndg", label: "Côte-des-Neiges–NDG", services: 0.0393, invest: 0.0214, fixe: 0 },
  { id: "ile_bizard", label: "L'Île-Bizard–Ste-Geneviève", services: 0.0822, invest: 0.087, fixe: 0 },
  { id: "lachine", label: "Lachine", services: 0.0434, invest: 0.0312, fixe: 57.91 },
  { id: "lasalle", label: "LaSalle", services: 0.0562, invest: 0.0319, fixe: 0 },
  { id: "plateau", label: "Le Plateau-Mont-Royal", services: 0.0513, invest: 0.0246, fixe: 0 },
  { id: "sud_ouest", label: "Le Sud-Ouest", services: 0.051, invest: 0.0263, fixe: 0 },
  { id: "mercier", label: "Mercier–Hochelaga-Maisonneuve", services: 0.0601, invest: 0.04, fixe: 0 },
  { id: "mtl_nord", label: "Montréal-Nord", services: 0.123, invest: 0.049, fixe: 0 },
  { id: "outremont", label: "Outremont", services: 0.0431, invest: 0.0298, fixe: 0 },
  { id: "pierrefonds", label: "Pierrefonds-Roxboro", services: 0.0706, invest: 0.0422, fixe: 0 },
  { id: "rdp_pat", label: "RDP–Pointe-aux-Trembles", services: 0.0714, invest: 0.0634, fixe: 0 },
  { id: "rosemont", label: "Rosemont–La Petite-Patrie", services: 0.0531, invest: 0.0308, fixe: 0 },
  { id: "saint_laurent", label: "Saint-Laurent", services: 0.0604, invest: 0.0334, fixe: 0 },
  { id: "saint_leonard", label: "Saint-Léonard", services: 0.0758, invest: 0.0449, fixe: 0 },
  { id: "verdun", label: "Verdun", services: 0.0627, invest: 0.0339, fixe: 0 },
  { id: "ville_marie", label: "Ville-Marie", services: 0.0391, invest: 0.0086, fixe: 0 },
  { id: "villeray", label: "Villeray–Saint-Michel–Parc-Extension", services: 0.0548, invest: 0.0297, fixe: 0 },
];

const CATEGORIES = [
  { id: "residentiel", label: "Résidentiel (≤ 5 logements)" },
  { id: "residentiel_6_plus", label: "Résidentiel (6+ logements)" },
  { id: "non_residentiel", label: "Non résidentiel / commercial" },
  { id: "terrain_vague", label: "Terrain vague desservi" },
];

const TAUX_CONSEIL = {
  fonciere: { res: 0.4631, nr1: 2.0084, nr2: 2.5719, tv: 1.8524 },
  artm: { res: 0.007, nr1: 0.0301, nr2: 0.0385, tv: 0.028 },
  voirie: { res: 0.0024, nr: 0.0168, tv: 0.0024 },
};

const SEUIL_NR = 900000;

function calcul(valPrec, valCour, anneeRole, categorie, arrId) {
  const arr = ARRONDISSEMENTS.find((a) => a.id === arrId);
  if (!arr) return null;

  const yr = Math.max(1, Math.min(3, anneeRole));
  const base = valPrec + (yr / 3) * (valCour - valPrec);

  const isRes = categorie === "residentiel" || categorie === "residentiel_6_plus";
  const isNR = categorie === "non_residentiel";
  const isTV = categorie === "terrain_vague";

  // Taxe foncière générale
  let tfg;
  if (isRes) {
    tfg = (base * TAUX_CONSEIL.fonciere.res) / 100;
  } else if (isNR) {
    const t1 = Math.min(base, SEUIL_NR);
    const t2 = Math.max(base - SEUIL_NR, 0);
    tfg = (t1 * TAUX_CONSEIL.fonciere.nr1) / 100 + (t2 * TAUX_CONSEIL.fonciere.nr2) / 100;
  } else {
    tfg = (base * TAUX_CONSEIL.fonciere.tv) / 100;
  }

  // Taxe ARTM
  let artm;
  if (isRes) artm = (base * TAUX_CONSEIL.artm.res) / 100;
  else if (isNR) {
    const t1 = Math.min(base, SEUIL_NR);
    const t2 = Math.max(base - SEUIL_NR, 0);
    artm = (t1 * TAUX_CONSEIL.artm.nr1) / 100 + (t2 * TAUX_CONSEIL.artm.nr2) / 100;
  } else artm = (base * TAUX_CONSEIL.artm.tv) / 100;

  // Taxe voirie
  let voirie;
  if (isRes) voirie = (base * TAUX_CONSEIL.voirie.res) / 100;
  else if (isNR) voirie = (base * TAUX_CONSEIL.voirie.nr) / 100;
  else voirie = (base * TAUX_CONSEIL.voirie.tv) / 100;

  // Taxes d'arrondissement
  const tauxArr = arr.services + arr.invest;
  const taxeArr = (base * tauxArr) / 100 + arr.fixe;

  const total = tfg + artm + voirie + taxeArr;

  return {
    base: Math.round(base * 100) / 100,
    tfg: Math.round(tfg * 100) / 100,
    artm: Math.round(artm * 100) / 100,
    voirie: Math.round(voirie * 100) / 100,
    arrServices: Math.round(((base * arr.services) / 100) * 100) / 100,
    arrInvest: Math.round(((base * arr.invest) / 100) * 100) / 100,
    arrFixe: arr.fixe,
    taxeArr: Math.round(taxeArr * 100) / 100,
    total: Math.round(total * 100) / 100,
    mensuel: Math.round((total / 12) * 100) / 100,
  };
}

function fmt(n) {
  return n.toLocaleString("fr-CA", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function Bar({ label, value, max, color }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13, marginBottom: 3, color: "#4a4a48" }}>
        <span>{label}</span>
        <span style={{ fontVariantNumeric: "tabular-nums", fontWeight: 500 }}>{fmt(value)} $</span>
      </div>
      <div style={{ background: "#e8e6df", borderRadius: 4, height: 8, overflow: "hidden" }}>
        <div
          style={{
            width: `${pct}%`,
            height: "100%",
            background: color,
            borderRadius: 4,
            transition: "width 0.5s cubic-bezier(.4,0,.2,1)",
          }}
        />
      </div>
    </div>
  );
}

export default function SimulateurTaxes() {
  const [valPrec, setValPrec] = useState(450000);
  const [valCour, setValCour] = useState(500000);
  const [annee, setAnnee] = useState(1);
  const [categorie, setCategorie] = useState("residentiel");
  const [arrId, setArrId] = useState("rosemont");

  const result = useMemo(
    () => calcul(valPrec, valCour, annee, categorie, arrId),
    [valPrec, valCour, annee, categorie, arrId]
  );

  const arrLabel = ARRONDISSEMENTS.find((a) => a.id === arrId)?.label || "";

  const handleNum = useCallback((setter) => (e) => {
    const v = e.target.value.replace(/[^0-9]/g, "");
    setter(v === "" ? 0 : parseInt(v, 10));
  }, []);

  return (
    <div style={{ fontFamily: "'DM Sans', 'Segoe UI', sans-serif", maxWidth: 720, margin: "0 auto", padding: "24px 16px" }}>
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 6 }}>
          <div style={{
            width: 36, height: 36, borderRadius: 8,
            background: "linear-gradient(135deg, #1a5276 0%, #2e86c1 100%)",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "#fff", fontWeight: 700, fontSize: 16, letterSpacing: -0.5,
          }}>
            OF
          </div>
          <div>
            <h1 style={{ margin: 0, fontSize: 20, fontWeight: 600, color: "#1a1a18", letterSpacing: -0.4 }}>
              Simulateur de taxes foncières
            </h1>
            <p style={{ margin: 0, fontSize: 12, color: "#7a7a76", letterSpacing: 0.5, textTransform: "uppercase" }}>
              Ville de Montréal · Budget 2026 · Propulsé par OpenFisca
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
        {/* Left: inputs */}
        <div>
          <fieldset style={{ border: "1px solid #d6d4cc", borderRadius: 10, padding: 16, margin: 0 }}>
            <legend style={{ fontSize: 13, fontWeight: 600, color: "#5a5a56", padding: "0 6px" }}>
              Votre immeuble
            </legend>

            <label style={lbl}>Catégorie</label>
            <select value={categorie} onChange={(e) => setCategorie(e.target.value)} style={sel}>
              {CATEGORIES.map((c) => (
                <option key={c.id} value={c.id}>{c.label}</option>
              ))}
            </select>

            <label style={lbl}>Arrondissement</label>
            <select value={arrId} onChange={(e) => setArrId(e.target.value)} style={sel}>
              {ARRONDISSEMENTS.map((a) => (
                <option key={a.id} value={a.id}>{a.label}</option>
              ))}
            </select>

            <label style={lbl}>Valeur au rôle précédent (2023-2025)</label>
            <div style={inputWrap}>
              <input type="text" value={valPrec.toLocaleString("fr-CA")} onChange={handleNum(setValPrec)} style={inp} />
              <span style={unit}>$</span>
            </div>

            <label style={lbl}>Valeur au rôle courant (2026-2028)</label>
            <div style={inputWrap}>
              <input type="text" value={valCour.toLocaleString("fr-CA")} onChange={handleNum(setValCour)} style={inp} />
              <span style={unit}>$</span>
            </div>

            <label style={lbl}>Année dans le rôle triennal</label>
            <div style={{ display: "flex", gap: 6 }}>
              {[1, 2, 3].map((y) => (
                <button
                  key={y}
                  onClick={() => setAnnee(y)}
                  style={{
                    flex: 1, padding: "8px 0", borderRadius: 6, fontSize: 14, fontWeight: 500,
                    cursor: "pointer", transition: "all 0.2s",
                    border: annee === y ? "2px solid #1a5276" : "1px solid #d6d4cc",
                    background: annee === y ? "#eaf2f8" : "#fff",
                    color: annee === y ? "#1a5276" : "#6a6a66",
                  }}
                >
                  {y === 1 ? "2026" : y === 2 ? "2027" : "2028"}
                </button>
              ))}
            </div>
          </fieldset>

          {/* Base d'imposition */}
          {result && (
            <div style={{
              marginTop: 14, padding: "12px 16px", borderRadius: 8,
              background: "#f4f2ec", border: "1px solid #e0ddd5",
            }}>
              <div style={{ fontSize: 12, color: "#7a7a76", textTransform: "uppercase", letterSpacing: 0.5 }}>
                Base d'imposition (après étalement)
              </div>
              <div style={{ fontSize: 22, fontWeight: 600, color: "#1a1a18", fontVariantNumeric: "tabular-nums" }}>
                {fmt(result.base)} $
              </div>
              <div style={{ fontSize: 11, color: "#9a9a96", marginTop: 2 }}>
                Variation lissée : {valPrec !== valCour ? `${fmt(valCour - valPrec)} $ sur 3 ans` : "aucune"}
              </div>
            </div>
          )}
        </div>

        {/* Right: results */}
        <div>
          {result && (
            <>
              {/* Total */}
              <div style={{
                padding: "20px 20px 16px", borderRadius: 10,
                background: "linear-gradient(135deg, #1a5276 0%, #2471a3 100%)",
                color: "#fff", marginBottom: 16,
              }}>
                <div style={{ fontSize: 12, opacity: 0.7, textTransform: "uppercase", letterSpacing: 0.8 }}>
                  Total annuel estimé
                </div>
                <div style={{ fontSize: 32, fontWeight: 700, letterSpacing: -1, fontVariantNumeric: "tabular-nums" }}>
                  {fmt(result.total)} $
                </div>
                <div style={{ fontSize: 14, opacity: 0.8, marginTop: 2 }}>
                  soit {fmt(result.mensuel)} $ / mois
                </div>
              </div>

              {/* Breakdown bars */}
              <div style={{
                padding: 16, borderRadius: 10,
                border: "1px solid #d6d4cc", background: "#faf9f6",
              }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#5a5a56", marginBottom: 14 }}>
                  Ventilation par composante
                </div>

                <Bar label="Taxe foncière générale" value={result.tfg} max={result.total} color="#2471a3" />
                <Bar label={`Arr. services (${arrLabel})`} value={result.arrServices} max={result.total} color="#1a8a5c" />
                <Bar label={`Arr. investissements`} value={result.arrInvest} max={result.total} color="#27ae60" />
                {result.arrFixe > 0 && (
                  <Bar label="Montant fixe (arrond.)" value={result.arrFixe} max={result.total} color="#52be80" />
                )}
                <Bar label="Taxe ARTM (transport)" value={result.artm} max={result.total} color="#c0852a" />
                <Bar label="Taxe voirie" value={result.voirie} max={result.total} color="#d4a84b" />
              </div>

              {/* OpenFisca API note */}
              <div style={{
                marginTop: 14, padding: "10px 14px", borderRadius: 8,
                background: "#eaf5f0", border: "1px solid #c8e6d7", fontSize: 12, color: "#1a6b42",
              }}>
                <strong>Rules as Code</strong> — Chaque règle de calcul est traçable à sa source
                réglementaire dans le code OpenFisca. Les taux proviennent du{" "}
                <a href="https://montreal.ca/articles/taux-de-taxes-pour-2026-106147"
                   target="_blank" rel="noopener noreferrer"
                   style={{ color: "#14854d" }}>
                  Budget 2026
                </a>.
              </div>
            </>
          )}
        </div>
      </div>

      {/* Footer: API endpoint preview */}
      <details style={{ marginTop: 24 }}>
        <summary style={{
          fontSize: 13, color: "#7a7a76", cursor: "pointer", userSelect: "none",
        }}>
          Requête API OpenFisca équivalente
        </summary>
        <pre style={{
          marginTop: 8, padding: 14, borderRadius: 8,
          background: "#1e1e1c", color: "#c8c6be", fontSize: 12,
          overflow: "auto", lineHeight: 1.5,
        }}>
{`POST /calculate
{
  "households": {
    "mon_immeuble": {
      "categorie_immeuble": {"2026": "${categorie}"},
      "arrondissement": {"2026": "${arrId}"},
      "valeur_fonciere_role_precedent": {"2026": ${valPrec}},
      "valeur_fonciere_role_courant": {"2026": ${valCour}},
      "annee_role": {"2026": ${annee}},
      "total_taxes_foncieres": {"2026": null}
    }
  },
  "persons": {"proprietaire": {}}
}`}
        </pre>
      </details>
    </div>
  );
}

const lbl = { display: "block", fontSize: 13, fontWeight: 500, color: "#5a5a56", marginTop: 12, marginBottom: 4 };
const sel = {
  width: "100%", padding: "8px 10px", borderRadius: 6, border: "1px solid #d6d4cc",
  fontSize: 14, color: "#1a1a18", background: "#fff", cursor: "pointer",
};
const inputWrap = { position: "relative" };
const inp = {
  width: "100%", padding: "8px 28px 8px 10px", borderRadius: 6,
  border: "1px solid #d6d4cc", fontSize: 14, color: "#1a1a18",
  fontVariantNumeric: "tabular-nums", boxSizing: "border-box",
};
const unit = {
  position: "absolute", right: 10, top: "50%", transform: "translateY(-50%)",
  fontSize: 14, color: "#9a9a96", pointerEvents: "none",
};
