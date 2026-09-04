import sys, json, openpyxl
from datetime import datetime, date, timezone

def d2s(v):
    if isinstance(v, datetime):
        return v.date().isoformat()
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, str):
        # Some months' "Day" column comes through as text (e.g. "9/01/2026")
        # instead of a real Excel date -- normalise it the same way, so the
        # dashboard's date sort/format never has to know which month behaved.
        for fmt in ('%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d'):
            try:
                return datetime.strptime(v.strip(), fmt).date().isoformat()
            except ValueError:
                continue
    return v

def extract(path, month_code):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)

    # --- South Africa Visit Plan: authoritative MTD target/actual + weekly split ---
    ws = wb['South Africa Visit Plan']
    hdr = next(ws.iter_rows(min_row=1, max_row=1, values_only=True))
    idx = {h: i for i, h in enumerate(hdr)}
    tgt_i, act_i = idx['Total Target (Oct21)'], idx['Actual (Oct 21 MTD)']
    wk_tgt_i = [idx['Week 1 Target'], idx['Week 2 Target'], idx['Week 3 Target'], idx['Week 4 Target'], idx['Week 5 Target']]
    wk_act_i = [idx['WK1 Actual'], idx['Wk 2 Actual'], idx['Wk 3 Actual'], idx['Wk 4 Actual'], idx['Wk 5 Actual']]
    # Real "Channel" column (Carin, 2026-08-29) -- looked up by name like
    # the columns above, not a hardcoded position.
    channel_i = idx['Channel']

    storeRows = []
    rep_agg = {}  # empId -> {name, region, repType, lineManager, banner, channel, division, storeCount, target, actual}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        empId = str(row[1])
        name = row[2]
        region = row[3]
        repType = row[4]
        lineManager = row[6]
        banner = row[7]
        channel = row[channel_i]
        division = row[8]
        store = row[12]
        target = row[tgt_i] or 0
        actual = row[act_i] or 0
        wk = [ (row[wk_tgt_i[i]] or 0, row[wk_act_i[i]] or 0) for i in range(5) ]

        storeRows.append({
            'empId': empId, 'repName': name, 'region': region, 'banner': banner, 'channel': channel,
            'division': division, 'lineManager': lineManager, 'repType': repType,
            'store': store, 'target': target, 'actual': actual, 'visited': actual > 0,
            'wk1Target': wk[0][0], 'wk1Actual': wk[0][1],
            'wk2Target': wk[1][0], 'wk2Actual': wk[1][1],
            'wk3Target': wk[2][0], 'wk3Actual': wk[2][1],
            'wk4Target': wk[3][0], 'wk4Actual': wk[3][1],
            'wk5Target': wk[4][0], 'wk5Actual': wk[4][1],
        })

        if empId not in rep_agg:
            rep_agg[empId] = {
                'empId': empId, 'name': name, 'region': region, 'repType': repType,
                'lineManager': lineManager, 'banner': banner, 'channel': channel, 'division': division,
                'storeCount': 0, 'target': 0, 'actual': 0
            }
        r = rep_agg[empId]
        r['storeCount'] += 1
        r['target'] += target
        r['actual'] += actual

    mtdReps = []
    for r in rep_agg.values():
        progress = round(r['actual'] / r['target'] * 100, 1) if r['target'] else 0
        mtdReps.append({**r, 'progress': progress})

    totalTarget = sum(r['target'] for r in mtdReps)
    totalActual = sum(r['actual'] for r in mtdReps)
    overallProgress = round(totalActual / totalTarget * 100, 1) if totalTarget else 0

    # --- Time Gone ---
    tg_ws = wb['Time Gone']
    tg_row = next(tg_ws.iter_rows(min_row=2, max_row=2, values_only=True))
    timeGone = {
        'start': d2s(tg_row[0]), 'end': d2s(tg_row[1]), 'today': d2s(tg_row[2]),
        'pct': round((tg_row[5] or 0) * 100, 1)
    }

    meta = {
        'totalTarget': totalTarget, 'totalActual': totalActual, 'overallProgress': overallProgress,
        'repCount': len(mtdReps), 'storeCount': len(storeRows), 'timeGone': timeGone,
        'generatedAt': datetime.now(timezone.utc).isoformat()
    }

    # --- Daily sheet: per-day per-store-rep rows (for trend chart / daily visit log) ---
    dw = wb['Daily']
    daily_hdr = next(dw.iter_rows(min_row=1, max_row=1, values_only=True))
    daily_idx = {h: i for i, h in enumerate(daily_hdr)}
    daily_channel_i = daily_idx.get('Channel')  # not confirmed to exist on this sheet -- degrade to None if absent
    dailyRows = []
    dates = set()
    for row in dw.iter_rows(min_row=2, values_only=True):
        if row[0] is None:
            continue
        dt = d2s(row[0])
        dates.add(dt)
        dailyRows.append({
            'date': dt, 'empId': str(row[14]), 'name': row[15], 'repType': row[16],
            'lineManager': row[20], 'region': row[12], 'banner': row[13],
            'channel': row[daily_channel_i] if daily_channel_i is not None else None,
            'division': row[10], 'store': row[2], 'target': row[-2] or 0, 'actual': row[-1] or 0
        })

    data = {
        'meta': meta, 'mtdReps': mtdReps, 'storeRows': storeRows,
        'dailyRows': dailyRows, 'dates': sorted(dates)
    }
    return data

if __name__ == '__main__':
    path, month_code, out_path, var_name = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    data = extract(path, month_code)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f'window.{var_name} = ')
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
        f.write(';\n')
    print('wrote', out_path, '-> meta:', data['meta'])
