"""Build portfolio-ready outputs for the retail BI case study."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "retail_bi.duckdb"
OUTPUTS = ROOT / "outputs"
DASHBOARD = ROOT / "dashboard"
SQL_SCHEMA = ROOT / "sql" / "01_create_schema_duckdb.sql"


def run_generator() -> None:
    subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_retail_data.py")], check=True)


def run_schema(connection: duckdb.DuckDBPyConnection) -> None:
    sql = SQL_SCHEMA.read_text(encoding="utf-8")
    for statement in [part.strip() for part in sql.split(";") if part.strip()]:
        connection.execute(statement)


def export_csv(connection: duckdb.DuckDBPyConnection, query: str, filename: str):
    df = connection.execute(query).fetchdf()
    df.to_csv(OUTPUTS / filename, index=False)
    return df


def money(value: float) -> str:
    if value is None:
        return "n/a"
    try:
        if math.isnan(float(value)):
            return "n/a"
    except (TypeError, ValueError):
        return "n/a"
    return f"R$ {value:,.0f}".replace(",", ".")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%".replace(".", ",")


def write_dashboard_variants(html: str) -> None:
    replacements = [
        ('<html lang="pt-BR">', '<html lang="en">'),
        ("Dashboard Executivo de Vendas e Margem", "Retail BI Sales Dashboard"),
        (
            "Visão executiva de vendas, margem e metas para uma operação de varejo multicanal.",
            "Executive sales, margin and target view for a multichannel retail operation.",
        ),
        ("Sem falhas críticas; ", "No critical failures; "),
        ("warnings monitorados fora da receita executiva.", "warnings monitored outside executive revenue."),
        ("falhas críticas encontradas antes da publicação de BI.", "critical failures found before BI publication."),
        ("Receita líquida", "Net revenue"),
        ("apenas pedidos entregues", "delivered orders only"),
        ("Margem bruta", "Gross margin"),
        (" de margem", " margin"),
        ("Pedidos entregues", "Delivered orders"),
        ("base comercial válida", "valid commercial base"),
        ("Ticket médio", "Average ticket"),
        ("receita líquida / pedidos", "net revenue / orders"),
        ("Unidades vendidas", "Units sold"),
        ("itens entregues", "delivered items"),
        ("Receita por canal", "Revenue by channel"),
        ("Acompanhamento de metas", "Target tracking"),
        ("Mês", "Month"),
        ("Atingimento de receita", "Revenue attainment"),
        ("Margem", "Margin"),
        ("Desempenho mensal", "Monthly performance"),
        ("Pedidos", "Orders"),
        ("Desempenho por categoria", "Category performance"),
        ("Categoria", "Category"),
        ("Unidades", "Units"),
        ("Casa", "Home"),
        ("Eletronicos", "Electronics"),
        ("Esporte", "Sports"),
        ("Moda", "Fashion"),
        ("Beleza", "Beauty"),
        ("Gate de qualidade dos dados", "Data quality gate"),
        ("Regra", "Rule"),
        ("Severidade", "Severity"),
        ("Registros com falha", "Failed records"),
        (
            "Falhas críticas bloqueiam a publicação. A receita de pedidos cancelados é monitorada como warning porque esses pedidos ficam fora da receita executiva.",
            "Critical failures block publication. Cancelled order revenue is monitored as a warning because these orders are excluded from executive revenue.",
        ),
    ]
    en_html = html
    for source, target in replacements:
        en_html = en_html.replace(source, target)

    (DASHBOARD / "retail_bi_sales_dashboard_pt-BR.html").write_text(html, encoding="utf-8")
    (DASHBOARD / "retail_bi_sales_dashboard_en.html").write_text(en_html, encoding="utf-8")
    (DASHBOARD / "retail_bi_sales_dashboard.html").write_text(en_html, encoding="utf-8")


def build_dashboard(data: dict) -> str:
    monthly_rows = "\n".join(
        f"""
        <tr>
          <td>{row['order_month']}</td>
          <td>{money(row['net_revenue'])}</td>
          <td>{pct(row['gross_margin_pct'])}</td>
          <td>{row['delivered_orders']}</td>
        </tr>
        """
        for row in data["monthly_performance"]
    )
    category_rows = "\n".join(
        f"""
        <tr>
          <td>{row['category']}</td>
          <td>{money(row['net_revenue'])}</td>
          <td>{pct(row['gross_margin_pct'])}</td>
          <td>{int(row['units_sold'])}</td>
        </tr>
        """
        for row in data["category_performance"]
    )
    channel_bars = "\n".join(
        f"""
        <div class="bar-row">
          <div class="bar-label">{row['sales_channel']}</div>
          <div class="bar-track"><span style="width:{row['revenue_share'] * 100:.1f}%"></span></div>
          <div class="bar-value">{money(row['net_revenue'])}</div>
        </div>
        """
        for row in data["channel_performance"]
    )
    target_rows = "\n".join(
        f"""
        <tr>
          <td>{row['target_month']}</td>
          <td>{row['sales_channel']}</td>
          <td>{pct(row['revenue_target_attainment'])}</td>
          <td>{pct(row['realized_margin_pct'])}</td>
        </tr>
        """
        for row in data["target_tracking"][:8]
    )
    dq_rows = "\n".join(
        f"""
        <tr>
          <td>{row['rule_name']}</td>
          <td><span class="badge {row['severity'].lower()}">{row['severity']}</span></td>
          <td>{row['failed_records']}</td>
        </tr>
        """
        for row in data["dq_summary"]
    )
    status_class = "approved" if data["publication_status"] == "Approved" else "blocked"

    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard Executivo de Vendas e Margem</title>
  <style>
    :root {{
      --ink: #111827;
      --muted: #5f6b7a;
      --line: #d8dee8;
      --paper: #f6f7f9;
      --panel: #ffffff;
      --green: #027a48;
      --red: #b42318;
      --blue: #175cd3;
      --amber: #b54708;
      --teal: #0f766e;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: Inter, Segoe UI, Arial, sans-serif;
    }}
    main {{
      width: min(1180px, calc(100vw - 32px));
      margin: 0 auto;
      padding: 28px 0 40px;
    }}
    header {{
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 20px;
      align-items: end;
      padding-bottom: 18px;
      margin-bottom: 18px;
      border-bottom: 1px solid var(--line);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: clamp(1.7rem, 3vw, 2.75rem);
      line-height: 1.04;
      letter-spacing: 0;
    }}
    p {{ margin: 0; color: var(--muted); line-height: 1.5; }}
    .status, .tile, section {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .status {{ min-width: 245px; padding: 16px; }}
    .status span {{
      display: inline-flex;
      padding: 6px 10px;
      border-radius: 999px;
      color: #fff;
      font-weight: 850;
      margin-bottom: 10px;
    }}
    .approved {{ background: var(--green); }}
    .blocked {{ background: var(--red); }}
    .kpis {{
      display: grid;
      grid-template-columns: repeat(5, minmax(0, 1fr));
      gap: 12px;
      margin-bottom: 16px;
    }}
    .tile {{ padding: 15px; min-height: 112px; }}
    .label {{ color: var(--muted); font-size: .8rem; font-weight: 800; }}
    .value {{ font-size: 1.72rem; line-height: 1.12; font-weight: 900; margin: 10px 0 6px; white-space: nowrap; }}
    .note {{ color: var(--muted); font-size: .84rem; }}
    .grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 14px;
      margin-bottom: 14px;
    }}
    section {{ padding: 16px; overflow: hidden; }}
    h2 {{ margin: 0 0 12px; font-size: 1rem; letter-spacing: 0; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .88rem; }}
    th, td {{ padding: 10px 8px; border-bottom: 1px solid #edf0f3; text-align: left; vertical-align: top; }}
    th {{ color: var(--muted); font-size: .76rem; text-transform: uppercase; }}
    .bar-row {{ display: grid; grid-template-columns: 112px 1fr 108px; gap: 10px; align-items: center; margin: 14px 0; }}
    .bar-label, .bar-value {{ color: var(--muted); font-size: .86rem; }}
    .bar-value {{ text-align: right; }}
    .bar-track {{ height: 14px; background: #e7ebf0; border-radius: 999px; overflow: hidden; }}
    .bar-track span {{ display: block; height: 100%; background: var(--blue); }}
    .badge {{ display: inline-flex; border-radius: 999px; padding: 4px 8px; font-weight: 850; font-size: .72rem; }}
    .critical {{ color: var(--red); background: #fef3f2; }}
    .warning {{ color: var(--amber); background: #fffaeb; }}
    .footnote {{ margin-top: 12px; color: var(--muted); font-size: .78rem; }}
    @media (max-width: 900px) {{
      header, .grid {{ grid-template-columns: 1fr; }}
      .kpis {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media (max-width: 560px) {{
      main {{ width: min(100vw - 20px, 1180px); padding-top: 16px; }}
      .kpis {{ grid-template-columns: 1fr; }}
      section {{ overflow-x: auto; }}
      table {{ min-width: 680px; }}
      .bar-row {{ grid-template-columns: 94px 1fr; }}
      .bar-value {{ grid-column: 2; text-align: left; }}
    }}
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>Retail BI Sales Dashboard</h1>
      <p>Visão executiva de vendas, margem e metas para uma operação de varejo multicanal.</p>
    </div>
    <div class="status">
      <span class="{status_class}">{data['publication_status']}</span>
      <p>{data['publication_reason']}</p>
    </div>
  </header>

  <div class="kpis">
    <div class="tile"><div class="label">Receita líquida</div><div class="value">{money(data['kpis']['net_revenue'])}</div><div class="note">apenas pedidos entregues</div></div>
    <div class="tile"><div class="label">Margem bruta</div><div class="value">{money(data['kpis']['gross_margin'])}</div><div class="note">{pct(data['kpis']['gross_margin_pct'])} de margem</div></div>
    <div class="tile"><div class="label">Pedidos entregues</div><div class="value">{int(data['kpis']['delivered_orders'])}</div><div class="note">base comercial válida</div></div>
    <div class="tile"><div class="label">Ticket médio</div><div class="value">{money(data['kpis']['average_ticket'])}</div><div class="note">receita líquida / pedidos</div></div>
    <div class="tile"><div class="label">Unidades vendidas</div><div class="value">{int(data['kpis']['units_sold'])}</div><div class="note">itens entregues</div></div>
  </div>

  <div class="grid">
    <section>
      <h2>Receita por canal</h2>
      {channel_bars}
    </section>
    <section>
      <h2>Acompanhamento de metas</h2>
      <table>
        <thead><tr><th>Mês</th><th>Canal</th><th>Atingimento de receita</th><th>Margem</th></tr></thead>
        <tbody>{target_rows}</tbody>
      </table>
    </section>
  </div>

  <div class="grid">
    <section>
      <h2>Desempenho mensal</h2>
      <table>
        <thead><tr><th>Mês</th><th>Receita líquida</th><th>Margem</th><th>Pedidos</th></tr></thead>
        <tbody>{monthly_rows}</tbody>
      </table>
    </section>
    <section>
      <h2>Desempenho por categoria</h2>
      <table>
        <thead><tr><th>Categoria</th><th>Receita líquida</th><th>Margem</th><th>Unidades</th></tr></thead>
        <tbody>{category_rows}</tbody>
      </table>
    </section>
  </div>

  <section>
    <h2>Gate de qualidade dos dados</h2>
    <table>
      <thead><tr><th>Regra</th><th>Severidade</th><th>Registros com falha</th></tr></thead>
      <tbody>{dq_rows}</tbody>
    </table>
    <p class="footnote">Falhas críticas bloqueiam a publicação. A receita de pedidos cancelados é monitorada como warning porque esses pedidos ficam fora da receita executiva.</p>
  </section>
</main>
</body>
</html>
"""


