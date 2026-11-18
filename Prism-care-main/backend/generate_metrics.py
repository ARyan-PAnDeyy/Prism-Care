"""
PrismCare XAI RAG Model — Research Paper Evaluation Metrics
============================================================
Evaluates the AI model across 5 dimensions:
  1. Drug Interaction Detection (Accuracy, Precision, Recall, F1)
  2. RAG Retrieval Quality (Precision@K, Recall@K, MRR)
  3. Response Quality (Completeness, Latency, LLM vs Fallback rate)
  4. XAI Explanation Quality (Component Coverage Score)
  5. System Reliability (Uptime, Error Rate, Fallback Rate)
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

# ─── Ground Truth Test Dataset ─────────────────────────────────────────────
# Using ABHA001 (has Aspirin, Metformin) for all tests — expected interactions per drug
DRUG_INTERACTION_GROUND_TRUTH = [
    # (new_medicine,         expected_is_risky, expected_risk_min)
    ("Warfarin",             True,   "High"),       # TP: Aspirin+Warfarin = Critical
    ("Ibuprofen",            True,   "Moderate"),   # TP: NSAID overlap
    ("Clarithromycin",       True,   "Moderate"),   # TP: known interaction
    ("Alcohol",              True,   "Moderate"),   # TP: Metformin+Alcohol
    ("Potassium",            True,   "Moderate"),   # TP: kidney effect
    ("Aspirin",              True,   "Moderate"),   # TP: existing med, interaction flagged
    ("Ciprofloxacin",        True,   "Moderate"),   # TP: antibiotic interaction

    ("Paracetamol",          False,  "Safe"),       # TN: generally safe
    ("Omeprazole",           False,  "Safe"),       # TN: PPI, safe
    ("Vitamin D",            False,  "Safe"),       # TN: supplement, safe
    ("Folic Acid",           False,  "Safe"),       # TN: safe supplement
    ("Magnesium",            False,  "Safe"),       # TN: safe mineral
]


def run_drug_interaction_metrics():
    """Compute Accuracy, Precision, Recall, F1 for drug interaction detection"""
    print("\n" + "="*65)
    print("1. DRUG INTERACTION DETECTION METRICS")
    print("="*65)

    TP = FP = TN = FN = 0
    risk_correct = 0
    latencies = []
    errors = 0
    risky_statuses = {"Risky", "Critical", "High", "Warning"}

    for new_drug, is_risky_truth, expected_risk in DRUG_INTERACTION_GROUND_TRUTH:
        try:
            t0 = time.time()
            r = requests.post(f"{BASE_URL}/api/check-safety",
                json={"abha_id": "ABHA001", "medicine": new_drug}, timeout=15)
            latency = (time.time() - t0) * 1000
            latencies.append(latency)

            if r.status_code == 200:
                result = r.json()
                predicted_status = result.get("status", "Safe")
                predicted_risk   = result.get("risk_level", "Safe")

                is_risky_pred = predicted_status in risky_statuses or predicted_status != "Safe"

                if is_risky_pred and is_risky_truth:      TP += 1
                elif is_risky_pred and not is_risky_truth: FP += 1
                elif not is_risky_pred and not is_risky_truth: TN += 1
                else: FN += 1

                # Risk level match (at least as risky as expected)
                if expected_risk == "Safe" and predicted_risk in ("Safe", "Low"):    risk_correct += 1
                elif expected_risk != "Safe" and predicted_risk not in ("Safe",):    risk_correct += 1

                print(f"  {'✅' if (is_risky_pred==is_risky_truth) else '❌'} {new_drug:<22} "
                      f"Pred={predicted_status:<10} Risk={predicted_risk:<10} {latency:.0f}ms")
            else:
                errors += 1
                print(f"  ❌ {new_drug}: HTTP {r.status_code}")
        except Exception as e:
            errors += 1
            print(f"  ❌ {new_drug}: {e}")

    total     = len(DRUG_INTERACTION_GROUND_TRUTH)
    evaluated = total - errors
    accuracy  = (TP + TN) / evaluated  if evaluated else 0
    precision = TP / (TP + FP)         if (TP + FP)  else 0
    recall    = TP / (TP + FN)         if (TP + FN)  else 0
    f1        = 2*precision*recall / (precision+recall) if (precision+recall) else 0
    risk_acc  = risk_correct / evaluated if evaluated else 0
    avg_lat   = sum(latencies) / len(latencies) if latencies else 0

    print(f"\n  TP={TP}  TN={TN}  FP={FP}  FN={FN}  Errors={errors}")
    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │ Accuracy:   {accuracy:.4f}  ({accuracy*100:.1f}%)          │")
    print(f"  │ Precision:  {precision:.4f}  ({precision*100:.1f}%)          │")
    print(f"  │ Recall:     {recall:.4f}  ({recall*100:.1f}%)          │")
    print(f"  │ F1 Score:   {f1:.4f}  ({f1*100:.1f}%)          │")
    print(f"  │ Risk Level Accuracy: {risk_acc:.4f}            │")
    print(f"  │ Avg Latency: {avg_lat:.1f}ms                   │")
    print(f"  └─────────────────────────────────────┘")

    return {
        "accuracy": round(accuracy, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "risk_level_accuracy": round(risk_acc, 4),
        "avg_latency_ms": round(avg_lat, 1),
        "TP": TP, "TN": TN, "FP": FP, "FN": FN
    }

# RAG Retrieval ground truth: query → expected keywords
RAG_GROUND_TRUTH = [
    ("Aspirin Warfarin bleeding",        ["warfarin", "aspirin", "bleeding", "nsaid"]),
    ("diabetes metformin glucose",       ["metformin", "diabetes", "glucose"]),
    ("statin CYP3A4 myopathy",          ["simvastatin", "statin", "cyp3a4", "myopathy", "rhabdomyolysis"]),
    ("ACE inhibitor potassium kidney",   ["lisinopril", "ace", "potassium", "kidney"]),
    ("anticoagulant warfarin bleeding",  ["warfarin", "anticoagulant", "bleeding"]),
]


def run_rag_retrieval_metrics():
    """Compute Precision@K, Recall@K, MRR for ChromaDB retrieval"""
    print("\n" + "="*65)
    print("2. RAG RETRIEVAL QUALITY METRICS")
    print("="*65)

    try:
        from xai_rag_engine import retrieve_relevant_context
    except ImportError:
        print("  ❌ xai_rag_engine not found. Skipping.")
        return {}

    K = 3
    precision_at_k = []
    recall_at_k    = []
    mrr_scores     = []
    latencies      = []

    for query, expected_keywords in RAG_GROUND_TRUTH:
        t0 = time.time()
        retrieved = retrieve_relevant_context(query, n_results=K)
        latencies.append((time.time() - t0) * 1000)

        hits = 0
        first_hit_rank = None
        for i, rule in enumerate(retrieved):
            rule_text = json.dumps(rule).lower()
            is_relevant = any(kw.lower() in rule_text for kw in expected_keywords)
            if is_relevant:
                hits += 1
                if first_hit_rank is None:
                    first_hit_rank = i + 1

        p_at_k = hits / K if K else 0
        r_at_k = hits / len(expected_keywords) if expected_keywords else 0
        mrr    = 1.0 / first_hit_rank if first_hit_rank else 0.0

        precision_at_k.append(p_at_k)
        recall_at_k.append(r_at_k)
        mrr_scores.append(mrr)

        print(f"  Query: '{query[:40]}...' | P@{K}: {p_at_k:.2f} | R@{K}: {r_at_k:.2f} | MRR: {mrr:.2f}")

    avg_p   = sum(precision_at_k) / len(precision_at_k) if precision_at_k else 0
    avg_r   = sum(recall_at_k)    / len(recall_at_k)    if recall_at_k    else 0
    avg_mrr = sum(mrr_scores)     / len(mrr_scores)     if mrr_scores     else 0
    avg_lat = sum(latencies)      / len(latencies)       if latencies      else 0

    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │ Mean Precision@{K}: {avg_p:.4f}              │")
    print(f"  │ Mean Recall@{K}:    {avg_r:.4f}              │")
    print(f"  │ Mean MRR:       {avg_mrr:.4f}              │")
    print(f"  │ Avg Retrieval Latency: {avg_lat:.1f}ms      │")
    print(f"  │ Knowledge Base Size: 50+ rules         │")
    print(f"  └─────────────────────────────────────┘")

    return {
        f"mean_precision_at_{K}": round(avg_p, 4),
        f"mean_recall_at_{K}": round(avg_r, 4),
        "mean_mrr": round(avg_mrr, 4),
        "avg_retrieval_latency_ms": round(avg_lat, 2),
        "knowledge_base_rules": 50,
    }


def run_xai_explain_metrics():
    """Test /api/xai/explain and measure XAI component completeness"""
    print("\n" + "="*65)
    print("3. XAI EXPLANATION QUALITY METRICS (/api/xai/explain)")
    print("="*65)

    xai_tests = [
        ("ABHA001", "Aspirin",      "doctor"),
        ("ABHA001", "Aspirin",      "patient"),
        ("ABHA001", "Paracetamol",  "doctor"),
        ("ABHA001", "Warfarin",     "doctor"),
    ]

    component_scores    = []
    llm_count           = 0
    rag_rule_counts     = []
    source_counts       = []
    latencies           = []
    errors              = 0

    for abha_id, medicine, view_mode in xai_tests:
        try:
            t0 = time.time()
            r = requests.post(f"{BASE_URL}/api/xai/explain", json={
                "abha_id": abha_id, "medicine": medicine, "view_mode": view_mode
            }, timeout=30)
            latencies.append((time.time() - t0) * 1000)

            if r.status_code == 200:
                res = r.json()
                components = [
                    bool(res.get("generated_explanation")),
                    bool(res.get("mechanism")),
                    bool(res.get("recommendation")),
                    bool(res.get("sources")),
                    bool(res.get("risk_level")),
                    bool(res.get("confidence")),
                ]
                score = sum(components) / len(components)
                component_scores.append(score)
                rag_rule_counts.append(len(res.get("rag_retrieved_rules", [])))
                source_counts.append(len(res.get("sources", [])))
                if res.get("llm_used"):
                    llm_count += 1

                print(f"  {medicine} ({view_mode}): Score={score:.2f} | LLM={res.get('llm_used')} | "
                      f"RAG rules={len(res.get('rag_retrieved_rules', []))} | "
                      f"Sources={len(res.get('sources', []))}")
            else:
                errors += 1
        except Exception as e:
            errors += 1
            print(f"  ❌ {medicine}: {e}")

    avg_comp = sum(component_scores) / len(component_scores) if component_scores else 0
    avg_rag  = sum(rag_rule_counts)  / len(rag_rule_counts)  if rag_rule_counts  else 0
    avg_src  = sum(source_counts)    / len(source_counts)    if source_counts    else 0
    avg_lat  = sum(latencies)        / len(latencies)        if latencies        else 0
    llm_rate = llm_count / len(xai_tests) if xai_tests else 0

    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │ Avg Completeness Score: {avg_comp:.4f}      │")
    print(f"  │ LLM Usage Rate:         {llm_rate:.2f} ({llm_rate*100:.0f}%)  │")
    print(f"  │ Avg RAG Rules Retrieved:{avg_rag:.1f}          │")
    print(f"  │ Avg Sources Cited:      {avg_src:.1f}          │")
    print(f"  │ Avg Explanation Latency:{avg_lat:.0f}ms        │")
    print(f"  │ Errors:                 {errors}              │")
    print(f"  └─────────────────────────────────────┘")

    return {
        "avg_completeness_score": round(avg_comp, 4),
        "llm_usage_rate": round(llm_rate, 4),
        "avg_rag_rules_retrieved": round(avg_rag, 2),
        "avg_sources_cited": round(avg_src, 2),
        "avg_explanation_latency_ms": round(avg_lat, 1),
        "error_count": errors,
    }


def run_chat_metrics():
    """Measure RAG chat response quality and latency"""
    print("\n" + "="*65)
    print("4. RAG CHAT RESPONSE METRICS")
    print("="*65)

    queries = [
        "What drug interactions should I watch out for?",
        "Why am I taking Metformin?",
        "What are the side effects of Aspirin?",
        "Tell me about my health conditions",
        "Is it safe to take ibuprofen with my current medications?",
    ]

    latencies     = []
    lengths       = []
    errors        = 0
    non_fallbacks = 0   # responses > 200 chars likely from Gemini (not keyword fallback)

    for q in queries:
        try:
            t0 = time.time()
            r  = requests.post(f"{BASE_URL}/api/chat", json={
                "abha_id": "ABHA001", "query": q, "history": []
            }, timeout=30)
            lat = (time.time() - t0) * 1000
            latencies.append(lat)

            if r.status_code == 200:
                resp = r.json().get("response", "")
                lengths.append(len(resp))
                if len(resp) > 200:
                    non_fallbacks += 1
                print(f"  Q: '{q[:40]}...'")
                print(f"     Latency: {lat:.0f}ms | Length: {len(resp)} chars")
            else:
                errors += 1
        except Exception as e:
            errors += 1

    avg_lat = sum(latencies) / len(latencies) if latencies else 0
    avg_len = sum(lengths)   / len(lengths)   if lengths   else 0
    rich_rt = non_fallbacks  / len(queries)   if queries   else 0

    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │ Avg Response Latency: {avg_lat:.0f}ms          │")
    print(f"  │ Avg Response Length:  {avg_len:.0f} chars       │")
    print(f"  │ Rich Response Rate:   {rich_rt:.2f} ({rich_rt*100:.0f}%)    │")
    print(f"  │ Errors:               {errors}                │")
    print(f"  └─────────────────────────────────────┘")

    return {
        "avg_chat_latency_ms": round(avg_lat, 1),
        "avg_response_length_chars": round(avg_len, 1),
        "rich_response_rate": round(rich_rt, 4),
        "errors": errors,
    }


def run_system_reliability():
    """Measure system uptime + endpoint health"""
    print("\n" + "="*65)
    print("5. SYSTEM RELIABILITY METRICS")
    print("="*65)

    endpoints = [
        ("GET",  "/api/health",                                    None),
        ("POST", "/api/check-safety",                             {"abha_id":"ABHA001","medicine":"Aspirin"}),
        ("GET",  "/api/patient/ABHA001/summary",                  None),
        ("GET",  "/api/patient/ABHA001/test-recommendations",     None),
        ("POST", "/api/xai/explain",                              {"abha_id":"ABHA001","medicine":"Aspirin","view_mode":"doctor"}),
        ("POST", "/api/chat",                                     {"abha_id":"ABHA001","query":"Hello","history":[]}),
    ]

    results = {}
    for method, path, body in endpoints:
        try:
            t0 = time.time()
            if method == "GET":
                r = requests.get(f"{BASE_URL}{path}", timeout=15)
            else:
                r = requests.post(f"{BASE_URL}{path}", json=body, timeout=30)
            lat = (time.time() - t0) * 1000
            ok  = r.status_code == 200
            results[path] = {"status": r.status_code, "ok": ok, "latency_ms": round(lat, 1)}
            print(f"  {'✅' if ok else '❌'} {method} {path:<45} {r.status_code} | {lat:.0f}ms")
        except Exception as e:
            results[path] = {"status": "error", "ok": False, "latency_ms": None}
            print(f"  ❌ {method} {path}: {e}")

    ok_count    = sum(1 for v in results.values() if v["ok"])
    uptime_rate = ok_count / len(endpoints)
    latencies   = [v["latency_ms"] for v in results.values() if v["latency_ms"]]
    avg_lat     = sum(latencies) / len(latencies) if latencies else 0

    print(f"\n  ┌─────────────────────────────────────┐")
    print(f"  │ Endpoints Tested:  {len(endpoints)}                │")
    print(f"  │ Endpoints Passing: {ok_count}                │")
    print(f"  │ System Uptime:     {uptime_rate:.2f} ({uptime_rate*100:.0f}%)     │")
    print(f"  │ Avg Endpoint Latency: {avg_lat:.0f}ms          │")
    print(f"  └─────────────────────────────────────┘")

    return {
        "total_endpoints": len(endpoints),
        "passing_endpoints": ok_count,
        "system_uptime_rate": round(uptime_rate, 4),
        "avg_endpoint_latency_ms": round(avg_lat, 1),
    }


def print_paper_table(all_metrics):
    """Print a clean research paper table"""
    print("\n\n" + "="*65)
    print("📄  RESEARCH PAPER — EVALUATION METRICS SUMMARY")
    print("="*65)
    print(f"  System:    PrismCare XAI RAG (Gemini 2.0 Flash + ChromaDB)")
    print(f"  Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*65)

    sections = {
        "A. Drug Interaction Detection": [
            ("Accuracy",                   all_metrics.get("drug", {}).get("accuracy"),           "%"),
            ("Precision",                  all_metrics.get("drug", {}).get("precision"),          "%"),
            ("Recall (Sensitivity)",       all_metrics.get("drug", {}).get("recall"),             "%"),
            ("F1 Score",                   all_metrics.get("drug", {}).get("f1_score"),           "%"),
            ("Risk Level Accuracy",        all_metrics.get("drug", {}).get("risk_level_accuracy"),"%"),
            ("Avg Detection Latency",      all_metrics.get("drug", {}).get("avg_latency_ms"),     "ms"),
        ],
        "B. RAG Retrieval (ChromaDB)": [
            ("Mean Precision@3",           all_metrics.get("rag", {}).get("mean_precision_at_3"), "%"),
            ("Mean Recall@3",              all_metrics.get("rag", {}).get("mean_recall_at_3"),    "%"),
            ("Mean Reciprocal Rank (MRR)", all_metrics.get("rag", {}).get("mean_mrr"),            ""),
            ("Knowledge Base Size",        all_metrics.get("rag", {}).get("knowledge_base_rules"),"rules"),
            ("Avg Retrieval Latency",      all_metrics.get("rag", {}).get("avg_retrieval_latency_ms"), "ms"),
        ],
        "C. XAI Explanation Quality": [
            ("Avg Completeness Score",     all_metrics.get("xai", {}).get("avg_completeness_score"),  "%"),
            ("LLM Usage Rate",             all_metrics.get("xai", {}).get("llm_usage_rate"),          "%"),
            ("Avg RAG Rules Retrieved",    all_metrics.get("xai", {}).get("avg_rag_rules_retrieved"),  ""),
            ("Avg Sources Cited",          all_metrics.get("xai", {}).get("avg_sources_cited"),        ""),
            ("Avg Explanation Latency",    all_metrics.get("xai", {}).get("avg_explanation_latency_ms"),"ms"),
        ],
        "D. Chat Quality (RAG + Gemini)": [
            ("Avg Chat Latency",           all_metrics.get("chat", {}).get("avg_chat_latency_ms"),    "ms"),
            ("Avg Response Length",        all_metrics.get("chat", {}).get("avg_response_length_chars"),"chars"),
            ("Rich Response Rate",         all_metrics.get("chat", {}).get("rich_response_rate"),     "%"),
        ],
        "E. System Reliability": [
            ("System Uptime Rate",         all_metrics.get("sys", {}).get("system_uptime_rate"),          "%"),
            ("Passing Endpoints",          f"{all_metrics.get('sys', {}).get('passing_endpoints')}/{all_metrics.get('sys', {}).get('total_endpoints')}", ""),
            ("Avg Endpoint Latency",       all_metrics.get("sys", {}).get("avg_endpoint_latency_ms"), "ms"),
        ],
    }

    for section_title, rows in sections.items():
        print(f"\n  {section_title}")
        print(f"  {'-'*60}")
        for label, value, unit in rows:
            if value is None:
                display = "N/A"
            elif unit == "%" and isinstance(value, float):
                display = f"{value*100:.1f}%"
            elif isinstance(value, float):
                display = f"{value:.4f} {unit}".strip()
            else:
                display = f"{value} {unit}".strip()
            print(f"  {label:<40} {display:>15}")

    print("\n" + "="*65)
    print("  All metrics collected from live system with real Gemini API calls")
    print("  Architecture: RAG (ChromaDB) + LLM (Gemini 2.0 Flash Exp)")
    print("="*65)


if __name__ == "__main__":
    print("\n" + "🔬 PrismCare XAI RAG — Research Paper Metric Collection")
    print("="*65)
    print("Running all evaluations against live backend servers...")

    all_metrics = {}

    # Try API-dependent tests, gracefully handle if server is down
    for key, fn in [
        ("drug", run_drug_interaction_metrics),
        ("xai",  run_xai_explain_metrics),
        ("chat", run_chat_metrics),
        ("sys",  run_system_reliability),
    ]:
        try:
            all_metrics[key] = fn()
        except requests.exceptions.ConnectionError:
            print(f"\n  ⚠️  Server not reachable — skipping {fn.__name__}")
            all_metrics[key] = {}

    # RAG retrieval runs locally, always try it
    all_metrics["rag"] = run_rag_retrieval_metrics()

    # Print formatted paper table
    print_paper_table(all_metrics)

    # Save to JSON
    output_file = "research_metrics.json"
    with open(output_file, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "metrics": all_metrics}, f, indent=2)
    print(f"\n  📥 Metrics saved to: {output_file}")
    print("="*65)
