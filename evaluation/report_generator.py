import json

def generate_report(summary_metrics, case_results, output_path="evaluation_report.json"):
    report = {
        "summary": summary_metrics,
        "case_details": case_results
    }
    
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\n--- Evaluation Summary ---")
    print(json.dumps(summary_metrics, indent=2))
    print(f"\nReport written to {output_path}")
