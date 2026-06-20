"""Generate synthetic retail data for the BI portfolio project.

The script refreshes the local sample dataset under data/.
It does not use real or sensitive data.
"""

from __future__ import annotations

import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data"
OUT.mkdir(parents=True, exist_ok=True)

CHANNELS = ["E-commerce", "Store", "Marketplace"]
STATES = ["PR", "SP", "RJ", "SC", "RS", "MG", "BA"]
PAYMENTS = ["Credit Card", "Debit Card", "Pix"]
STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered", "Cancelled"]
SEGMENTS = ["New", "Recurring"]

PRODUCTS = [
    ("P-001", "Eletronicos", "Acessorios", "Fone Bluetooth Basic", 89.90, 48.00),
    ("P-002", "Eletronicos", "Acessorios", "Carregador Turbo USB-C", 129.90, 72.00),
    ("P-003", "Casa", "Cozinha", "Panela Antiaderente 5L", 249.90, 170.00),
    ("P-004", "Casa", "Eletroportateis", "Air Fryer Digital 4L", 399.90, 285.00),
    ("P-005", "Beleza", "Cuidado Pessoal", "Sabonete Liquido Premium", 24.90, 10.50),
    ("P-006", "Beleza", "Cuidado Pessoal", "Secador Compacto", 159.90, 92.00),
    ("P-007", "Esporte", "Fitness", "Bicicleta Ergometrica Compacta", 329.90, 240.00),
    ("P-008", "Esporte", "Acessorios", "Garrafa Termica 700ml", 39.90, 18.00),
    ("P-009", "Moda", "Acessorios", "Cinto Casual", 59.90, 31.00),
    ("P-010", "Moda", "Calcados", "Tenis Urbano", 199.90, 118.00),
    ("P-011", "Eletronicos", "Audio", "Caixa de Som Portatil", 499.90, 340.00),
    ("P-012", "Casa", "Organizacao", "Kit Organizadores", 74.90, 38.00),
]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def generate_customers(n: int = 250) -> list[dict[str, object]]:
    cities = {
        "PR": ["Curitiba", "Londrina", "Maringa"],
        "SP": ["Sao Paulo", "Campinas", "Santos"],
        "RJ": ["Rio de Janeiro", "Niteroi"],
        "SC": ["Florianopolis", "Joinville"],
        "RS": ["Porto Alegre", "Caxias do Sul"],
        "MG": ["Belo Horizonte", "Uberlandia"],
        "BA": ["Salvador", "Feira de Santana"],
    }
    rows = []
    for idx in range(1, n + 1):
        state = random.choice(STATES)
        signup = date(2025, 1, 1) + timedelta(days=random.randint(0, 430))
        rows.append(
            {
                "customer_id": f"C-{idx:04d}",
                "customer_segment": random.choice(SEGMENTS),
                "city": random.choice(cities[state]),
                "state": state,
                "signup_date": signup.isoformat(),
            }
        )
    return rows


def generate_orders(customers: list[dict[str, object]], n: int = 1200) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    orders = []
    items = []
    start = date(2026, 1, 1)
    for order_idx in range(1, n + 1):
        customer = random.choice(customers)
        order_date = start + timedelta(days=random.randint(0, 180))
        order_id = f"O-{order_idx:05d}"
        channel = random.choice(CHANNELS)
        status = random.choice(STATUSES)
        orders.append(
            {
                "order_id": order_id,
                "order_date": order_date.isoformat(),
                "customer_id": customer["customer_id"],
                "sales_channel": channel,
                "state": customer["state"],
                "payment_method": random.choice(PAYMENTS),
                "order_status": status,
                "shipping_days": 0 if status == "Cancelled" else random.randint(1, 8),
            }
        )
        for item_number in range(1, random.randint(2, 5)):
            product = random.choice(PRODUCTS)
            quantity = random.randint(1, 4)
            discount = random.choice([0, 0, 0.03, 0.05, 0.08, 0.10, 0.15])
            items.append(
                {
                    "order_item_id": f"OI-{len(items) + 1:06d}",
                    "order_id": order_id,
                    "product_id": product[0],
                    "quantity": quantity,
                    "unit_price": product[4],
                    "unit_cost": product[5],
                    "discount_pct": discount,
                }
            )
    return orders, items


def generate_targets(orders: list[dict[str, object]], items: list[dict[str, object]]) -> list[dict[str, object]]:
    order_lookup = {
        order["order_id"]: {
            "target_month": month_key(date.fromisoformat(str(order["order_date"]))),
            "sales_channel": order["sales_channel"],
            "order_status": order["order_status"],
        }
        for order in orders
    }
    actuals: dict[tuple[str, str], dict[str, float]] = {}
    for item in items:
        order = order_lookup[item["order_id"]]
        if order["order_status"] != "Delivered":
            continue
        key = (order["target_month"], order["sales_channel"])
        actuals.setdefault(key, {"revenue": 0.0, "margin": 0.0})
        revenue = float(item["quantity"]) * float(item["unit_price"]) * (1 - float(item["discount_pct"]))
        margin = revenue - float(item["quantity"]) * float(item["unit_cost"])
        actuals[key]["revenue"] += revenue
        actuals[key]["margin"] += margin

    rows = []
    for month in ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]:
        for channel in CHANNELS:
            actual = actuals.get((month, channel), {"revenue": 0.0, "margin": 0.0})
            target_attainment = random.choice([0.91, 0.96, 0.99, 1.03, 1.07, 1.12])
            revenue_target = actual["revenue"] / target_attainment if actual["revenue"] else 0
            actual_margin_pct = actual["margin"] / actual["revenue"] if actual["revenue"] else 0.3
            margin_target_pct = min(max(actual_margin_pct + random.choice([-0.015, -0.005, 0.0, 0.01, 0.02]), 0.24), 0.38)
            rows.append(
                {
                    "target_month": month,
                    "sales_channel": channel,
                    "revenue_target": round(revenue_target, 2),
                    "margin_target_pct": round(margin_target_pct, 4),
                }
            )
    return rows


def main() -> None:
    customers = generate_customers()
    orders, items = generate_orders(customers)
    product_rows = [
        {
            "product_id": product_id,
            "category": category,
            "subcategory": subcategory,
            "product_name": product_name,
        }
        for product_id, category, subcategory, product_name, _, _ in PRODUCTS
    ]
    targets = generate_targets(orders, items)

    write_csv(OUT / "sample_customers.csv", list(customers[0].keys()), customers)
    write_csv(OUT / "sample_orders.csv", list(orders[0].keys()), orders)
    write_csv(OUT / "sample_order_items.csv", list(items[0].keys()), items)
    write_csv(OUT / "sample_products.csv", list(product_rows[0].keys()), product_rows)
    write_csv(OUT / "sample_targets.csv", list(targets[0].keys()), targets)

    print(f"Generated files in {OUT}")
    print(f"Orders: {len(orders)} | Items: {len(items)} | Customers: {len(customers)}")


if __name__ == "__main__":
    main()
