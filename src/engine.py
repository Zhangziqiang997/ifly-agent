"""Orchestrator: ties Layer 1 (parser), Layer 2 (matcher), Layer 3 (advisor) together."""
from data_loader import load_competitors, load_xunfei, load_bid
from parser import find_best_match
from matcher import identify_controller
from advisor import batch_analyze


def run_analysis(bid_filename: str = "sample-bid.json") -> dict:
    """Run the full 3-layer bidding analysis.

    Returns:
        {project, controller: {vendor, confidence, scores, hits, anomalies},
         matching: [{seq, category, name, bid_req, xunfei_spec, deviation, match_method, detail, suggestion}],
         summary: {total, positive, negative_wording, negative_real}}
    """
    competitors = load_competitors()
    xunfei = load_xunfei()
    bid = load_bid(filename=bid_filename)

    xunfei_params = xunfei.get('params', [])
    bid_items = bid.get('items', [])

    # Layer 2: Controller identification (programmatic, no AI)
    controller_result = identify_controller(bid_items, competitors)

    # Layer 1: Try programmatic match for each bid item
    matching = []
    uncertain_items = []

    for item in bid_items:
        status, matched_param, detail = find_best_match(item, xunfei_params)

        if status == 'positive':
            matching.append({
                'seq': item['seq'],
                'category': item.get('category', ''),
                'name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'deviation': 'positive',
                'match_method': 'program',
                'detail': detail,
                'suggestion': None
            })
        elif status == 'negative':
            matching.append({
                'seq': item['seq'],
                'category': item.get('category', ''),
                'name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'deviation': 'negative_real',
                'match_method': 'program',
                'detail': detail,
                'suggestion': None
            })
            uncertain_items.append({
                'seq': item['seq'],
                'bid_name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_name': matched_param.get('name', '') if matched_param else '',
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'category': item.get('category', '')
            })
        else:  # uncertain
            uncertain_items.append({
                'seq': item['seq'],
                'bid_name': item.get('name', ''),
                'bid_req': item.get('requirement', ''),
                'xunfei_name': matched_param.get('name', '') if matched_param else '',
                'xunfei_spec': matched_param.get('spec', '') if matched_param else '',
                'category': item.get('category', '')
            })

    # Layer 3: AI batch analysis for all uncertain items (1 API call total)
    if uncertain_items:
        ai_results = batch_analyze(uncertain_items, xunfei_params)
        ai_map = {r.get('seq', 0): r for r in ai_results}

        for item in uncertain_items:
            seq = item['seq']
            ai = ai_map.get(seq, {})
            existing = [m for m in matching if m['seq'] == seq]
            if existing:
                existing[0]['deviation'] = ai.get('deviation', 'negative_wording')
                existing[0]['match_method'] = 'ai_semantic'
                existing[0]['suggestion'] = ai.get('suggestion', '')
            else:
                matching.append({
                    'seq': seq,
                    'category': item.get('category', ''),
                    'name': item.get('bid_name', ''),
                    'bid_req': item.get('bid_req', ''),
                    'xunfei_spec': item.get('xunfei_spec', ''),
                    'deviation': ai.get('deviation', 'negative_real'),
                    'match_method': 'ai_semantic',
                    'detail': ai.get('explanation', ''),
                    'suggestion': ai.get('suggestion', '')
                })

    matching.sort(key=lambda m: m['seq'])

    summary = {
        'total': len(matching),
        'positive': sum(1 for m in matching if m['deviation'] == 'positive'),
        'negative_wording': sum(1 for m in matching if m['deviation'] == 'negative_wording'),
        'negative_real': sum(1 for m in matching if m['deviation'] == 'negative_real')
    }

    return {
        'project': bid.get('project', ''),
        'controller': controller_result,
        'matching': matching,
        'summary': summary
    }
