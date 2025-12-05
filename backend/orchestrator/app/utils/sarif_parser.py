import json


def parse_sarif(sarif_data):
    data = json.loads(sarif_data)
    findings = []
    runs = data.get("runs", [])
    for run in runs:
        results = run.get("results", [])
        for r in results:
            rule_id = r.get("ruleId") or r.get("ruleId", "")
            message = r.get("message", {}).get("text", "")
            level = r.get("level", "warning") # some serifs use level properties
            locations = r.get("locations", [])
            if locations:
                physical = locations[0].get("physicalLocation", {})
                artifact = physical.get("artifactLocation", {}).get("uri", "")
                region = physical.get("region", {})
                start = region.get("startline", 0)
                end = region.get("endline", start)
            else:
                artifact, start, end = "", 0, 0
            findings.append({
                "file_path" : artifact,
                "start_line" : start,
                "end_line" : end,
                "rule_id" : rule_id,
                "message" : message,
                "severity" : level,
                "raw" : r
            })        

    return findings
    