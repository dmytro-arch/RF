#!/usr/bin/env python3
"""Build corrected Airtable-importable PIM tables and normalized marketplace offers."""

from __future__ import annotations

import csv
import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_INPUT = ROOT / "master_pim.csv"
VARIATIONS_INPUT = ROOT / "Master_Pim_Variations.csv"

SITE_BRANDS = {
    "royalfoam.art": "Royal Foam Art Design",
    "decorativearchitecturalshapes.com": "Decorative Architectural Shapes",
    "decorativearchitecturalproducts.com": "Decorative Architectural Products",
    "3dsignfactory.com": "3D Sign Factory",
    "3dsignfactory.us": "3D Sign Factory",
    "greenwall.art": "Green Wall Art",
}


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, headers: list[str], rows: Iterable[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, headers, extrasaction="ignore", quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def clean(value: str | None) -> str:
    value = (value or "").replace("\r", "").strip()
    # Remove a single pair of serialization quotes around a whole Airtable value.
    if len(value) >= 2 and value[0] == value[-1] == '"':
        value = value[1:-1].replace('""', '"').strip()
    return value


def parse_list(value: str | None) -> list[str]:
    value = value or ""
    if not value.strip():
        return []
    try:
        return [clean(item) for item in next(csv.reader([value], skipinitialspace=True)) if clean(item)]
    except csv.Error:
        return [clean(item) for item in value.split(",") if clean(item)]


def split_attribute(token: str) -> tuple[str, str] | None:
    parts = re.split(r"\s+[—–-]\s+", token, maxsplit=1)
    if len(parts) != 2:
        return None
    return clean(parts[0]).title(), clean(parts[1])


def attributes(value: str | None) -> tuple[dict[str, list[str]], list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    malformed: list[str] = []
    for token in parse_list(value):
        pair = split_attribute(token)
        if pair is None:
            malformed.append(token)
            continue
        name, selected = pair
        result[name].append(selected)
    return dict(result), malformed


def first_url(value: str | None) -> str:
    match = re.search(r"https?://[^\s,)]+", value or "")
    return match.group(0) if match else ""


def all_urls(value: str | None) -> list[str]:
    return re.findall(r"https?://[^\s,)]+", value or "")


def plain_text(value: str | None) -> str:
    text = html.unescape(value or "")
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def sites(value: str | None) -> list[str]:
    return list(dict.fromkeys(clean(item).lower().removeprefix("www.") for item in (value or "").split(",") if clean(item)))


def brand_mapping(site_values: list[str]) -> dict[str, str]:
    return {site: SITE_BRANDS.get(site, "") for site in site_values}


def money_amount(value: str | None) -> str:
    value = clean(value)
    if not value:
        return ""
    normalized = re.sub(r"[^0-9.\-]", "", value)
    try:
        return f"{float(normalized):.2f}"
    except ValueError:
        return ""


def bool_checked(value: str | None) -> bool:
    return clean(value).lower() in {"checked", "1", "true", "yes"}


def add_issue(issues: list[str], condition: bool, message: str) -> None:
    if condition:
        issues.append(message)


def build() -> None:
    product_headers, products = read_csv(PRODUCTS_INPUT)
    variation_headers, variations = read_csv(VARIATIONS_INPUT)

    # Normalize product identity first.
    for product in products:
        product["Product Label"] = clean(product.get("Product Label"))
        product["Name"] = clean(product.get("Name"))
        product["SKU"] = clean(product.get("SKU"))

    products_by_label = {product["Product Label"]: product for product in products}
    products_by_sku = {product["SKU"]: product for product in products if product["SKU"]}
    product_skus = sorted(products_by_sku, key=len, reverse=True)

    # Resolve every variation to one parent when this can be done without guessing.
    resolved_parent: dict[str, dict[str, str] | None] = {}
    linked_variation_labels: dict[str, list[str]] = defaultdict(list)

    for variation in variations:
        variation["Variation Label"] = clean(variation.get("Variation Label"))
        variation["Variation SKU"] = clean(variation.get("Variation SKU"))
        raw_parent = clean(variation.get("Parent Product"))
        parent = products_by_label.get(raw_parent)

        # Fix serialization/newline differences in linked-record labels.
        if parent is None:
            raw_key = re.sub(r"\s+", " ", raw_parent).strip('" ')
            for label, candidate in products_by_label.items():
                if re.sub(r"\s+", " ", label).strip('" ') == raw_key:
                    parent = candidate
                    break

        # If a malformed field contains many parents, resolve by variation SKU prefix.
        if parent is None and variation["Variation SKU"]:
            matches = [sku for sku in product_skus if variation["Variation SKU"].startswith(f"{sku}-")]
            if len(matches) == 1:
                parent = products_by_sku[matches[0]]

        resolved_parent[variation["Variation Label"]] = parent
        if parent is not None:
            variation["Parent Product"] = parent["Product Label"]
            linked_variation_labels[parent["SKU"]].append(variation["Variation Label"])
        else:
            variation["Parent Product"] = ""

    corrected_products: list[dict[str, object]] = []
    normalized_products: list[dict[str, object]] = []

    for product in products:
        site_values = sites(product.get("Linked Sites"))
        mapping = brand_mapping(site_values)
        unique_brands = sorted({brand for brand in mapping.values() if brand})
        attrs, malformed = attributes(product.get("Product Attributes"))
        image_urls = all_urls(product.get("Images"))
        description = plain_text(product.get("Description") or product.get("Short description"))
        issues: list[str] = []

        add_issue(issues, not site_values, "Linked Sites is empty")
        add_issue(issues, any(not value for value in mapping.values()), "Unknown site-to-brand mapping")
        add_issue(issues, not description, "Description is empty")
        add_issue(issues, bool(re.search(r"(?i)\btest\b|dfsdf|hjgh", description)), "Description contains test/placeholder text")
        add_issue(issues, not image_urls, "Image is missing")
        add_issue(issues, bool(image_urls) and all("airtableusercontent.com" in url for url in image_urls), "Images use temporary Airtable URLs")
        add_issue(issues, bool(malformed), "Malformed Product Attributes")
        add_issue(issues, not linked_variation_labels.get(product["SKU"]), "No valid linked variations")

        brand_json = json.dumps(mapping, ensure_ascii=False, sort_keys=True)
        product_url_mapping = {site: "" for site in site_values}
        additions = {
            "Product SKU Key": product["SKU"],
            "Corrected Variations": ",".join(linked_variation_labels.get(product["SKU"], [])),
            "Site Brand Mapping": brand_json,
            "Default Brand": unique_brands[0] if len(unique_brands) == 1 else "",
            "Product URL Mapping": json.dumps(product_url_mapping, ensure_ascii=False, sort_keys=True),
            "Condition": "new",
            "Currency": "USD",
            "Product Type": clean(product.get("Categories")),
            "Google Product Category": "",
            "GTIN": "",
            "MPN": "",
            "Identifier Exists": "",
            "Material": "",
            "Color Options": " | ".join(attrs.get("Color", [])),
            "Texture Options": " | ".join(attrs.get("Texture", [])),
            "Length Options": " | ".join(attrs.get("Length", [])),
            "Width Options": " | ".join(attrs.get("Width", [])),
            "Height Options": " | ".join(attrs.get("Height", [])),
            "Depth Options": " | ".join(attrs.get("Depth", [])),
            "Projection Options": " | ".join(attrs.get("Projection", [])),
            "Diameter Options": " | ".join(attrs.get("Diameter", [])),
            "Sides Options": " | ".join(attrs.get("Sides", [])),
            "Primary Image URL": image_urls[0] if image_urls else "",
            "Additional Image URLs": " | ".join(image_urls[1:]),
            "PIM Review Status": "NEEDS_REVIEW" if issues else "READY",
            "PIM Issues": " | ".join(issues),
        }
        corrected = dict(product)
        corrected["Variations"] = additions["Corrected Variations"]
        corrected.update(additions)
        corrected_products.append(corrected)

        normalized_products.append({
            "Product SKU": product["SKU"],
            "Product Label": product["Product Label"],
            "Name": product["Name"],
            "Product Type": additions["Product Type"],
            "Linked Sites": ",".join(site_values),
            "Site Brand Mapping": brand_json,
            "Short Description": plain_text(product.get("Short description")),
            "Description": description,
            "Primary Image URL": additions["Primary Image URL"],
            "Additional Image URLs": additions["Additional Image URLs"],
            "Video URL": first_url(product.get("Product Video")),
            "Condition": "new",
            "Currency": "USD",
            "Google Product Category": "",
            "GTIN": "",
            "MPN": "",
            "Identifier Exists": "",
            "Material": "",
            "Color Options": additions["Color Options"],
            "Texture Options": additions["Texture Options"],
            "Length Options": additions["Length Options"],
            "Width Options": additions["Width Options"],
            "Height Options": additions["Height Options"],
            "Depth Options": additions["Depth Options"],
            "Projection Options": additions["Projection Options"],
            "Diameter Options": additions["Diameter Options"],
            "Sides Options": additions["Sides Options"],
            "Variation Labels": additions["Corrected Variations"],
            "PIM Review Status": additions["PIM Review Status"],
            "PIM Issues": additions["PIM Issues"],
        })

    normalized_product_by_sku = {row["Product SKU"]: row for row in normalized_products}
    corrected_variations: list[dict[str, object]] = []
    normalized_variations: list[dict[str, object]] = []
    marketplace_offers: list[dict[str, object]] = []

    for variation in variations:
        parent = resolved_parent.get(variation["Variation Label"])
        parent_norm = normalized_product_by_sku.get(parent["SKU"]) if parent else None
        selected, malformed = attributes(variation.get("Linked Attributes"))
        price = money_amount(variation.get("Regular Price"))
        stock = clean(variation.get("Stock"))
        active = bool_checked(variation.get("Is Active?"))
        published = bool_checked(variation.get("Published"))
        parent_sites = sites(parent.get("Linked Sites")) if parent else []
        mapping = brand_mapping(parent_sites)
        issues: list[str] = []

        add_issue(issues, not variation["Variation SKU"], "Variation SKU is empty")
        add_issue(issues, parent is None, "Valid parent product is missing")
        add_issue(issues, not price, "Regular Price is empty or invalid")
        add_issue(issues, not stock, "Stock is empty")
        add_issue(issues, not active, "Variation is not active")
        add_issue(issues, not published, "Variation is not published")
        add_issue(issues, "TEST" in variation["Variation SKU"].upper(), "Test SKU")
        add_issue(issues, bool(malformed), "Malformed Linked Attributes")
        duplicates = sorted(name for name, values in selected.items() if len(values) > 1)
        add_issue(issues, bool(duplicates), f"Multiple values selected: {', '.join(duplicates)}")

        if parent:
            allowed, _ = attributes(parent.get("Product Attributes"))
            disallowed = []
            allowed_tokens = set(parse_list(parent.get("Product Attributes")))
            for token in parse_list(variation.get("Linked Attributes")):
                if token not in allowed_tokens:
                    disallowed.append(token)
            add_issue(issues, bool(disallowed), "Selected attributes are not listed on parent")
            missing_selected = sorted(set(allowed) - set(selected))
            add_issue(issues, bool(missing_selected), f"Parent attributes not selected: {', '.join(missing_selected)}")

        availability = ""
        if active and published and stock.isdigit():
            availability = "in_stock" if int(stock) > 0 else "out_of_stock"

        selected_summary = ", ".join(
            f"{name}: {' | '.join(values)}" for name, values in selected.items()
        )
        title_suffix = ", ".join(
            " | ".join(values) for name, values in selected.items() if values
        )
        parent_name = parent["Name"] if parent else ""
        feed_title = f"{parent_name} — {title_suffix}" if parent_name and title_suffix else parent_name
        description = parent_norm["Description"] if parent_norm else ""
        image_link = parent_norm["Primary Image URL"] if parent_norm else ""
        item_group_id = parent["SKU"] if parent else ""

        variation_record_key = variation["Variation SKU"] or f"UNRESOLVED::{variation['Variation Label']}"
        variation_additions = {
            "Variation Record Key": variation_record_key,
            "Parent SKU": item_group_id,
            "Parent Name": parent_name,
            "Linked Sites": ",".join(parent_sites),
            "Site Brand Mapping": json.dumps(mapping, ensure_ascii=False, sort_keys=True),
            "Feed Title": feed_title[:500],
            "Feed Description": description,
            "Price Amount": price,
            "Currency": "USD",
            "Feed Price": f"{price} USD" if price else "",
            "Availability": availability,
            "Condition": "new",
            "Item Group ID": item_group_id,
            "Color": " | ".join(selected.get("Color", [])),
            "Texture / Pattern": " | ".join(selected.get("Texture", [])),
            "Material": "",
            "Length": " | ".join(selected.get("Length", [])),
            "Width": " | ".join(selected.get("Width", [])),
            "Height": " | ".join(selected.get("Height", [])),
            "Depth": " | ".join(selected.get("Depth", [])),
            "Projection": " | ".join(selected.get("Projection", [])),
            "Diameter": " | ".join(selected.get("Diameter", [])),
            "Sides": " | ".join(selected.get("Sides", [])),
            "Selected Attributes": selected_summary,
            "Image Link": image_link,
            "Product Link": "",
            "Google Product Category": "",
            "GTIN": "",
            "MPN": "",
            "Identifier Exists": "",
            "Airtable Import Status": "NEEDS_REVIEW" if any(
                marker in " | ".join(issues)
                for marker in ["SKU is empty", "parent product is missing", "Multiple values"]
            ) else "READY",
            "Marketplace Export Status": "BLOCKED" if issues or not image_link else "NEEDS_URL_AND_IDENTIFIERS",
            "PIM Issues": " | ".join(issues),
        }
        corrected = dict(variation)
        corrected.update(variation_additions)
        corrected_variations.append(corrected)

        normalized = {
            "Variation SKU": variation["Variation SKU"],
            "Variation Label": variation["Variation Label"],
            **variation_additions,
            "Regular Price Original": clean(variation.get("Regular Price")),
            "Tiered Pricing": clean(variation.get("Tiered Pricing")),
            "Stock": stock,
            "Is Active": "1" if active else "0",
            "Published": "1" if published else "0",
        }
        normalized_variations.append(normalized)

        offer_sites = parent_sites or [""]
        for site in offer_sites:
            brand = mapping.get(site, "")
            offer_issues = list(issues)
            add_issue(offer_issues, not site, "Destination site is missing")
            add_issue(offer_issues, not brand, "Brand is missing")
            add_issue(offer_issues, not description, "Description is missing")
            add_issue(offer_issues, not image_link, "Image is missing")
            add_issue(offer_issues, bool(image_link) and "airtableusercontent.com" in image_link, "Image URL is temporary")
            add_issue(offer_issues, True, "Product URL is missing")
            add_issue(offer_issues, True, "Google Product Category is missing")
            add_issue(offer_issues, True, "Product identifiers require review")
            marketplace_offers.append({
                "Offer Key": f"{site or 'NO_SITE'}::{variation_record_key}",
                "Destination Site": site,
                "id": variation["Variation SKU"],
                "item_group_id": item_group_id,
                "title": feed_title[:150],
                "description": description,
                "link": "",
                "image_link": image_link,
                "additional_image_link": parent_norm["Additional Image URLs"] if parent_norm else "",
                "price": f"{price} USD" if price else "",
                "availability": availability,
                "condition": "new",
                "brand": brand,
                "gtin": "",
                "mpn": "",
                "identifier_exists": "",
                "google_product_category": "",
                "product_type": parent_norm["Product Type"] if parent_norm else "",
                "color": variation_additions["Color"],
                "size": title_suffix,
                "material": "",
                "pattern": variation_additions["Texture / Pattern"],
                "stock": stock,
                "active": "1" if active else "0",
                "published": "1" if published else "0",
                "Google Status": "BLOCKED" if offer_issues else "READY",
                "Pinterest Status": "BLOCKED" if offer_issues else "READY",
                "Meta Status": "BLOCKED" if offer_issues else "READY",
                "Export Issues": " | ".join(dict.fromkeys(offer_issues)),
            })

    product_extra_headers = [
        "Product SKU Key", "Corrected Variations", "Site Brand Mapping", "Default Brand",
        "Product URL Mapping", "Condition", "Currency", "Product Type",
        "Google Product Category", "GTIN", "MPN", "Identifier Exists", "Material",
        "Color Options", "Texture Options", "Length Options", "Width Options",
        "Height Options", "Depth Options", "Projection Options", "Diameter Options",
        "Sides Options", "Primary Image URL", "Additional Image URLs",
        "PIM Review Status", "PIM Issues",
    ]
    variation_extra_headers = [
        "Variation Record Key", "Parent SKU", "Parent Name", "Linked Sites", "Site Brand Mapping", "Feed Title",
        "Feed Description", "Price Amount", "Currency", "Feed Price", "Availability",
        "Condition", "Item Group ID", "Color", "Texture / Pattern", "Material", "Length",
        "Width", "Height", "Depth", "Projection", "Diameter", "Sides",
        "Selected Attributes", "Image Link", "Product Link", "Google Product Category",
        "GTIN", "MPN", "Identifier Exists", "Airtable Import Status",
        "Marketplace Export Status", "PIM Issues",
    ]
    normalized_product_headers = list(normalized_products[0])
    normalized_variation_headers = list(normalized_variations[0])
    offer_headers = list(marketplace_offers[0])

    write_csv(ROOT / "airtable_products_corrected.csv", product_headers + product_extra_headers, corrected_products)
    write_csv(ROOT / "airtable_variations_corrected.csv", variation_headers + variation_extra_headers, corrected_variations)
    write_csv(ROOT / "airtable_products_normalized.csv", normalized_product_headers, normalized_products)
    write_csv(ROOT / "airtable_variations_normalized.csv", normalized_variation_headers, normalized_variations)
    write_csv(ROOT / "airtable_marketplace_offers.csv", offer_headers, marketplace_offers)

    print(json.dumps({
        "products": len(corrected_products),
        "variations": len(corrected_variations),
        "offers": len(marketplace_offers),
        "valid_parent_variations": sum(bool(row["Parent SKU"]) for row in normalized_variations),
        "airtable_ready_variations": sum(row["Airtable Import Status"] == "READY" for row in normalized_variations),
        "marketplace_ready_variations": sum(row["Marketplace Export Status"] == "READY" for row in normalized_variations),
    }, indent=2))


if __name__ == "__main__":
    build()
