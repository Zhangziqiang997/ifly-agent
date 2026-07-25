"""Layer 2: Controller identification -- find unique features, score each vendor."""
from parser import quick_match, find_best_match


def match_with_competitor(bid_item: dict, comp_params: list) -> bool:
    """Check if a competitor satisfies the bidding requirement. Returns True/False."""
    status, _, _ = find_best_match(bid_item, comp_params)
    return status == 'positive'


def match_loose(bid_item: dict, comp_params: list) -> bool:
    """More lenient match for controller identification.
    Counts positive + uncertain as satisfied, to catch partial matches as suspicious."""
    status, _, _ = find_best_match(bid_item, comp_params)
    return status in ('positive', 'uncertain')


def identify_controller(bid_items: list, competitors: dict) -> dict:
    """Identify which competitor the bidding document is designed for.

    Args:
        bid_items: [{seq, category, name, requirement, indicators, star_mark, triangle_mark}, ...]
        competitors: {'xiwo': {vendor, product, params: [...]}, 'honghe': {...}, ...}

    Returns:
        {vendor, confidence, scores: {vendor_name: unique_feature_count},
         hits: [{seq, param_name, hit_vendor, reason}],
         anomalies: [{seq, param_name, reason}]}
    """
    scores = {name: 0 for name in competitors}
    hits = []
    anomalies = []

    for item in bid_items:
        satisfied_by = []
        for comp_name, comp_data in competitors.items():
            if match_with_competitor(item, comp_data.get('params', [])):
                satisfied_by.append(comp_name)

        if len(satisfied_by) == 1:
            vendor = satisfied_by[0]
            scores[vendor] += 1
            hits.append({
                'seq': item.get('seq'),
                'param_name': item.get('name', ''),
                'hit_vendor': vendor,
                'reason': f'Only {vendor} satisfies this requirement'
            })
        elif len(satisfied_by) == 0:
            anomalies.append({
                'seq': item.get('seq'),
                'param_name': item.get('name', ''),
                'reason': 'No vendor in database satisfies this requirement'
            })

    total_valid = len(bid_items) - len(anomalies)
    total_hits = sum(scores.values())

    if total_hits > 0 and total_valid > 0:
        controller = max(scores, key=scores.get)
        confidence = total_hits / total_valid
        vendor_name = competitors.get(controller, {}).get('vendor', controller)
    else:
        controller = max(scores, key=scores.get) if scores else list(competitors.keys())[0]
        vendor_name = competitors.get(controller, {}).get('vendor', 'Unable to determine')
        confidence = 0

    return {
        'vendor': vendor_name,
        'confidence': round(confidence, 2),
        'scores': {competitors.get(k, {}).get('vendor', k): v for k, v in scores.items()},
        'hits': hits,
        'anomalies': anomalies
    }
