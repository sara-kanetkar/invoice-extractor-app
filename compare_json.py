import json

def compare_json_data(data1_str, data2_str):
    try:
        data1 = json.loads(data1_str)
        data2 = json.loads(data2_str)
        result = []

        keys = set(data1.keys()).union(data2.keys())
        for key in sorted(keys):
            if key not in data1:
                result.append(f"{key} missing in File 1")
                continue
            if key not in data2:
                result.append(f"{key} missing in File 2")
                continue

            item1 = data1[key]
            item2 = data2[key]

            def extract_value(item):
                if isinstance(item, dict):
                    return str(item.get("value", "")).lower()
                return str(item).lower()

            val1 = extract_value(item1)
            val2 = extract_value(item2)

            if val1 == val2:
                result.append(f"✅ {key} matches")
            else:
                result.append(f"❌ {key} mismatch → {val1} ≠ {val2}")

        return result
    except Exception as e:
        return [f"Error parsing files: {str(e)}"]
