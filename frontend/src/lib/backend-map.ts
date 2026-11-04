/** Maps UI values to FastAPI / Mongo enums and normalises API documents for display. */

const UI_CONDITION_TO_API: Record<string, string> = {
  new: "EXCELLENT",
  like_new: "GOOD",
  good: "GOOD",
  fair: "FAIR",
  poor: "POOR",
  excellent: "EXCELLENT",
};

export function toApiCondition(value: string): string {
  const key = value.trim().toLowerCase();
  return UI_CONDITION_TO_API[key] ?? value.toUpperCase();
}

export function toApiUnit(value: string): string {
  const u = value.trim().toLowerCase();
  if (["piece", "pieces", "pc", "pcs", "nos"].some((x) => u.includes(x))) return "PIECE";
  if (u.includes("ton")) return "TONNE";
  if (u === "kg" || u.includes("kilogram")) return "KG";
  if (u.includes("m³") || u.includes("cubic meter") || u.includes("cum")) return "CUBIC_METER";
  if (u.includes("ft³") || u.includes("cubic feet")) return "CUBIC_FEET";
  if (u.includes("bag")) return "BAG";
  if (u.includes("sqm") || u.includes("square meter")) return "SQUARE_METER";
  if (u.includes("sqft") || u.includes("square feet")) return "SQUARE_FEET";
  if (u.includes("litre") || u.includes("liter")) return "LITRE";
  return "OTHER";
}

export function normaliseQueryParams(params?: Record<string, unknown>): Record<string, unknown> | undefined {
  if (!params) return params;
  const p = { ...params };
  if (p.search != null && p.q == null) {
    p.q = p.search;
    delete p.search;
  }
  if (typeof p.limit === "number" && p.page_size == null) {
    p.page_size = p.limit;
    delete p.limit;
  }
  if (typeof p.sort === "string") {
    const s = p.sort;
    if (s.startsWith("-")) {
      p.sort_by = s.slice(1);
      p.sort_order = "desc";
    } else {
      p.sort_by = s;
      p.sort_order = "asc";
    }
    delete p.sort;
  }
  if (typeof p.condition === "string" && p.condition) {
    p.condition = toApiCondition(p.condition);
  }
  delete p.status;
  return p;
}

export function buildMaterialCreatePayload(form: {
  title: string;
  category_id: string;
  quantity: number;
  unit: string;
  condition: string;
  price?: number;
  city: string;
  available_from?: string;
  description?: string;
}) {
  return {
    material_title: form.title,
    material_description: form.description,
    category_id: form.category_id,
    material_type: form.title,
    available_quantity: form.quantity,
    unit: toApiUnit(form.unit),
    material_condition: toApiCondition(form.condition),
    expected_price: form.price ?? 0,
    location: form.city,
    availability_date: form.available_from || undefined,
    availability_type: form.available_from ? "CUSTOM_DATE" : "READY",
    listing_status: "ACTIVE",
  };
}

export function buildMaterialRequestPayload(materialId: string, quantity: number, message: string) {
  return {
    material_id: materialId,
    requested_quantity: quantity,
    offered_price: 0,
    message: message || undefined,
  };
}

export function buildRequirementCreatePayload(form: {
  title: string;
  category_id: string;
  quantity: number;
  unit: string;
  city: string;
  needed_by: string;
}) {
  return {
    requirement_title: form.title,
    material_type: form.title,
    category_id: form.category_id,
    required_quantity: form.quantity,
    unit: toApiUnit(form.unit),
    minimum_acceptable_condition: "GOOD",
    preferred_location: form.city,
    required_availability_date: form.needed_by,
    requirement_status: "ACTIVE",
  };
}
