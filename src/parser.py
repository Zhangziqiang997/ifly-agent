"""Layer 1: Programmatic quick-match -- numeric extraction, unit normalization, keyword matching."""
import re


def extract_numeric(text: str) -> list:
    """Extract all (number, unit_hint) pairs from a text string.
    Examples:
        '>=500cd/m2' -> [(500.0, 'cd_m2')]
        '3840*2160'  -> [(3840.0, 'px'), (2160.0, 'px')]
        '<=28mm'     -> [(28.0, 'mm')]
    """
    results = []
    patterns = [
        (r'(\d+\.?\d*)\s*cd\s*/\s*m\s*[²2]', 'cd_m2'),
        (r'(\d+\.?\d*)\s*mm', 'mm'),
        (r'(\d+\.?\d*)\s*英寸', 'inch'),
        (r'(\d+\.?\d*)\s*inch', 'inch'),
        (r'(\d+\.?\d*)\s*[Ww]', 'watt'),
        (r'(\d+\.?\d*)\s*GB', 'gb'),
        (r'(\d+\.?\d*)\s*[点個]', 'touch_points'),
        (r'(\d+\.?\d*)\s*[级級]', 'pressure_level'),
        (r'(\d+\.?\d*)\s*[°度]', 'degree'),
        (r'(\d+\.?\d*)\s*[%％]', 'pct'),
        (r'(\d+\.?\d*)\s*[条路個个]', 'count'),
        (r'(\d+\.?\d*)\s*万像素', 'mp'),
    ]
    for pat, unit in patterns:
        for m in re.finditer(pat, text):
            results.append((float(m.group(1)), unit))

    for m in re.finditer(r'(\d{3,5})\s*[xX\*×]\s*(\d{3,5})', text):
        results.append((float(m.group(1)), 'px'))
        results.append((float(m.group(2)), 'px'))

    for m in re.finditer(r'[≥≤>＜>=]\s*(\d+\.?\d*)', text):
        num = float(m.group(1))
        if not any(abs(r[0] - num) < 0.01 for r in results):
            results.append((num, 'unknown'))

    return results


def normalize_unit(value: float, from_unit: str, to_unit: str) -> float:
    """Convert value between units. Returns same value if units are directly comparable."""
    if from_unit == to_unit:
        return value
    equivalent_pairs = [('px', 'pixel_width'), ('inch_inch', 'inch')]
    for a, b in equivalent_pairs:
        if from_unit in (a, b) and to_unit in (a, b):
            return value
    return value


def compare_indicators(bid_inds: list, our_inds: list) -> tuple:
    """Compare two indicator lists.
    Returns ('positive'|'negative'|'uncertain', explanation).
    Matches by unit first, then verifies name similarity to prevent false matches."""
    if not bid_inds:
        return ("uncertain", "no indicators to compare")

    matches, total = 0, 0
    for bi in bid_inds:
        total += 1
        matched_oi = None
        # Primary match: same unit AND similar name
        for oi in our_inds:
            if bi.get('unit') == oi.get('unit'):
                bn = bi.get('name', '')
                on = oi.get('name', '')
                # Name check: one contains the other, or they share key characters
                if bn and on and (bn in on or on in bn or _name_overlap(bn, on) > 0.5):
                    matched_oi = oi
                    break
        # Fallback: only same unit (no name match)
        # BUT: for non-numeric types (feature, cert, spec), REQUIRE name match to prevent false positives
        non_numeric = {'feature', 'cert', 'spec', 'type'}
        if not matched_oi and bi.get('unit', '') not in non_numeric:
            for oi in our_inds:
                if bi.get('unit') == oi.get('unit'):
                    matched_oi = oi
                    break

        if matched_oi is None:
            continue

        bv, ov = bi.get('value'), matched_oi.get('value')
        if isinstance(bv, (int, float)) and isinstance(ov, (int, float)):
            our_val = normalize_unit(ov, matched_oi.get('unit', ''), bi.get('unit', ''))
            comp = bi.get('comparator', 'eq')
            if comp in ('gte', 'gt', 'eq') and our_val >= bv:
                matches += 1
            elif comp in ('lte', 'lt') and our_val <= bv:
                matches += 1
            elif comp == 'eq' and abs(our_val - bv) < 0.01:
                matches += 1
        elif isinstance(bv, bool) and isinstance(ov, bool):
            if bv == ov:
                matches += 1
        elif bv is True and ov is True:
            matches += 1

    if total == 0:
        return ("uncertain", "no numeric indicators")
    if matches == total:
        return ("positive", f"{matches}/{total} indicators matched")
    elif matches == 0:
        return ("negative", f"0/{total} indicators matched")
    else:
        return ("uncertain", f"{matches}/{total} indicators matched, needs AI review")


def _name_overlap(n1: str, n2: str) -> float:
    """Character-level Jaccard overlap between two indicator names."""
    s1, s2 = set(n1.replace(' ', '')), set(n2.replace(' ', ''))
    if not s1 or not s2:
        return 0.0
    return len(s1 & s2) / len(s1 | s2)


def keyword_overlap(text1: str, text2: str) -> float:
    """Jaccard similarity between two texts based on 2-char bigrams."""
    if not text1 or not text2:
        return 0.0

    def bigrams(s):
        s = s.lower().replace(' ', '')
        return set(s[i:i + 2] for i in range(len(s) - 1))

    b1, b2 = bigrams(text1), bigrams(text2)
    if not b1 or not b2:
        return 0.0
    return len(b1 & b2) / len(b1 | b2)


def quick_match(bid_item: dict, our_param: dict) -> tuple:
    """Determine if our_param satisfies bid_item.
    Returns (status, detail) where status is 'positive'|'negative'|'uncertain'.
    """
    bid_req = bid_item.get('requirement', '')
    our_spec = our_param.get('spec', '')

    bid_inds = bid_item.get('indicators', [])
    our_inds = our_param.get('indicators', [])
    if bid_inds and our_inds:
        status, detail = compare_indicators(bid_inds, our_inds)
        if status != 'uncertain':
            return (status, detail)

    bid_nums = extract_numeric(bid_req)
    our_nums = extract_numeric(our_spec)
    if bid_nums and our_nums:
        matched = 0
        for bn, bu in bid_nums:
            for on_val, ou in our_nums:
                if bu == ou:
                    if on_val >= bn:
                        matched += 1
                        break
        if matched == len(bid_nums):
            return ("positive", f"numeric: {matched}/{len(bid_nums)} satisfied")
        elif matched > 0:
            return ("uncertain", f"numeric: {matched}/{len(bid_nums)} partial, needs AI")

    overlap = keyword_overlap(bid_req, our_spec)
    if overlap > 0.5:
        return ("positive", f"keyword similarity: {overlap:.0%}")
    elif overlap > 0.3:
        return ("uncertain", f"keyword similarity: {overlap:.0%}, needs AI")
    else:
        return ("uncertain", f"keyword similarity: {overlap:.0%}, needs AI")


def find_best_match(bid_item: dict, our_params: list) -> tuple:
    """Find the best matching param in our_params for bid_item.
    Returns (status, matched_param_or_None, detail).
    """
    best_status, best_param, best_detail = ("uncertain", None, "no match found")
    for p in our_params:
        status, detail = quick_match(bid_item, p)
        if status == 'positive':
            return (status, p, detail)
        if status == 'uncertain' and best_status == 'uncertain':
            if p.get('category') == bid_item.get('category'):
                best_status, best_param, best_detail = (status, p, detail)
    if best_param is None and our_params:
        best_param = our_params[0]
    return (best_status, best_param, best_detail)
