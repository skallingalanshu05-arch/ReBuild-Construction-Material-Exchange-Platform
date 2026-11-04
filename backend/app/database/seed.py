from app.schemas.common import doc_timestamps

DEFAULT_CATEGORIES = [
    ("Bricks and Blocks", "Clay bricks, blocks, and masonry units"),
    ("Cement", "Portland cement and blended cements"),
    ("Sand", "River sand, M-sand, and fine aggregates"),
    ("Aggregates", "Coarse aggregates and crushed stone"),
    ("Steel and Metal", "Rebar, structural steel, and metal scrap"),
    ("Wood and Timber", "Lumber, plywood, and timber products"),
    ("Doors and Windows", "Doors, windows, frames, and fittings"),
    ("Tiles and Flooring", "Ceramic, vitrified tiles and flooring"),
    ("Glass", "Flat glass, tempered glass panels"),
    ("Roofing Materials", "Sheets, tiles, and roofing systems"),
    ("Plumbing Materials", "Pipes, fittings, and fixtures"),
    ("Electrical Materials", "Cables, conduits, and electrical components"),
    ("Soil and Excavated Materials", "Excavated soil and fill materials"),
    ("Other Construction Materials", "Miscellaneous construction materials"),
]


async def seed_categories(db) -> None:
    for name, description in DEFAULT_CATEGORIES:
        existing = await db.categories.find_one({"name": name})
        if existing:
            continue
        await db.categories.insert_one(
            {
                "name": name,
                "description": description,
                "parent_category_id": None,
                "image_url": None,
                "is_active": True,
                **doc_timestamps(),
            }
        )