def main() -> None:
    run_generator()
    OUTPUTS.mkdir(exist_ok=True)
    DASHBOARD.mkdir(exist_ok=True)

    if DB_PATH.exists():
        DB_PATH.unlink()

    con = duckdb.connect(str(DB_PATH))
    try:
        run_schema(con)

        dq_summary = export_csv(
            con,
            """
            WITH rule_results AS (
              SELECT 'orders_without_items' AS rule_name, 'Critical' AS severity, COUNT(*) AS failed_records
              FROM dim_orders AS orders
              LEFT JOIN fact_sales AS sales ON orders.order_id = sales.order_id
              WHERE sales.order_item_id IS NULL
              UNION ALL
              SELECT 'items_without_valid_product', 'Critical', COUNT(*)
              FROM fact_sales AS sales
              LEFT JOIN dim_products AS products ON sales.product_id = products.product_id
              WHERE products.product_id IS NULL
              UNION ALL
              SELECT 'orders_without_valid_customer', 'Critical', COUNT(*)
              FROM dim_orders AS orders
              LEFT JOIN dim_customers AS customers ON orders.customer_id = customers.customer_id
              WHERE customers.customer_id IS NULL
              UNION ALL
              SELECT 'discount_outside_range', 'Critical', COUNT(*)
              FROM fact_sales
              WHERE discount_pct < 0 OR discount_pct > 1
              UNION ALL
              SELECT 'non_positive_price_or_cost', 'Critical', COUNT(*)
              FROM fact_sales
              WHERE unit_price <= 0 OR unit_cost <= 0
              UNION ALL
              SELECT 'cancelled_orders_with_potential_revenue', 'Warning', COUNT(DISTINCT order_id)
              FROM fact_sales
              WHERE order_status = 'Cancelled'
            )
            SELECT *
            FROM rule_results
            ORDER BY CASE severity WHEN 'Critical' THEN 1 ELSE 2 END, failed_records DESC, rule_name
            """,
            "dq_summary.csv",
        )
        kpi_summary = export_csv(
            con,
            """
            SELECT
                ROUND(SUM(net_revenue), 2) AS net_revenue,
                ROUND(SUM(gross_margin), 2) AS gross_margin,
                ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
                COUNT(DISTINCT order_id) AS delivered_orders,
                ROUND(SUM(net_revenue) / NULLIF(COUNT(DISTINCT order_id), 0), 2) AS average_ticket,
                SUM(quantity) AS units_sold
            FROM vw_sales_enriched
            WHERE order_status = 'Delivered'
            """,
            "kpi_summary.csv",
        )
        monthly = export_csv(
            con,
            """
            SELECT order_month,
                   ROUND(SUM(net_revenue), 2) AS net_revenue,
                   ROUND(SUM(gross_margin), 2) AS gross_margin,
                   ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
                   COUNT(DISTINCT order_id) AS delivered_orders
            FROM vw_sales_enriched
            WHERE order_status = 'Delivered'
            GROUP BY order_month
            ORDER BY order_month
            """,
            "monthly_performance.csv",
        )
        channel = export_csv(
            con,
            """
            WITH channel_metrics AS (
              SELECT sales_channel,
                     ROUND(SUM(net_revenue), 2) AS net_revenue,
                     ROUND(SUM(gross_margin), 2) AS gross_margin,
                     ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
                     COUNT(DISTINCT order_id) AS delivered_orders
              FROM vw_sales_enriched
              WHERE order_status = 'Delivered'
              GROUP BY sales_channel
            )
            SELECT *,
                   ROUND(net_revenue / SUM(net_revenue) OVER (), 4) AS revenue_share
            FROM channel_metrics
            ORDER BY net_revenue DESC
            """,
            "channel_performance.csv",
        )
        category = export_csv(
            con,
            """
            SELECT category,
                   ROUND(SUM(net_revenue), 2) AS net_revenue,
                   ROUND(SUM(gross_margin), 2) AS gross_margin,
                   ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct,
                   SUM(quantity) AS units_sold
            FROM vw_sales_enriched
            WHERE order_status = 'Delivered'
            GROUP BY category
            ORDER BY net_revenue DESC
            """,
            "category_performance.csv",
        )
        target_tracking = export_csv(
            con,
            """
            WITH realized AS (
              SELECT order_month AS target_month,
                     sales_channel,
                     ROUND(SUM(net_revenue), 2) AS realized_revenue,
                     ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS realized_margin_pct
              FROM vw_sales_enriched
              WHERE order_status = 'Delivered'
              GROUP BY order_month, sales_channel
            )
            SELECT targets.target_month,
                   targets.sales_channel,
                   targets.revenue_target,
                   COALESCE(realized.realized_revenue, 0) AS realized_revenue,
                   ROUND(COALESCE(realized.realized_revenue, 0) / NULLIF(targets.revenue_target, 0), 4) AS revenue_target_attainment,
                   targets.margin_target_pct,
                   realized.realized_margin_pct
            FROM fact_targets AS targets
            LEFT JOIN realized
              ON targets.target_month = realized.target_month
             AND targets.sales_channel = realized.sales_channel
            ORDER BY targets.target_month, targets.sales_channel
            """,
            "target_tracking.csv",
        )
        product_ranking = export_csv(
            con,
            """
            SELECT product_name,
                   category,
                   SUM(quantity) AS units_sold,
                   ROUND(SUM(net_revenue), 2) AS net_revenue,
                   ROUND(SUM(gross_margin), 2) AS gross_margin,
                   ROUND(SUM(gross_margin) / NULLIF(SUM(net_revenue), 0), 4) AS gross_margin_pct
            FROM vw_sales_enriched
            WHERE order_status = 'Delivered'
            GROUP BY product_name, category
            ORDER BY net_revenue DESC
            """,
            "product_ranking.csv",
        )

        kpis = kpi_summary.iloc[0].to_dict()
        critical_failures = int(dq_summary.loc[dq_summary["severity"] == "Critical", "failed_records"].sum())
        warning_failures = int(dq_summary.loc[dq_summary["severity"] == "Warning", "failed_records"].sum())
        publication_status = "Approved" if critical_failures == 0 else "Blocked"
        publication_reason = (
            f"{critical_failures} falhas críticas encontradas antes da publicação de BI."
            if critical_failures
            else f"Sem falhas críticas; {warning_failures} warnings monitorados fora da receita executiva."
        )
        strongest_channel = channel.iloc[0].to_dict()
        strongest_category = category.iloc[0].to_dict()
        weakest_margin_category = category.sort_values("gross_margin_pct").iloc[0].to_dict()
        best_target = target_tracking.sort_values("revenue_target_attainment", ascending=False).iloc[0].to_dict()

        data = {
            "publication_status": publication_status,
            "publication_reason": publication_reason,
            "kpis": kpis,
            "dq_summary": dq_summary.to_dict(orient="records"),
            "monthly_performance": monthly.to_dict(orient="records"),
            "channel_performance": channel.to_dict(orient="records"),
            "category_performance": category.to_dict(orient="records"),
            "target_tracking": target_tracking.to_dict(orient="records"),
            "product_ranking": product_ranking.to_dict(orient="records"),
        }

        (OUTPUTS / "dashboard_data.json").write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
        write_dashboard_variants(build_dashboard(data))
        executive_findings_en = "\n".join(
            [
                "# Executive findings - Retail BI Sales Dashboard",
                "",
                f"- Publication status: **{publication_status}**.",
                f"- Net revenue: **{money(float(kpis['net_revenue']))}**.",
                f"- Gross margin: **{money(float(kpis['gross_margin']))}** (**{pct(float(kpis['gross_margin_pct']))}**).",
                f"- Delivered orders: **{int(kpis['delivered_orders'])}**; average ticket: **{money(float(kpis['average_ticket']))}**.",
                f"- Strongest channel by revenue: **{strongest_channel['sales_channel']}** with **{money(float(strongest_channel['net_revenue']))}**.",
                f"- Strongest category by revenue: **{strongest_category['category']}** with **{money(float(strongest_category['net_revenue']))}**.",
                f"- Lowest margin category: **{weakest_margin_category['category']}** at **{pct(float(weakest_margin_category['gross_margin_pct']))}**.",
                f"- Best target attainment: **{best_target['target_month']} / {best_target['sales_channel']}** at **{pct(float(best_target['revenue_target_attainment']))}**.",
                "- Recommendation: protect margin in lower-margin categories and review target calibration where attainment is consistently above plan.",
            ]
        )
        executive_findings_pt = "\n".join(
            [
                "# Achados executivos - Retail BI Sales Dashboard",
                "",
                f"- Status de publicação: **{publication_status}**.",
                f"- Receita líquida: **{money(float(kpis['net_revenue']))}**.",
                f"- Margem bruta: **{money(float(kpis['gross_margin']))}** (**{pct(float(kpis['gross_margin_pct']))}**).",
                f"- Pedidos entregues: **{int(kpis['delivered_orders'])}**; ticket médio: **{money(float(kpis['average_ticket']))}**.",
                f"- Canal mais forte por receita: **{strongest_channel['sales_channel']}** com **{money(float(strongest_channel['net_revenue']))}**.",
                f"- Categoria mais forte por receita: **{strongest_category['category']}** com **{money(float(strongest_category['net_revenue']))}**.",
                f"- Categoria com menor margem: **{weakest_margin_category['category']}** com **{pct(float(weakest_margin_category['gross_margin_pct']))}**.",
                f"- Melhor atingimento de meta: **{best_target['target_month']} / {best_target['sales_channel']}** com **{pct(float(best_target['revenue_target_attainment']))}**.",
                "- Recomendação: proteger margem nas categorias menos rentáveis e revisar a calibração de metas quando o realizado fica acima do planejado de forma recorrente.",
            ]
        )
        (OUTPUTS / "executive_findings.md").write_text(executive_findings_en, encoding="utf-8")
        (OUTPUTS / "executive_findings.pt-BR.md").write_text(executive_findings_pt, encoding="utf-8")
    finally:
        con.close()

    print(f"Outputs written to {OUTPUTS}")
    print(f"Dashboard written to {DASHBOARD / 'retail_bi_sales_dashboard.html'}")


if __name__ == "__main__":
    main()
