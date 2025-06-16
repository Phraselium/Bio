import json
import csv
import sys
from pathlib import Path
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

REGENERATIVE_KEYWORDS = [
    "regeneracion",
    "regeneración",
    "ciclo cerrado",
    "restauracion ecologica",
    "restauración ecológica",
    "biodiversidad",
    "mejora del habitat",
    "mejora del hábitat",
    "recuperacion de recursos",
    "recuperación de recursos",
    "soluciones basadas en la naturaleza",
    "sbn",
    "nbs",
    "ciclos cerrados",
    "cierre de ciclos",
    "integracion con comunidades",
    "integración con comunidades",
]

BIOMIMETIC_KEYWORDS = [
    "inspirado en la naturaleza",
    "ventilacion pasiva",
    "ventilación pasiva",
    "estructura alveolar",
    "eficiencia energetica natural",
    "eficiencia energética natural",
    "alas",
    "panales",
    "enfriamiento por evaporacion",
    "enfriamiento por evaporación",
    "estructura adaptativa",
    "resiliente",
    "organismos vivos",
]


def fetch_description(url: str) -> Optional[str]:
    """Retrieve meta description text from a project URL."""
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                return meta["content"].strip()
    except Exception:
        pass
    return None


def read_projects(path: Path):
    ext = path.suffix.lower()
    if ext == ".json":
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # If file contains 'data' key (as from ACCIONA filter.json) adapt structure
        if isinstance(data, dict) and "data" in data:
            projects = []
            for item in data["data"]:
                name = item.get("title") or item.get("nombre")
                location = None
                if "labels" in item:
                    for lab in item["labels"]:
                        if lab.get("icon") == "icon-globe-16":
                            location = lab.get("text")
                            break
                    if not location and item["labels"]:
                        location = item["labels"][0].get("text")
                projects.append({
                    "nombre": name,
                    "ubicacion": location,
                    "actionUrl": item.get("actionUrl"),
                    "descripcion": item.get("descripcion")
                })
            return projects
        else:
            return data
    elif ext == ".csv":
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    elif ext in [".txt", ".md"]:
        projects = []
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        for block in content.split("\n\n"):
            lines = [line.strip() for line in block.splitlines() if line.strip()]
            if len(lines) >= 3:
                projects.append({
                    "nombre": lines[0],
                    "ubicacion": lines[1],
                    "descripcion": " ".join(lines[2:])
                })
        return projects
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


def analyze_description(desc: str):
    text = desc.lower()
    regen = any(k in text for k in REGENERATIVE_KEYWORDS)
    bio = any(k in text for k in BIOMIMETIC_KEYWORDS)
    reason_regen = None
    reason_bio = None
    if regen:
        matches = [k for k in REGENERATIVE_KEYWORDS if k in text]
        reason_regen = f"Se encontraron términos: {', '.join(matches)}"
    else:
        reason_regen = "No se identifica contenido explícito o implícito en la descripción"
    if bio:
        matches = [k for k in BIOMIMETIC_KEYWORDS if k in text]
        reason_bio = f"Se encontraron términos: {', '.join(matches)}"
    else:
        reason_bio = "No se identifica contenido explícito o implícito en la descripción"
    return regen, bio, reason_regen, reason_bio


def main():
    if len(sys.argv) < 2:
        print("Uso: python analizar_proyectos.py <archivo_entrada> [archivo_salida]", file=sys.stderr)
        sys.exit(1)
    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("proyectos_analizados.json")
    projects = read_projects(input_path)
    analyzed = []
    for proj in projects:
        desc = proj.get("descripcion", "") or ""
        if not desc and proj.get("actionUrl"):
            url = "https://www.acciona.com" + proj["actionUrl"]
            fetched = fetch_description(url)
            if fetched:
                desc = fetched
        regen, bio, reason_regen, reason_bio = analyze_description(desc)
        analyzed.append({
            "nombre": proj.get("nombre"),
            "ubicacion": proj.get("ubicacion"),
            "url": "https://www.acciona.com" + proj.get("actionUrl", ""),
            "regenerativo": regen,
            "biomimetico": bio,
            "razon_regenerativo": reason_regen,
            "razon_biomimetico": reason_bio,
        })
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(analyzed, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
