"""File import/export handlers supporting CSV, JSON, and XML structured data formats."""

import csv
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Tuple
from .validators import Validators
from .logging_config import get_logger

logger = get_logger("file_handlers")


class DataExporter:
    """Handles exporting records to CSV, JSON, and XML formats."""

    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], file_path: str, fieldnames: List[str] = None) -> bool:
        """Export list of dictionaries to CSV format."""
        if not data:
            logger.warning("No data provided to export_to_csv.")
            return False

        keys = fieldnames or list(data[0].keys())
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(data)
            logger.info("Successfully exported %d records to CSV: %s", len(data), file_path)
            return True
        except Exception as e:
            logger.error("Failed to export to CSV: %s", e)
            raise

    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], file_path: str, indent: int = 4) -> bool:
        """Export records to JSON format."""
        try:
            with open(file_path, mode="w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, default=str)
            logger.info("Successfully exported %d records to JSON: %s", len(data), file_path)
            return True
        except Exception as e:
            logger.error("Failed to export to JSON: %s", e)
            raise

    @staticmethod
    def export_to_xml(data: List[Dict[str, Any]], file_path: str, root_tag: str = "library_catalog", item_tag: str = "book") -> bool:
        """Export records to XML format (Module IV: Third structured format)."""
        try:
            root = ET.Element(root_tag)
            for item in data:
                elem = ET.SubElement(root, item_tag)
                for key, val in item.items():
                    child = ET.SubElement(elem, str(key))
                    child.text = str(val if val is not None else "")
            
            tree = ET.ElementTree(root)
            ET.indent(tree, space="  ", level=0)
            tree.write(file_path, encoding="utf-8", xml_declaration=True)
            logger.info("Successfully exported %d records to XML: %s", len(data), file_path)
            return True
        except Exception as e:
            logger.error("Failed to export to XML: %s", e)
            raise


class DataImporter:
    """Handles importing records from CSV, JSON, and XML with validation."""

    @staticmethod
    def import_from_csv(file_path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Import book records from CSV. Returns (valid_records, error_messages)."""
        valid_records = []
        errors = []

        try:
            with open(file_path, mode="r", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                required = {"book_id", "title", "author", "category", "price", "total_copies"}
                
                # Check headers
                if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
                    missing = required - set(reader.fieldnames or [])
                    return [], [f"CSV missing required columns: {missing}"]

                for row_idx, row in enumerate(reader, start=2):
                    b_id = row.get("book_id", "").strip()
                    title = row.get("title", "").strip()
                    author = row.get("author", "").strip()
                    category = row.get("category", "").strip()
                    price = row.get("price", "0").strip()
                    total = row.get("total_copies", "1").strip()
                    avail = row.get("available_copies", total).strip()

                    ok, err = Validators.validate_book_inputs(b_id, title, author, category, price, total, avail)
                    if not ok:
                        errors.append(f"Row {row_idx}: {err}")
                        continue

                    valid_records.append({
                        "book_id": b_id,
                        "title": title,
                        "author": author,
                        "category": category,
                        "price": float(price),
                        "total_copies": int(total),
                        "available_copies": int(avail)
                    })
        except Exception as e:
            logger.error("Error reading CSV file %s: %s", file_path, e)
            errors.append(f"File reading error: {e}")

        return valid_records, errors

    @staticmethod
    def import_from_json(file_path: str) -> Tuple[List[Dict[str, Any]], List[str]]:
        """Import book records from JSON. Returns (valid_records, error_messages)."""
        valid_records = []
        errors = []

        try:
            with open(file_path, mode="r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                return [], ["JSON root must be an array of book objects."]

            for idx, item in enumerate(data, start=1):
                if not isinstance(item, dict):
                    errors.append(f"Item {idx}: Expected JSON object.")
                    continue

                b_id = str(item.get("book_id", "")).strip()
                title = str(item.get("title", "")).strip()
                author = str(item.get("author", "")).strip()
                category = str(item.get("category", "")).strip()
                price = item.get("price", 0.0)
                total = item.get("total_copies", 1)
                avail = item.get("available_copies", total)

                ok, err = Validators.validate_book_inputs(b_id, title, author, category, price, total, avail)
                if not ok:
                    errors.append(f"Item {idx} ({b_id}): {err}")
                    continue

                valid_records.append({
                    "book_id": b_id,
                    "title": title,
                    "author": author,
                    "category": category,
                    "price": float(price),
                    "total_copies": int(total),
                    "available_copies": int(avail)
                })
        except Exception as e:
            logger.error("Error reading JSON file %s: %s", file_path, e)
            errors.append(f"File reading error: {e}")

        return valid_records, errors
