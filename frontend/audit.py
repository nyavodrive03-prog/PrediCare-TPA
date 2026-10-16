"""Journal d'audit et métriques d'exploitation (CDC : plateforme supervisable).

RGPD : le journal ne stocke JAMAIS le texte des questions (données de santé
potentielles), seulement l'événement, l'origine de la réponse et la durée.
"""
import auth

_pret = False


def creer_table():
    conn = auth.connexion()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS journal_audit (
                id SERIAL PRIMARY KEY,
                horodatage TIMESTAMPTZ NOT NULL DEFAULT now(),
                login TEXT,
                role TEXT,
                evenement TEXT NOT NULL,
                detail TEXT,
                duree_ms INT,
                statut TEXT NOT NULL DEFAULT 'ok'
            );
            CREATE INDEX IF NOT EXISTS idx_audit_horodatage
                ON journal_audit (horodatage);""")
    conn.commit()
    conn.close()


def journaliser(login, role, evenement, detail=None, duree_ms=None,
                statut="ok"):
    """Ajoute une ligne au journal. Ne doit jamais faire planter l'application."""
    global _pret
    try:
        if not _pret:
            creer_table()
            _pret = True
        conn = auth.connexion()
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO journal_audit
                   (login, role, evenement, detail, duree_ms, statut)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                ((login or "")[:50], role, evenement, detail, duree_ms,
                 statut))
        conn.commit()
        conn.close()
    except Exception:  # noqa: BLE001
        pass


def metriques(heures=24):
    """Indicateurs d'exploitation sur la période (volume, latence, erreurs)."""
    _, lignes = auth.requete(
        """SELECT
             COUNT(*) FILTER (WHERE evenement = 'question'),
             COUNT(*) FILTER (WHERE evenement = 'question'
                              AND statut = 'erreur'),
             COALESCE(AVG(duree_ms) FILTER (WHERE evenement = 'question'
                                            AND detail = 'llm'), 0),
             COALESCE(percentile_cont(0.95) WITHIN GROUP (ORDER BY duree_ms)
                      FILTER (WHERE evenement = 'question'), 0),
             COUNT(*) FILTER (WHERE evenement = 'question'
                              AND detail = 'cache'),
             COUNT(*) FILTER (WHERE evenement = 'question'
                              AND detail = 'refus'),
             COUNT(*) FILTER (WHERE evenement = 'connexion'
                              AND statut = 'echec')
           FROM journal_audit
           WHERE horodatage > now() - (%s || ' hours')::interval""",
        (str(heures),))
    q, err, lat_llm, p95, cache, refus, echecs = lignes[0]
    return {"questions": q, "erreurs": err, "latence_llm_ms": float(lat_llm),
            "p95_ms": float(p95), "cache": cache, "refus": refus,
            "connexions_echouees": echecs}
